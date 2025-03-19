from langchain_ollama import OllamaLLM, OllamaEmbeddings
from langchain_community.document_loaders import YoutubeLoader, PyPDFLoader, TextLoader, Docx2txtLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
import sqlite3
from datetime import datetime
import os

# 1. Define the LLM and Embeddings (Centralized)
model_name = "phi4"  # Define the model name as a variable
llm = OllamaLLM(model=model_name)
embeddings = OllamaEmbeddings(model=model_name)

# 2. YouTube handling functions
def create_vector_db_from_youtube(video_url: str, embeddings):
    """Creates a vector database from a YouTube video transcript."""
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db

# 3. Document handling functions
def create_vector_db_from_documents(file_paths, embeddings):
    """Creates a vector database from uploaded documents."""
    documents = []
    
    for file_path in file_paths:
        file_extension = os.path.splitext(file_path)[1].lower()
        
        if file_extension == '.pdf':
            loader = PyPDFLoader(file_path)
        elif file_extension == '.docx':
            loader = Docx2txtLoader(file_path)
        elif file_extension == '.txt':
            loader = TextLoader(file_path)
        else:
            continue  # Skip unsupported file types
            
        documents.extend(loader.load())
    
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100)
    docs = text_splitter.split_documents(documents)
    
    db = FAISS.from_documents(docs, embeddings)
    return db

# 4. Query processing function
def get_response_from_query(db, query, llm, k=2):
    """Gets a response to a query based on the vector database."""
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful assistant that can answer questions about content based on the provided context.

        Answer the following question: {question}
        By searching the following context: {docs}

        Only use the factual information from the context to answer the question.

        If you feel like you don't have enough information to answer the question, say "I don't know".

        Your answers should be verbose and detailed.
        """,
    )

    chain = prompt | llm | StrOutputParser()
    response = chain.invoke({"question": query, "docs": docs_page_content})

    return response

# 5. Database functions
def init_db():
    """Initialize the SQLite database with the required table."""
    conn = sqlite3.connect('ai_assistant.db')
    c = conn.cursor()
    
    c.execute('''
    CREATE TABLE IF NOT EXISTS chat_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        source_id TEXT NOT NULL,
        source_type TEXT NOT NULL,
        user_question TEXT NOT NULL,
        assistant_response TEXT NOT NULL,
        timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
    )
    ''')
    
    conn.commit()
    conn.close()

def save_chat_to_db(source_id, user_question, assistant_response, source_type="youtube"):
    """Save a chat exchange to the database."""
    init_db()
    
    conn = sqlite3.connect('ai_assistant.db')
    c = conn.cursor()
    
    c.execute(
        "INSERT INTO chat_history (source_id, source_type, user_question, assistant_response) VALUES (?, ?, ?, ?)",
        (source_id, source_type, user_question, assistant_response)
    )
    
    conn.commit()
    conn.close()

def load_chat_from_db(source_id, source_type="youtube"):
    """Load chat history for a specific source."""
    init_db()
    
    conn = sqlite3.connect('ai_assistant.db')
    conn.row_factory = sqlite3.Row
    c = conn.cursor()
    
    c.execute(
        "SELECT user_question, assistant_response FROM chat_history WHERE source_id = ? AND source_type = ? ORDER BY timestamp",
        (source_id, source_type)
    )
    
    rows = c.fetchall()
    conn.close()
    
    chat_history = []
    for row in rows:
        chat_history.append({"role": "user", "content": row['user_question']})
        chat_history.append({"role": "assistant", "content": row['assistant_response']})
    
    return chat_history