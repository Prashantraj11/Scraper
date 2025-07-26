## Demo
Live website: https://scraper-pied.vercel.app/

https://github.com/user-attachments/assets/94e735fe-738e-42c1-89b4-a41e1063a14c

---
## API Endpoints
https://wb6nvu1fl1.execute-api.ap-south-1.amazonaws.com/dev/api/reviews?page={PRODUCT_URL}
> [!NOTE]  
> Make sure to enter full URL in query parameter like this: `?page=https://www.example.com`

Response:
```json
{
    "statusCode": 
    "reviews_count": ,
    "reviews": [
        {
            "title": "",
            "body": "",
            "author": "",
            "rating": ""
        },
    ]
}
```
---
## Workflow
| ![flow-2](https://github.com/user-attachments/assets/d59e19f2-1274-4f2e-a516-de077f7c34a0) | 
|:--:| 
| *Pipeline v2 (current)* |

| ![flow-1](https://github.com/user-attachments/assets/187b9a4e-1cb7-4fca-a3f4-d7756ade1a7b) | 
|:--:| 
| *Lagacy pipeline* |

#### Technologies used: 
- Backend: AWS Lambda, EC2, API Gateway, S3
- Script: Python (Beautiful Soup, Playwright)
- LLM: Gemini-1.5-flash
- Frontend: Next.js

#### Components:
- *HTML Content Filtering:* The process begins by accepting a webpage URL, filtering its source code using `Beautiful Soup` to extract meaningful content while discarding irrelevant elements to reduce the token size before passing it on to the LLM.
- *Extract class selector:* To automate actions like pagination, extracing reviews, we need the class selector to interact with the page elements programmatically, and to get that, it uses `Gemini-1.5-flash` model. 
- *Browser Automation:* An `EC2` instance (Windows 2022 Server) runs `Playwright` scripts with Chromium for browser automation, as Lambda cannot handle Chromium directly.
- *Review Extraction:* `Beautiful Soup` is used to extract the source code of each review page, with dynamically fetched CSS selectors provided by the LLM.
---
#### Folder structure:
```
src/
├── legacy-pipeline/
│   ├── ec2-script/
│   │   └── pagination-automation/
│   │       └── automation.py
│   ├── lambda-function/
│   │   ├── extract-css-selector/
│   │   │   └── lambda_function.py
│   │   ├── extract-reviews/
│   │   │   └── lambda_function.py
│   │   ├── filter-source/
│   │   │   └── lambda_function.py
│   │   ├── pagination-automation-trigger/
│   │   │   └── lambda_function.py
│   │   ├── poll-step-function-result/
│   │   │   └── lambda_function.py
│   │   └── trigger-step-function/
│   │       └── lambda_function.py
│   └── step-function/
│       └── MyStateMachine-t759b6k2.asl.json
├── pipeline-v2/
│   ├── ec2-script/
│   │   └── final_automation.py
│   └── lambda-function/
│       └── review-automation-trigger/
│           └── lambda_function.py
├── test/
│   ├── filter_source_extract_class.ipynb
│   ├── final_web_scrape.ipynb
│   └── review_scrape_automation.ipynb
├── frontend/
├── .gitignore
└── README.md

```
- `src/`: This folder contains all the scripts deployed on AWS. It includes Lambda functions, Step Function definitions, and EC2 scripts for automation tasks.
- `test/`: This folder contains Jupyter Notebook (.ipynb) files, which were used to create the Lambda functions and test their output during development.
- `frontend/`: This folder contains all the files associated with the next.js frontend.
---

## Steps to run frontend locally
Step 1. Navigate to the frontend directory:
```bash
cd Product_Review_Scraper/frontend
```
Step 2. Install dependencies:
```bash
npm install
```
Step 3. Start the development server:
```bash
npm run dev
```
## Steps to run review scraper locally
Step 1. Navigate to the test directory:
```bash
cd Product_Review_Scraper/test
```
Step 2. Create the .env file with the GOOGLE_API_KEY:
```bash
echo "GOOGLE_API_KEY=your-google-api-key" > .env
```
- Replace your-google-api-key with your actual Google API key.
  
Step 3. Open the Jupyter Notebook:
- If Jupyter Notebook is installed, start it with:
```bash
jupyter notebook
```
Step 4. Run the Notebook:
- In the Jupyter interface, open `final_web_scrape.ipynb`.
- Run the cells sequentially.


## Optimization strategy (TBD Later)
- Executing multiple pipelines parallely to retrive mode reliable data and increase website compatibility (it will add extra overhead but API sucess rate will increase.)
- Executing the Beautiful Soup script using distributed map with the total number of concurrent requests equal to the total number of review pages which can reduce latency by 15-20 seconds.
- Handling SSR and CSR websites separately will also improve compatibility with a wider variety of websites.
- Streaming data chunks: Because waiting 1 minute for an API call is the worst.
