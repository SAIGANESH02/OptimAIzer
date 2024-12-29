import json
import boto3
import configparser
import base64
from io import BytesIO
from PyPDF2 import PdfReader

# Load configuration
config = configparser.ConfigParser()
config.read("conf.ini")

S3_BUCKET_NAME = config.get("s3", "bucket_name")
AWS_ACCESS_KEY_ID = config.get("s3readwrite", "aws_access_key_id")
AWS_SECRET_ACCESS_KEY = config.get("s3readwrite", "aws_secret_access_key")
AWS_REGION = config.get("s3readwrite", "region_name")

# Initialize S3 client
s3_client = boto3.client(
    "s3",
    aws_access_key_id=AWS_ACCESS_KEY_ID,
    aws_secret_access_key=AWS_SECRET_ACCESS_KEY,
    region_name=AWS_REGION
)

def lambda_handler(event, context):
    try:
        body = event.get("body")
        if isinstance(body, str):
            body = json.loads(body)

        s3_key = body.get("s3_key", "").strip()
        if not s3_key:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "S3 key is missing"})
            }

        # Fetch the PDF from S3
        try:
            response = s3_client.get_object(Bucket=S3_BUCKET_NAME, Key=s3_key)
            pdf_bytes = response['Body'].read()
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Error fetching PDF from S3: {str(e)}"})
            }

        # Parse the PDF
        try:
            pdf_stream = BytesIO(pdf_bytes)
            reader = PdfReader(pdf_stream)
            extracted_text = ""
            for page in reader.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Error parsing PDF: {str(e)}"})
            }

        # Save the parsed text to S3
        parsed_key = f"parsed_resumes/{s3_key.split('/')[-1].split('.')[0]}.txt"
        try:
            s3_client.put_object(
                Bucket=S3_BUCKET_NAME,
                Key=parsed_key,
                Body=extracted_text,
                ContentType="text/plain"
            )
        except Exception as e:
            return {
                "statusCode": 500,
                "body": json.dumps({"error": f"Error saving parsed text to S3: {str(e)}"})
            }

        return {
            "statusCode": 200,
            "body": json.dumps({"s3_key": parsed_key})
        }

    except Exception as e:
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An unexpected error occurred: {str(e)}"})
        }
