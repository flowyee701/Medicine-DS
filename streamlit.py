import streamlit as st
import pandas as pd
import json
import requests

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")
st.title("ECG")
st.write(data.head())

response = requests.get("http://127.0.0.1:8000/heart/80_120")
rep = json.loads(response.json())
st.json(response.json())