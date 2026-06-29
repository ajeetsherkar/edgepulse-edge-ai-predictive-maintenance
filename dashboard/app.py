import requests
import streamlit as st
import pandas as pd

st.subheader("🔮 Live Prediction")

mean = st.number_input("Mean", value=-0.09)
std = st.number_input("Std", value=0.08)
rms = st.number_input("RMS", value=0.12)
max_v = st.number_input("Max", value=0.38)
min_v = st.number_input("Min", value=-0.72)
ptp = st.number_input("Peak to Peak", value=1.10)

if st.button("Predict Health"):
    
    payload = {
        "mean": mean,
        "std": std,
        "rms": rms,
        "max": max_v,
        "min": min_v,
        "peak_to_peak": ptp
    }

    response = requests.post(
        "http://127.0.0.1:8000/predict",
        json=payload
    )

    result = response.json()

    st.success(
        f"Prediction: {result['prediction']}"
    )

    st.metric(
        "Confidence",
        f"{result['confidence']}%"
    )

    st.info(
        f"Maintenance Action: {result['maintenance_action']}"
    )

    
st.set_page_config(
    page_title="EdgePulse Dashboard",
    layout="wide"
)

st.title("⚙️ EdgePulse")

st.subheader(
    "Edge-AI Predictive Maintenance Dashboard"
)

data = pd.read_csv(
    "data/processed/prediction_results.csv"
)
# ==================
# KPI CARDS
# ==================

total = len(data)

healthy = (
    data["prediction"]
    .eq("Healthy")
    .sum()
)

early = (
    data["prediction"]
    .eq("Early_Degradation")
    .sum()
)

critical = (
    data["prediction"]
    .eq("Critical")
    .sum()
)

failure = (
    data["prediction"]
    .eq("Imminent_Failure")
    .sum()
)

avg_conf = round(
    data["confidence"].mean(),
    2
)

c1,c2,c3,c4,c5 = st.columns(5)

c1.metric(
    "Total",
    total
)

c2.metric(
    "Healthy",
    healthy
)

c3.metric(
    "Early",
    early
)

c4.metric(
    "Critical",
    critical
)

c5.metric(
    "Failure",
    failure
)

st.write(
    f"Average Confidence: {avg_conf}%"
)

st.divider()

st.subheader(
    "Prediction Results"
)

st.dataframe(data)

import matplotlib.pyplot as plt

st.subheader(
    "Machine Health Distribution"
)

fig, ax = plt.subplots(
    figsize=(8,5)
)

data["prediction"].value_counts().plot(
    kind="bar",
    ax=ax
)

ax.set_xlabel(
    "Health Stage"
)

ax.set_ylabel(
    "Count"
)

st.pyplot(fig)

import matplotlib.pyplot as plt

st.subheader(
    "Prediction Confidence Distribution"
)

fig2, ax2 = plt.subplots(
    figsize=(10,5)
)

ax2.hist(
    data["confidence"],
    bins=10
)

ax2.set_xlabel(
    "Confidence (%)"
)

ax2.set_ylabel(
    "Machines"
)

st.pyplot(fig2)

st.subheader(
    "🚨 Machines Requiring Attention"
)

alerts = data[
    data["prediction"] != "Healthy"
]

alerts = alerts[
    [
        "file",
        "prediction",
        "confidence",
        "maintenance_action"
    ]
]

st.dataframe(
    alerts.head(20).style.applymap(
        lambda x:
        "background-color:#ffcccc"
        if x=="Critical"
        else (
            "background-color:#fff0b3"
            if x=="Early_Degradation"
            else ""
        ),
        subset=["prediction"]
    )
)