import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json
import sqlite3
from sqlite3 import Error
import os

class DataProcessor:
    def __init__(self, db_path=None):
        """Initialize with optional database path"""
        self.db_path = db_path
        self.tables = []
        self.current_table = None
        self.df = None
        
        # If database provided, connect and load tables
        if db_path and os.path.exists(db_path):
            self.connect_to_database()
    
    def connect_to_database(self, db_path=None):
        """Connect to SQLite database and get table names"""
        if db_path:
            self.db_path = db_path
            
        if not self.db_path or not os.path.exists(self.db_path):
            raise ValueError("Valid database path required")
            
        try:
            # Connect to database
            conn = sqlite3.connect(self.db_path)
            
            # Get list of tables
            cursor = conn.cursor()
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
            self.tables = [table[0] for table in cursor.fetchall()]
            
            conn.close()
            return True
        except Error as e:
            print(f"Database connection error: {e}")
            return False
    
    def load_table_data(self, table_name=None, query=None):
        """Load data from specified table or custom query"""
        if not self.db_path:
            raise ValueError("Database not connected")
            
        if table_name:
            self.current_table = table_name
            query = f"SELECT * FROM {table_name}"
        elif not query:
            raise ValueError("Either table_name or query must be provided")
            
        try:
            # Connect and load data into pandas DataFrame
            conn = sqlite3.connect(self.db_path)
            self.df = pd.read_sql_query(query, conn)
            conn.close()
            return True
        except Error as e:
            print(f"Error loading data: {e}")
            return False
    
    def get_table_list(self):
        """Return list of tables in the database"""
        return self.tables
    
    def get_column_info(self, table_name=None):
        """Get column names and data types for a table"""
        if not table_name and self.current_table:
            table_name = self.current_table
            
        if not table_name:
            raise ValueError("Table name required")
            
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute(f"PRAGMA table_info({table_name})")
            columns = cursor.fetchall()
            conn.close()
            
            # Format column info
            column_info = [{'name': col[1], 'type': col[2]} for col in columns]
            return column_info
        except Error as e:
            print(f"Error getting column info: {e}")
            return []
    
    def get_data_preview(self, rows=5):
        """Return a preview of the current dataframe"""
        if self.df is None:
            return {}
            
        preview_df = self.df.head(rows)
        return preview_df.to_dict(orient='records')
    
    def get_data_as_dict(self):
        """Return the DataFrame as a dictionary suitable for JSON"""
        if self.df is None:
            return {}
            
        # Convert dates to strings if present
        df_copy = self.df.copy()
        for col in df_copy.select_dtypes(include=['datetime64']).columns:
            df_copy[col] = df_copy[col].dt.strftime('%Y-%m-%d')
            
        return df_copy.to_dict(orient='records')
    
    def get_basic_stats(self):
        """Get basic statistics about numeric columns"""
        if self.df is None:
            return {}
            
        stats = {
            'total_records': len(self.df),
            'columns': {}
        }
        
        # Get stats for numeric columns
        numeric_cols = self.df.select_dtypes(include=['number']).columns
        for col in numeric_cols:
            stats['columns'][col] = {
                'mean': round(self.df[col].mean(), 2) if not pd.isna(self.df[col].mean()) else 'N/A',
                'median': round(self.df[col].median(), 2) if not pd.isna(self.df[col].median()) else 'N/A',
                'min': round(self.df[col].min(), 2) if not pd.isna(self.df[col].min()) else 'N/A',
                'max': round(self.df[col].max(), 2) if not pd.isna(self.df[col].max()) else 'N/A'
            }
            
        # Get value counts for categorical columns
        categorical_cols = self.df.select_dtypes(include=['object']).columns
        for col in categorical_cols[:5]:  # Limit to first 5 categorical columns
            value_counts = self.df[col].value_counts().head(10).to_dict()  # Top 10 values
            stats['columns'][col] = {
                'type': 'categorical',
                'unique_values': self.df[col].nunique(),
                'top_values': value_counts
            }
            
        return stats
    
    def filter_data(self, filter_params):
        """Filter data based on provided parameters"""
        if self.df is None:
            return {}
            
        filtered_df = self.df.copy()
        
        # Apply filters from filter_params dict
        for column, condition in filter_params.items():
            if column in filtered_df.columns:
                if isinstance(condition, list):
                    # Multiple values for inclusion
                    filtered_df = filtered_df[filtered_df[column].isin(condition)]
                elif isinstance(condition, dict):
                    # Range condition with min/max
                    if 'min' in condition and condition['min'] is not None:
                        filtered_df = filtered_df[filtered_df[column] >= condition['min']]
                    if 'max' in condition and condition['max'] is not None:
                        filtered_df = filtered_df[filtered_df[column] <= condition['max']]
                else:
                    # Exact match
                    filtered_df = filtered_df[filtered_df[column] == condition]
        
        # Convert dates to strings if present
        for col in filtered_df.select_dtypes(include=['datetime64']).columns:
            filtered_df[col] = filtered_df[col].dt.strftime('%Y-%m-%d')
            
        return filtered_df.to_dict(orient='records')
    
    def detect_chart_types(self):
        """Automatically detect appropriate chart types for the data"""
        if self.df is None:
            return {}
            
        chart_suggestions = {}
        
        # Get numeric and categorical columns
        numeric_cols = self.df.select_dtypes(include=['number']).columns.tolist()
        categorical_cols = self.df.select_dtypes(include=['object']).columns.tolist()
        date_cols = self.df.select_dtypes(include=['datetime64']).columns.tolist()
        
        # Bar charts for categorical columns
        for col in categorical_cols[:5]:  # Limit to first 5
            chart_suggestions[f'bar_{col}'] = {
                'type': 'bar',
                'title': f'Distribution of {col}',
                'x_col': col,
                'agg_func': 'count'
            }
            
        # Numeric column distributions (histograms)
        for col in numeric_cols[:5]:  # Limit to first 5
            chart_suggestions[f'hist_{col}'] = {
                'type': 'histogram',
                'title': f'Distribution of {col}',
                'x_col': col
            }
            
        # Time series if date columns exist
        for date_col in date_cols:
            for num_col in numeric_cols[:3]:  # First 3 numeric columns
                chart_suggestions[f'time_{date_col}_{num_col}'] = {
                    'type': 'line',
                    'title': f'{num_col} Over Time',
                    'x_col': date_col,
                    'y_col': num_col
                }
                
        # Scatter plots between numeric columns
        if len(numeric_cols) >= 2:
            for i in range(min(3, len(numeric_cols))):
                for j in range(i+1, min(4, len(numeric_cols))):
                    chart_suggestions[f'scatter_{numeric_cols[i]}_{numeric_cols[j]}'] = {
                        'type': 'scatter',
                        'title': f'{numeric_cols[i]} vs {numeric_cols[j]}',
                        'x_col': numeric_cols[i],
                        'y_col': numeric_cols[j]
                    }
                    
        # Add categorical breakdowns
        if categorical_cols and numeric_cols:
            chart_suggestions['categorical_breakdown'] = {
                'type': 'box',
                'title': f'{numeric_cols[0]} by {categorical_cols[0]}',
                'x_col': categorical_cols[0],
                'y_col': numeric_cols[0]
            }
            
        return chart_suggestions
    
    def create_chart(self, chart_config):
        """Create a chart based on configuration"""
        if self.df is None:
            return None
            
        chart_type = chart_config.get('type', 'bar')
        title = chart_config.get('title', 'Chart')
        x_col = chart_config.get('x_col')
        y_col = chart_config.get('y_col')
        color_col = chart_config.get('color_col')
        
        if not x_col or x_col not in self.df.columns:
            return None
            
        try:
            if chart_type == 'bar':
                if y_col and y_col in self.df.columns:
                    # Grouped bar chart
                    fig = px.bar(
                        self.df,
                        x=x_col,
                        y=y_col,
                        color=color_col,
                        title=title
                    )
                else:
                    # Count bar chart
                    counts = self.df[x_col].value_counts().reset_index()
                    counts.columns = [x_col, 'count']
                    fig = px.bar(
                        counts,
                        x=x_col,
                        y='count',
                        title=title
                    )
                    
            elif chart_type == 'line':
                if not y_col or y_col not in self.df.columns:
                    return None
                    
                # For time series, sort by date
                if pd.api.types.is_datetime64_any_dtype(self.df[x_col]):
                    plot_df = self.df.sort_values(by=x_col)
                else:
                    plot_df = self.df
                    
                fig = px.line(
                    plot_df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=title
                )
                
            elif chart_type == 'scatter':
                if not y_col or y_col not in self.df.columns:
                    return None
                    
                fig = px.scatter(
                    self.df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    size=chart_config.get('size_col'),
                    title=title
                )
                
            elif chart_type == 'histogram':
                fig = px.histogram(
                    self.df,
                    x=x_col,
                    color=color_col,
                    title=title
                )
                
            elif chart_type == 'box':
                if not y_col or y_col not in self.df.columns:
                    return None
                    
                fig = px.box(
                    self.df,
                    x=x_col,
                    y=y_col,
                    color=color_col,
                    title=title
                )
                
            elif chart_type == 'pie':
                counts = self.df[x_col].value_counts().reset_index()
                counts.columns = [x_col, 'count']
                fig = px.pie(
                    counts,
                    names=x_col,
                    values='count',
                    title=title
                )
            else:
                return None
                
            return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
            
        except Exception as e:
            print(f"Error creating chart: {e}")
            return None
    
    def generate_dashboard_charts(self):
        """Generate charts for dashboard based on data types"""
        if self.df is None:
            return {}
            
        charts = {}
        chart_suggestions = self.detect_chart_types()
        
        # Create each suggested chart
        for chart_id, config in chart_suggestions.items():
            chart_json = self.create_chart(config)
            if chart_json:
                charts[chart_id] = {
                    'config': config,
                    'json': chart_json
                }
                
        return charts
    
    def run_custom_query(self, query):
        """Run a custom SQL query on the database"""
        if not self.db_path:
            raise ValueError("Database not connected")
            
        try:
            conn = sqlite3.connect(self.db_path)
            result_df = pd.read_sql_query(query, conn)
            conn.close()
            return result_df.to_dict(orient='records')
        except Error as e:
            print(f"Query error: {e}")
            return {"error": str(e)}