import json
import os
import sys
from pathlib import Path
import pytest
import pandas as pd
import matplotlib.pyplot as plt

# Ensure the root directory is in sys.path so we can import visualizer
sys.path.append(str(Path(__file__).parent.parent))

from visualizer.core import Visualizer

# Fixture to create a temporary config file
@pytest.fixture
def temp_config_file(tmp_path):
    config_path = tmp_path / "config.json"
    return config_path

# Test: Check if Config File Loads Correctly
def test_load_config_valid(temp_config_file):
    config_data = [{
        "directory": "dummy_path/*.csv",
        "columns": "Income",
        "groupby": "Year",
        "chart_type": "bar"
    }]
    
    with open(temp_config_file, 'w') as f:
        json.dump(config_data, f)
        
    viz = Visualizer()
    viz.load_config(str(temp_config_file))
    
    assert len(viz.config_data) == 1
    assert viz.config_data[0]['directory'] == "dummy_path/*.csv"

# Test: Check if Config File Not Found Error is Raised
def test_load_config_file_not_found():
    viz = Visualizer()
    with pytest.raises(FileNotFoundError):
        viz.load_config("non_existent_file.json")

# Test: Check if Invalid JSON Error is Raised
def test_load_config_invalid_json(temp_config_file):
    with open(temp_config_file, 'w') as f:
        f.write("{invalid_json: true") # Malformed JSON
        
    viz = Visualizer()
    with pytest.raises(ValueError, match="Failed to decode JSON"):
        viz.load_config(str(temp_config_file))

# Test: Check if Empty Config Error is Raised
def test_load_config_empty(temp_config_file):
    with open(temp_config_file, 'w') as f:
        json.dump([], f) # Empty list
        
    viz = Visualizer()
    with pytest.raises(ValueError, match="No config data found"):
        viz.load_config(str(temp_config_file))

# Test: End-to-End Processing
def test_process_end_to_end(tmp_path):
    """
    Creates a temporary CSV file and a config file pointing to it.
    Runs the visualizer and checks if the output PNG is created.
    """
    # 1. Setup Test Data Directory
    data_dir = tmp_path / "data"
    data_dir.mkdir()
    
    csv_file = data_dir / "test_financials.csv"
    
    # Create Dummy Data
    df = pd.DataFrame({
        'Year': [2023, 2023, 2024, 2024],
        'Category': ['A', 'B', 'A', 'B'],
        'Amount': [100, 200, 150, 250]
    })
    df.to_csv(csv_file, index=False)
    
    # 2. Setup Config File
    # Ensure pattern uses forward slashes for cross-platform compatibility in glob
    search_pattern = str(data_dir / "*.csv").replace("\\", "/")
    
    config_data = [{
        "directory": search_pattern,
        "columns": "Amount",
        "groupby": "Year",
        "chart_type": "bar",
        "chart_label": "Total Amount"
    }]
    
    config_file = tmp_path / "test_config.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
        
    # 3. Run Visualizer
    viz = Visualizer()
    viz.load_config(str(config_file))
    viz.process_all()
    
    # 4. Verify Output
    # Expected filename format: {base_filename}_{groupby_col}_{chart_type}.png
    expected_output = data_dir / "test_financials_Year_bar.png"
    
    assert expected_output.exists(), f"Expected chart file {expected_output} was not created."
    
    # Optional: Check if file size > 0 to ensure it's not empty
    assert expected_output.stat().st_size > 0

# Test: Check handling of multiple columns summation
def test_process_multiple_columns_sum(tmp_path):
    data_dir = tmp_path / "data_multi"
    data_dir.mkdir()
    csv_file = data_dir / "multi_col.csv"
    
    df = pd.DataFrame({
        'Year': [2023, 2024],
        'Salary': [50000, 52000],
        'Bonus': [5000, 6000]
    })
    df.to_csv(csv_file, index=False)
    
    search_pattern = str(data_dir / "*.csv").replace("\\", "/")
    
    config_data = [{
        "directory": search_pattern,
        "columns": ["Salary", "Bonus"],
        "groupby": "Year",
        "chart_type": "line"
    }]
    
    config_file = tmp_path / "config_multi.json"
    with open(config_file, 'w') as f:
        json.dump(config_data, f)
        
    viz = Visualizer()
    viz.load_config(str(config_file))
    viz.process_all()
    
    expected_output = data_dir / "multi_col_Year_line.png"
    assert expected_output.exists()
