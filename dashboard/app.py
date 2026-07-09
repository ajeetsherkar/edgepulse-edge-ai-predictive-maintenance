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

        prediction_df = uploaded_df.copy()
        prediction_df["Prediction"] = prediction_labels
        prediction_df["Confidence (%)"] = confidence_scores.round(2)
        prediction_df["Maintenance"] = maintenance_actions

        # Store results so they survive reruns (e.g. filter changes)
        st.session_state["prediction_df"] = prediction_df
        st.session_state["prediction_time"] = prediction_time
        st.session_state["feature_count"] = len(feature_columns)

        history_records = []

        for i in range(len(prediction_df)):
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

    if "prediction_df" in st.session_state:
        prediction_df = st.session_state["prediction_df"]

        st.markdown("---")
        st.subheader("Filter Predictions")

        selected_status = st.multiselect(
            "Filter by Predicted Health Status",
            options=[
                "Healthy",
                "Early_Degradation",
                "Critical",
                "Imminent_Failure"
            ],
            default=[
                "Healthy",
                "Early_Degradation",
                "Critical",
                "Imminent_Failure"
            ]
        )

        filtered_results = prediction_df[
            prediction_df["Prediction"].isin(selected_status)
        ]

        search_text = st.text_input(
            "🔍 Search by Machine/File Name"
        )

        if search_text:
            if "file" in filtered_results.columns:
                filtered_results = filtered_results[
                    filtered_results["file"].str.contains(
                        search_text,
                        case=False,
                        na=False
                    )
                ]
            else:
                st.warning(
                    "No 'file' column found in the uploaded data — search is unavailable for this dataset."
                )

        st.markdown("---")
        st.subheader("Prediction Summary")

        summary = filtered_results["Prediction"].value_counts()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Healthy", summary.get("Healthy", 0))
        c2.metric("Early Degradation", summary.get("Early_Degradation", 0))
        c3.metric("Critical", summary.get("Critical", 0))
        c4.metric("Imminent Failure", summary.get("Imminent_Failure", 0))

        st.write(
            f"Showing **{len(filtered_results)}** of **{len(prediction_df)}** machines"
        )

        st.markdown("---")
        st.subheader("Sort Predictions")

        sort_option = st.selectbox(
            "Sort By",
            [
                "File Name",
                "Confidence (High → Low)",
                "Confidence (Low → High)",
                "Prediction"
            ]
        )

        if sort_option == "File Name":
            if "file" in filtered_results.columns:
                filtered_results = filtered_results.sort_values(
                    "file",
                    ascending=True
                )
            else:
                st.warning(
                    "No 'file' column found in the uploaded data — sorting by file name is unavailable for this dataset."
                )
        elif sort_option == "Confidence (High → Low)":
            filtered_results = filtered_results.sort_values(
                "Confidence (%)",
                ascending=False
            )
        elif sort_option == "Confidence (Low → High)":
            filtered_results = filtered_results.sort_values(
                "Confidence (%)",
                ascending=True
            )
        elif sort_option == "Prediction":
            filtered_results = filtered_results.sort_values(
                "Prediction",
                ascending=True
            )

        st.markdown("---")
        st.subheader("Prediction Results")

        if filtered_results.empty:
            st.warning(
                "No machines match the selected filters or search text. Try changing your filters."
            )
        else:
            st.dataframe(
                filtered_results,
                use_container_width=True
            )

        csv = filtered_results.to_csv(index=False)

        download_filename = (
            f"prediction_results_"
            f"{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        )

        st.download_button(
            label=f"📥 Download {len(filtered_results)} Predictions",
            data=csv,
            file_name=download_filename,
            mime="text/csv",
            disabled=filtered_results.empty
        )

        st.info(f"""
Model : XGBoost

Records Processed : {len(prediction_df)}

Features : {st.session_state['feature_count']}

Prediction Time : {st.session_state['prediction_time']:.2f} sec

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

        for i in range(min(len(filtered_results), 10)):
            prediction = filtered_results.iloc[i]["Prediction"]
            confidence = filtered_results.iloc[i]["Confidence (%)"]
            maintenance = filtered_results.iloc[i]["Maintenance"]

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

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("---")
        st.subheader("Machine Health Distribution")

        stage_order = [
            "Healthy",
            "Early_Degradation",
            "Critical",
            "Imminent_Failure"
        ]

        health_distribution = (
            filtered_results["Prediction"]
            .value_counts()
            .reindex(stage_order, fill_value=0)
            .reset_index()
        )
        health_distribution.columns = ["Health Stage", "Count"]
        health_distribution["Health Stage"] = (
            health_distribution["Health Stage"]
            .str.replace("_", " ")
        )

        fig = px.bar(
            health_distribution,
            x="Health Stage",
            y="Count",
            color="Health Stage",
            text="Count",
            title="Bearing Health Stages (Filtered Predictions)"
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

if "prediction_df" not in st.session_state:
    st.markdown("<br>", unsafe_allow_html=True)
    st.markdown("---")
    st.subheader("Machine Health Distribution")
    fig = px.bar(
        health_df,
        x="Health Stage",
        y="Count",
        color="Health Stage",
        text="Count",
        title="Bearing Health Stages (Sample Data)"
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