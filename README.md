# Retail Sales Forecasting and Business Analytics

**Author:** LAKSHANA R  
**Institution:** Kumaraguru College of Liberal Arts and Science, Coimbatore  
**Project Title:** Machine Learning-Based Sales Forecasting and Business Analytics for a Retail Business  

---

## 📌 Project Overview
This project provides a complete Machine Learning and Business Analytics web application designed for retail sales forecasting. It uses the actual Superstore retail dataset, aggregates transactions into chronological monthly intervals, trains a **Linear Regression** model, and presents an interactive **Orange-themed** executive dashboard.

---

## 🚀 How to Run the Project Locally

### 1. Requirements
Ensure you have Python 3.9+ installed on your system.

### 2. Install Dependencies
Open terminal or command prompt inside this folder and run:
```bash
pip install -r requirements.txt
```

### 3. (Optional) Re-train the Model
To re-run the ML training pipeline and generate fresh metrics:
```bash
python model.py
```
This will train the Linear Regression model, evaluate $R^2$, MAE, MSE, and RMSE, and save `model.pkl`.

### 4. Start the Web Application
```bash
python app.py
```
After starting, open your browser and navigate to:
```
http://localhost:5000
```
or
```
http://127.0.0.1:5000
```

---

## 📂 Project Directory Structure

```
retail-sales-forecasting/
│
├── app.py                      # Flask web server & prediction API endpoints
├── model.py                    # Preprocessing, Linear Regression training & evaluation
├── dataset.csv                 # Cleaned source dataset (Sample Superstore, 48 monthly periods)
├── model.pkl                   # Trained Linear Regression model
├── requirements.txt            # Python dependencies (flask, pandas, numpy, scikit-learn, joblib)
├── test_flow.py                # Automated end-to-end verification script
├── README.md                   # Project documentation & run guide
│
├── templates/
│   └── index.html              # Modern, orange-themed executive dashboard UI
│
└── static/
    ├── style.css               # Orange theme stylesheet
    └── script.js               # Reactive month selection, Chart.js graphs & currency toggle
```

---

## 📊 Key Features
1. **Month-Wise Sales Forecasting**: Select any of the 48 actual months from the dropdown to see:
   - **Actual Sales** recorded in dataset
   - **Predicted Sales** from trained Linear Regression
   - **Monetary Difference** and percentage variance
2. **Actual vs Predicted Sales Graph**: Interactive line chart tracking actual revenue vs. model forecast across 2014–2017.
3. **Executive KPI Cards**: Total Sales, Average Monthly Sales, Highest Sales Month, Lowest Sales Month, and Model $R^2$ Score.
4. **Category Breakdown**: Sales distribution across Technology, Office Supplies, and Furniture.
5. **Model Evaluation Metrics**: $R^2$ Score (0.7102), MAE, MSE, RMSE.
6. **Orange Theme Design**: Crisp white background with radiant orange accents, clean cards, and responsive typography.
