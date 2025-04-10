import pandas as pd
import numpy as np
import plotly
import plotly.express as px
import plotly.graph_objects as go
import json

class DataProcessor:
    def __init__(self):
        # For this example, we'll create sample data
        # In a real application, you would load data from a file or database
        np.random.seed(42)
        dates = pd.date_range('2023-01-01', periods=100)
        self.df = pd.DataFrame({
            'date': dates,
            'value': np.random.randn(100).cumsum(),
            'category': np.random.choice(['A', 'B', 'C', 'D'], 100),
            'size': np.random.randint(10, 100, 100)
        })
    
    def get_data_as_dict(self):
        """Return the DataFrame as a dictionary suitable for JSON"""
        return {
            'dates': self.df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'values': self.df['value'].tolist(),
            'categories': self.df['category'].tolist(),
            'sizes': self.df['size'].tolist()
        }
    
    def get_basic_stats(self):
        """Get basic statistics about the data"""
        return {
            'total_records': len(self.df),
            'average_value': round(self.df['value'].mean(), 2),
            'max_value': round(self.df['value'].max(), 2),
            'min_value': round(self.df['value'].min(), 2),
            'category_counts': self.df['category'].value_counts().to_dict()
        }
    
    def filter_data(self, filter_params):
        """Filter data based on provided parameters"""
        filtered_df = self.df.copy()
        
        if 'category' in filter_params:
            filtered_df = filtered_df[filtered_df['category'].isin(filter_params['category'])]
        
        if 'date_range' in filter_params:
            start_date, end_date = filter_params['date_range']
            filtered_df = filtered_df[(filtered_df['date'] >= start_date) & 
                                      (filtered_df['date'] <= end_date)]
        
        return {
            'dates': filtered_df['date'].dt.strftime('%Y-%m-%d').tolist(),
            'values': filtered_df['value'].tolist(),
            'categories': filtered_df['category'].tolist(),
            'sizes': filtered_df['size'].tolist()
        }
    
    def create_bar_chart(self):
        """Create a bar chart of category counts"""
        category_counts = self.df['category'].value_counts().reset_index()
        category_counts.columns = ['category', 'count']
        
        fig = px.bar(
            category_counts, 
            x='category', 
            y='count',
            title='Count by Category',
            labels={'count': 'Count', 'category': 'Category'},
            color='category'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_line_chart(self):
        """Create a line chart of values over time"""
        # Aggregate data by day
        daily_data = self.df.groupby(self.df['date'].dt.date)['value'].mean().reset_index()
        
        fig = px.line(
            daily_data, 
            x='date', 
            y='value',
            title='Values Over Time',
            labels={'value': 'Average Value', 'date': 'Date'}
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_scatter_plot(self):
        """Create a scatter plot of values by size and category"""
        fig = px.scatter(
            self.df, 
            x='date', 
            y='value',
            size='size',
            color='category',
            title='Value by Date, Size, and Category',
            labels={'value': 'Value', 'date': 'Date', 'size': 'Size', 'category': 'Category'}
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
    
    def create_pie_chart(self):
        """Create a pie chart of category distribution"""
        category_counts = self.df['category'].value_counts().reset_index()
        category_counts.columns = ['category', 'count']
        
        fig = px.pie(
            category_counts, 
            values='count', 
            names='category',
            title='Category Distribution'
        )
        
        return json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
