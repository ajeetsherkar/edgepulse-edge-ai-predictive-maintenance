import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
import plotly.express as px
import plotly.graph_objects as go

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