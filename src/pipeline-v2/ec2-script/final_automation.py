import requests
import json
from bs4 import BeautifulSoup, Comment, SoupStrainer
import nest_asyncio
import asyncio
from playwright.async_api import async_playwright
import boto3
import argparse
import time
import os

def filter_source(source):
  soup = BeautifulSoup(source, 'html.parser')
#   body_content = soup.body.decode_contents()

  for script in soup(["script", "style", "img", "nav", "header", "footer", "picture", "svg", "path", "form"]):
      script.decompose()

  cleaned_body_content = str(soup.body)
  return cleaned_body_content

#global variable
review_paginate_next = ""
review_author = ""
review_title = ""
review_text = ""
review_rating = ""

prompt = """extract the following class name for each of the following elements:
- pagination "next page" button of review section
- name of reviewer
- title of review
- text of review
- rating classname
from the provided codebase.
Just return a comma seperated value of classnames, if multiple class name is found for the same section, use the most relevant one which is unique.
Don't trim the values, return the value as it is in source code.
Don't return any other text than mentioned. Here is the code: """

google_api_key = os.getenv('GOOGLE_API_KEY')

def filter_css_selector(source_text, max_retries = 3):
    response = requests.post(
        url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_api_key}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": prompt + source_text
                        }
                    ]
                }
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()
        message_content = data['candidates'][0]['content']['parts'][0]['text']
        message_content = message_content.strip("\n")
        try:
          global review_paginate_next, review_author, review_title, review_text, review_rating
          review_paginate_next, review_author, review_title, review_text, review_rating = message_content.split(",")
          next_buttons.append(f'.{review_paginate_next}')
          print(review_paginate_next)
          print(review_author)
          print(review_title)
          print(review_text)
          print(review_rating)

        except:
          # also try with some other model
          if (max_retries > 0):
            time.sleep(2)
            filter_css_selector(source_text, max_retries - 1)
    else:
        # handles model overload error or any other error encountered by LLM API
        print(response.json())
        if (max_retries > 0):
          time.sleep(2)
          filter_css_selector(source_text, max_retries - 1)

fallback_reviews = dict()
fallback_prompt = """extract the reviews from the given source code in json object in the format {
  "reviews_count": 100,
  "reviews": [
    {
      "title": "Review Title",
      "body": "Review body text",
      "rating": 5,
      "reviewer": "Reviewer Name"
    },
    ...
  ]
}.
Don't add any code formating.
Here is the source code: """

def fallback_review_extraction(source_text, max_retries = 3):
    response = requests.post(
        url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_api_key}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": fallback_prompt + source_text
                        }
                    ]
                }
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()
        message_content = data['candidates'][0]['content']['parts'][0]['text']
        message_content = message_content.strip("\n")
        global fallback_reviews
        fallback_reviews = json.loads(message_content)
        print(fallback_reviews)

    else:
        # handles model overload error or any other error encountered by LLM API
        print(response.json())
        if (max_retries > 0):
          time.sleep(2)
          fallback_review_extraction(source_text, max_retries - 1)

# class determine_pagination_type:
#   def __init__(self, source):
#     self.source = source

#   def handle_scroll_pagination():
#   #def

#   def handle_load_more_pagination():
#   #def

#   def handle_next_button_pagination():
#   #def

#   def handle_page_number_pagination():
#   #def

#   def handle_url_param_pagination():
#   #def

def extract_reviews(source):

  body_strainer = SoupStrainer('body')
  soup = BeautifulSoup(source, 'html.parser', parse_only=body_strainer)

  titles = soup.find_all(class_=review_title)
  bodies = soup.find_all(class_=review_text)
  authors = soup.find_all(class_=review_author)
  ratings = soup.find_all(class_=review_rating)


  for i in range(max(len(titles), len(bodies), len(authors), len(ratings))):
      review = {
          "title": titles[i].get_text(strip=True) if i < len(titles) else "",
          "body": bodies[i].get_text(strip=True) if i < len(bodies) else "",
          "author": authors[i].get_text(strip=True) if i < len(authors) else "",
          "rating": ratings[i].get_text(strip=True) if i < len(ratings) else ""
      }
      reviews.append(review)

dialog_prompt = """extract the classname of popup close button.
Just return a single word containing the classname.
Don't add any code formating.
Here is the source code: """

def get_dialog_close_button(source_text, max_retries = 2):
    response = requests.post(
        url=f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={google_api_key}",
        headers={
            "Content-Type": "application/json"
        },
        json={
            "contents": [
                {
                    "parts": [
                        {
                            "text": dialog_prompt + source_text
                        }
                    ]
                }
            ]
        }
    )

    if response.status_code == 200:
        data = response.json()
        message_content = data['candidates'][0]['content']['parts'][0]['text']
        message_content = message_content.strip("\n")
        return message_content
    else:
        # handles model overload error or any other error encountered by LLM API
        print(response.json())
        if (max_retries > 0):
          time.sleep(2)
          get_dialog_close_button(source_text, max_retries - 1)
        return ''

