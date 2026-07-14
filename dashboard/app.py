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

# ---------------------------------------------------------------------
# Consistent color theme used across every chart / badge in the app
# ---------------------------------------------------------------------
STATUS_COLORS = {
    "Healthy": "#16A34A",
    "Early_Degradation": "#EAB308",
    "Critical": "#F97316",
    "Imminent_Failure": "#DC2626"
}

MAINTENANCE_COLORS = {
    "No Action Required": "#16A34A",
    "Schedule Inspection": "#EAB308",
    "Maintenance Within 7 Days": "#F97316",
    "Immediate Shutdown": "#DC2626"
}

# Some data sources use "Early_Degradation" style keys, others use
# "Early Degradation" — support both so the color map always applies.
STATUS_COLORS = {
    **STATUS_COLORS,
    **{k.replace("_", " "): v for k, v in STATUS_COLORS.items()}
}

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
st.divider()

st.sidebar.title("EdgePulse")
st.sidebar.markdown("---")
st.sidebar.success("XGBoost Model")
st.sidebar.info("Industrial Rotating Machinery")

st.sidebar.divider()

st.sidebar.subheader("ℹ️ Model Information")

st.sidebar.markdown(
    """
**Version:** v1.0

**Algorithm:** XGBoost

**Dataset:** NASA IMS Bearing Dataset

**Model Type:** Multi-Class Classification

**Target Classes:** 4
"""
)

st.sidebar.markdown("---")
st.sidebar.subheader("Upload Sensor Data")
uploaded_file = st.sidebar.file_uploader(
    "Choose a CSV file",
    type=["csv"],
    key="file_uploader"
)

if st.sidebar.button("🔄 Reset Dashboard", use_container_width=True):
    st.session_state.clear()
    st.rerun()

