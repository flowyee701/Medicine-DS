import streamlit as st
import pandas as pd
import json
import requests
import plotly.io as pio

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")
st.title("ECG")
st.write("Data visualisation",data.head())
st.info("Графики — в разделах слева: Polar и Hypo3")

API = "http://127.0.0.1:8000"

def show_chart(path, title):
    st.title(title)
    resp = requests.get(f"{API}{path}")
    st.plotly_chart(pio.from_json(resp.text), use_container_width=True)