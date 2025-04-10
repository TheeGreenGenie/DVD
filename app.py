from flask import Flask, render_template, jsonify, request
import pandas as pd
import json
import plotly
import plotly.express as px
from data_processor import DataProcessor

app = Flask(__name__)

# Initialize data processor
data_processor = DataProcessor()

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/dashboard')
def dashboard():
    # Get basic stats
    stats = data_processor.get_basic_stats()
    
    # Create visualizations
    plot1_json = data_processor.create_bar_chart()
    plot2_json = data_processor.create_line_chart()
    plot3_json = data_processor.create_scatter_plot()
    plot4_json = data_processor.create_pie_chart()
    
    return render_template('dashboard.html', 
                           stats=stats,
                           plot1=plot1_json,
                           plot2=plot2_json,
                           plot3=plot3_json,
                           plot4=plot4_json)

@app.route('/api/data')
def get_data():
    data = data_processor.get_data_as_dict()
    return jsonify(data)

@app.route('/api/filter', methods=['POST'])
def filter_data():
    filter_params = request.json
    filtered_data = data_processor.filter_data(filter_params)
    return jsonify(filtered_data)

if __name__ == '__main__':
    app.run(debug=True)
