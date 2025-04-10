# Flask Database Visualizer

A dynamic web application that connects to SQLite databases and automatically generates visualizations based on database content. This tool makes it easy to explore and understand your data without writing any code.


## Features

- **Connect to any SQLite database** (.db, .sqlite, .sqlite3)
- **Automatic visualization generation** based on data types
- **Interactive charts** using Plotly.js
- **Data filtering** capabilities
- **Table/column statistics**
- **Custom SQL query** execution

## Getting Started

These instructions will help you get a copy of the project up and running on your local machine.

### Prerequisites

- Python 3.8+ 
- pip (Python package manager)

### Installation

1. **Clone the repository**

```bash
git clone https://github.com/yourusername/flask-db-visualizer.git
cd flask-db-visualizer
```

2. **Create and activate a virtual environment**

Windows:
```bash
python -m venv venv
venv\Scripts\activate
```

macOS/Linux:
```bash
python3 -m venv venv
source venv/bin/activate
```

3. **Install the required packages**

```bash
pip install -r requirements.txt
```

If requirements.txt isn't available, install the core dependencies:

```bash
pip install flask pandas plotly numpy
```

### Running the Application

Start the Flask server:

```bash
python app.py
```

The application will be accessible at: [http://127.0.0.1:5000](http://127.0.0.1:5000)

## Using the Application

### Connecting to a Database

1. **Start the application** and navigate to the homepage
2. **Click "Connect Database"** 
3. **Choose one of the options**:
   - **Upload a database file**: Select a SQLite database file from your computer
   - **Connect to existing database**: Provide the path to a database file on the server

### Exploring Database Tables

1. Once connected, you'll see a list of tables in your database
2. **View Table**: Click to see the raw data and column information
3. **Dashboard**: Click to see automatically generated visualizations

### Visualizing Your Data

The dashboard shows several types of visualizations based on the data types in your table:

- **Bar charts** for categorical data
- **Histograms** for numeric distributions 
- **Line charts** for time series data
- **Scatter plots** for relationships between numeric fields
- **Box plots** for statistical distributions

### Filtering Data

Each dashboard includes a filter panel to narrow down your data:
- **Text filters** for string columns
- **Range filters** (min/max) for numeric columns

### Running Custom Queries

1. Click **"Custom Query"** in the navigation
2. Enter your SQL query in the text area
3. Click **"Run Query"** to execute
4. View the results in a tabular format

## Sample Databases

If you don't have a database to visualize, you can download these sample SQLite databases:

- [Chinook Database](https://www.sqlitetutorial.net/sqlite-sample-database/) - A digital media store database
- [Northwind Database](https://github.com/jpwhite3/northwind-SQLite3) - A sample sales database

## Troubleshooting

### Common Issues

- **"No such table" error**: Ensure your database contains the table you're trying to access
- **Empty visualizations**: Some tables may not have data suitable for visualization
- **Slow performance**: Large databases may take longer to process

### Error Handling

The application includes built-in error handling for common issues:
- Invalid SQL queries
- Inaccessible database files
- Incompatible data types
