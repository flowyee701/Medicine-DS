import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="Records API", layout="wide")

API = "http://127.0.0.1:8000"

DIAGNOSIS_OPTIONS = [
    "NORM", "CRBBB", "CLBBB", "IRBBB", "LAFB", "IVCD", "1AVB", "LVH",
    "LAO/LAE", "IMI", "AMI", "ASMI", "ILMI", "ISC", "ISCAL", "NDT",
    "NST", "PVC",
]

st.title("Dataset API")
st.caption("This page talks to the FastAPI REST API")
def api_online():
    try:
        requests.get(API + "/", timeout=2)
        return True
    except requests.exceptions.RequestException:
        return False


if not api_online():
    st.error("API is not reachable. Run `uvicorn main:app --reload` in the project folder.")
    st.stop()

st.subheader("Browse records - GET /records")
c1, c2, c3 = st.columns(3)
min_age = c1.number_input("Min age", 0, 120, 50)
max_age = c1.number_input("Max age", 0, 120, 70)
min_hr = c2.number_input("Min heart rate", 0, 300, 0)
max_hr = c2.number_input("Max heart rate", 0, 300, 200)
abnormal = c3.selectbox("Abnormal flag", ["any", "0", "1"])
limit = c3.number_input("Page size", 1, 200, 20)
offset = st.number_input("Offset", 0, 100000, 0, step=20)

params = {"min_age": min_age, "max_age": max_age, "min_hr": min_hr,
          "max_hr": max_hr, "limit": limit, "offset": offset}
if abnormal != "any":
    params["abnormal"] = int(abnormal)

data = requests.get(API + "/records", params=params).json()
st.write(f"Total matched: **{data['total']}** - showing {data['count']} from offset {offset}")
if data["records"]:
    st.dataframe(pd.DataFrame(data["records"]))

st.divider()

st.subheader("Add a record - POST /records")
with st.form("add_record"):
    a1, a2, a3 = st.columns(3)
    age = a1.number_input("Age", 0, 120, 60)
    sex_label = a1.selectbox("Sex", ["Male", "Female"])
    heart_rate = a1.number_input("Heart rate", 20.0, 250.0, 71.0)
    rr_mean = a1.number_input("RR mean", 250.0, 2000.0, 842.0)
    pr_interval = a2.number_input("PR interval", 0.0, 400.0, 160.0)
    qrs_duration = a2.number_input("QRS duration", 40.0, 250.0, 94.0)
    qt_interval = a2.number_input("QT interval", 200.0, 700.0, 394.0)
    qtc_bazett = a2.number_input("QTc Bazett", 300.0, 650.0, 430.0)
    p_axis = a3.number_input("P axis", -180.0, 180.0, 50.0)
    qrs_axis = a3.number_input("QRS axis", -180.0, 180.0, 20.0)
    t_axis = a3.number_input("T axis", -180.0, 270.0, 45.0)
    p_duration = a3.number_input("P duration", 0.0, 200.0, 114.0)

    st.markdown("**Diagnosis**")
    d1, d2 = st.columns(2)
    abnormal_label = d1.selectbox("Record status", ["Normal", "Abnormal"])
    diagnoses = d2.multiselect("SCP codes (diagnoses)", DIAGNOSIS_OPTIONS, default=["NORM"])

    submitted = st.form_submit_button("Send POST")

if submitted:
    body = {"age": age, "sex": 1 if sex_label == "Female" else 0,
            "heart_rate": heart_rate, "rr_mean": rr_mean, "pr_interval": pr_interval,
            "qrs_duration": qrs_duration, "qt_interval": qt_interval,
            "qtc_bazett": qtc_bazett, "p_axis": p_axis, "qrs_axis": qrs_axis,
            "t_axis": t_axis, "p_duration": p_duration,
            "abnormal_flag": 1 if abnormal_label == "Abnormal" else 0,
            "scp_codes": ", ".join(diagnoses)}
    resp = requests.post(API + "/records", json=body)
    if resp.status_code == 201:
        st.success("Record created and saved to user_submissions.csv")
        st.json(resp.json()["record"])
    else:
        st.error(f"Failed: {resp.status_code} - {resp.text}")
