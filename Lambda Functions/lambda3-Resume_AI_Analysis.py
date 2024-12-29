import requests
from bs4 import BeautifulSoup
from urllib.parse import unquote
import boto3
import json
import configparser

def lambda_handler(event, context):
    # Load configuration from conf.ini
    config = configparser.ConfigParser()
    config.read("conf.ini")

    # Retrieve configuration details
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

    try:
        # Log the received event
        print("Received event:", json.dumps(event))

        # Parse the incoming request body
        body = event.get("body")
        if body and isinstance(body, str):
            body = json.loads(body)

        encoded_url = body.get("url", "").strip()
        s3_key = body.get("s3_key", "").strip()

        if not encoded_url:
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "URL is missing from the request"})
            }

        decoded_url = unquote(encoded_url)
        print("Decoded URL:", decoded_url)

        if not decoded_url.startswith(("http://", "https://")):
            return {
                "statusCode": 400,
                "body": json.dumps({"error": "Invalid URL format. Must start with http:// or https://"})
            }

        # Fetch content from the decoded URL
        response = requests.get(decoded_url, timeout=10)
        response.raise_for_status()

        # Parse content using BeautifulSoup
        soup = BeautifulSoup(response.content, "html.parser")
        text_content = soup.get_text(separator="\n", strip=True)

        # Save scraped content to S3
        if s3_key:
            try:
                s3_client.put_object(
                    Bucket=S3_BUCKET_NAME,
                    Key=s3_key,
                    Body=text_content,
                    ContentType="text/plain"
                )
                print(f"Content successfully uploaded to S3: {s3_key}")
            except Exception as e:
                return {
                    "statusCode": 500,
                    "body": json.dumps({"error": f"Error uploading to S3: {str(e)}"})
                }

        return {
            "statusCode": 200,
            "body": json.dumps({
                "content": text_content,  # Truncate content for response
                "s3_key": s3_key
            })
        }

    except requests.exceptions.RequestException as e:
        print(f"Request error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"Request failed: {str(e)}"})
        }
    except Exception as e:
        print(f"Unhandled error: {e}")
        return {
            "statusCode": 500,
            "body": json.dumps({"error": f"An error occurred: {str(e)}"})
        }
