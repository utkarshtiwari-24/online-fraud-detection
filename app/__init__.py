from flask import Flask
from flask_restx import Api
from flask_cors import CORS
from .views import main

def fraud_app():
    app = Flask(__name__)
    CORS(app)
    api = Api(app, version='1.0', title='Fraud Detection API',
              description='A simple API for fraud detection')
    app.register_blueprint(main, url_prefix='/api')

    return app
