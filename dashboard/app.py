import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

# ==========================
# PAGE CONFIG
# ==========================
st.set_page_config(
    page_title="EdgePulse Dashboard",
    layout="wide"
)

# ==========================
# LIVE PREDICTION
# ==========================
st.title("⚙️ EdgePulse")
st.subheader("Edge-AI Predictive Maintenance Dashboard")

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
                "maintenance_action": result["maintenance_action"]
            })

        result_df = pd.concat(
            [
                df.reset_index(drop=True),
                pd.DataFrame(results)
            ],
            axis=1
        )

        st.subheader("Prediction Results")
        st.dataframe(result_df)

        csv = result_df.to_csv(index=False)

        st.download_button(
            "⬇ Download Results CSV",
            csv,
            "prediction_results.csv",
            "text/csv"
        )

    else:
        st.error(
            f"CSV must contain columns: {required_columns}"
        )

# ==========================
# DASHBOARD ANALYTICS
# ==========================
try:
    data = pd.read_csv(
        "data/processed/prediction_results.csv"
    )

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

    st.divider()
    st.header("📊 Dashboard Analytics")

    c1, c2, c3, c4, c5 = st.columns(5)

    c1.metric("Total", total)
    c2.metric("Healthy", healthy)
    c3.metric("Early", early)
    c4.metric("Critical", critical)
    c5.metric("Failure", failure)

    st.write(
        f"Average Confidence: {avg_conf}%"
    )

    st.subheader(
        "Prediction Results"
    )

    st.dataframe(data)

    st.subheader(
        "Machine Health Distribution"
    )

    fig, ax = plt.subplots(
        figsize=(8, 5)
    )

    data["prediction"].value_counts().plot(
        kind="bar",
        ax=ax
    )

    ax.set_xlabel("Health Stage")
    ax.set_ylabel("Count")

    st.pyplot(fig)

    st.subheader(
        "Prediction Confidence Distribution"
    )

    fig2, ax2 = plt.subplots(
        figsize=(10, 5)
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

    if not alerts.empty:

        alerts = alerts[
            [
                "file",
                "prediction",
                "confidence",
                "maintenance_action"
            ]
        ]

        st.dataframe(
            alerts.head(20)
        )

except:
    st.warning(
        "prediction_results.csv not found yet."
    )