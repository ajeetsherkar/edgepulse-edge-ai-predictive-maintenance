import sys
from pathlib import Path

# Add project root to Python path
PROJECT_ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(PROJECT_ROOT))


import streamlit as st
import pandas as pd
import joblib
from pathlib import Path
from utils.constants import *
from utils.charts import (
    create_health_chart,
    create_feature_importance_chart,
    create_confidence_chart,
    create_maintenance_chart,
)
from utils.helpers import (
    get_health_summary,
    get_average_confidence,
    get_prediction_count,
    get_current_timestamp,
    format_prediction_labels,
    get_alert_level,
    get_top_critical,
    get_health_counts,
)
from reports.executive_report import generate_executive_report
from datetime import datetime
import plotly.express as px
import plotly.graph_objects as go
import time
import os

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

# NOTE: keys here must stay in sync with the *values* produced by
# maintenance_map below. If you rename a maintenance_map value, update
# the matching key here too, or the maintenance chart will fail to
# find a color for that category.
MAINTENANCE_COLORS = {
    "Monitor": "#16A34A",
    "Schedule Inspection": "#EAB308",
    "Maintain Within 7 Days": "#F97316",
    "Immediate Shutdown": "#DC2626"
}

# Some data sources use "Early_Degradation" style keys, others use
# "Early Degradation" — support both so the color map always applies.
STATUS_COLORS = {
    **STATUS_COLORS,
    **{k.replace("_", " "): v for k, v in STATUS_COLORS.items()}
}

# Maps the "color" returned by get_alert_level() to the right Streamlit
# banner function, so the fleet alert banner can be driven entirely by
# the shared helper instead of a local if/elif chain.
ALERT_RENDER_MAP = {
    "red": st.error,
    "orange": st.warning,
    "gold": st.warning,
    "green": st.success,
}

model = joblib.load(MODEL_PATH)
feature_df = pd.read_csv(FEATURE_PATH)
health_df = pd.read_csv(HEALTH_PATH)
metrics_df = pd.read_csv(METRICS_PATH)
history_df = pd.read_csv(HISTORY_PATH)

st.set_page_config(
    page_title="EdgePulse | Edge AI Predictive Maintenance",
    page_icon="⚙️",
    layout="wide"
)

st.title("🚀 Edge AI Predictive Maintenance System")
st.caption(
    "Real-time industrial health forecasting and maintenance recommendations using Edge AI."
)
st.divider()

st.sidebar.title("⚙️ EdgePulse")
st.sidebar.caption(
    "Edge AI Predictive Maintenance System"
)
st.sidebar.markdown("---")
st.sidebar.success("XGBoost Model")
st.sidebar.info("Industrial Rotating Machinery")

st.sidebar.divider()

st.sidebar.subheader("📦 Model Information")

st.sidebar.markdown("**Algorithm**")
st.sidebar.write("XGBoost")

st.sidebar.markdown("**Version**")
st.sidebar.write("v1.0")

st.sidebar.markdown("**Dataset**")
st.sidebar.write("NASA IMS Bearing Dataset")

st.sidebar.markdown("**Runtime**")
st.sidebar.write("Native XGBoost")

st.sidebar.markdown("**Deployment**")
st.sidebar.write("Edge Gateway Ready")

st.sidebar.markdown("**Inference**")
st.sidebar.write("Local Edge AI")

st.sidebar.markdown("**Offline Mode**")
st.sidebar.write("Supported")

st.sidebar.markdown("**Cloud Sync**")
st.sidebar.write("Optional")

st.sidebar.markdown("---")

st.sidebar.subheader("⚡ Edge AI Status")

st.sidebar.success("🟢 Edge AI Enabled")

st.sidebar.info("⚡ Local Inference")

st.sidebar.info("📡 Cloud Sync Optional")

st.sidebar.success("🖥 Edge Gateway Ready")

st.sidebar.markdown("---")

st.sidebar.subheader("🖥 Deployment Status")

