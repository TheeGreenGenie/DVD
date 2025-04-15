from flask import Flask, render_template, jsonify, request, redirect, url_for, flash
import os
import json
import pandas as pd
from data_processor import DataProcessor

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'

# Create uploads folder if it doesn't exist
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Initialize data processor without database
data_processor = DataProcessor()

@app.context_processor
def inject_data_processor():
    return dict(data_processor=data_processor)

@app.route('/')
def index():
    """Home page"""
    # Check if database is connected
    is_connected = hasattr(data_processor, 'db_path') and data_processor.db_path
    
    return render_template('index.html', is_connected=is_connected)

@app.route('/connect', methods=['GET', 'POST'])
def connect_db():
    """Connect to a database"""
    if request.method == 'POST':
        # Check if database file was uploaded
        if 'database_file' in request.files:
            db_file = request.files['database_file']
            
            if db_file.filename:
                # Save the uploaded file
                file_path = os.path.join(app.config['UPLOAD_FOLDER'], db_file.filename)
                db_file.save(file_path)
                
                # Connect to the database
                success = data_processor.connect_to_database(file_path)
                
                if success:
                    return redirect(url_for('tables'))
                else:
                    flash("Error connecting to database")
                    return redirect(url_for('index'))
        
        # Alternative: Use existing database path
        db_path = request.form.get('db_path')
        if db_path and os.path.exists(db_path):
            success = data_processor.connect_to_database(db_path)
            
            if success:
                return redirect(url_for('tables'))
            else:
                flash("Error connecting to database")
                
    # GET request: show connection form
    return render_template('connect.html')

@app.route('/tables')
def tables():
    """Show available tables in the database"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        flash("Please connect to a database first")
        return redirect(url_for('connect_db'))
    
    tables = data_processor.get_table_list()

    # Add basic stats for the tables page
    stats = {
        'total_records': 0,
    }
    

    return render_template('tables.html', tables=tables, db_path=data_processor.db_path)

@app.route('/view/<table_name>')
def view_table(table_name):
    """View a specific table and its basic info"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        flash("Please connect to a database first")
        return redirect(url_for('connect_db'))
    
    # Load the table data
    success = data_processor.load_table_data(table_name)
    
    if not success:
        flash(f"Error loading table {table_name}")
        return redirect(url_for('tables'))
    
    # Get column information
    columns = data_processor.get_column_info(table_name)
    
    # Get data preview
    preview = data_processor.get_data_preview(10)
    
    # Get basic stats
    stats = data_processor.get_basic_stats()
    
    return render_template(
        'table_view.html', 
        table_name=table_name, 
        columns=columns, 
        preview=preview,
        stats=stats
    )

@app.route('/dashboard/<table_name>')
def dashboard(table_name):
    """Show dashboard for a specific table"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        flash("Please connect to a database first")
        return redirect(url_for('connect_db'))
    
    # Load the table data if not already loaded
    if not data_processor.current_table or data_processor.current_table != table_name:
        success = data_processor.load_table_data(table_name)
        
        if not success:
            flash(f"Error loading table {table_name}")
            return redirect(url_for('tables'))
    
    # Generate charts for dashboard
    charts = data_processor.generate_dashboard_charts()
    
    # Get basic stats
    stats = data_processor.get_basic_stats()
    
    # Get column info for filter options
    columns = data_processor.get_column_info(table_name)
    
    return render_template(
        'dashboard.html',
        table_name=table_name,
        stats=stats,
        charts=charts,
        columns=columns
    )

@app.route('/api/data/<table_name>')
def get_data(table_name):
    """Get JSON data for a table"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        return jsonify({"error": "Not connected to database"})
    
    # Load table data if not already loaded
    if not data_processor.current_table or data_processor.current_table != table_name:
        success = data_processor.load_table_data(table_name)
        
        if not success:
            return jsonify({"error": f"Failed to load table {table_name}"})
    
    # Return data as JSON
    return jsonify(data_processor.get_data_as_dict())

@app.route('/api/filter/<table_name>', methods=['POST'])
def filter_data(table_name):
    """Filter data based on parameters"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        return jsonify({"error": "Not connected to database"})
    
    # Load table data if not already loaded
    if not data_processor.current_table or data_processor.current_table != table_name:
        success = data_processor.load_table_data(table_name)
        
        if not success:
            return jsonify({"error": f"Failed to load table {table_name}"})
    
    # Get filter parameters
    filter_params = request.json or {}
    
    # Apply filters and return results
    filtered_data = data_processor.filter_data(filter_params)
    return jsonify(filtered_data)

@app.route('/custom_query', methods=['GET', 'POST'])
def custom_query():
    """Run a custom SQL query"""
    if not hasattr(data_processor, 'db_path') or not data_processor.db_path:
        flash("Please connect to a database first")
        return redirect(url_for('connect_db'))
    
    results = None
    error = None
    
    if request.method == 'POST':
        query = request.form.get('query')
        if query:
            try:
                results = data_processor.run_custom_query(query)
                if isinstance(results, dict) and 'error' in results:
                    error = results['error']
                    results = None
            except Exception as e:
                error = str(e)
    
    return render_template('custom_query.html', results=results, error=error)

if __name__ == '__main__':
    app.run(debug=True)