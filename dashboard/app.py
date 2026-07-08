import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time

ROOT = Path(__file__).resolve().parents[1]
MODEL_PATH = ROOT / "models" / "xgb_baseline.pkl"
FEATURE_PATH = ROOT / "models" / "dashboard_feature_importance.csv"
HEALTH_PATH = ROOT / "models" / "health_distribution.csv"
METRICS_PATH = ROOT / "models" / "model_metrics.csv"
HISTORY_PATH = ROOT / "data" / "logs" / "prediction_history.csv"

model = joblib.load(MODEL_PATH)
feature_df = pd.read_csv(FEATURE_PATH)
health_df = pd.read_csv(HEALTH_PATH)
metrics_df = pd.read_csv(METRICS_PATH)
history_df = pd.read_csv(HISTORY_PATH)

st.set_page_config(
    page_title="EdgePulse",
    page_icon="⚙️",
    layout="wide"
)

st.title("⚙️ EdgePulse")
st.subheader("AI-Based Predictive Maintenance Dashboard")
st.markdown("---")

st.sidebar.title("EdgePulse")
st.sidebar.markdown("---")
st.sidebar.success("XGBoost Model")
st.sidebar.info("Industrial Rotating Machinery")
st.sidebar.markdown("---")
st.sidebar.write("Model Version")
st.sidebar.write("v1.0")
st.sidebar.write("Algorithm")
st.sidebar.write("XGBoost")
st.sidebar.write("Dataset")
st.sidebar.write("NASA IMS Bearing Dataset")

st.sidebar.markdown("---")
st.sidebar.subheader("Upload Sensor Data")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=["csv"]
)

if uploaded_file is not None:
    uploaded_df = pd.read_csv(uploaded_file)

    required_columns = [
        "mean",
        "std",
        "rms",
        "max",
        "min",
        "peak_to_peak"
    ]

    missing_columns = [
        col
        for col in required_columns
        if col not in uploaded_df.columns
    ]

    if missing_columns:
        st.error(
            "Invalid CSV file! Missing columns:\n\n"
            + ", ".join(missing_columns)
        )
        st.stop()

    st.success("Valid sensor CSV uploaded successfully!")

    st.markdown("---")

    run_prediction = st.button(
        "🚀 Run AI Prediction",
        use_container_width=True
    )

    if run_prediction:
        feature_columns = [
            "mean",
            "std",
            "rms",
            "max",
            "min",
            "peak_to_peak"
        ]

        prediction_input = uploaded_df[feature_columns]

        with st.spinner("Running XGBoost Model..."):
            start_time = time.time()
            predictions = model.predict(prediction_input)
            probabilities = model.predict_proba(prediction_input)
            confidence_scores = probabilities.max(axis=1) * 100
            prediction_time = time.time() - start_time

        st.success("AI Prediction Completed Successfully!")

        label_map = {
            0: "Healthy",
            1: "Early_Degradation",
            2: "Critical",
            3: "Imminent_Failure"
        }

        prediction_labels = [
            label_map[p]
            for p in predictions
        ]

        maintenance_map = {
            "Healthy": "No Action Required",
            "Early_Degradation": "Schedule Inspection",
            "Critical": "Maintenance Within 7 Days",
            "Imminent_Failure": "Immediate Shutdown"
        }

        maintenance_actions = [
            maintenance_map[label]
            for label in prediction_labels
        ]

        st.markdown("---")
        st.subheader("Prediction Summary")

        summary = pd.Series(prediction_labels).value_counts()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Healthy", summary.get("Healthy", 0))
        c2.metric("Early Degradation", summary.get("Early_Degradation", 0))
        c3.metric("Critical", summary.get("Critical", 0))
        c4.metric("Imminent Failure", summary.get("Imminent_Failure", 0))

        st.markdown("---")
        st.subheader("Prediction Results")

        uploaded_df["Prediction"] = prediction_labels
        uploaded_df["Confidence (%)"] = confidence_scores.round(2)
        uploaded_df["Maintenance"] = maintenance_actions

        prediction_df = uploaded_df

        st.dataframe(
            prediction_df,
            use_container_width=True
        )

        csv = prediction_df.to_csv(index=False)

        st.download_button(
            label="📥 Download Prediction Report",
            data=csv,
            file_name="prediction_results.csv",
            mime="text/csv"
        )

        st.info(f"""
Model : XGBoost

Records Processed : {len(uploaded_df)}

Features : {len(feature_columns)}

Prediction Time : {prediction_time:.2f} sec

Prediction Completed Successfully
""")

        st.markdown("---")
        st.subheader("Machine Health Summary")

        card_colors = {
            "Healthy": "#d4edda",
            "Early_Degradation": "#fff3cd",
            "Critical": "#ffe5b4",
            "Imminent_Failure": "#f8d7da"
        }

        icons = {
            "Healthy": "🟢",
            "Early_Degradation": "🟡",
            "Critical": "🟠",
            "Imminent_Failure": "🔴"
        }

        for i in range(min(len(uploaded_df), 10)):
            prediction = uploaded_df.loc[i, "Prediction"]
            confidence = uploaded_df.loc[i, "Confidence (%)"]
            maintenance = uploaded_df.loc[i, "Maintenance"]

            st.markdown(
                f"""
<div style="
background-color:{card_colors[prediction]};
padding:20px;
border-radius:12px;
margin-bottom:15px;
">

<h4>Machine {i+1}</h4>

<h2>{icons[prediction]} {prediction.replace("_"," ")}</h2>

<b>Confidence:</b> {confidence:.2f}%<br>

<b>Maintenance:</b> {maintenance}

</div>
""",
                unsafe_allow_html=True
            )

        history_records = []

        for i in range(len(uploaded_df)):
            history_records.append({
                "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "prediction": prediction_labels[i],
                "confidence": round(confidence_scores[i], 2),
                "maintenance_action": maintenance_actions[i]
            })

        history_new = pd.DataFrame(history_records)

        history_df = pd.concat(
            [history_df, history_new],
            ignore_index=True
        )

        history_df.to_csv(
            HISTORY_PATH,
            index=False
        )

        st.success(
            f"{len(history_new)} predictions saved to history."
        )