def upload_to_s3(data, unique_file_name):
    s3_client = boto3.client('s3')  # Create an S3 client

    bucket_name = 'extracted-reviews'  # Replace with your bucket name

    s3_client.put_object(
        Bucket=bucket_name,
        Key=unique_file_name,
        Body=json.dumps(data),  # Convert list to JSON string
        ContentType='application/json'
    )

    print(f"Responses uploaded to s3://{bucket_name}/{unique_file_name}")

# url = "https://2717recovery.com/products/recovery-cream"
# url = "https://www.trustpilot.com"
# url = "https://milky-mama.com/pages/customer-reviews"
# url = "https://lyfefuel.com/products/essentials-nutrition-shake"
# url = "https://www.allbirds.com/products/mens-tree-dashers-twilight-white-twilight-teal?price-tiers=msrp%2Ctier-1%2Ctier-2"
# url = "https://www.shopclues.com/chamria-hing-wati-digestive-mouth-freshner-200-gm-can-pack-of-2-153514795.html"
nest_asyncio.apply()
responses_list = {}
reviews = []
next_buttons = ['a[aria-label="Goto next page"]']
dialog_close_buttons = ['.store-selection-popup--close']

async def scrape(url, file_name):
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url)

        await page.wait_for_selector('body')
        page_source = await page.content()

        cleaned_body_content = filter_source(page_source)
        filter_css_selector(cleaned_body_content)
        # time.sleep(5)
        
        # Perform all three operation on pagination, click read more, load more etc button. Scroll to the bottom of page.

        # pagination_type = determine_pagination_type(page_source)

        dialog_close_attempt = 1
        for elm in next_buttons:
          count = 0
          while True:
              await page.wait_for_selector('body')
              page_source = await page.content()

              extract_reviews(page_source)

              print(count)
              count += 1
              if (count > 20): break
              
              try:
                  next_button = page.locator(elm)
                  
                  await page.mouse.click(x=0, y=page.viewport_size['height'] // 2)
                  
                  await asyncio.wait_for(next_button.click(), timeout=5)
                  
                  # Wait for the next page to load and for specific element to be visible
                  await page.wait_for_load_state('networkidle')  
                  await page.wait_for_selector('body')  
                  
              except asyncio.TimeoutError:
                  # print("Timeout occurred while waiting for the next page. Stopping the process.")
                  # if (dialog_close_attempt > 0 and count < 2):
                  #   dialog_close_attempt -= 1
                  #   await page.mouse.click(x=0, y=page.viewport_size['height'] // 2)
                  #   cleaned_source = filter_source(page_source)
                  #   dialog_close_button_class = get_dialog_close_button(cleaned_source)
                  #   dialog_close_buttons.append(f'.{dialog_close_button_class}')
                  #   for elm in dialog_close_buttons:
                  #     print(elm)
                  #     if dialog_close_button_class:
                  #       dialog_close_button = page.locator(elm)
                  #       try:
                  #         await asyncio.wait_for(dialog_close_button.click(), timeout=3)
                  #         break
                  #       except:
                  #         continue
                  # else:
                  #   break  # Break the loop if it takes too long to change pages
                  break
              except Exception as e:
                print("Bro, error with pagination? ", e)
                break

        #Handle infinite scroll
        prev_height = -1
        max_scrolls = 5  # Set a maximum number of scrolls to prevent infinite loops
        scroll_count = 0

        while scroll_count < max_scrolls:
            await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            await page.wait_for_timeout(200)
            new_height = await page.evaluate("document.body.scrollHeight")

            if new_height == prev_height:
                break 

            prev_height = new_height  
            scroll_count += 1  

        page_source = await page.content()
        extract_reviews(page_source)
        #Handle infinite scroll end
        
        # print(len(reviews))
        # print(reviews)

        if (len(reviews) == 0):
          fallback_review_extraction(cleaned_body_content)
          fallback_reviews["reviews_count"] = len(fallback_reviews["reviews"])
          upload_to_s3(fallback_reviews, file_name)
          # print(fallback_reviews)
        else:
          reviews_dict = {"reviews_count" : len(reviews), "reviews": reviews}
          # print(reviews_dict)
          upload_to_s3(reviews_dict, file_name)

# asyncio.run(scrape())

async def main(url, unique_id):
    unique_file_name = f'{unique_id}.json'  # Use provided UUID for file naming
    await scrape(url, unique_file_name)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Scrape a website and upload results to S3.')

    parser.add_argument('url', type=str, help='The URL of the website to scrape')
    parser.add_argument('uuid', type=str, help='A unique identifier (UUID) for the output file')

    args = parser.parse_args()

    asyncio.run(main(args.url, args.uuid))