st.sidebar.markdown("""
- ✅ **Edge Ready**
- ✅ **Offline Inference**
- ✅ **Real-Time Prediction**
- ✅ **Industrial Deployment Compatible**
""")

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

        st.success("✅ Industrial asset health assessment completed successfully.")

        # NOTE: these are the canonical/internal labels. They are kept
        # underscored ("Early_Degradation", "Imminent_Failure") because
        # they're used as dict keys throughout the rest of the app
        # (maintenance_map, card_colors, icons, multiselect options,
        # stage_order, get_health_summary/get_health_counts). Display-only
        # formatting (spaces instead of underscores) happens at render
        # time via format_prediction_labels() / .replace("_", " ").
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

        # Maintenance action wording aligned with the report's expected
        # terminology (Monitor / Schedule Inspection / Maintain Within 7
        # Days / Immediate Shutdown). Keep MAINTENANCE_COLORS above in
        # sync with these values.
        maintenance_map = {
            "Healthy": "Monitor",
            "Early_Degradation": "Schedule Inspection",
            "Critical": "Maintain Within 7 Days",
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

        # A fresh prediction run invalidates any previously generated
        # report, so clear it out to avoid downloading a stale PDF.
        st.session_state.pop("executive_report_bytes", None)

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
            f"💾 Saved {len(history_new)} industrial health assessments to history."
        )

    if "prediction_df" in st.session_state:
        prediction_df = st.session_state["prediction_df"]

        st.divider()
        st.subheader("Filter by Health Classification")

        selected_status = st.multiselect(
            "Filter by Health Classification",
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

        summary = get_health_summary(filtered_results)

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
        st.subheader("🏭 Industrial Asset Health Assessment")

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
            display_df = filtered_results.copy()

            display_df["Prediction"] = (
                display_df["Prediction"].apply(format_prediction_labels)
            )

            display_df = display_df.rename(
                columns={
                    "Prediction": "Health Classification",
                    "Maintenance": "Recommended Maintenance Action",
                }
            )

            st.dataframe(
                display_df,
                use_container_width=True,
                hide_index=True
            )

        health_counts = get_health_counts(filtered_results)

        total = get_prediction_count(filtered_results)

        healthy_count = health_counts["Healthy"]
        early_count = health_counts["Early_Degradation"]
        critical_count = health_counts["Critical"]
        imminent_count = health_counts["Imminent_Failure"]

        avg_confidence = get_average_confidence(filtered_results)

        report_accuracy = metrics_df.loc[
            metrics_df["Metric"] == "Accuracy",
            "Value"
        ].iloc[0]

        report_prediction_time = st.session_state.get("prediction_time", 0)

        report_timestamp = get_current_timestamp()
        report_date, report_time = report_timestamp.split("\n")

        # -----------------------------------------------------------
        # Executive PDF Report
        # -----------------------------------------------------------
        # NOTE: st.download_button can't lazily generate its payload —
        # Streamlit renders the whole page (and evaluates every button)
        # on every rerun, before it knows whether the download button
        # itself was clicked. So we use a two-step pattern: a regular
        # button triggers PDF generation, and only then do we render
        # the download button with the freshly generated bytes.
        st.divider()
        st.subheader("📄 Edge AI Executive Report")

        model_info = {
            "Model": "EdgePulse",
            "Algorithm": "XGBoost",
            "Dataset": "NASA IMS Bearing Dataset",
            "Version": "v1.0",
            "Model Type": "Multi-Class Classification",
            "Target Classes": 4,
            "Accuracy": f"{report_accuracy * 100:.1f}%"
        }

        # The report always represents the FULL uploaded/predicted
        # dataset, not whatever the user currently has filtered on the
        # dashboard — otherwise "Generate Executive Report" while
        # filtered to e.g. only Critical machines would silently
        # produce an incomplete report.
        results_df = st.session_state.get("prediction_df")

        if results_df is None or results_df.empty:
            st.warning("Please upload data and generate predictions first.")
            st.stop()

        results_df = results_df.copy()

        report_exists = "executive_report_bytes" in st.session_state

        generate_report_clicked = st.button(
            "📄 Generate Executive Report",
            use_container_width=True,
            disabled=results_df.empty or report_exists
        )

        if generate_report_clicked:
            output_pdf = Path("reports") / "EdgePulse_Executive_Report.pdf"

            with st.spinner("Generating Executive Report..."):
                pdf_path = generate_executive_report(
                    output_path=str(output_pdf),
                    model_info=model_info,
                    results_df=results_df,
                )

                with open(pdf_path, "rb") as pdf_file:
                    pdf_bytes = pdf_file.read()

            st.session_state["executive_report_bytes"] = pdf_bytes
            st.success(
                "✅ Executive Report generated successfully. Click the button below to download."
            )

        if "executive_report_bytes" in st.session_state:
            st.download_button(
                "📥 Download Edge AI Executive Report",
                data=st.session_state["executive_report_bytes"],
                file_name="EdgePulse_Executive_Report.pdf",
                mime="application/pdf",
                disabled=results_df.empty,
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

        confidence_fig = create_confidence_chart(filtered_results)

        confidence_chart_path = "reports/charts/confidence_distribution.png"

        confidence_fig.write_image(
            confidence_chart_path,
            width=1200,
            height=700
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

        st.subheader("🐞 Debug Maintenance Data")

        st.write("Maintenance Summary:")
        st.write(maintenance_summary)

        st.write("Unique Maintenance Values:")
        st.write(filtered_results["Maintenance"].unique())

        maintenance_fig = create_maintenance_chart(maintenance_summary)

        maintenance_chart_path = "reports/charts/maintenance_distribution.png"

        maintenance_fig.write_image(
            maintenance_chart_path,
            width=1200,
            height=700
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

        health_fig = create_health_chart(health_distribution, display_stage_colors)

        os.makedirs("reports/charts", exist_ok=True)

        health_chart_path = "reports/charts/health_distribution.png"

        health_fig.write_image(
            health_chart_path,
            width=1200,
            height=700
        )

        st.plotly_chart(
            health_fig,
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
    fleet_summary = get_health_summary(st.session_state["prediction_df"])
    fleet_counts = get_health_counts(st.session_state["prediction_df"])

    healthy = fleet_counts["Healthy"]
    early = fleet_counts["Early_Degradation"]
    critical = fleet_counts["Critical"]
    failure = fleet_counts["Imminent_Failure"]
    total_predictions = get_prediction_count(st.session_state["prediction_df"])
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

else:

    alert = get_alert_level(fleet_summary)
    render_alert = ALERT_RENDER_MAP.get(alert["color"], st.info)

    render_alert(
        f"""
{alert['icon']} **{alert['title']}**

{alert['message']}
"""
    )

st.divider()
st.subheader("📊 Executive Dashboard")

if prediction_available:

    accuracy = metrics_df.loc[
        metrics_df["Metric"] == "Accuracy",
        "Value"
    ].iloc[0]

    prediction_count = get_prediction_count(st.session_state["prediction_df"])

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
    feature_fig = create_feature_importance_chart(feature_df)

    feature_chart_path = "reports/charts/feature_importance.png"

    feature_fig.write_image(
        feature_chart_path,
        width=1200,
        height=700
    )

    st.plotly_chart(
        feature_fig,
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