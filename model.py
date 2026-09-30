"""
Retail Sales Forecasting - Linear Regression ML Pipeline
Author: LAKSHANA R
College: Kumaraguru College of Liberal Arts and Science, Coimbatore
"""

import os
import joblib
import numpy as np
import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATASET_PATH = os.path.join(BASE_DIR, "dataset.csv")
MODEL_PATH = os.path.join(BASE_DIR, "model.pkl")

def load_and_preprocess_data():
    """
    Load actual dataset and aggregate transaction rows into monthly sales records.
    """
    if not os.path.exists(DATASET_PATH):
        raise FileNotFoundError(f"Dataset not found at {DATASET_PATH}")

    df = pd.read_csv(DATASET_PATH, encoding='latin1')
    
    # Identify and parse date column
    date_col = None
    for col in df.columns:
        if 'order date' in col.lower() or 'date' in col.lower():
            date_col = col
            break
            
    if date_col is None:
        raise ValueError("Could not find a Date column in the dataset.")
        
    df[date_col] = pd.to_datetime(df[date_col], format='mixed')
    df['Year'] = df[date_col].dt.year
    df['Month'] = df[date_col].dt.month
    df['Month_Year'] = df[date_col].dt.strftime('%Y-%m')
    df['Month_Name'] = df[date_col].dt.strftime('%B %Y')
    
    # Aggregate transaction records month-wise
    monthly = df.groupby(['Year', 'Month', 'Month_Year', 'Month_Name']).agg({
        'Sales': 'sum',
        'Profit': 'sum',
        'Quantity': 'sum',
        'Discount': 'mean'
    }).reset_index().sort_values(['Year', 'Month']).reset_index(drop=True)
    
    # Feature engineering: trend & calendar seasonality
    monthly['Month_Index'] = np.arange(1, len(monthly) + 1)
    monthly['Quarter'] = (monthly['Month'] - 1) // 3 + 1
    
    # Also extract category level breakdown for dashboard visuals
    cat_sales = df.groupby('Category')['Sales'].sum().to_dict()
    
    return df, monthly, cat_sales

def train_linear_regression():
    """
    Trains Linear Regression on month-wise features and calculates true metrics.
    """
    df, monthly, cat_sales = load_and_preprocess_data()
    
    feature_cols = ['Month_Index', 'Month', 'Quarter', 'Year', 'Quantity', 'Discount']
    X = monthly[feature_cols]
    y = monthly['Sales']
    
    # Train / Test split
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # Initialize and fit Linear Regression
    model = LinearRegression()
    model.fit(X_train, y_train)
    
    # Evaluate model on test set
    y_pred_test = model.predict(X_test)
    r2 = float(r2_score(y_test, y_pred_test))
    mae = float(mean_absolute_error(y_test, y_pred_test))
    mse = float(mean_squared_error(y_test, y_pred_test))
    rmse = float(np.sqrt(mse))
    
    # Generate predictions across the full chronological sequence for visualization
    y_pred_all = model.predict(X)
    monthly['Predicted_Sales'] = np.round(y_pred_all, 2)
    monthly['Difference'] = np.round(monthly['Sales'] - monthly['Predicted_Sales'], 2)
    monthly['Abs_Difference'] = np.round(np.abs(monthly['Difference']), 2)
    
    # Save trained model to disk
    joblib.dump(model, MODEL_PATH)
    print(f"Model saved to {MODEL_PATH}")
    print(f"Linear Regression Metrics -> R2: {r2:.4f}, MAE: {mae:.2f}, MSE: {mse:.2f}, RMSE: {rmse:.2f}")
    
    # Prepare monthly lookup dictionary
    months_data = []
    for _, row in monthly.iterrows():
        months_data.append({
            'month_name': row['Month_Name'],
            'year': int(row['Year']),
            'month': int(row['Month']),
            'month_index': int(row['Month_Index']),
            'actual_sales': round(float(row['Sales']), 2),
            'predicted_sales': round(float(row['Predicted_Sales']), 2),
            'difference': round(float(row['Difference']), 2),
            'abs_difference': round(float(row['Abs_Difference']), 2),
            'quantity': int(row['Quantity']),
            'discount': round(float(row['Discount'] * 100), 1),
            'profit': round(float(row['Profit']), 2)
        })
        
    # Overall Dashboard KPIs
    total_sales = float(monthly['Sales'].sum())
    avg_monthly_sales = float(monthly['Sales'].mean())
    highest_row = monthly.loc[monthly['Sales'].idxmax()]
    lowest_row = monthly.loc[monthly['Sales'].idxmin()]
    
    kpis = {
        'total_sales': round(total_sales, 2),
        'avg_monthly_sales': round(avg_monthly_sales, 2),
        'highest_month': {
            'month_name': highest_row['Month_Name'],
            'sales': round(float(highest_row['Sales']), 2)
        },
        'lowest_month': {
            'month_name': lowest_row['Month_Name'],
            'sales': round(float(lowest_row['Sales']), 2)
        },
        'total_predicted_sales': round(float(monthly['Predicted_Sales'].sum()), 2),
        'model_metrics': {
            'r2_score': round(r2, 4),
            'mae': round(mae, 2),
            'mse': round(mse, 2),
            'rmse': round(rmse, 2)
        }
    }
    
    return {
        'model': model,
        'feature_cols': feature_cols,
        'kpis': kpis,
        'months_data': months_data,
        'category_sales': {k: round(float(v), 2) for k, v in cat_sales.items()}
    }

if __name__ == '__main__':
    train_linear_regression()
