from app import fraud_app

app = fraud_app()

if __name__ == '__main__':
    print("flask server running")
    app.run(debug=True)
