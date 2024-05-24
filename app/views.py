import OpenSSL
import ssl
import socket
import requests as rs
import whois
import datetime

from flask import Blueprint, jsonify, request, Flask
from urllib.parse import urlparse, urlunparse
from flask_restx import Api, Namespace, Resource, fields
from flask_cors import CORS
from transformers import pipeline
from openai import OpenAI
import json

# Flask Setup
app = Flask(__name__)
CORS(app)  # Enable CORS for the entire app

main = Blueprint('main', __name__)
api = Api(main, title='Fraud Detection API', version='1.0', description='A simple API for fraud detection')
ns = api.namespace('AI', description='AI Fraud Detection')

model = ns.model('FraudInput', {
    'website_url': fields.String(required=True, description='URL to analyze')
})
openai_model = ns.model('FraudInput', {
    'openai_key': fields.String(required=True, description='OPENAI API KEY'),
    'website_url': fields.String(required=True, description='URL to analyze'),
    'website_content': fields.String(required=True, description='Website content to analyze'),
})

@ns.route('/fraud-ai')
class FraudAI(Resource):
    def call_bert(self, input_str):
        pipe = pipeline("text-classification", model="Utkarsh-Tiwari/bert-finetuned-fraud-veg-kebab")
        output = pipe(input_str)
        print(output)
        return output[0]

    def format_dict(self, d):
        return '; '.join([f"{key}:{value}" for key, value in d.items()])

    def analyze_url(self, url):
        if not urlparse(url).scheme:
            url = 'http://' + url
        parsed_url = urlparse(url)
        domain = parsed_url.netloc
        contains_www = 'www.' in domain
        parts = domain.split('.')
        base_domain = domain
        tld = parts[-1] if len(parts) > 1 else ''
        letter_count = sum(c.isalpha() for c in url)
        dot_count = url.count('.')
        hyphen_count = url.count('-')
        number_count = sum(c.isdigit() for c in domain)
        domain_length = len(domain)

        result = {
            'original_url': url,
            'domain': domain,
            'base_domain': base_domain,
            'tld': tld,
            'contains_www': contains_www,
            'letter_count': letter_count,
            'dot_count': dot_count,
            'hyphen_count': hyphen_count,
            'domain_length': domain_length,
            'tld_length': len(tld),
            'num_count': number_count
        }
        return result

    def get_ssl_details(self, url):
        parsed_url = urlparse(url)
        hostname = parsed_url.netloc
        context = ssl.create_default_context()
        try:
            with socket.create_connection((hostname, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                    binary_cert = ssock.getpeercert(binary_form=True)
                    cert = OpenSSL.crypto.load_certificate(OpenSSL.crypto.FILETYPE_ASN1, binary_cert)
                    issuer = cert.get_issuer().CN
                    valid_from = datetime.datetime.strptime(cert.get_notBefore().decode('utf-8'), '%Y%m%d%H%M%SZ')
                    valid_to = datetime.datetime.strptime(cert.get_notAfter().decode('utf-8'), '%Y%m%d%H%M%SZ')

                    return {
                        "Issuer": issuer,
                        "Valid From": valid_from,
                        "Valid To": valid_to
                    }
        except socket.gaierror:
            error_msg = "Domain name could not be resolved (DNS error)"
            return {"Issuer": error_msg, "Valid From": error_msg, "Valid To": error_msg}
        except ssl.SSLCertVerificationError:
            error_msg = "SSL Certificate verification failed"
            return {"Issuer": error_msg, "Valid From": error_msg, "Valid To": error_msg}
        except OpenSSL.crypto.Error:
            error_msg = "Error processing SSL Certificate"
            return {"Issuer": error_msg, "Valid From": error_msg, "Valid To": error_msg}
        except socket.timeout:
            error_msg = "Connection timed out"
            return {"Issuer": error_msg, "Valid From": error_msg, "Valid To": error_msg}
        except Exception as e:
            error_msg = f"An unexpected error occurred: {str(e)}"
            return {"Issuer": error_msg, "Valid From": error_msg, "Valid To": error_msg}

    def get_domain_info(self, domain_name):
        try:
            domain_info = whois.whois(domain_name)
            registration_date = domain_info.creation_date
            if isinstance(registration_date, list):
                registration_date = registration_date[0]
            return {
                "Domain Registration Date": registration_date,
                "Registrar": domain_info.registrar,
                "Whois Server": domain_info.whois_server
            }
        except whois.parser.PywhoisError:
            return {"Error": "Domain registration information not available"}
        except Exception as e:
            return {"Error": f"An unexpected error occurred: {str(e)}"}
    
    @ns.doc('handle_fraud_detection')
    @ns.expect(model)
    def post(self):
        data = request.get_json()
        website_url = data['website_url']
        if 'website_url' not in data:
            return 'Missing website url', 400
        else:
            analysis = self.analyze_url(website_url)
            ssl_details = self.get_ssl_details(website_url)
            domain_details = self.get_domain_info(website_url)
            result_dict = {'Online shop URL': website_url,'Domain length': analysis['domain_length'], 'Top domain length': analysis['tld_length'],
        'Presence of prefix \'www\' ': analysis['contains_www'], 'Number  of digits': analysis['num_count'], 'Number  of letters': analysis['letter_count'],
        'Number  of dots (.)': analysis['dot_count'], 'Number  of hyphens (-)': analysis['hyphen_count'],'SSL certificate issuer': ssl_details['Issuer'], 'SSL certificate expire date': ssl_details['Valid To'],'Domain registration date': domain_details['Domain Registration Date']}
            combined_input = self.format_dict(result_dict)
            print(combined_input)
            output = self.call_bert(combined_input)
            response = {
                 'label': output['label'],
                 'confidence_score': output['score'],
                 'Online shop URL': website_url,
                 'Domain length': analysis['domain_length'], 
                 'Top domain length': analysis['tld_length'],
                 'Presence of prefix www': analysis['contains_www'],
                 'Number  of digits': analysis['num_count'], 
                 'Number  of letters': analysis['letter_count'],
                 'Number  of dots (.)': analysis['dot_count'], 
                 'Number  of hyphens (-)': analysis['hyphen_count'],
                 'SSL certificate issuer': ssl_details['Issuer'], 
                 'SSL certificate expire date': str(ssl_details['Valid To']),
                 'Domain registration date': str(domain_details['Domain Registration Date'])
            }
            return response, 200
        
@ns.route('/website_content_review')
class ScrapeContent(Resource):

    def call_openai(self, user_msg, openai_key):
        client = OpenAI(api_key = openai_key)
        
        response = client.chat.completions.create(
            model="gpt-4-turbo",
            messages=[
                {
                "role": "system",
                "content": [
                    {
                    "text": "You are an expert at analysing the scraped html contents of any website or even any simple string provided by the user. You will be provided the scraped content of a website or a simple string (that might not be from any website) as input and you have to analyze and decide if this website (or string in other case) can be fraudulent or not. You also need to give a fraud score percentage out of 100 for each input provided and the reason for the given fraud score. \n\nThe output format should be in the form of a json like:\n{\n\"fraud_score_percent\": <your fraud percentage score after analyzing the content>,\n\"reason\": <your one line reason for your fraud score>}\n\nNote - Make sure that you follow the required output format only. Don't write anything else other than the output in output format.\n",
                    "type": "text"
                    }
                ]
                },
                {
                "role": "user",
                "content": [
                    {
                    "text": user_msg,
                    "type": "text"
                    }
                ]
                }
            ],
            temperature=1,
            max_tokens=256,
            top_p=1,
            frequency_penalty=0,
            presence_penalty=0
            )
        print(response.choices[0])
        return str(response.choices[0].message.content)
    
    def fetch_html(self, url):
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        try:
            response = rs.get(url, headers=headers)
            response.raise_for_status()  # Check if the request was successful
            return response.text
        except rs.RequestException as e:
            print(f"Error fetching {url}: {e}")
            return None

    @ns.doc('website_content_analysis')
    @ns.expect(openai_model)
    def post(self):
        data = request.get_json()
        website_url = data['website_url']
        openai_key = data['openai_key']
        if not openai_key or openai_key == "string":
            return {"error": "Please provide a valid OpenAI key to proceed."}
        if 'website_content' not in data and 'website_url' not in data:
            return {'error': 'Missing website content and url'}, 400
        else:
            if data['website_content'] and data['website_content'] != "string":
                output = json.loads(self.call_openai(data['website_content'], openai_key=openai_key))
            elif data['website_url'] and data['website_url'] != "string":
                html_content = self.fetch_html(website_url)
                if html_content:
                    print(html_content)
                    output = json.loads(self.call_openai(html_content, openai_key=openai_key))
                else:
                    return {"error": "Could not fetch content from the website. Please try a different website url."}, 400
            else:
                return {"error": "Please provide a valid website content or url."}, 400
            return {"fraud_score_percent": output['fraud_score_percent'], "reason": output['reason']}, 200
            
