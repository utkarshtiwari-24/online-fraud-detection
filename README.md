### Steps to run the application

1. Clone the repository in your system.
2. Open terminal and go to the cloned repo's location.
3. Create a virtual env at the same path as the repo:
   > python -m venv venv
   > source venv/bin/activate
4. Install requirements:
   > pip install -r requirements.txt
5. Go inside the repository and run this command:
   > python run.py
6. Your flask server will start running.
7. Please visit the api swagger url location: http://127.0.0.1:5000/api/


### API Documentation
There are two APIs to detect fraud websites:
1. POST - /AI/fraud-ai
   This API takes a website url as an input and collects information related to the website and passes the information to the finetuned BERT model (https://huggingface.co/Utkarsh-Tiwari/bert-finetuned-fraud-veg-kebab) on Hugging Face, which classifies the website information as 'fraudulent' or 'legitimate' along with the confidence score for the given output.
   
   Example - 
   Request Body:
   {
    "website_url": "https://www.example.com"
   }
   
   Response Body:
     {
        "label": "legitimate",
        "confidence_score": 0.9999829530715942,
        "Online shop URL": "https://www.example.com",
        "Domain length": 15,
        "Top domain length": 3,
        "Presence of prefix www": true,
        "Number  of digits": 0,
        "Number  of letters": 18,
        "Number  of dots (.)": 2,
        "Number  of hyphens (-)": 0,
        "SSL certificate issuer": "DigiCert Global G2 TLS RSA SHA256 2020 CA1",
        "SSL certificate expire date": "2025-03-01 23:59:59",
        "Domain registration date": "1995-08-14 04:00:00"
   }

   Note: Please ensure that you provide the complete url including the 'http' or 'https' substrings.


2. POST - AI/website_content_review
   This API takes either a website url or the string content of a website (or any string content) as an input, and sends the information to the OpenAI GPT-4-turbo model to generate a fraud percentage score and the reason for the fraud score as the output.
   If provided both the website content and the url, the preference would be given to the website content.
   Example - 
   Request Body:
   {
    "openai_key": "<your openai api key>",
    "website_url": "",
    "website_content": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission."
   }

   Response Body:
   {
    "fraud_score_percent": 5,
    "reason": "The content indicates a placeholder or example domain usage, generally not fraudulent but low risk due to lack of context."
  }
   
