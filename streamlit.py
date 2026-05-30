import streamlit as st
import pandas as pd
import json
import requests
import plotly.io as pio

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")
st.title("ECG")
st.write(data.head())

response = requests.get("http://127.0.0.1:8000/heart/80_120")
resp = requests.get("http://127.0.0.1:8000/elaxis")
fig = pio.from_json(json.dumps(resp.json()))
st.plotly_chart(fig, use_container_width=True)