from langchain_ollama.llms import OllamaLLM
from langchain_community.document_loaders import YoutubeLoader
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_ollama import OllamaEmbeddings
from langchain_community.vectorstores import FAISS

# 1. Define the LLM
llm = OllamaLLM(model="phi4")  # Or your preferred model

# Instantiate the class embeddings WITH the model name
embeddings = OllamaEmbeddings(model="phi4")  # Change: added the parameter `model`


def create_vector_db_from_youtube(video_url: str):
    """Creates a vector database from a YouTube video transcript.

    Args:
        video_url: The URL of the YouTube video.

    Returns:
        A FAISS vector database.
    """
    loader = YoutubeLoader.from_youtube_url(video_url)
    transcript = loader.load()

    # --- Optimization 1: Larger chunk size, smaller overlap ---
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=100) # increase the chunk_size
    docs = text_splitter.split_documents(transcript)

    db = FAISS.from_documents(docs, embeddings)
    return db


def get_response_from_query(db, query, k=2): # Change: reduced k
    """Gets a response to a query based on the vector database.

    Args:
        db: The FAISS vector database.
        query: The user's question.
        k: The number of nearest neighbors to consider.

    Returns:
        The LLM's response to the query.
    """
    # --- Optimization 2: Reduced k in similarity_search ---
    docs = db.similarity_search(query, k=k)
    docs_page_content = " ".join([d.page_content for d in docs])

    llm = OllamaLLM(model="phi4")
    prompt = PromptTemplate(
        input_variables=["question", "docs"],
        template="""
        You are a helpful Youtube assistant that can answer questions about videos based on the video's transcript.
        
        Answer the following question: {question}
        By searching the following video transcript: {docs}
        
        Only use the factual information from the transcript to answer the question.

        if you feel like you don't have enough information to answer the question, say "I don't know".
        
        Your answers should be verbose and detailed.
        """,
    )

    chain = prompt | llm
    response = chain.invoke({"question": query, "docs": docs_page_content})

    return response
