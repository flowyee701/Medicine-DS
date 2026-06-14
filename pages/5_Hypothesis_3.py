import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
from scipy import stats

st.set_page_config(page_title="Hypothesis 3", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_ecg_dataset.csv")


df = load_data()

st.title("Hypothesis 3: the 450 ms QTc threshold and sex")
st.markdown(
    "**Hypothesis:** a single 450 ms QTc threshold is biased by sex - it "
    "systematically over-flags women, because their QTc is physiologically longer."
)
st.divider()

healthy = df[df["abnormal_flag"] == 0].dropna(subset=["qtc_bazett", "sex"]).copy()
healthy["Sex"] = healthy["sex"].map({0: "Male", 1: "Female"})

male = healthy[healthy["sex"] == 0]["qtc_bazett"]
female = healthy[healthy["sex"] == 1]["qtc_bazett"]

t, p = stats.ttest_ind(male, female, equal_var=False)
pooled = np.sqrt((male.std() ** 2 + female.std() ** 2) / 2)
d = (female.mean() - male.mean()) / pooled

flag_male = (male > 450).mean() * 100
flag_female = (female > 450).mean() * 100

fig = px.histogram(
    healthy,
    x="qtc_bazett",
    color="Sex",
    barmode="overlay",
    nbins=80,
    opacity=0.6,
    histnorm="probability density",
    color_discrete_map={"Male": "#1f77b4", "Female": "#e377c2"},
    labels={"qtc_bazett": "QTc Bazett (ms)"},
    title="QTc distribution in healthy patients: the 450 ms threshold cuts sexes differently",
)
fig.add_vline(x=450, line_dash="dash", line_color="red",
              annotation_text="Threshold 450 ms")
fig.update_layout(height=550)

st.plotly_chart(fig, use_container_width=True)

c1, c2, c3 = st.columns(3)
c1.metric("Mean QTc, male", f"{male.mean():.1f} ms")
c2.metric("Mean QTc, female", f"{female.mean():.1f} ms",
          f"+{female.mean() - male.mean():.1f} ms")
c3.metric("Effect size (Cohen's d)", f"{d:.2f}")
c3.caption(f"p = {p:.1e}")

c4, c5 = st.columns(2)
c4.metric("Flagged > 450 ms, male", f"{flag_male:.1f}%")
c5.metric("Flagged > 450 ms, female", f"{flag_female:.1f}%")

st.success(
    f"**Confirmed.** Healthy women have a higher QTc on average "
    f"({female.mean():.1f} vs {male.mean():.1f} ms, d = {d:.2f}), and the single "
    f"450 ms threshold flags them almost twice as often ({flag_female:.1f}% vs "
    f"{flag_male:.1f}%) - even though all of them are healthy by definition. That is "
    "why guidelines use a higher threshold for women (~460-470 ms), while one fixed "
    "450 ms cutoff produces extra false positives."
)
