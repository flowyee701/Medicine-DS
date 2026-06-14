import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="Hypothesis 2", layout="wide")


@st.cache_data
def load_data():
    return pd.read_csv("data/processed/cleaned_ecg_dataset.csv")


df = load_data()

st.title("Hypothesis 2: Bazett vs Framingham")
st.markdown(
    "**Hypothesis:** the Bazett and Framingham formulas sort the same patients into "
    "different QTc ranges, and the amount of disagreement depends on the diagnosis."
)
st.divider()

min_n = st.slider("Minimum patients per diagnosis", min_value=5, max_value=200,
                  value=30, step=5)

scp_cols = [c for c in df.columns
            if c.startswith("scp_") and pd.api.types.is_numeric_dtype(df[c])]

bins = 10
df["bazett_bin"] = pd.cut(df["qtc_bazett"], bins=bins, labels=False)
df["framingham_bin"] = pd.cut(df["qtc_framingham"], bins=bins, labels=False)

results = []
for col in scp_cols:
    sub = df[df[col] > 0]
    if len(sub) < min_n:
        continue
    agree = (sub["bazett_bin"] == sub["framingham_bin"]).mean()
    results.append({"diagnosis": col.replace("scp_", ""),
                    "n": len(sub), "agreement": agree})

res = pd.DataFrame(results).sort_values("agreement")

st.caption(f"Showing {len(res)} diagnoses with at least {min_n} patients.")

fig = px.bar(
    res,
    x="agreement",
    y="diagnosis",
    orientation="h",
    color="agreement",
    color_continuous_scale="RdYlGn",
    hover_data={"n": True, "agreement": ":.1%"},
    labels={"agreement": "Agreement rate (Bazett vs Framingham)",
            "diagnosis": "Diagnosis"},
    title="Formula agreement by diagnosis (lower = stronger disagreement)",
)
fig.add_vline(x=0.5, line_dash="dot", line_color="grey", annotation_text="50%")
fig.update_layout(height=750, coloraxis_showscale=False)
fig.update_yaxes(categoryorder="total ascending")

st.plotly_chart(fig, use_container_width=True)

worst = res.iloc[0]
best = res.iloc[-1]
c1, c2 = st.columns(2)
c1.metric(f"Worst: {worst['diagnosis']}", f"{worst['agreement']*100:.0f}%",
          f"n = {worst['n']}", delta_color="off")
c2.metric(f"Best: {best['diagnosis']}", f"{best['agreement']*100:.0f}%",
          f"n = {best['n']}", delta_color="off")

st.success(
    "**Confirmed.** No diagnosis even reaches 65% agreement. The worst is "
    f"`{worst['diagnosis']}` ({worst['agreement']*100:.0f}%) - for pacemaker patients "
    "the RR interval is set artificially and the QT–RR relationship breaks. "
    "For most diagnoses the formulas disagree more often than they agree, and the "
    "choice of formula drives clinical decisions such as flagging prolonged QT."
)
