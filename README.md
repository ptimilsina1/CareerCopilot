# Cover Letter and Interview Questions Generator

This Streamlit application generates a customized cover letter and interview questions based on a given job description and resume. It uses OpenAI's language model to create professional content and compiles everything into a downloadable PDF.

## Features

- **Generate Cover Letter**: Create a personalized cover letter tailored to the job description and resume provided.
- **Generate Interview Questions**: Generate behavioral, technical, Python coding, and SQL coding questions for interview preparation.
- **Downloadable PDF**: All generated content is compiled into a formatted PDF for easy download.

## Prerequisites

- Python 3.7 or higher
- Streamlit
- OpenAI API Key
- LangChain API Key

## Installation

1. Clone the repository:
    ```bash
    git clone https://github.com/yourusername/cover-letter-interview-questions-generator.git
    cd cover-letter-interview-questions-generator
    ```

2. Create a virtual environment and activate it:
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3. Install the required packages:
    ```bash
    pip install -r requirements.txt
    ```

4. Create a `.env` file in the project directory and add your API keys:
    ```plaintext
    OPENAI_API_KEY=your_openai_api_key
    LANGCHAIN_API_KEY=your_langchain_api_key
    ```

## Usage

1. Run the Streamlit application:
    ```bash
    streamlit run app.py
    ```

2. Open your web browser and navigate to `http://localhost:8501`.

3. Fill in the required fields:
    - Job Description
    - Resume
    - Company Name
    - Role
    - (Optional) Professional Summary, Skills, Experience Suggestions

4. Use the sliders to select the number of questions for each category:
    - Behavioral Questions
    - Technical Questions
    - Python Coding Questions
    - SQL Coding Questions

5. Click the "Generate Cover Letter and Interview Questions" button.

6. After processing, download the generated PDF by clicking the "Download PDF" button.

## Project Structure

- `app.py`: Main application code.
- `requirements.txt`: List of Python dependencies.
- `.env`: Environment variables (not included in the repository).
- `README.md`: This file.

## Function Descriptions

### `remove_text_between_answers_and_1`

Removes unwanted content between "Answers:" and the first answer using regex.

### `create_pdf`

Generates a PDF file with sections for the professional summary, skills, experience, cover letter, and interview questions.

### `create_cover_letter`

Generates a cover letter using OpenAI's language model based on the provided job description and resume.

### `generate_interview_questions`

Generates interview questions (behavioral, technical, Python coding, and SQL coding) based on the job description and resume using OpenAI's language model.

### `summarize_text`

Summarizes the given text using OpenAI's language model.

## Notes

- Ensure you have a valid OpenAI API key and LangChain API key.
- The application requires internet access to communicate with the OpenAI API and LangChain API.

## License

This project is licensed under the MIT License.

## Acknowledgments

- [OpenAI](https://openai.com) for the language model API.
- [LangChain](https://langchain.com) for the NLP framework.
- [Streamlit](https://streamlit.io) for the web application framework.
- [FPDF](http://www.fpdf.org) for the PDF generation library.
