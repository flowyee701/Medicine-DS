import streamlit as st
from streamlit.components.v1 import html as st_html
from pathlib import Path

st.set_page_config(layout="wide")
st.title("Heart visualisation")
heart_path = heart_path = Path(__file__).parent.parent / "Heart animation" / "heart.html"
heart_html = heart_path.read_text(encoding="utf-8")
st_html(heart_html, height=820, scrolling=True)