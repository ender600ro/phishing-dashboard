from flask import Flask, render_template
from dotenv import load_dotenv
import os

load_dotenv()  # This loads all variables from your .env file

vt_key = os.getenv("VIRUSTOTAL_KEY")
urlscan_key = os.getenv("URLSCAN_KEY")

app = Flask(__name__)
app.secret_key = os.getenv("FLASK_SECRET_KEY")

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)