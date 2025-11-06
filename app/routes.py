from flask import render_template, request, jsonify
from app import app

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    email_content = request.form.get('email_content')
    # Analysis logic will go here
    return jsonify({'status': 'success', 'message': 'Analysis complete'})