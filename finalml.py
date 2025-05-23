# -*- coding: utf-8 -*-
"""finalML.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1Sw09q5zJWBJreXnQpB6sPHVQQBTtWySu
"""

import pandas as pd
import numpy as np
import re, math
from urllib.parse import urlparse
from collections import Counter
import joblib
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
import plotly.express as px
import gradio as gr

# Step 1: Feature Extraction
def extract_features(url):
    parsed = urlparse(url)
    features = {}
    features['url_length'] = len(url)
    features['https'] = 1 if parsed.scheme == 'https' else 0
    features['num_dots'] = parsed.netloc.count('.')
    suspicious_keywords = ['credit', 'card', 'secure', 'login', 'verify', 'account']
    features['suspicious_keywords'] = sum(1 for keyword in suspicious_keywords if keyword in url.lower())
    entropy = 0
    for char, count in Counter(url).items():
        p = count / len(url)
        entropy += -p * math.log2(p) if p > 0 else 0
    features['entropy'] = entropy
    features['has_ip'] = 1 if re.match(r'^\d+\.\d+\.\d+\.\d+', parsed.netloc) else 0
    features['special_chars'] = len(re.findall(r'[^a-zA-Z0-9.]', url))
    return features

# Step 2: Load or Train Model
try:
    model = joblib.load('phishing_detector.pkl')
except FileNotFoundError:
    # Fallback: train a default model
    data = {
        'url': [
            'https://secure.bank.com/login',
            'http://phishing-site.com/credit-card',
            'https://example.com',
            'http://malicious.site/verify',
            'https://legitimate-site.net'
        ],
        'label': [0, 1, 0, 1, 0]
    }
    df = pd.DataFrame(data)
    df_features = df['url'].apply(lambda x: pd.Series(extract_features(x)))
    X = df_features
    y = df['label']
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    joblib.dump(model, 'phishing_detector.pkl')

# Global history for dashboard
history = {'predictions': []}

# Step 3: Prediction and Visualization
def predict_dashboard(url):
    features = extract_features(url)
    features_df = pd.DataFrame([features])
    proba = model.predict_proba(features_df)[0]
    labels = ['Legitimate', 'Phishing']
    pie_fig = px.pie(names=labels, values=proba, title='Prediction Probabilities')
    pred_index = int(np.argmax(proba))
    pred_label = labels[pred_index]
    history['predictions'].append(pred_label)
    count_series = pd.Series(history['predictions']).value_counts()
    bar_fig = px.bar(x=count_series.index, y=count_series.values, title='Prediction Counts',
                     labels={'x':'Prediction','y':'Count'})
    return pred_label, pie_fig, bar_fig

# Step 4: Create Gradio App
with gr.Blocks() as demo:
    gr.Markdown("## Phishing URL Detection App")
    with gr.Row():
        url_input = gr.Textbox(label="Enter URL", placeholder="https://example.com/login")
        predict_btn = gr.Button("Predict")
    with gr.Row():
        label_output = gr.Textbox(label="Prediction Result")
    with gr.Tabs():
        with gr.Tab("Probability Distribution"):
            pie_output = gr.Plot()
        with gr.Tab("Dashboard"):
            bar_output = gr.Plot()
    predict_btn.click(fn=predict_dashboard,
                      inputs=[url_input],
                      outputs=[label_output, pie_output, bar_output])
demo.launch(share=True)

pip install gradio



"""# New Section"""