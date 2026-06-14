import streamlit as st
from streamlit.components.v1 import html as st_html
from pathlib import Path

st.set_page_config(page_title="Heart", layout="wide")

st.title("Heart Animation")
st.caption("3D model of a beating heart with the sound of a heartbeat")

st.audio("Heart animation/stuk_serdca_-_zvuk_serdcebieniya.mp3", autoplay=True)

heart_path = Path(__file__).parent.parent / "Heart animation" / "heart.html"
heart_html = heart_path.read_text(encoding="utf-8")

st_html(heart_html, height=820, scrolling=True)
