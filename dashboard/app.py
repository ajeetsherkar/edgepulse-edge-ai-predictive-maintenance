import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt
from datetime import datetime
import os

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="EdgePulse Dashboard",
    layout="wide"
)

# ==========================
# TITLE
# ==========================
st.title("⚙️ EdgePulse")
st.subheader(
    "Edge-AI Predictive Maintenance Dashboard"
)

# ==========================
# LIVE PREDICTION
# ==========================
st.header("🔮 Live Prediction")

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

    st.progress(int(result["confidence"]))

# ==========================
# BATCH PREDICTION
# ==========================
st.divider()

st.header("📂 Batch Prediction")

uploaded_file = st.file_uploader(
    "Upload CSV File",
    type=["csv"]
)

if uploaded_file is not None:

    df = pd.read_csv(uploaded_file)

    st.subheader("Uploaded Data")
    st.dataframe(df.head())

    required_columns = [
        "mean",
        "std",
        "rms",
        "max",
        "min",
        "peak_to_peak"
    ]

    if all(col in df.columns for col in required_columns):

        results = []

        for _, row in df.iterrows():

            payload = {
                "mean": float(row["mean"]),
                "std": float(row["std"]),
                "rms": float(row["rms"]),
                "max": float(row["max"]),
                "min": float(row["min"]),
                "peak_to_peak": float(row["peak_to_peak"])
            }

            response = requests.post(
                "http://127.0.0.1:8000/predict",
                json=payload
            )

            result = response.json()

            results.append({
                "prediction": result["prediction"],
                "confidence": result["confidence"],
                "maintenance_action":
                result["maintenance_action"]
            })

        result_df = pd.concat(
            [
                df.reset_index(drop=True),
                pd.DataFrame(results)
            ],
            axis=1
        )

        st.subheader(
            "Prediction Results"
        )

        st.dataframe(result_df)

        csv = result_df.to_csv(
            index=False
        )

        st.download_button(
            "⬇ Download Results CSV",
            csv,
            "prediction_results.csv",
            "text/csv"
        )

        os.makedirs(
            "data/processed",
            exist_ok=True
        )

        result_df.to_csv(
            "data/processed/prediction_results.csv",
            index=False
        )

    else:
        st.error(
            f"CSV must contain columns: {required_columns}"
        )


# ==========================
# DASHBOARD ANALYTICS
# ==========================
healthy = 0
early = 0
critical = 0
failure = 0

try:

    data = pd.read_csv(
        "data/processed/prediction_results.csv"
    )

    st.caption(
        f"Last Updated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}"
    )

    selected_status = st.sidebar.multiselect(
        "Filter by Health Status",
        options=data["prediction"].unique(),
        default=list(data["prediction"].unique())
    )

    filtered_data = data[
        data["prediction"].isin(selected_status)
    ]

    total = len(filtered_data)

    healthy = (
        filtered_data["prediction"]
        .eq("Healthy")
        .sum()
    )

    early = (
        filtered_data["prediction"]
        .eq("Early_Degradation")
        .sum()
    )

    critical = (
        filtered_data["prediction"]
        .eq("Critical")
        .sum()
    )

    failure = (
        filtered_data["prediction"]
        .eq("Imminent_Failure")
        .sum()
    )

    avg_conf = round(
        filtered_data["confidence"].mean(),
        2
    )

    st.divider()

    st.header(
        "📊 Dashboard Analytics"
    )

    c1, c2, c3, c4, c5 = st.columns(5)

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

    if total > 0:
        system_health = round(
            healthy / total * 100,
            2
        )
    else:
        system_health = 0

    st.metric(
        "🏭 Overall Fleet Health",
        f"{system_health}%"
    )

    if failure > 0:
        st.error(
            f"🚨 {failure} machines are in Imminent Failure state!"
        )

    elif critical > 0:
        st.warning(
            f"⚠️ {critical} machines require urgent maintenance."
        )

    else:
        st.success(
            "✅ All machines are operating normally."
        )

    st.write(
        f"Average Confidence: {avg_conf}%"
    )

    st.subheader(
        "Prediction Results"
    )

    def color_prediction(val):
        if val == "Healthy":
            return "background-color: lightgreen"
        elif val == "Early_Degradation":
            return "background-color: yellow"
        elif val == "Critical":
            return "background-color: orange"
        elif val == "Imminent_Failure":
            return "background-color: red"
        return ""

    st.dataframe(
        filtered_data.style.applymap(
            color_prediction,
            subset=["prediction"]
        )
    )

    # ==========================
    # BAR CHART
    # ==========================
    st.subheader(
        "Machine Health Distribution"
    )

    fig, ax = plt.subplots(
        figsize=(8,5)
    )

    filtered_data["prediction"].value_counts().plot(
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

    # ==========================
    # PIE CHART
    # ==========================
    st.subheader(
        "Health Status Breakdown"
    )

    fig2, ax2 = plt.subplots(
        figsize=(7,7)
    )

    filtered_data["prediction"].value_counts().plot(
        kind="pie",
        autopct="%1.1f%%",
        ax=ax2
    )

    ax2.set_ylabel("")

    st.pyplot(fig2)

    # ==========================
    # CONFIDENCE HISTOGRAM
    # ==========================
    st.subheader(
        "Prediction Confidence Distribution"
    )

    fig3, ax3 = plt.subplots(
        figsize=(10,5)
    )

    ax3.hist(
        filtered_data["confidence"],
        bins=10
    )

    ax3.set_xlabel(
        "Confidence (%)"
    )

    ax3.set_ylabel(
        "Machines"
    )

    st.pyplot(fig3)

    # ==========================
    # ALERT TABLE
    # ==========================
    st.subheader(
        "🚨 Machines Requiring Attention"
    )

    alerts = filtered_data[
        filtered_data["prediction"] != "Healthy"
    ]

    if not alerts.empty:

        alerts = alerts[
            [
                "file",
                "prediction",
                "confidence",
                "maintenance_action"
            ]
        ]

        alerts = alerts.sort_values(
            by="confidence",
            ascending=False
        )

        st.subheader(
            "🔥 Top Risk Machines"
        )

        st.dataframe(
            alerts.head(10)
        )

except Exception as e:
    st.warning(
        f"Analytics data unavailable: {e}"
    )

st.subheader("🛠 Maintenance Summary")

st.write(f"🟢 Healthy Machines: {healthy}")
st.write(f"🟡 Early Degradation: {early}")
st.write(f"🟠 Critical Machines: {critical}")
st.write(f"🔴 Imminent Failure: {failure}")