if "last_prediction_timestamp" in st.session_state:
    st.sidebar.markdown("---")
    st.sidebar.subheader("🕒 Last Prediction")
    st.sidebar.write(
        st.session_state["last_prediction_timestamp"].strftime("%d %b %Y")
    )
    st.sidebar.write(
        st.session_state["last_prediction_timestamp"].strftime("%I:%M %p")
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
            "❌ Invalid CSV format. Please upload a valid sensor data file.\n\n"
            "Missing columns:\n\n"
            + ", ".join(missing_columns)
        )
        st.stop()

    st.success("📂 Sensor CSV uploaded successfully.")

    st.divider()

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

        st.success("✅ Prediction completed successfully.")

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
        st.session_state["last_prediction_timestamp"] = datetime.now()

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
            f"💾 Saved {len(history_new)} predictions to history."
        )

    if "prediction_df" in st.session_state:
        prediction_df = st.session_state["prediction_df"]

        st.divider()
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

        st.divider()
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

        st.divider()
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

        st.divider()
        st.subheader("📋 Prediction Results")

        if filtered_results.empty:
            st.info(
                """
🔍 No machines match your current filters.

Try one of the following:

• Clear the search box

• Select additional health statuses

• Upload another CSV file
"""
            )
        else:
            def prediction_color(value):

                colors = {
                    "Healthy": "color: green; font-weight:bold;",
                    "Early_Degradation": "color: goldenrod; font-weight:bold;",
                    "Critical": "color: orange; font-weight:bold;",
                    "Imminent_Failure": "color: red; font-weight:bold;"
                }

                return colors.get(value, "")

            def confidence_color(value):

                if value >= 90:
                    return "color: green; font-weight:bold;"

                elif value >= 75:
                    return "color: goldenrod; font-weight:bold;"

                else:
                    return "color: red; font-weight:bold;"

            display_df = filtered_results.copy()

            display_df["Prediction"] = (
                display_df["Prediction"]
                .replace({
                    "Healthy": "🟢 Healthy",
                    "Early_Degradation": "🟡 Early Degradation",
                    "Critical": "🟠 Critical",
                    "Imminent_Failure": "🔴 Imminent Failure"
                })
            )

            styled_df = (
                filtered_results.style
                .applymap(
                    prediction_color,
                    subset=["Prediction"]
                )
                .applymap(
                    confidence_color,
                    subset=["Confidence (%)"]
                )
            )

            st.dataframe(
                styled_df,
                use_container_width=True
            )

        total = len(filtered_results)

        healthy_count = (filtered_results["Prediction"] == "Healthy").sum()
        early_count = (filtered_results["Prediction"] == "Early_Degradation").sum()
        critical_count = (filtered_results["Prediction"] == "Critical").sum()
        imminent_count = (filtered_results["Prediction"] == "Imminent_Failure").sum()

        avg_confidence = filtered_results["Confidence (%)"].mean()

        report_accuracy = metrics_df.loc[
            metrics_df["Metric"] == "Accuracy",
            "Value"
        ].iloc[0]

        report_prediction_time = st.session_state.get("prediction_time", 0)

        report = f"""
EdgePulse AI Prediction Report

==============================================

Generated On:
{datetime.now().strftime("%d %B %Y")}
Time:
{datetime.now().strftime("%H:%M:%S")}

----------------------------------------------
MODEL INFORMATION
----------------------------------------------

Algorithm          : XGBoost
Dataset            : NASA IMS Bearing Dataset
Model Accuracy     : {report_accuracy*100:.1f}%
Prediction Time    : {report_prediction_time:.2f} sec

----------------------------------------------
PREDICTION SUMMARY
----------------------------------------------

Total Machines          : {total}

Healthy                 : {healthy_count}
Early Degradation       : {early_count}
Critical                : {critical_count}
Imminent Failure        : {imminent_count}

Average Confidence      : {avg_confidence:.2f}%

==============================================

Generated by EdgePulse

==============================================
"""

        report += "\n\nDETAILED PREDICTIONS\n\n"

        report += filtered_results.to_csv(index=False)

        st.download_button(
            "📥 Download Prediction Report",
            report,
            file_name="EdgePulse_Prediction_Report.txt",
            mime="text/plain",
            disabled=filtered_results.empty,
            use_container_width=True
        )

        st.info(f"""
Model : XGBoost

Records Processed : {len(prediction_df)}

Features : {st.session_state['feature_count']}

Prediction Time : {st.session_state['prediction_time']:.2f} sec

Prediction Completed Successfully
""")

        st.divider()
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

        st.divider()
        st.subheader("📈 Confidence Distribution")

        confidence_fig = px.histogram(
            filtered_results,
            x="Confidence (%)",
            nbins=10,
            title="Prediction Confidence Distribution"
        )

        confidence_fig.update_layout(
            height=450,
            xaxis_title="Confidence (%)",
            yaxis_title="Number of Machines"
        )

        st.plotly_chart(
            confidence_fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

        st.divider()
        st.subheader("🛠️ Maintenance Action Distribution")

        maintenance_summary = (
            filtered_results["Maintenance"]
            .value_counts()
            .reset_index()
        )
        maintenance_summary.columns = [
            "Maintenance",
            "Count"
        ]

        maintenance_fig = px.pie(
            maintenance_summary,
            names="Maintenance",
            values="Count",
            hole=0.55,
            title="Maintenance Action Distribution",
            color="Maintenance",
            color_discrete_map=MAINTENANCE_COLORS
        )

        maintenance_fig.update_layout(
            height=450,
            legend_title="Maintenance Action"
        )

        st.plotly_chart(
            maintenance_fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

        st.divider()
        st.subheader("🏭 Machine Health Distribution")

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

        display_stage_colors = {
            stage.replace("_", " "): color
            for stage, color in STATUS_COLORS.items()
        }

        fig = px.bar(
            health_distribution,
            x="Health Stage",
            y="Count",
            color="Health Stage",
            color_discrete_map=display_stage_colors,
            text="Count",
            title="Bearing Health Stages (Filtered Predictions)"
        )

        fig.update_layout(
            height=450,
            xaxis_title="Health Stage",
            yaxis_title="Number of Machines"
        )
        st.plotly_chart(
            fig,
            use_container_width=True,
            config={
                "displayModeBar": False
            }
        )

# ---------------------------------------------------------------------
# Fleet alert banner
# Computed once here from the full (unfiltered) prediction set, then
# reused below by the Executive Dashboard metric cards so the counts
# can't drift out of sync between the two sections.
# ---------------------------------------------------------------------
prediction_available = "prediction_df" in st.session_state

if prediction_available:
    fleet_summary = (
        st.session_state["prediction_df"]["Prediction"]
        .value_counts()
    )

    healthy = fleet_summary.get("Healthy", 0)
    early = fleet_summary.get("Early_Degradation", 0)
    critical = fleet_summary.get("Critical", 0)
    failure = fleet_summary.get("Imminent_Failure", 0)
    total_predictions = len(st.session_state["prediction_df"])
else:
    healthy = 0
    early = 0
    critical = 0
    failure = 0
    total_predictions = 0

if not prediction_available:

    st.info(
        """
ℹ️ **System Ready**

Upload a sensor CSV file and run AI prediction to view machine health insights.
"""
    )

elif failure > 0:

    st.error(
        f"""
🚨 **Critical Alert**

**{failure} machine(s)** are predicted to be in the **Imminent Failure** stage.

**Recommended Action:** Perform an immediate shutdown and inspect the affected machines to prevent catastrophic failure.
"""
    )

elif critical > 0:

    st.warning(
        f"""
🟠 **Maintenance Required**

**{critical} machine(s)** are in the **Critical** stage.

**Recommended Action:** Schedule maintenance within the next 7 days.
"""
    )

elif early > 0:

    st.warning(
        f"""
🟡 **Inspection Recommended**

**{early} machine(s)** show early signs of degradation.

**Recommended Action:** Inspect the machines and monitor them closely.
"""
    )

else:

    st.success(
        """
🟢 **System Status**

All monitored machines are operating within normal conditions.

No maintenance action is currently required.
"""
    )

st.divider()
st.subheader("📊 Executive Dashboard")

if prediction_available:

    accuracy = metrics_df.loc[
        metrics_df["Metric"] == "Accuracy",
        "Value"
    ].iloc[0]

    prediction_count = len(st.session_state["prediction_df"])

    prediction_time = st.session_state.get("prediction_time", 0)

    features = len(feature_df)

    algorithm = "XGBoost"

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "🎯 Model Accuracy",
        f"{accuracy*100:.1f}%",
        help="Overall accuracy of the trained XGBoost model, evaluated on the validation dataset."
    )

    col2.metric(
        "⚡ Prediction Time",
        f"{prediction_time:.2f} sec",
        help="Time required to generate predictions for all uploaded machines."
    )

    col3.metric(
        "📁 Uploaded Machines",
        prediction_count,
        help="Total number of machines processed from the uploaded CSV."
    )

    col4.metric(
        "🤖 Algorithm",
        algorithm,
        help="Machine learning model used for bearing health classification."
    )

    col5, col6, col7, col8 = st.columns(4)

    col5.metric(
        "🟢 Healthy",
        healthy,
        help="Machines predicted to be operating normally, with no action required."
    )

    col6.metric(
        "🟡 Early Degradation",
        early,
        help="Machines showing early signs of wear that should be inspected soon."
    )

    col7.metric(
        "🟠 Critical",
        critical,
        help="Machines that require maintenance within the next 7 days."
    )

    col8.metric(
        "🔴 Imminent Failure",
        failure,
        help="Machines at high risk of failure that require immediate shutdown and inspection."
    )

else:
    st.info(
        "🚀 Upload a sensor CSV file and run AI prediction to view dashboard metrics."
    )

st.divider()
st.subheader("📊 Feature Importance")

if prediction_available:
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
        height=450,
        yaxis=dict(
            categoryorder="total ascending"
        )
    )
    st.plotly_chart(
        fig,
        use_container_width=True,
        config={
            "displayModeBar": False
        }
    )
else:
    st.info(
        "📊 Run a prediction to view model feature importance."
    )

st.divider()
st.subheader("🕒 Recent Prediction History")

if prediction_available:
    if history_df.empty:
        st.info(
            """
🔍 No prediction history yet.

Upload a sensor CSV and run a prediction to start building history.
"""
        )
    else:
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
else:
    st.info(
        """🕒 No prediction history yet.

Run your first prediction to begin tracking machine health."""
    )

st.divider()
st.markdown(
    """
<div style='text-align:center; color:gray;'>
⚙️ <b>EdgePulse v1.0</b><br>
AI-Based Predictive Maintenance Dashboard<br>
Powered by <b>Python • Streamlit • XGBoost • Plotly</b>
</div>
""",
    unsafe_allow_html=True
)