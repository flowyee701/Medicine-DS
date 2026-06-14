import ast
from collections import defaultdict
from pathlib import Path

import numpy as np
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st
from plotly.subplots import make_subplots

st.set_page_config(page_title="Data Analysis", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_ecg_dataset.csv")


@st.cache_data
def load_parsed_codes():
    df = load_data()
    return df["scp_codes"].apply(ast.literal_eval)


df = load_data()

st.title("Data Analysis")
st.markdown(
    "Exploratory analysis of the cleaned dataset (21,419 records). "
    "This page mirrors the EDA part of the notebook: every chart comes with a short read."
)

st.header("1. Descriptive statistics")
numeric_cols = ["heart_rate", "rr_mean", "qrs_duration", "qt_interval", "pr_interval",
                "age", "qtc_bazett", "qtc_fridericia", "qtc_framingham", "qtc_spread"]
stats = df[numeric_cols].agg(["mean", "median", "std", "min", "max"]).round(2)
st.dataframe(stats, use_container_width=True)

g1, g2, g3 = st.columns(3)
g1.markdown("**Heart rate group**")
g1.dataframe(df["heart_rate_group"].value_counts())
g2.markdown("**Age group**")
g2.dataframe(df["age_group"].value_counts())
g3.markdown("**Axis deviation**")
g3.dataframe(df["axis_deviation"].value_counts())

st.divider()

st.header("2. Distribution of ECG parameters")
fig = make_subplots(rows=2, cols=2, subplot_titles=(
    "Heart Rate (bpm)", "QRS Duration (ms)", "QT Interval (ms)", "Age (years)"))
panels = [("heart_rate", 1, 1), ("qrs_duration", 1, 2), ("qt_interval", 2, 1), ("age", 2, 2)]
for col, r, c in panels:
    fig.add_trace(go.Histogram(x=df[col], nbinsx=60, marker_color="steelblue",
                               marker_line_color="white", marker_line_width=0.3,
                               showlegend=False), row=r, col=c)
    fig.add_vline(x=df[col].median(), line_color="darkred", row=r, col=c,
                  annotation_text=f"median {df[col].median():.0f}")
fig.update_layout(height=650, bargap=0.02)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "Heart rate is right-skewed (median 71 bpm) with a long tail toward tachycardia. "
    "QRS duration peaks sharply at 94 ms. the tail above 120 ms corresponds to conduction "
    "abnormalities like bundle branch block. QT is roughly symmetric around 394 ms. Age is "
    "bimodal: a small cluster of young patients and a large 50-80 group (median 61), typical "
    "of a cardiology clinic."
)

st.divider()

st.header("3. Heart rate groups")
fig = px.histogram(df, x="heart_rate", nbins=60, labels={"heart_rate": "Heart rate (bpm)"},
                   title="Heart rate split into bradycardia / normal / tachycardia")
fig.add_vline(x=60, line_dash="dash", line_color="green", annotation_text="60")
fig.add_vline(x=100, line_dash="dash", line_color="red", annotation_text="100")
fig.update_layout(height=420)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "Cut-offs at 60 and 100 bpm define the three groups: **bradycardia** (<60), "
    "**normal_hr** (60-100), **tachycardia** (>=100). Most records fall into the normal band."
)

st.divider()

st.header("4. Diagnostic confidence")
statements_path = Path("data/raw/ptb-xl/scp_statements.csv")
if statements_path.exists():
    scp_stat = pd.read_csv(statements_path)
    cat = scp_stat.set_index(scp_stat.columns[0])
    pure = cat[cat["diagnostic"].notna() & cat["form"].isna() & cat["rhythm"].isna()]
    vals = defaultdict(list)
    for codes in load_parsed_codes():
        for k, v in codes.items():
            if k in pure.index:
                vals[k].append(v)
    agg = pd.DataFrame([
        {"code": k, "class": pure.loc[k, "diagnostic_class"],
         "description": pure.loc[k, "description"], "n": len(v), "mean_conf": np.mean(v)}
        for k, v in vals.items()])
    agg = agg[agg["n"] >= 30].sort_values("mean_conf")

    fig = px.bar(agg, x="mean_conf", y="code", orientation="h", color="class",
                 hover_data={"description": True, "n": True, "mean_conf": ":.1f"},
                 labels={"mean_conf": "Average doctor's confidence (0-100)",
                         "code": "Diagnosis", "class": "Class"},
                 title="Which diagnoses do doctors make with less confidence?")
    fig.update_yaxes(categoryorder="array", categoryarray=agg["code"])
    fig.add_vline(x=100, line_dash="dot", line_color="grey")
    fig.update_layout(height=800)
    st.plotly_chart(fig, use_container_width=True)
    st.markdown(
        "Conduction disorders (CD) sit near 100 - their ECG criteria are unambiguous. "
        "Myocardial infarction codes (MI) cluster at the low-confidence end, since MI "
        "localization needs subtle multi-lead changes. ST/T changes (STTC) span the widest "
        "range. Confidence should be treated as a soft label, not a hard 0/1."
    )
else:
    st.info("scp_statements.csv not found - skipping the diagnostic confidence chart.")

st.divider()

st.header("5. Interrelationships of ECG parameters")
sample = df.sample(5000, random_state=42).copy()
sample["Status"] = sample["abnormal_flag"].map({0: "Norm", 1: "Pathology"})
col_a, col_b = st.columns(2)

fig = px.scatter(sample, x="rr_mean", y="qt_interval", color="heart_rate",
                 color_continuous_scale="RdBu_r", opacity=0.7,
                 labels={"rr_mean": "RR mean (ms)", "qt_interval": "QT interval (ms)",
                         "heart_rate": "Heart rate"},
                 title="RR mean vs QT interval (color = heart rate)")