accuracy = metrics_df.loc[
    metrics_df["Metric"] == "Accuracy",
    "Value"
].iloc[0]

samples = len(history_df)
features = len(feature_df)
algorithm = "XGBoost"

col1, col2, col3, col4 = st.columns(4)
col1.metric(
    label="Model Accuracy",
    value=f"{accuracy*100:.1f}%"
)
col2.metric(
    label="Predictions Logged",
    value=samples
)
col3.metric(
    label="Features Used",
    value=features
)
col4.metric(
    label="ML Algorithm",
    value=algorithm
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Machine Health Distribution")
fig = px.bar(
    health_df,
    x="Health Stage",
    y="Count",
    color="Health Stage",
    text="Count",
    title="Bearing Health Stages"
)
fig.update_layout(
    xaxis_title="Health Stage",
    yaxis_title="Number of Samples",
    height=500
)
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Feature Importance")
fig = px.bar(
    feature_df,
    x="importance",
    y="feature",
    orientation="h",
    color="importance",
    text="importance",
    title="XGBoost Feature Importance"
)
fig.update_layout(
    height=500,
    yaxis=dict(categoryorder="total ascending")
)
st.plotly_chart(
    fig,
    use_container_width=True,
    config={
        "displayModeBar": False
    }
)

st.markdown("<br>", unsafe_allow_html=True)
st.markdown("---")
st.subheader("Recent Prediction History")
display_df = history_df[
    [
        "timestamp",
        "prediction",
        "confidence",
        "maintenance_action"
    ]
].copy()
display_df.columns = [
    "Timestamp",
    "Prediction",
    "Confidence (%)",
    "Maintenance Action"
]
display_df["Prediction"] = (
    display_df["Prediction"]
    .str.replace("_", " ")
)
st.dataframe(
    display_df.tail(10),
    use_container_width=True,
    hide_index=True
)

st.markdown("---")
st.caption(
    "EdgePulse • AI-Based Predictive Maintenance System • Built with Streamlit + XGBoost"
)