import requests
import json
from bs4 import BeautifulSoup, Comment
import nest_asyncio
import asyncio
from playwright.async_api import async_playwright
import boto3
import uuid  # Import UUID for unique identifiers
import argparse  # Import argparse for command-line arguments

nest_asyncio.apply()

async def scrape_website(url, next_button_class, element_to_check, unique_file_name):
    count = 0
    responses_list = {}  # Initialize an empty list to store responses
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        while True:
            await page.wait_for_selector('body')
            page_source = await page.content()

            # FILTER 
            soup = BeautifulSoup(page_source, 'html.parser')

            for tag in soup(['script', 'style', 'meta', 'link']):
                tag.decompose()

            # Remove all comments
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

            cleaned_html = str(soup)

            # Append cleaned HTML source code to the list
            print(count)
            count += 1
            responses_list[str(count)] = cleaned_html  # Append cleaned HTML to responses_list

            if (count > 14): break
            
            try:
                next_button = page.locator(f'.{next_button_class}')
                
                await asyncio.wait_for(next_button.click(), timeout=5)
                
                # Wait for the next page to load and for specific element to be visible
                await page.wait_for_load_state('networkidle')  
                await page.wait_for_selector(element_to_check)  
                await page.mouse.click(x=0, y=page.viewport_size['height'] // 2)
                
            except asyncio.TimeoutError:
                print("Timeout occurred while waiting for the next page. Stopping the process.")
                break  # Break the loop if it takes too long to change pages
            
            except Exception as e:
                print(f"An error occurred: {e}")
                break

        await browser.close()

    # After reaching the end of pages, upload responses_list to S3
    upload_to_s3(responses_list, unique_file_name)  # Pass unique_file_name here
    

def upload_to_s3(data, unique_file_name):
    s3_client = boto3.client('s3')  # Create an S3 client
    
    bucket_name = 'extracted-source-list'  # Replace with your bucket name

    #data_dict = {"sources" : data}
    
    # Convert list to JSON string and upload it to S3
    s3_client.put_object(
        Bucket=bucket_name,
        Key=unique_file_name,
        Body=json.dumps(data)  # Convert list to JSON string
    )
    
    print(f"Responses uploaded to s3://{bucket_name}/{unique_file_name}")

async def main(url, unique_id):
    unique_file_name = f'{unique_id}.json'  # Use provided UUID for file naming
    await scrape_website(url, 'jdgm-paginate__next-page', 'body', unique_file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a website and upload results to S3.')
    
    parser.add_argument('url', type=str, help='The URL of the website to scrape')
    parser.add_argument('uuid', type=str, help='A unique identifier (UUID) for the output file')
    
    args = parser.parse_args()
    
    asyncio.run(main(args.url, args.uuid))
