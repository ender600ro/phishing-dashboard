# Phishing Detection Dashboard

**Project:** Design and Implementation of a Web-Based Phishing Email Detection Dashboard Using Open-Source Tools and Threat Intelligence Techniques for SMEs  

This project implements a lightweight web dashboard that helps small and medium-sized enterprises (SMEs) analyse suspicious emails for phishing indicators. The system combines a machine-learning model with open-source threat-intelligence services (VirusTotal and urlscan.io) and presents results in a simple, non-technical interface.

---

## Features

- Paste suspicious email headers or body text into the dashboard
- Extract sender, subject, URLs, and basic indicators
- Predict phishing probability using a TF-IDF + Logistic Regression model
- Query VirusTotal for URL reputation
- Query urlscan.io for behavioural verdicts
- Fuse ML and threat-intelligence signals into a colour-coded threat level
- Display full JSON analysis; exportable for further investigation
- Simple caching layer to reduce external API calls

---

## Project Structure

```text
phishing-dashboard/
│
├── app/                    # Flask application package
│   ├── __init__.py         # App factory / configuration
│   ├── analysis_service.py # Orchestrates parsing, ML, and TI calls
│   ├── cache.py            # In-memory cache for API lookups
│   ├── email_parser.py     # Extracts sender, subject, URLs, indicators
│   ├── ml_model.py         # Loads model and exposes predict function
│   ├── routes.py           # Flask routes (/, /analyze)
│   ├── urlscan_api.py      # urlscan.io integration
│   └── virustotal_api.py   # VirusTotal integration
│
├── data/                   # Datasets
│   ├── Phishing_Email.csv  # Raw Kaggle dataset
│   └── labeled_emails.csv  # Cleaned dataset used for training
│
├── models/
│   └── ml_model.joblib     # Trained TF-IDF + Logistic Regression model
│
├── reports/                # Evaluation artefacts (created after training)
│   ├── confusion_matrix.png
│   └── metrics.json
│
├── static/
│   └── style.css           # CSS for the dashboard UI
│
├── templates/
│   └── index.html          # Main dashboard page
│
├── tests/
│   ├── test_fusion.py      # Tests for fusion logic
│   ├── test_parser.py      # Tests for email parsing
│   ├── train_model.py      # Script used during experimentation
│   └── samples/            # Example emails for tests/demo
│       ├── phish1.txt
│       └── Phishing_Email.csv
│
├── prepare_dataset_from_csv.py  # Cleans raw CSV into labelled dataset
├── train_model.py               # Trains and saves the ML model
├── report_confusion.py          # Generates confusion matrix plot
├── run.py                       # Runs the Flask development server
├── requirements.txt             # Runtime dependencies
└── requirements-dev.txt         # Extra tools for development / testing
