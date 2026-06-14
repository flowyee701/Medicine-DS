import streamlit as st
import pandas as pd
import json
import requests
import plotly.io as pio

data = pd.read_csv("data/processed/cleaned_ecg_dataset.csv")
data['age'] = data['age'].astype(int)
data['heart_rate'] = data['heart_rate'].astype(int)

st.title("ECG")
st.write("Data visualisation",data.head())
st.info("Графики — в разделах слева: Polar и Hypo3")

API = "http://127.0.0.1:8000"

def show_chart(path, title):
    st.title(title)
    resp = requests.get(f"{API}{path}")
    st.plotly_chart(pio.from_json(resp.text), use_container_width=True)

with st.form("my_form"):
    st.write("Inside the form")
    slider_age = st.slider("Age", min_value=1, max_value=115, value=[0, int(data['age'].median())])
    slider_hr = st.slider("Heart Rate", min_value=30, max_value=150, value=[20,int(data['heart_rate'].median())])

    # Every form must have a submit button.
    submitted = st.form_submit_button("Submit")
    if submitted:
        # data[(data['age'].between(*slider_age)) & (data['heart_rate'] == slider_hr)]
        st.spinner()
        show_chart(f"/ageheart/{slider_age[0]}_{slider_age[1]}_{slider_hr[0]}_{slider_hr[1]}", " ")
        st.balloons()
        col1, col2 = st.columns(2)
        slider_age_mean = int((slider_age[0] + slider_age[1]) / 2)
        slider_hr_mean = int((slider_hr[0] + slider_hr[1]) / 2)
        col2.metric("Age", f"{slider_age_mean} y.o", f"{round((slider_age_mean - int(data['age'].median())) / int(data['age'].median()), 2) * 100:.0f}%")
        col1.metric("Heart rate", f"{slider_hr_mean} hpm", f"{round((slider_hr_mean-int(data['heart_rate'].median())) / int(data['heart_rate'].median()), 2) * 100:.0f}%")
        

options = st.multiselect(
    "What are your favorite cat names?",
    ["Jellybeans", "Fish Biscuit", "Madam President"],
    max_selections=5,
    accept_new_options=True,
)

st.write("You selected:", options)


popover = st.popover("Filter items")
red = popover.checkbox("Show red items.", True)
blue = popover.checkbox("Show blue items.", True)

if red:
    st.write(":red[This is a red item.]")
if blue:
    st.write(":blue[This is a blue item.]")
        
