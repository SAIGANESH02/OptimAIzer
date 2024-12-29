# Client-Side Python Application: ResumeBoost AI
#
# This client application communicates with backend AWS services to analyze and 
# optimize resumes for better ATS (Applicant Tracking System) compliance. The app 
# retrieves and processes user-uploaded PDF resumes, fetches relevant job descriptions 
# from a given URL, and leverages API endpoints (backed by AWS Lambda and API Gateway) 
# to perform a detailed analysis. The result is a set of insights and recommendations 
# designed to strengthen the resume and improve the candidate’s chances of securing 
# interviews and job offers.
#

import streamlit as st
import requests
import boto3
from botocore.exceptions import NoCredentialsError
import configparser
from urllib.parse import quote
from concurrent.futures import ThreadPoolExecutor

# Load configuration from config.ini
config = configparser.ConfigParser()
config.read("config.ini")

# Extract S3 and API configuration
S3_BUCKET_NAME = config.get("s3", "bucket_name")
AWS_ACCESS_KEY_ID = config.get("s3readwrite", "aws_access_key_id")
AWS_SECRET_ACCESS_KEY = config.get("s3readwrite", "aws_secret_access_key")
AWS_REGION = config.get("s3readwrite", "region_name")
PDF_PARSER_URL = config.get("api", "pdf_parser_url")
WEB_SCRAPER_URL = config.get("api", "web_scraper_url")
RESUME_ANALYSIS_URL = config.get("api", "resume_analysis_url")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

# Function to fetch content from S3
def fetch_from_s3(bucket, key):
    try:
        response = s3_client.get_object(Bucket=bucket, Key=key)
        return response["Body"].read().decode("utf-8")
    except Exception as e:
        st.error(f"Error fetching content from S3: {str(e)}")
        return None

# Function to upload files to S3
def upload_to_s3(file, bucket, key):
    try:
        s3_client.upload_fileobj(file, bucket, key)
        return f"s3://{bucket}/{key}"
    except NoCredentialsError:
        return "Error: AWS credentials not found."
    except Exception as e:
        return f"Error uploading to S3: {str(e)}"

# Streamlit UI Configuration
st.set_page_config(page_title="ResumeBoost AI", layout="wide")

# Custom CSS for styling
st.markdown(
    """
    <style>
        .main {
            background-color: #f9f9f9;
            font-family: Arial, sans-serif;
        }
        .stButton>button {
            background-color: #4CAF50;
            color: white;
            padding: 10px 24px;
            border-radius: 5px;
            border: none;
        }
        .stTextInput>div>div>input {
            border-radius: 5px;
        }
        .stTextArea>div>textarea {
            font-size: 16px;
        }
    </style>
    """,
    unsafe_allow_html=True,
)

st.title("OptimAIzers")
st.header("_ResumeBoost AI_")
st.subheader("Optimize Your Resume for ATS and Land Your Dream Job")

# File Upload Section
uploaded_file = st.file_uploader("Upload your resume (PDF)", type=["pdf"])

# Job Description Input Section
job_url = st.text_input("Enter the job description URL")

if job_url:
    if not job_url.startswith(("http://", "https://")):
        st.error("Invalid URL! Please enter a valid job description URL starting with http:// or https://")
        st.stop()
    encoded_url = quote(job_url, safe="")

# Analysis Option Section
analysis_option = st.radio("Choose analysis type:", ["Quick Scan", "Detailed Analysis", "ATS Optimization"])

