"""
Flask Web Application for Retail Sales Forecasting & Business Analytics
Project: Machine Learning-Based Sales Forecasting and Business Analytics for a Retail Business
Author: LAKSHANA R
Institution: Kumaraguru College of Liberal Arts and Science, Coimbatore
"""

import os
import json
import joblib
import numpy as np
import pandas as pd
from flask import Flask, render_template, request, jsonify, send_file

app = Flask(__name__)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

# Import our ML pipeline function
from model import load_and_preprocess_data, train_linear_regression

# Global in-memory cache for fast responsive queries
print("Initializing dataset and ML model...")
pipeline_data = train_linear_regression()
model = pipeline_data['model']
feature_cols = pipeline_data['feature_cols']
kpis = pipeline_data['kpis']
months_data = pipeline_data['months_data']
category_sales = pipeline_data['category_sales']

# Month lookup dictionary by Month_Name
month_dict = {m['month_name']: m for m in months_data}
available_months = [m['month_name'] for m in months_data]

@app.route('/')
def home():
    """Renders the main dashboard page."""
    default_month = months_data[0] if months_data else None
    return render_template(
        'index.html',
        available_months=available_months,
        default_month=default_month,
        kpis=kpis,
        category_sales=category_sales
    )

@app.route('/api/dashboard_data')
def get_dashboard_data():
    """Returns complete real dataset metrics and chronological sequence for charts."""
    return jsonify({
        "status": "success",
        "kpis": kpis,
        "available_months": available_months,
        "months_data": months_data,
        "category_sales": category_sales,
        "author": "LAKSHANA R",
        "institution": "Kumaraguru College of Liberal Arts and Science, Coimbatore"
    })

@app.route('/api/predict', methods=['POST', 'GET'])
def predict_month():
    """
    Given a selected month from the dropdown:
    1. Finds that month's data from the actual dataset.
    2. Displays actual sales from the dataset.
    3. Passes appropriate features to the trained Linear Regression model.
    4. Generates predicted sales amount.
    5. Returns actual sales, predicted sales, difference, and operational metadata.
    """
    if request.method == 'POST':
        req_json = request.get_json(silent=True) or {}
        selected_month = req_json.get('month')
    else:
        selected_month = request.args.get('month')
        
    if not selected_month:
        selected_month = available_months[0]
        
    if selected_month not in month_dict:
        return jsonify({
            "status": "error",
            "message": f"Month '{selected_month}' not found in dataset."
        }), 404
        
    m_info = month_dict[selected_month]
    
    # Extract the features for this month
    feat_vector = np.array([[
        m_info['month_index'],
        m_info['month'],
        (m_info['month'] - 1) // 3 + 1, # Quarter
        m_info['year'],
        m_info['quantity'],
        m_info['discount'] / 100.0      # Discount fraction
    ]])
    
    # Model prediction via trained Linear Regression
    pred_val = float(model.predict(feat_vector)[0])
    pred_val = max(0.0, pred_val) # non-negative
    actual_val = m_info['actual_sales']
    diff_val = actual_val - pred_val
    
    return jsonify({
        "status": "success",
        "month_name": selected_month,
        "year": m_info['year'],
        "month": m_info['month'],
        "actual_sales": round(actual_val, 2),
        "predicted_sales": round(pred_val, 2),
        "difference": round(diff_val, 2),
        "abs_difference": round(abs(diff_val), 2),
        "difference_pct": round((diff_val / actual_val * 100) if actual_val > 0 else 0, 2),
        "quantity": m_info['quantity'],
        "discount_pct": m_info['discount'],
        "profit": m_info['profit'],
        "model_type": "Linear Regression"
    })

@app.route('/download')
def download_project_zip():
    """Serves the complete project zip file for direct user download."""
    zip_path = os.path.join(BASE_DIR, "retail_sales_forecasting_project.zip")
    if os.path.exists(zip_path):
        return send_file(zip_path, as_attachment=True, download_name="retail_sales_forecasting_project.zip")
    return "Zip file not found", 404

if __name__ == '__main__':
    # Run local web server
    print("Starting Retail Sales Forecasting Flask Application on http://127.0.0.1:5000 ...")
    app.run(host='0.0.0.0', port=5000, debug=False)