fig.update_layout(height=500)
col_a.plotly_chart(fig, use_container_width=True)

fig = px.scatter(sample, x="age", y="qrs_duration", color="Status",
                 color_discrete_map={"Norm": "#2ca02c", "Pathology": "#d62728"},
                 opacity=0.6, labels={"age": "Age", "qrs_duration": "QRS duration (ms)"},
                 title="Age vs QRS duration (color = norm / pathology)")
fig.update_layout(height=500)
col_b.plotly_chart(fig, use_container_width=True)
st.markdown(
    "Left: a strong positive RR-QT relationship - longer cardiac cycle (lower HR, blue) means "
    "longer QT. This coupling is the basis of all QTc formulas (see Hypothesis 1). "
    "Right: normal QRS stays in a flat 75-110 ms band at any age. wide QRS (>120 ms) is almost "
    "exclusively pathology, and its density grows with age."
)

st.divider()

st.header("6. Distribution of ECG parameters by group")
b1, b2, b3 = st.columns(3)

fig = px.box(df, x="heart_rate_group", y="qt_interval",
             category_orders={"heart_rate_group": ["bradycardia", "normal_hr", "tachycardia"]},
             color="heart_rate_group", labels={"qt_interval": "QT interval (ms)",
                                                "heart_rate_group": "Heart rate group"},
             title="QT by heart rate group")
fig.update_layout(height=450, showlegend=False)
b1.plotly_chart(fig, use_container_width=True)

sex_frame = df.assign(Sex=df["sex"].map({0: "Male", 1: "Female"}))
fig = px.box(sex_frame, x="Sex", y="qrs_duration", color="Sex",
             labels={"qrs_duration": "QRS duration (ms)"}, title="QRS by sex")
fig.update_layout(height=450, showlegend=False)
b2.plotly_chart(fig, use_container_width=True)

pr_data = df[df["p_found"] == 1]
fig = px.box(pr_data, x="age_group", y="pr_interval",
             category_orders={"age_group": ["young", "middle", "senior"]},
             color="age_group", labels={"pr_interval": "PR interval (ms)",
                                        "age_group": "Age group"},
             title="PR by age group (p_found = 1)")
fig.update_layout(height=450, showlegend=False)
b3.plotly_chart(fig, use_container_width=True)
st.markdown(
    "QT drops from bradycardia (~450 ms) to tachycardia (~340 ms) as the cycle shortens. "
    "Men have wider QRS than women (~98 vs ~88 ms). PR grows with age (young ~150, senior "
    "~165 ms) - AV conduction slows down. Only sinus-rhythm records are used for PR."
)

st.divider()

st.header("7. Correlation heatmap")
corr_cols = ["heart_rate", "pr_interval", "qrs_duration", "qt_interval"]
corr = df[corr_cols].corr()
fig = px.imshow(corr, text_auto=".2f", color_continuous_scale="RdBu_r", zmin=-1, zmax=1,
                title="Correlations between ECG intervals")
fig.update_layout(height=450)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "Strongest link: heart_rate vs qt_interval (r = -0.73) - faster rate, shorter QT. "
    "QRS correlates moderately with QT (r = 0.36). PR is almost independent of everything "
    "else, confirming AV-node delay is separate from ventricular conduction."
)

st.divider()

st.header("8. Distribution of SCP codes")
codes = load_parsed_codes().apply(lambda x: list(x.keys())).explode()
num_codes = codes.value_counts().reset_index()
num_codes.columns = ["category", "count"]
num_codes.loc[num_codes["count"] / num_codes["count"].sum() < 0.025, "category"] = "Others"
num_codes = num_codes.groupby("category", as_index=False)["count"].sum()
fig = px.pie(num_codes, names="category", values="count", title="SCP code distribution")
fig.update_layout(height=550)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "SR (sinus rhythm) and NORM together make up over 40% of all assignments - most records "
    "are normal or near-normal. 'Others' aggregates rare codes (<2.5% each). The dataset is "
    "class-imbalanced, which any classifier has to account for."
)

st.divider()

st.header("9. Electrical axis vs QRS duration")
axis_sample = df.dropna(subset=["qrs_axis", "qrs_duration"]).sample(4000, random_state=42)
fig = px.scatter_polar(
    axis_sample, r="qrs_duration", theta="qrs_axis", color="axis_deviation",
    category_orders={"axis_deviation": ["normal", "left_deviation", "right_deviation"]},
    color_discrete_map={"normal": "#2ca02c", "left_deviation": "#d62728",
                        "right_deviation": "#1f77b4"},
    opacity=0.45,
    hover_data={"age": True, "heart_rate": True, "abnormal_flag": True},
    title="Electrical axis vs QRS duration (angle = axis, radius = QRS)")
fig.update_traces(marker=dict(size=4))
fig.update_layout(
    polar=dict(
        angularaxis=dict(direction="clockwise", rotation=0, tickmode="array",
                         tickvals=[-180, -150, -120, -90, -60, -30, 0, 30, 60, 90, 120, 150],
                         ticktext=["+/-180", "-150", "-120", "-90", "-60", "-30",
                                   "0", "+30", "+60", "+90", "+120", "+150"]),
        radialaxis=dict(title="QRS duration (ms)", range=[50, 200])),
    legend_title_text="Axis deviation", height=650)
st.plotly_chart(fig, use_container_width=True)
st.markdown(
    "Normal axis (green) forms a dense core in the 0-60 sector at short radii (healthy, narrow "
    "QRS). Left deviation (red) sits in the -30 to -90 zone and reaches large radii - many cases "
    "have QRS >120 ms, hinting at left bundle branch / fascicular blocks. Right deviation (blue) "
    "is sparse with mostly short QRS."
)