# Button to Analyze Resume
if st.button("Analyze Resume"):
    if not uploaded_file:
        st.error("Please upload a PDF file.")
        st.stop()

    # Step 1: Upload Resume to S3
    s3_key = f"resumes/{uploaded_file.name}"
    upload_response = upload_to_s3(uploaded_file, S3_BUCKET_NAME, s3_key)

    if "Error" in upload_response:
        st.error(upload_response)
        st.stop()
    else:
        st.success(f"File uploaded successfully to {upload_response}")

    # Define the tasks for parallel execution
    def parse_resume_task():
        try:
            pdf_response = requests.post(PDF_PARSER_URL, json={"s3_bucket": S3_BUCKET_NAME, "s3_key": s3_key})
            pdf_data = pdf_response.json()

            if pdf_response.status_code != 200:
                st.error(f"Error parsing resume: {pdf_data.get('error', 'Unknown error')}")
                return {"error": pdf_data.get("error", "Unknown error")}

            parsed_resume_key = pdf_data.get("s3_key")
            if not parsed_resume_key:
                st.error("Parsed resume text key not returned.")
                return {"error": "Parsed resume text key not returned."}

            resume_text = fetch_from_s3(S3_BUCKET_NAME, parsed_resume_key)
            if not resume_text:
                st.error("Could not retrieve parsed resume text.")
                return {"error": "Could not retrieve parsed resume text."}

            st.success("Resume parsed and content retrieved successfully.")
            print("Resume parsed and content retrieved successfully.")
            return {"resume_text": resume_text}
        except Exception as e:
            st.error(f"Error parsing resume: {str(e)}")
            return {"error": str(e)}

    def scrape_job_description_task():
        try:
            job_s3_key = f"scraped_content/{quote(job_url, safe='')}"
            web_response = requests.post(WEB_SCRAPER_URL, json={"url": encoded_url, "s3_key": job_s3_key})
            web_data = web_response.json()

            if web_response.status_code != 200:
                st.error(f"Error scraping job description: {web_data.get('error', 'Unknown error')}")
                return {"error": web_data.get("error", "Unknown error")}

            job_description = web_data.get("content", "").strip()
            if not job_description:
                st.error("Web scraper did not return any job description content.")
                return {"error": "Web scraper did not return any job description content."}

            st.success(f"Job description scraped and saved to S3: {job_s3_key}")
            print(f"Job description scraped and saved to S3: {job_s3_key}")
            return {"job_description": job_description}
        except Exception as e:
            st.error(f"Error scraping job description: {str(e)}")
            return {"error": str(e)}


    # Execute tasks in parallel
    with ThreadPoolExecutor() as executor:
        tasks = {
            "resume_parsing": executor.submit(parse_resume_task),
            "job_scraping": executor.submit(scrape_job_description_task),
        }
        results = {name: task.result() for name, task in tasks.items()}

    # Handle results
    resume_result = results["resume_parsing"]
    if "error" in resume_result:
        st.error(f"Error parsing resume: {resume_result['error']}")
        st.stop()

    job_result = results["job_scraping"]
    if "error" in job_result:
        st.error(f"Error scraping job description: {job_result['error']}")
        st.stop()

    # Step 3: Analyze Resume and Job Description
    resume_text = resume_result["resume_text"]
    job_description = job_result["job_description"]
    try:
        analysis_response = requests.post(RESUME_ANALYSIS_URL, json={
            "resume_text": resume_text,
            "job_description": job_description,
            "analysis_option": analysis_option
        })
        analysis_data = analysis_response.json()

        if analysis_response.status_code != 200:
            st.error(f"Error analyzing resume: {analysis_data.get('error', 'Unknown error')}")
            st.stop()

        analysis_result = analysis_data.get("analysis")
        if not analysis_result:
            st.error("Error: Analysis result could not be retrieved.")
            st.stop()

        st.subheader("Analysis Result")
        st.write(analysis_result)

    except Exception as e:
        st.error(f"Error analyzing resume: {str(e)}")

# Additional resources in the sidebar
st.sidebar.title("Resources")
st.sidebar.markdown("""
- [Resume Writing Tips](https://cdn-careerservices.fas.harvard.edu/wp-content/uploads/sites/161/2023/08/College-resume-and-cover-letter-4.pdf)
- [ATS Optimization Guide](https://career.io/career-advice/create-an-optimized-ats-resume)
- [Interview Preparation](https://hbr.org/2021/11/10-common-job-interview-questions-and-how-to-answer-them)
""")
