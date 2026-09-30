import urllib.request
import urllib.parse
import json

base_url = 'http://127.0.0.1:5000'

print("=== 1. TESTING WEBSITE & DASHBOARD LOAD ===")
with urllib.request.urlopen(base_url) as resp:
    assert resp.status == 200
    html = resp.read().decode('utf-8')
    html_lower = html.lower()
    assert 'retail sales forecasting' in html_lower
    assert 'monthly sales forecast' in html_lower
    assert 'actual vs predicted sales' in html_lower
    assert 'model performance' in html_lower
    assert 'how the prediction works' in html_lower
print("SUCCESS: Website and HTML layout loaded cleanly.")

print("\n=== 2. TESTING DATASET & AVAILABLE MONTHS ===")
with urllib.request.urlopen(f"{base_url}/api/dashboard_data") as resp:
    data = json.loads(resp.read().decode('utf-8'))
    months = data['available_months']
    print(f"SUCCESS: Found {len(months)} chronological months in actual dataset.")
    print(f"First month: {months[0]} | Last month: {months[-1]}")
    assert len(months) == 48

print("\n=== 3. TESTING DROPDOWN SELECTION & PREDICTION FLOW ===")
test_months = ['January 2014', 'March 2015', 'September 2016', 'November 2017']
for m in test_months:
    with urllib.request.urlopen(f"{base_url}/api/predict?month={urllib.parse.quote(m)}") as resp:
        res = json.loads(resp.read().decode('utf-8'))
        print(f"Selected Month: {res['month_name']}")
        print(f"  Actual Sales:    {res['actual_sales']:,.2f}")
        print(f"  Predicted Sales: {res['predicted_sales']:,.2f}")
        print(f"  Difference:      {res['difference']:,.2f} ({res['difference_pct']}%)")
        assert res['actual_sales'] > 0
        assert res['predicted_sales'] > 0
        diff_check = abs(res['difference'] - (res['actual_sales'] - res['predicted_sales']))
        assert diff_check < 0.05

print("\n=== 4. TESTING MODEL PERFORMANCE METRICS ===")
metrics = data['kpis']['model_metrics']
print(f"R2 Score: {metrics['r2_score']}")
print(f"MAE:      {metrics['mae']:,.2f}")
print(f"MSE:      {metrics['mse']:,.2f}")
print(f"RMSE:     {metrics['rmse']:,.2f}")

print("\n=== ALL FULL-FLOW ACCEPTANCE CRITERIA VERIFIED 100% ===")
