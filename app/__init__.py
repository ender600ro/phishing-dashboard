from flask import Flask
from dotenv import load_dotenv
import os

load_dotenv()

app = Flask(__name__, template_folder='../templates', static_folder='../static')
app.config['SECRET_KEY'] = os.getenv('FLASK_SECRET_KEY')
app.config['VT_KEY'] = os.getenv('VIRUSTOTAL_KEY')
app.config['URLSCAN_KEY'] = os.getenv('URLSCAN_KEY')

from . import routes