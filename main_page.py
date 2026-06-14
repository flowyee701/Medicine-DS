import socket
import threading

import streamlit as st
import pandas as pd
import uvicorn

from main import app as api_app

st.set_page_config(page_title="ECG Explorer", layout="wide")


class APIServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass


def api_is_running():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex(("127.0.0.1", 8000)) == 0


def start_api():
    config = uvicorn.Config(api_app, host="127.0.0.1", port=8000, log_level="error")
    APIServer(config=config).run()


if not api_is_running():
    threading.Thread(target=start_api, daemon=True).start()


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_ecg_dataset.csv")


df = load_data()

st.title("ECG Arrhythmia Explorer")
st.markdown(
    "Analysis of ECG features based on the clinical **PTB-XL** database. "
    "The menu on the left has the heart animation and three tested hypotheses."
)

st.divider()

col1, col2, col3 = st.columns(3)
col1.metric("ECG records", f"{len(df):,}")
col2.metric("Features", df.shape[1])
abnormal_share = df["abnormal_flag"].mean() * 100
col3.metric("Abnormal share", f"{abnormal_share:.1f}%")

st.subheader("About the data")
st.markdown(
    """
- **PTB-XL** - 21,837 12-lead ECG records from ~19k patients (PhysioNet).
- Every record comes with SCP-ECG diagnoses and measured parameters
  (heart rate, PR / QRS / QT intervals, axes, etc.).
- We computed several derived columns: `abnormal_flag` (pathology present or not),
  number of diagnoses, age and heart rate groups.
"""
)

st.subheader("Hypotheses")
st.markdown(
    """
1. **QT–RR slope** differs between healthy and pathological patients.
2. **Bazett vs Framingham** - the formulas disagree, and it depends on the diagnosis.
3. **The 450 ms QTc threshold** is biased by sex and over-flags women.
"""
)

with st.expander("Show the first rows of the data"):
    st.dataframe(df.head(20))

st.info("Pick a page in the menu on the left to view the animation or the hypotheses.")
