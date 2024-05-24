### Steps to Run the Application

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

### API Documentation

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
