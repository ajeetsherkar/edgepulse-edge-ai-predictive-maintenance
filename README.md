# 🚀 EdgePulse – Edge AI Predictive Maintenance System

> **An Edge AI-powered predictive maintenance platform for industrial rotating machinery that performs local inference, health forecasting, and maintenance recommendations while minimizing dependence on cloud connectivity.**

---

## 📌 Overview

EdgePulse is an **Edge AI-based Predictive Maintenance System** designed for monitoring industrial rotating machinery such as bearings and motors.

The system performs **local machine learning inference** using an XGBoost model to classify machine health conditions and generate maintenance recommendations without requiring continuous cloud connectivity.

It demonstrates how **Artificial Intelligence at the Edge** can improve equipment reliability, reduce unexpected downtime, and support proactive maintenance decisions.

---

## 🎯 Problem Statement

Unexpected failures in industrial rotating machinery lead to:

- High maintenance costs
- Unplanned downtime
- Reduced equipment life
- Production losses
- Safety risks

Traditional cloud-based monitoring systems also introduce:

- Network dependency
- Higher latency
- Privacy concerns
- Increased operational costs

EdgePulse addresses these challenges by enabling **real-time, offline-capable Edge AI inference**.

---

# 🏗 System Architecture

```
Industrial Sensor Data
            │
            ▼
Data Preprocessing
            │
            ▼
Feature Extraction
            │
            ▼
Edge AI (XGBoost Model)
            │
            ▼
Health Classification
            │
            ▼
Maintenance Recommendation
            │
            ▼
Executive Dashboard
            │
            ▼
Executive PDF Report
            │
            ▼
Cloud Sync (Optional)
```

---

# ✨ Features

- ✅ Edge AI-based inference
- ✅ Offline prediction support
- ✅ XGBoost health classification
- ✅ Real-time dashboard
- ✅ Interactive visualizations
- ✅ Confidence analysis
- ✅ Feature importance analysis
- ✅ Maintenance recommendation engine
- ✅ Executive PDF report generation
- ✅ Fleet risk assessment
- ✅ Professional reporting
- ✅ Industrial-ready UI

---

# 🧠 Machine Learning Model

| Item | Value |
|------|-------|
| Algorithm | XGBoost |
| Problem Type | Multi-Class Classification |
| Deployment | Edge AI |
| Runtime | Native XGBoost |
| Inference | Local |
| Cloud Dependency | Optional |

---

# 🏭 Health Classes

The model classifies industrial equipment into four health stages.

| Health Stage | Meaning |
|--------------|----------|
| Healthy | Machine operating normally |
| Early Degradation | Early signs of wear detected |
| Critical | Maintenance required soon |
| Imminent Failure | Immediate shutdown recommended |

---

# 🔧 Maintenance Recommendations

Based on the predicted health condition, EdgePulse automatically recommends actions.

| Prediction | Recommendation |
|------------|----------------|
| Healthy | Continue Monitoring |
| Early Degradation | Schedule Inspection |
| Critical | Maintenance Within 7 Days |
| Imminent Failure | Immediate Shutdown |

---

# 📊 Dashboard Features

The Streamlit dashboard provides:

- Industrial health assessment
- Machine health distribution
- Maintenance distribution
- Prediction confidence analysis
- Feature importance visualization
- Fleet risk monitoring
- Executive report generation

---

# 📄 Executive Report

EdgePulse automatically generates a professional executive report containing:

- Cover page
- Executive summary
- Model information
- KPI cards
- Health distribution
- Prediction summary
- Maintenance summary
- Confidence statistics
- Feature importance
- Operational insights
- Maintenance recommendations
- Business impact
- Future scope
- Conclusion

---

# 💻 Technology Stack

### Programming

- Python

### Machine Learning

- XGBoost
- Scikit-learn
- Pandas
- NumPy

### Visualization

- Matplotlib
- Plotly

### Dashboard

- Streamlit

### Reporting

- ReportLab

### Development Tools

- Git
- GitHub

---

# 📁 Project Structure

```
EdgePulse/
│
├── dashboard/
├── reports/
├── charts/
├── models/
├── utils/
├── scripts/
├── data/
├── assets/
├── README.md
└── requirements.txt
```

---

# 🚀 Installation

Clone the repository

```bash
git clone <repository-url>
```

Go to project folder

```bash
cd EdgePulse
```

Install dependencies

```bash
pip install -r requirements.txt
```

Run the application

```bash
streamlit run dashboard/app.py
```

---

# 🎯 Future Enhancements

- ONNX Runtime deployment
- Live sensor streaming
- Fleet monitoring
- Trend analysis
- Remaining Useful Life estimation
- SHAP explainability
- Edge gateway deployment
- Cloud synchronization
- Multi-plant monitoring

---

# 📷 Screenshots

> Screenshots of the dashboard, charts, and executive report will be added here.

---

# 👨‍💻 Team

**Team Name:** EdgePulse

**Theme:** AI at the Edge

**Domain:** Industrial Heavy Machinery

---

# 📜 License

This project is developed for educational and hackathon purposes.

---

# ⭐ Project Vision

EdgePulse is designed to demonstrate how **Edge AI** can transform industrial maintenance by enabling intelligent, low-latency, and offline-capable predictive analytics directly at the edge.

Instead of being just another machine learning dashboard, EdgePulse aims to represent an industrial Edge AI solution suitable for modern manufacturing environments.