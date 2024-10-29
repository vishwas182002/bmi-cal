# app.py
from flask import Flask, request, jsonify, render_template
import pandas as pd
import os

app = Flask(__name__)
CSV_FILE = 'bmi.csv'  # Define the CSV file name

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/bmi_calculator', methods=['GET'])
def bmi_calculator():
    return render_template('bmi_calculator.html')

@app.route('/data_analytics', methods=['GET'])
def data_analytics():
    return render_template('data_analytics.html')

@app.route('/calculate_bmi', methods=['POST'])
def calculate_bmi_route():
    data = request.json
    gender = data['gender']
    height = float(data['height'])
    weight = float(data['weight'])
    
    # BMI calculation
    bmi = weight / ((height / 100) ** 2)
    
    # Determine BMI index
    index = 0
    if bmi < 16:
        index = 0  # Extremely Weak
    elif 16 <= bmi < 17:
        index = 1  # Weak
    elif 17 <= bmi < 25:
        index = 2  # Normal
    elif 25 <= bmi < 30:
        index = 3  # Overweight
    elif 30 <= bmi < 35:
        index = 4  # Obesity
    else:
        index = 5  # Extreme Obesity
    
    # Save to CSV
    new_entry = pd.DataFrame({'Gender': [gender], 'Height': [height], 'Weight': [weight], 'Index': [index]})
    if os.path.exists(CSV_FILE):
        df = pd.read_csv(CSV_FILE)
        df = pd.concat([df, new_entry], ignore_index=True)
    else:
        df = new_entry
    
    df.to_csv(CSV_FILE, index=False)
    return jsonify({'bmi': round(bmi, 2), 'index': index})

@app.route('/get_analytics_data', methods=['GET'])
def get_analytics_data():
    if not os.path.exists(CSV_FILE):
        return jsonify({
            'error': 'No data available'
        })

    df = pd.read_csv(CSV_FILE)
    
    # Basic statistics
    total_records = len(df)
    gender_distribution = df['Gender'].value_counts().to_dict()
    
    # BMI Index distribution
    index_mapping = {
        0: 'Extremely Weak',
        1: 'Weak',
        2: 'Normal',
        3: 'Overweight',
        4: 'Obesity',
        5: 'Extreme Obesity'
    }
    
    index_distribution = df['Index'].value_counts().to_dict()
    index_distribution = {index_mapping[k]: v for k, v in index_distribution.items()}
    
    # Gender-wise BMI Index distribution
    gender_index_dist = df.groupby(['Gender', 'Index']).size().unstack(fill_value=0).to_dict()
    
    # Average height and weight by gender
    avg_metrics = df.groupby('Gender')[['Height', 'Weight']].mean().round(2).to_dict()
    
    # Prepare data for charts
    bmi_trends = df.groupby('Index').size().to_dict()
    bmi_trends = {index_mapping[k]: v for k, v in bmi_trends.items()}
    
    analytics_data = {
        'totalRecords': total_records,
        'genderDistribution': gender_distribution,
        'indexDistribution': index_distribution,
        'genderIndexDistribution': gender_index_dist,
        'averageMetrics': avg_metrics,
        'bmiTrends': bmi_trends
    }
    
    return jsonify(analytics_data)

@app.route('/get_bmi_history', methods=['GET'])
def get_bmi_history():
    if not os.path.exists(CSV_FILE):
        return jsonify({
            'error': 'No data available'
        })
        
    df = pd.read_csv(CSV_FILE)
    
    # Get the last 10 entries
    last_entries = df.tail(10).to_dict('records')
    
    return jsonify(last_entries)

if __name__ == '__main__':
    app.run(debug=True)
