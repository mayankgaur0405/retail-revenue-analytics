# 🛒 Retail Revenue Assurance & Risk Analytics Pipeline

![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![SQLite](https://img.shields.io/badge/SQLite-07405E?style=for-the-badge&logo=sqlite&logoColor=white)
![Scikit-Learn](https://img.shields.io/badge/scikit--learn-%23F7931E.svg?style=for-the-badge&logo=scikit-learn&logoColor=white)
![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)
![Power BI](https://img.shields.io/badge/PowerBI-F2C811?style=for-the-badge&logo=Power%20BI&logoColor=black)

## 📌 Project Overview
The **Retail Revenue Assurance Dashboard** is an end-to-end Data Analytics and Machine Learning ETL pipeline designed to detect financial anomalies, potential fraud, and revenue leakage securely within a corporation's transaction network. 

By simulating over 15,000+ realistic point-of-sale transactions (along with injected system errors and statistical anomalies), this project integrates SQL extraction, Pandas data cleansing, Unsupervised Machine Learning, and dual-layer Data Visualization (Streamlit & Power BI).

---

## 🏗️ Architecture & Data Flow (The ETL Process)

This project strictly adheres to enterprise data processing standards:

### 1. Extract (SQL Integration)
* Raw transactional data and structured dimension tables (Stores/Regions) are housed locally in a **SQLite** database (`retail_db.sqlite`).
* Data is extracted programmatically using precise relational **SQL Queries** (`LEFT JOIN`, `GROUP BY`, `HAVING`) to retrieve comprehensive reporting metrics.

### 2. Transform (Data Cleansing)
* Processing is handled via **Python (Pandas)**.
* Realistic "dirty" data (NULL values, string inconsistencies) are resolved using advanced statistical imputation (e.g., `.transform('median')`).
* Duplicates are rigorously removed via unique Transaction IDs to maintain high data integrity prior to modeling.

### 3. Load & Machine Learning (Anomaly Detection)
* Processed data runs through an Unsupervised Machine Learning model.
* Utilizes **Scikit-Learn's Isolation Forest** to dynamically flag irregular refund behavior based on multivariate features (`HourOfDay`, `Sales_Amount`, `IsRefund`).

### 4. Visualize (Reporting Layer)
* **Streamlit App:** A live, Python-based interactive dashboard exposing total gross revenue and an audit log of strictly anomalous transactions.
* **Power BI:** The processed pipeline data is actively digested by Microsoft Power BI Desktop for C-suite demographic slicers and KPI tracking.

---
### Power BI

<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/a2275329-ad85-4372-b7d5-dfbb9e1c352a" />
<img width="1920" height="1063" alt="image" src="https://github.com/user-attachments/assets/61b47023-2d44-450f-b563-21f270225901" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/e14a5d61-f0e3-495b-b57c-090186c4cee0" />
<img width="1920" height="1080" alt="image" src="https://github.com/user-attachments/assets/7152f6f6-91fc-4fee-96f5-a3413cb9c4c6" />






---

## 🛠️ Technology Stack
* **Database Engine:** SQLite3
* **Data Processing:** Python (Pandas, NumPy)
* **Data Science / ML:** Scikit-Learn (IsolationForest algorithm)
* **Dashboards & Visualization:** Streamlit, Plotly, Microsoft Power BI
* **Version Control:** Git

---

## 🚀 How to Run Locally

### Prerequisites
Make sure you have Python 3.9+ installed.

### 1. Clone the repository
```bash
git clone https://github.com/mayankgaur0405/retail-revenue-analytics.git
cd retail-revenue-analytics
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Re-generate the Database & Run the ETL Pipeline
*Ensure you generate the mock database locally first.*
```bash
python data_generator.py
python analysis_model.py
```

### 4. Launch the Streamlit Dashboard
```bash
streamlit run app.py
```
*The app will automatically open in your web browser at `http://localhost:8501`.*

---

## 📊 Power BI Implementation
To view the final reporting layer in Power BI without starting a local python server:
1. Open **Power BI Desktop**.
2. Connect Data Source to the generated `data/powerbi_processed_export.csv`.
3. Filter visuals using the pre-calculated `Is_Anomaly` column.

## 🤝 Contact
Developed by **Mayank Gaur**. Connect with me regarding Data Analytics, Risk Management, or full-stack software development roles!
