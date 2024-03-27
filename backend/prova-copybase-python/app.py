from flask import Flask, request, jsonify
import pandas as pd
from flask_cors import CORS
import numpy as np

app = Flask(__name__)
CORS(app, resources={r"/upload": {"origins": "http://localhost:8082"}}, methods=['POST', 'GET'])

def calculate_metrics(data):
    metrics = {}
    data['month_year'] = data['subscription_start'].dt.to_period('M')
    
    # Calcula a receita mensal recorrente (MRR)
    metrics['mrr'] = data.groupby('month_year')['valor'].sum()
    
    # Calcula a taxa de churn
    data['churned'] = data['status'] == 'cancelled'
    metrics['churn_rate'] = data.groupby('month_year')['churned'].mean()
    
    # Calcula a duração média da assinatura
    data['subscription_length'] = (data['próximo ciclo'] - data['data início']).dt.days
    metrics['average_subscription_length'] = data['subscription_length'].mean()
    
    return metrics

@app.route('/', methods=['GET'])
def home():
    return "Backend da Aplicação!"

@app.route('/upload', methods=['POST', 'GET'])
def upload_file():
    if request.method == 'POST':
        file = request.files['file']
        data = pd.read_excel(file)
        data['subscription_start'] = pd.to_datetime(data['subscription_start'])
        data['subscription_end'] = pd.to_datetime(data['subscription_end'])
        metrics = calculate_metrics(data)
        return jsonify(metrics)  # Retorna as métricas como JSON
    elif request.method == 'GET':
        # Lógica para lidar com solicitações GET, se necessário
        return "GET request received for /upload endpoint"
        # return metrics.to_json(orient='split')

if __name__ == '__main__':
    app.run(debug=True)