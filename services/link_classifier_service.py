# This service will handle link classification logic (ML + LLM)

import joblib
import numpy as np
from utils.helpers import extract_features
from model import LamaLangChainClient

def classify_url_service(url):
    if not url:
        return None, 'URL is missing'
    model = joblib.load('./weights/rf_model.pkl')
    features = extract_features(url)
    features = np.array(features).reshape(1, -1)
    pred = model.predict(features)[0]
    label = 'Safe' if pred == 1 else 'Unsafe'
    gemini = LamaLangChainClient()
    m2_label = gemini.get_report(f"I will send you a link. Respond with only one word: safe or unsafe. No explanation, no punctuation, no newline—just the word,  link : {url} ")
    m2_label = m2_label.strip().capitalize()
    if label == m2_label:
        return label, None
    else:
        return m2_label, None
