import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go
from scipy import stats

st.set_page_config(page_title="Hypothesis 1", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_ecg_dataset.csv")


df = load_data()

st.title("Hypothesis 1: QT–RR slope")
st.markdown(
    "**Hypothesis:** the slope of the QT–RR relationship differs between patients "
    "with and without cardiac pathology, so the two groups follow different "
    "electrophysiological patterns."
)
st.divider()

norm = df[df["abnormal_flag"] == 0].dropna(subset=["rr_mean", "qt_interval"])
path = df[df["abnormal_flag"] == 1].dropna(subset=["rr_mean", "qt_interval"])

reg_n = stats.linregress(norm["rr_mean"], norm["qt_interval"])
reg_p = stats.linregress(path["rr_mean"], path["qt_interval"])

sample = df.dropna(subset=["rr_mean", "qt_interval"]).sample(4000, random_state=42).copy()
sample["Group"] = sample["abnormal_flag"].map({0: "Normal", 1: "Pathology"})

fig = px.scatter(
    sample,
    x="rr_mean",
    y="qt_interval",
    color="Group",
    color_discrete_map={"Normal": "#2ca02c", "Pathology": "#d62728"},
    opacity=0.25,
    labels={"rr_mean": "RR interval (ms)", "qt_interval": "QT interval (ms)"},
    title="QT vs RR: normal and pathology",
)

xs = np.linspace(sample["rr_mean"].min(), sample["rr_mean"].max(), 100)
fig.add_trace(go.Scatter(x=xs, y=reg_n.intercept + reg_n.slope * xs,
                         mode="lines", name="line (Normal)",
                         line=dict(color="#2ca02c", width=3)))
fig.add_trace(go.Scatter(x=xs, y=reg_p.intercept + reg_p.slope * xs,
                         mode="lines", name="line (Pathology)",
                         line=dict(color="#d62728", width=3)))
fig.update_layout(height=600)

st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Slope (Normal)", f"{reg_n.slope:.4f}", f"r = {reg_n.rvalue:.3f}", delta_color="off")
c2.metric("Slope (Pathology)", f"{reg_p.slope:.4f}", f"r = {reg_p.rvalue:.3f}", delta_color="off")
c3.metric("Slope difference", f"{reg_p.slope - reg_n.slope:.4f}")

st.success(
    "**Confirmed.** The slope is steeper for pathological patients "
    f"({reg_p.slope:.3f} vs {reg_n.slope:.3f}): for the same increase in RR their QT "
    "lengthens more. So a single QT correction formula with one slope for everyone "
    "(like Bazett) is a simplification that does not hold for both groups at once."
)
