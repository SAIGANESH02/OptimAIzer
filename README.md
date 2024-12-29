**OptimAIzers**

# ResumeBoost AI

## Overview
This application provides a Streamlit-based client interface to parse, analyze, and optimize a resume against a given job description. The solution integrates multiple components:

1. **Client (Streamlit App):** A front-end interface for users to upload their resumes, provide a job description URL, and receive a tailored analysis.
2. **Backend Services (APIs):** 
   - **PDF Parser API:** Extracts and processes text from uploaded resumes stored in Amazon S3.
   - **Web Scraper API:** Retrieves and processes job description content from a given URL.
   - **Resume Analysis API:** Compares the candidate's resume against the job description and provides an optimization analysis.

3. **Amazon S3:** Used as storage for both the uploaded resume PDFs and processed job descriptions.

## Prerequisites
- **Python 3.8+** installed locally.
- **pip** (Python package manager) for installing dependencies.
- **AWS Credentials:** You will need valid AWS credentials (Access Key ID and Secret Access Key) with permissions to read/write to the specified S3 bucket.
- **config.ini File:** A configuration file containing details like:
  - S3 bucket name
  - AWS credentials and region
  - URLs for the PDF Parser, Web Scraper, and Resume Analysis APIs

A sample `config.ini` might look like:
```ini
[s3]
bucket_name = your-s3-bucket-name

[s3readwrite]
aws_access_key_id = YOUR_AWS_ACCESS_KEY
aws_secret_access_key = YOUR_AWS_SECRET_KEY
region_name = your-region

[api]
pdf_parser_url = https://your-pdf-parser-api.com/parse
web_scraper_url = https://your-web-scraper-api.com/scrape
resume_analysis_url = https://your-analysis-api.com/analyze
```

## Installation Steps

1. **Clone or Download the Repository:**
   ```bash
   git clone https://github.com/SAIGANESH02/OptimAIzer.git
   cd your-repo
   ```

2. **Create and Activate a Virtual Environment (Optional but Recommended):**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies:**
   Assuming you have a `requirements.txt` file, run:
   ```bash
   pip install -r requirements.txt
   ```
   If not, manually install packages required (e.g., `streamlit`, `requests`, `boto3`, `configparser`):
   ```bash
   pip install streamlit requests boto3 configparser
   ```

4. **Set up Configuration:**
   - Copy the sample `config.ini` (above) into the project directory.
   - Update the file with your AWS credentials, region, bucket name, and API endpoints.

5. **Run the Application:**
   ```bash
   streamlit run app.py
   ```
   For example, if your client code is in `app.py`, you would run:
   ```bash
   streamlit run app.py
   ```

6. **Access the Application:**
   After running the command, Streamlit will start a local server. By default, it’s accessible at:
   ```
   http://localhost:8501
   ```

7. **Usage:**
   - **Upload a PDF Resume:** Click the "Browse files" button in the interface and select your resume PDF.
   - **Enter Job Description URL:** Input the URL of the job description you want to analyze against.
   - **Select Analysis Type:** Choose between "Quick Scan", "Detailed Analysis", or "ATS Optimization".
   - **Analyze:** Click the "Analyze Resume" button and wait for the results to appear.

## Additional Notes
- Make sure your APIs are up and running and that the correct endpoints are specified in the `config.ini` file.
- Ensure that the S3 bucket is accessible with the provided credentials and that the credentials have proper permissions for `get_object` and `put_object`.
- If you encounter errors or issues, check Streamlit logs in the terminal for debug information.

This concludes the setup instructions. You should now be able to run and interact with the application.