import os
import streamlit as st
import openai
from langchain.llms import OpenAI
from langchain_core.prompts import PromptTemplate
from langchain.chains import LLMChain
from langchain.document_loaders import PyPDFLoader
from dotenv import load_dotenv
from fpdf import FPDF
import re
from difflib import unified_diff

def remove_text_between_answers_and_1(input_string):
    # Regular expression to match text between 'Answers:' and '1.'
    pattern = r'Answers:.*?1\.' 
    # Substitute the matched text with 'Answers: 1.'
    result = re.sub(pattern, 'Answers: 1.', input_string, flags=re.DOTALL)
    return result

# Load environment variables from .env file
load_dotenv()

# Now you can access the OpenAI API key using os.getenv()
openai_api_key = os.getenv("OPENAI_API_KEY")
langchain_api_key = os.getenv("LANGCHAIN_API_KEY")

# Check if the API keys are set
if not openai_api_key:
    st.error("Please set the OpenAI API key as an environment variable `OPENAI_API_KEY`.")
else:
    api_key = openai_api_key

if not langchain_api_key:
    st.error("Please set the LangSmith API key as an environment variable `LANGCHAIN_API_KEY`.")

# Function to create a PDF with the generated content
def create_pdf(professional_summary, skills, experience, cover_letter, interview_qa, company):
    pdf = FPDF()
    pdf.add_page()
    
    # Function to add a section with a heading and content
    def add_section(heading, content):
        pdf.set_font("Arial", 'B', size=14)
        pdf.multi_cell(0, 10, heading)
        pdf.ln(8)
        pdf.set_font("Arial", size=12)
        pdf.multi_cell(0, 5, content)
        pdf.ln(5)
    
    # Adding sections
    add_section("Professional Summary Suggestions:", professional_summary)
    pdf.add_page()
    add_section("Skills Suggestions:", skills)
    pdf.add_page()
    add_section("Professional Experience Suggestions:", experience)
    pdf.add_page()
    add_section("Cover Letter:", cover_letter)
    pdf.add_page()
    add_section("Interview Questions and Answers:", interview_qa)
    
    # Output PDF
    pdf_output = f"application_package_{company}.pdf"
    pdf.output(pdf_output)
    return pdf_output

# Function to create a cover letter
def create_cover_letter(job_description, resume, company, role):
    prompt_template = PromptTemplate(
        input_variables=["job_description", "resume", "company", "role"],
        template=("Create a cover letter for the role of {role} at {company} based on the following job description and resume. "
                  "Ensure the cover letter is complete, professional, and tailored to the job description:\n\n"
                  "Job Description:\n{job_description}\n\nResume:\n{resume}")
    )
    llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7), 
        prompt=prompt_template
    )
    
    response = llm_chain.run({"job_description": job_description, "resume": resume, "company": company, "role": role})
    return response

