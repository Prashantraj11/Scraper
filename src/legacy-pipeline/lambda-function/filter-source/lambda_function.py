from bs4 import BeautifulSoup, Comment
import requests
import boto3
import uuid

def upload_to_s3(data, unique_file_name):
    s3_client = boto3.client('s3')  # Create an S3 client
    
    bucket_name = 'filtered-source-gg'

    #data_dict = {"sources" : data}
    
    # Convert list to JSON string and upload it to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=unique_file_name,
        Body=data  # Convert list to JSON string
    )
    
    print(f"Responses uploaded to s3://{bucket_name}/{unique_file_name}")

def lambda_handler(event, context):
    # Get the URL from the event input
    url = event.get('page')
    
    unique_id = str(uuid.uuid4())
    unique_file_name = f'{unique_id}.txt'

    try:
        response = requests.get(url)

        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')

            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.decompose()

            # Remove all comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            cleaned_html = str(soup)
            upload_to_s3(cleaned_html, unique_file_name)
            return {
                'statusCode': 200,
                'body': unique_file_name,
                'url': url
            }
        else:
            return {
                'statusCode': response.status_code,
                'body': f"Failed to retrieve the webpage. Status code: {response.status_code}",
                'url': url
            }
    except requests.exceptions.RequestException as e:
        return {
            'statusCode': 500,
            'body': f"An error occurred: {e}"
        }
