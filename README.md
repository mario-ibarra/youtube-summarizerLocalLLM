# YouTube Assistant - AI-Powered Video Q\&A

This project is a Streamlit-based application that allows you to ask questions about YouTube videos and get answers directly from the video's transcript, powered by large language models installed locally on your computer. No need to pay for external LLM services such a OpenAI, Gemini, etc.

## Features

*   **YouTube Transcript Processing:** Extracts and processes the transcript of a YouTube video.
*   **Vector Database:** Creates a vector database (using FAISS) from the transcript for efficient similarity search.
*   **Question Answering:** Uses an LLM (Ollama's `phi4` model) to answer your questions based on the video's content.
*   **Streamlit UI:** Provides a user-friendly interface for entering the YouTube URL and your question.
*   **Error Handling:** Implements error handling to provide feedback to the user.
*   **Modular Design:** The code is organized into separate modules for improved maintainability and reusability.
* **Pass database as parameter:** the database is now a parameter in the `get_response_from_query` function.

## Technologies Used

*   **LangChain:** A framework for developing applications powered by language models.
*   **Ollama:** A tool for running large language models locally.
*   **Streamlit:** A Python library for creating interactive web applications.
*   **FAISS:** A library for efficient similarity search and clustering of dense vectors.
*   **`langchain_community.document_loaders`**: Library to load the content of a URL.
*   **`langchain_core.output_parsers`**: Library to parse the output.
*   **`langchain_core.prompts`**: Library to create prompts.
*   **`langchain.text_splitter`**: Library to split the text into parts.
*   **`langchain_ollama`**: Library to use Ollama with langchain.

## Prerequisites

1.  **Ollama:**
    *   Make sure you have Ollama installed and running.
    *   You need to have the `phi4` model (or another preferred model) downloaded in Ollama. You can download it with this command:
    ```bash
    ollama pull phi4
    ```
2.  **Python 3.8+:**
    *   You need to have Python 3.8 or higher version installed.
3.  **Python Packages:**
    *   You need the following packages installed. You can install them using pip:
        ```bash
        pip install streamlit langchain langchain-community langchain-ollama faiss-cpu textwrap
        ```
        or
        ```bash
        pip install -r requirements.txt
        ```
        Create the `requirements.txt` with:
        ```bash
        pip freeze > requirements.txt
        ```

## Setup and Installation

1.  **Clone the Repository:**
    ```bash
    git clone <repository_url> # Replace <repository_url> with the URL of your repository
    cd youtube-summarizer
    ```

2.  **Install Dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Run the app:**
    ```bash
    streamlit run main.py
    ```

4.  **Open your browser:**
    Open your browser and go to the link `localhost:8501`

## Usage

1.  **Run the Streamlit App:**
    ```bash
    streamlit run main.py
    ```

2.  **Enter YouTube URL:** In the sidebar, paste the URL of the YouTube video you're interested in.

3.  **Ask Your Question:** Also in the sidebar, type the question you want to ask about the video.

4.  **Submit:** Click the "Submit" button.

5.  **View the Response:** The app will process the transcript, generate a response based on the LLM, and display the answer in the main area.

## How it works

1.  The user inputs the YouTube URL and the question.
2.  The app downloads the transcript of the video.
3.  The app creates a Vector Database from the transcript.
4.  The app searches for similarities in the database for the question.
5.  The app uses the model to create a response using the information from the database.
6.  The app shows the response to the user.

## Code Structure

*   **`main.py`:**
    *   The main Streamlit application.
    *   Handles the user interface (URL input, question input, submit button).
    *   Calls the functions from `langchain_helper.py`.
    *   Displays the LLM's response.
    *   Handles error cases.
    *   **Passes the Vector Database:** Creates the vector database and passes it to `get_response_from_query`.
*   **`langchain_helper.py`:**
    *   Contains the core logic for interacting with LangChain and the LLM.
    *   `create_vector_db_from_youtube()`: Downloads the transcript, splits it into chunks, and creates a vector database (FAISS).
    *   `get_response_from_query(db, query)`: Searches the vector database (`db`) for relevant information and queries the LLM to generate a response. **Now this function receives the database `db` as a parameter.**

## Potential Improvements

*   **More Robust Error Handling:** Implement more specific error handling (e.g., handling cases where the YouTube video has no transcript, invalid URL, Ollama model not available).
*   **Caching:** Implement caching to avoid re-processing the same YouTube video multiple times.
*   **Multiple LLM Support:** Allow the user to choose from multiple LLMs.
*   **Choose the model to use:** Implement a way to change the model inside the UI.
*   **Improve Prompt:** The user can create or improve the prompt.

## Contributing

Contributions are welcome! If you have any ideas for improving this project, feel free to open an issue or submit a pull request.

## License

[Use as you want] (e.g., MIT License)