# Function to generate interview questions and answers
def generate_interview_questions(job_description, resume, behavioral_q, technical_q, python_q, sql_q):
    job_description_summary = summarize_text(job_description)

    behavioral_prompt_template = PromptTemplate(
        input_variables=["job_description", "resume", "num_questions"],
        template=("Based on the following job description and resume, generate exactly {num_questions} behavioral interview questions with detailed answers. "
                  "Ensure the questions are relevant to the job description and the candidate's resume:\n\n"
                  "Job Description:\n{job_description}\n\nResume:\n{resume}")
    )

    technical_prompt_template = PromptTemplate(
        input_variables=["job_description", "resume", "num_questions"],
        template=("Based on the following job description and resume, generate exactly {num_questions} technical interview questions with detailed answers. "
                  "Ensure the questions are relevant to the job description and the candidate's resume:\n\n"
                  "Job Description:\n{job_description}\n\nResume:\n{resume}")
    )

    python_coding_prompt_template = PromptTemplate(
        input_variables=["job_description", "resume", "num_questions"],
        template=("Based on the following job description and resume, generate exactly {num_questions} Python coding interview questions with detailed answers. "
                  "Ensure the questions are relevant to the job description and the candidate's resume. The questions should be in the style of typical coding exercises found on w3resource:\n\n"
                  "Job Description:\n{job_description}\n\nResume:\n{resume}\n\n"
                  "Example Question Format:\n\n"
                  "Python List Exercises:\n"
                  "1. Python program to interchange first and last elements in a list\n"
                  "   Answer:\n"
                  "   ```python\n"
                  "   def interchange_first_last(lst):\n"
                  "       lst[0], lst[-1] = lst[-1], lst[0]\n"
                  "       return lst\n"
                  "   ```\n"
                  "2. Python program to swap two elements in a list\n"
                  "   Answer:\n"
                  "   ```python\n"
                  "   def swap_elements(lst, pos1, pos2):\n"
                  "       lst[pos1], lst[pos2] = lst[pos2], lst[pos1]\n"
                  "       return lst\n"
                  "   ```\n\n"
                  "More Programs on List\n\n"
                  "Python String Exercises:\n"
                  "1. Python program to check whether the string is Symmetrical or Palindrome\n"
                  "   Answer:\n"
                  "   ```python\n"
                  "   def is_symmetric_or_palindrome(s):\n"
                  "       return s == s[::-1], s[:len(s)//2] == s[len(s)//2:]\n"
                  "   ```\n"
                  "2. Reverse words in a given String in Python\n"
                  "   Answer:\n"
                  "   ```python\n"
                  "   def reverse_words(s):\n"
                  "       return ' '.join(reversed(s.split()))\n"
                  "   ```\n\n"
                  "More Programs on String\n\n"
                  "Generate the questions accordingly with detailed answers.")
    )

    sql_coding_prompt_template = PromptTemplate(
        input_variables=["job_description", "resume", "num_questions"],
        template=("Based on the following job description and resume, generate exactly {num_questions} SQL coding interview questions with detailed answers. "
                  "Ensure the questions are relevant to the job description and the candidate's resume. The questions should be in the style of typical SQL exercises found on w3resource:\n\n"
                  "Job Description:\n{job_description}\n\nResume:\n{resume}\n\n"
                  "Example Question Format:\n\n"
                  "SQL Query Exercises:\n"
                  "1. Write an SQL query to fetch the first 10 records from a table named 'employees'.\n"
                  "   Answer:\n"
                  "   ```sql\n"
                  "   SELECT * FROM employees LIMIT 10;\n"
                  "   ```\n"
                  "2. Write an SQL query to find the employee with the highest salary.\n"
                  "   Answer:\n"
                  "   ```sql\n"
                  "   SELECT * FROM employees ORDER BY salary DESC LIMIT 1;\n"
                  "   ```\n\n"
                  "More SQL Query Exercises\n\n"
                  "SQL Join Exercises:\n"
                  "1. Write an SQL query to join two tables 'employees' and 'departments' on the department_id field.\n"
                  "   Answer:\n"
                  "   ```sql\n"
                  "   SELECT employees.*, departments.*\n"
                  "   FROM employees\n"
                  "   JOIN departments ON employees.department_id = departments.department_id;\n"
                  "   ```\n"
                  "2. Write an SQL query to find all employees who have not been assigned a department.\n"
                  "   Answer:\n"
                  "   ```sql\n"
                  "   SELECT * FROM employees WHERE department_id IS NULL;\n"
                  "   ```\n\n"
                  "More SQL Join Exercises\n\n"
                  "Generate the questions accordingly with detailed answers.")
    )

    behavioral_llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7),
        prompt=behavioral_prompt_template
    )

    technical_llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7),
        prompt=technical_prompt_template
    )

    python_coding_llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7),
        prompt=python_coding_prompt_template
    )

    sql_coding_llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7),
        prompt=sql_coding_prompt_template
    )

    behavioral_response = behavioral_llm_chain.run({"job_description": job_description_summary, "resume": resume, "num_questions": behavioral_q})
    technical_response = technical_llm_chain.run({"job_description": job_description_summary, "resume": resume, "num_questions": technical_q})
    python_coding_response = python_coding_llm_chain.run({"job_description": job_description_summary, "resume": resume, "num_questions": python_q})
    sql_coding_response = sql_coding_llm_chain.run({"job_description": job_description_summary, "resume": resume, "num_questions": sql_q})

        # Concatenate the responses
    response = (
        "Behavioral Questions and Answers:\n\n<br>" + behavioral_response + "\n\n" +
        "Technical Questions and Answers:\n\n<br>" + technical_response + "\n\n" +
        "Python Coding Questions and Answers:\n\n<br>"+ python_coding_response + "\n\n" +
        "SQL Coding Questions and Answers:\n\n<br>" + sql_coding_response
    )
    response = remove_text_between_answers_and_1(response)
    return response

