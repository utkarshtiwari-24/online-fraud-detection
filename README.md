# Aim of the project
This project aims at detecting fraud websites using AI and improve the security of any system that might be exposed to illegitimate websites. This project uses two AI models for this project:

### Finetuned BERT model on fraudulent and non fraudulent website dataset (https://huggingface.co/Utkarsh-Tiwari/bert-finetuned-fraud-veg-kebab) 
This AI model was finetuned using the custom dataset of fraud and legitimate online websites, with google-bert/bert-base-uncased as the base model. This model takes in information such as 'Online shop URL', 'Domain length', 'Top domain length', 'Presence of prefix 'www', 'Number  of digits', 'Number  of letters', 'Number  of dots (.)','Number  of hyphens (-)','SSL certificate issuer', 'SSL certificate expire date','Domain registration date'. Then, it classifies the website as 'fraudulent' or 'legitimate', along with the confidence score.

### GPT-4-turbo OpenAI model
A prompt, with the website content provided as input from the user or by scraping the website url provided by the user, is sent to the GPT-4-turbo model, which in turn generates an output with the fraud percentage score and the reason for the fraud score percentage. For the second api - AI/website_content_review, please use your OpenAI API key in the input request body as shown in the below steps.   
    
    
    
    
# Steps to Run the Application

1. Clone the repository to your system.
2. Open a terminal and navigate to the cloned repository's location.
3. Create a virtual environment in the same directory as the repository:
   ```
   python -m venv venv
   source venv/bin/activate
   ```
4. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```
5. Navigate into the repository and execute the following command:
   ```
   python run.py
   ```
6. Your Flask server will start running.
7. Please visit the API Swagger URL at: [http://127.0.0.1:5000/api/](http://127.0.0.1:5000/api/)
    
    
    
      
# API Documentation

There are two APIs available to detect fraudulent websites:

1. **POST - /AI/fraud-ai**  
   This API takes a website URL as input, collects information related to the website, and then passes the information to a fine-tuned BERT model available on Hugging Face. The model classifies the website information as 'fraudulent' or 'legitimate', along with a confidence score for the output.

   **Example**:
   - **Request Body**:  
     ```
     {
      "website_url": "https://www.example.com"
     }
     ```
   - **Response Body**:  
     ```json
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
     ```

2. **POST - AI/website_content_review**  
   This API takes either a website URL or the string content of a website (or any string content) as input. It then sends the information to the OpenAI GPT-4-turbo model to generate a fraud percentage score and the reason for the fraud score as output. If both the website content and the URL are provided as input, preference will be given to the website content.

   **Example 1**:
   - **Request Body**:  
     ```json
     {
      "openai_key": "<your openai api key>",
      "website_url": "",
      "website_content": "This domain is for use in illustrative examples in documents. You may use this domain in literature without prior coordination or asking for permission."
     }
     ```
   - **Response Body**:  
     ```json
     {
      "fraud_score_percent": 5,
      "reason": "The content indicates a placeholder or example domain usage, generally not fraudulent but low risk due to lack of context."
     }
     ```

   **Example 2**:
   - **Request Body**:  
     ```json
     {
      "openai_key": "<your openai api key>",
      "website_url": "https://www.example.com",
      "website_content": ""
     }
     ```
   - **Response Body**:  
     ```json
     {
      "fraud_score_percent": 0,
      "reason": "Content indicates a legitimate example domain used for illustrative purposes."
     }
     ```

---

Note: Please ensure that you provide the complete URL including the 'http' or 'https' substrings.  
Dataset Source for training the BERT model: https://data.mendeley.com/datasets/m7xtkx7g5m/1  
Third party open source libraries such as whois and openssl were used to collect website ssl and domain information.
