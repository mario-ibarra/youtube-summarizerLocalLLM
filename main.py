import streamlit as st
from helper import (
    create_vector_db_from_youtube,
    get_response_from_query,
    save_chat_to_db,
    load_chat_from_db,
    create_vector_db_from_documents,
    llm,
    embeddings
)
import os
from tempfile import NamedTemporaryFile

st.title('AI Assistant Chat')

# Initialize session state variables
if "chat_history" not in st.session_state:
    st.session_state.chat_history = []
if "db" not in st.session_state:
    st.session_state.db = None
if "source_id" not in st.session_state:
    st.session_state.source_id = None
if "source_type" not in st.session_state:
    st.session_state.source_type = None

with st.sidebar:
    st.header("Select Source")
    source_type = st.radio("Choose your source type:", ["YouTube Video", "Document Upload"])
    
    if source_type == "YouTube Video":
        youtube_url = st.text_area(
            label="YouTube video URL",
            max_chars=500,
        )
        source_id = youtube_url
        
        # Button to load the video
        if st.button("Load Video"):
            if youtube_url:
                try:
                    with st.spinner("Loading the video..."):
                        # Check if we need to reset the database
                        if st.session_state.source_type != "YouTube Video" or st.session_state.source_id != youtube_url:
                            st.session_state.db = create_vector_db_from_youtube(youtube_url, embeddings)
                            st.session_state.chat_history = load_chat_from_db(youtube_url, "youtube")
                            st.session_state.source_id = youtube_url
                            st.session_state.source_type = "YouTube Video"
                            st.success("Video loaded successfully!")
                except Exception as e:
                    st.error(f"Error loading video: {e}")
    
    else:  # Document Upload
        uploaded_files = st.file_uploader("Upload your documents", accept_multiple_files=True, type=['pdf', 'docx', 'txt'])
        
        # Button to load documents
        if st.button("Process Documents"):
            if uploaded_files:
                try:
                    with st.spinner("Processing documents..."):
                        # Create a unique source ID for these documents
                        source_id = "-".join([f.name for f in uploaded_files])
                        
                        # Save uploaded files to temporary location
                        temp_files = []
                        for file in uploaded_files:
                            with NamedTemporaryFile(delete=False, suffix=f".{file.name.split('.')[-1]}") as tmp:
                                tmp.write(file.getbuffer())
                                temp_files.append(tmp.name)
                        
                        # Create vector database from documents
                        st.session_state.db = create_vector_db_from_documents(temp_files, embeddings)
                        st.session_state.chat_history = load_chat_from_db(source_id, "document")
                        st.session_state.source_id = source_id
                        st.session_state.source_type = "Document"
                        
                        # Clean up temp files
                        for path in temp_files:
                            os.unlink(path)
                            
                        st.success("Documents processed successfully!")
                except Exception as e:
                    st.error(f"Error processing documents: {e}")

# Main chat interface
st.header("Chat")

# Display the chat history (only showing each message once)
for message in st.session_state.chat_history:
    with st.chat_message(message["role"]):
        st.write(message["content"])

# Input for the user's question
user_question = st.chat_input("Ask a question about the content...")

# Handle user input
if user_question and st.session_state.db:
    # Add the user question to the chat history
    st.session_state.chat_history.append({"role": "user", "content": user_question})

    # Display the user's question (already handled in the history display)
    with st.chat_message("user"):
        st.write(user_question)

    # Get the response from the LLM
    try:
        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                response = get_response_from_query(st.session_state.db, user_question, llm)
                
                # Add the assistant's response to the chat history
                st.session_state.chat_history.append({"role": "assistant", "content": response})
                
                # Display the response (without duplicating)
                st.write(response)

                # Save to DB
                save_chat_to_db(st.session_state.source_id, user_question, response, st.session_state.source_type)
    except Exception as e:
        st.error(f"Error generating response: {e}")

# Show guidance if no source is loaded
if not st.session_state.db:
    st.info("Please load a YouTube video or upload documents to start chatting!")