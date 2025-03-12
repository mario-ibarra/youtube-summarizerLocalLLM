import streamlit as st
from langchain_helper import create_vector_db_from_youtube, get_response_from_query
import textwrap

st.title('Youtube Assistant')

with st.sidebar:
    youtube_url = st.sidebar.text_area(
        label="What is the Youtube video URL?",
        max_chars=500  # Increased max_chars for realistic URLs
    )
    query = st.sidebar.text_area(
        label="Ask me about the video?",
        max_chars=500,  # Increased max_chars for realistic queries
        key="query"
    )
    with st.form(key='my_form'):
        submit_button = st.form_submit_button(label='Submit')

if query and youtube_url:
    try:
        db = create_vector_db_from_youtube(youtube_url)
        response = get_response_from_query(db, query)  # Pass db to the function

        # Display the response in the main area
        st.text_area("Response:", value=response, height=600)

    except Exception as e:
        st.error(f"An error occurred: {e}")
        st.error("Please check the YouTube URL or try a different query.")
        # Consider more specific error handling here if needed.
        # For example, catch specific exceptions like `YouTubeUnavailable` or similar if provided by the libraries.
else:
    st.info("Please enter a YouTube URL and a question in the sidebar.")