# Function to replace non-Latin characters
def replace_non_latin_chars(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

# Function to parse resume into sections
def parse_resume(resume_text):
    sections = {
        "personal_info": "",
        "professional_summary": "",
        "skills": "",
        "education": "",
        "experience": ""
    }
    # Basic method to identify sections
    lines = resume_text.split('\n')
    current_section = None

    for line in lines:
        line_lower = line.lower()
        if "professional summary" in line_lower:
            current_section = "professional_summary"
        elif "skills" in line_lower:
            current_section = "skills"
        elif "education" in line_lower:
            current_section = "education"
        elif "professional experience" in line_lower:
            current_section = "experience"
        elif current_section:
            sections[current_section] += line + "\n"
        else:
            sections["personal_info"] += line + "\n"
    
    return sections

# Function to suggest updates for resume sections
def suggest_updates(job_description, section_name):
    if section_name == "skills":
        prompt_template = PromptTemplate(
            input_variables=["job_description", "section_name"],
            template=("Based on the following job description, suggest technology terms, tools, and relevant skills that can be added or updated in the {section_name} "
                      "section of a resume. Ensure the suggestions are relevant to the job description and include specific technology terms and tools:\n\n"
                      "Job Description:\n{job_description}\n\nSection Name:\n{section_name}")
        )
    else:
        prompt_template = PromptTemplate(
            input_variables=["job_description", "section_name"],
            template=("Based on the following job description, suggest 5 points for the professional summary or 10 points for the experience section that can be added or updated in the {section_name} "
                      "section of a resume. Ensure that the suggestions are relevant to the job description and provide clear, actionable points:\n\n"
                      "Job Description:\n{job_description}\n\nSection Name:\n{section_name}")
        )
        
    llm_chain = LLMChain(
        llm=OpenAI(api_key=openai_api_key, max_tokens=1000, temperature=0.7),
        prompt=prompt_template
    )
    
    response = llm_chain.run({"job_description": job_description, "section_name": section_name})
    return response

# Function to summarize text
def summarize_text(text, max_length=1000):
    prompt = (
        f"Summarize the following text in less than {max_length} tokens:\n\n{text}"
    )
    client = openai.OpenAI(
        api_key=openai_api_key
    )
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a summarization assistant."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=max_length
    )
    
    return response.choices[0].message.content.strip()

# Function to truncate job description to a specific word count
def truncate_text(text, max_words=200):
    words = text.split()
    if len(words) > max_words:
        return ' '.join(words[:max_words]) + '...'
    return text

# Streamlit app
st.title('Career Copilot')
st.header('AI-Powered Resume and Application Generator')

# Input for job description
job_description = st.text_area("Job Description", height=200)

# Input for resume
resume = st.text_area("Resume", height=200)

# Input for company name and role
company = st.text_input("Company Name")
role = st.text_input("Role")

# Input for maximum length of job description
max_words = st.number_input("Maximum word count for Job Description", min_value=250, max_value=600, value=600)

# Truncate the job description
truncated_job_description = truncate_text(job_description, max_words)


behavioral_q = st.number_input("Number of Behavioral Questions", min_value=1, max_value=5, value=5)
technical_q = st.number_input("Number of Technical Questions", min_value=1, max_value=8, value=8)
python_q = st.number_input("Number of Python Coding Questions", min_value=1, max_value=10, value=5)
sql_q = st.number_input("Number of SQL Coding Questions", min_value=1, max_value=10, value=5)


# Function to replace non-Latin characters
def replace_non_latin_chars(text):
    return text.encode('latin-1', 'replace').decode('latin-1')

# Process inputs and generate outputs
if st.button("Generate Outputs"):
    # Parse the resume into sections
    parsed_resume = parse_resume(resume)
    
    # Generate suggestions for each section
    professional_summary_suggestions = replace_non_latin_chars(suggest_updates(truncated_job_description, "professional_summary"))
    skills_suggestions = replace_non_latin_chars(suggest_updates(truncated_job_description, "skills"))
    experience_suggestions = replace_non_latin_chars(suggest_updates(truncated_job_description, "experience"))
    cover_letter = replace_non_latin_chars(create_cover_letter(truncated_job_description, resume, company, role))
    interview_qa = generate_interview_questions(job_description, resume, behavioral_q, technical_q, python_q, sql_q)        
    interview_qa = replace_non_latin_chars(remove_text_between_answers_and_1(interview_qa))    
    # Display suggestions in Streamlit
    st.subheader("Professional Summary Suggestions")
    st.write(professional_summary_suggestions)

    st.subheader("Skills Suggestions")
    st.write(skills_suggestions)

    st.subheader("Professional Experience Suggestions")
    st.write(experience_suggestions)

    st.subheader("Cover Letter")
    st.write(cover_letter)

    # Generate interview questions and answers
    st.subheader("Interview Questions and Answers")
    st.write(interview_qa)

    # Create and display PDF
    pdf_path = create_pdf(professional_summary_suggestions, skills_suggestions, experience_suggestions, cover_letter, interview_qa, company)
    # Provide a download link for the PDF
    with open(pdf_path, "rb") as pdf_file:
        st.download_button("Download Application Package PDF", pdf_file, file_name=pdf_path)
   
