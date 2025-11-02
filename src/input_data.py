"""
Input data loading and preprocessing functions.

Handles reading CSV files and preprocessing data for workforce projections.
"""

import pandas as pd
from pathlib import Path
from utils import get_data_dir


def load_csv(file_path, skipinitialspace=True):
    """
    Load a CSV file.
    
    Args:
        file_path: Path to the CSV file (can be string or Path object)
        skipinitialspace: Whether to skip whitespace after delimiter
    
    Returns:
        pd.DataFrame: Loaded dataframe
    """
    return pd.read_csv(file_path, skipinitialspace=skipinitialspace)


def preprocess_numeric_column(df, column_name, remove_chars=None):
    """
    Preprocess a numeric column by removing non-numeric characters and converting to numeric.
    
    Args:
        df: DataFrame to process
        column_name: Name of the column to preprocess
        remove_chars: List of characters to remove (default: [',', '"'])
    
    Returns:
        pd.Series: Preprocessed numeric series
    """
    if remove_chars is None:
        remove_chars = [',', '"']
    
    # Convert to string, remove unwanted characters, then convert to numeric
    series = df[column_name].astype(str)
    for char in remove_chars:
        series = series.str.replace(char, '', regex=False)
    
    return pd.to_numeric(series, errors='coerce')


def load_registrants_data(data_dir=None, filename='gphc-total-number-of-pharmacy-registrants.csv'):
    """
    Load and preprocess the total number of pharmacy registrants data.
    
    Args:
        data_dir: Optional data directory path. If None, uses default project structure.
        filename: Name of the CSV file to load
    
    Returns:
        pd.DataFrame: Preprocessed dataframe with registrants data
    """
    data_dir = get_data_dir(data_dir)
    file_path = data_dir / filename
    
    # Load CSV
    df = load_csv(file_path)
    
    # Preprocess registrants column (handle commas, quotes, etc.)
    df['registrants'] = preprocess_numeric_column(df, 'registrants').astype(int)
    
    # Convert month and year to numeric for proper sorting
    df['month'] = pd.to_numeric(df['month'])
    df['year'] = pd.to_numeric(df['year'])
    
    # Sort by profession, year, and month for consistency
    df = df.sort_values(['profession', 'year', 'month']).reset_index(drop=True)
    
    return df


def load_joiners_data(data_dir=None, filename='gphc-registrants-joiners.csv'):
    """
    Load and preprocess the joiners data.
    
    Args:
        data_dir: Optional data directory path. If None, uses default project structure.
        filename: Name of the CSV file to load
    
    Returns:
        pd.DataFrame: Preprocessed dataframe with joiners data
    """
    data_dir = get_data_dir(data_dir)
    file_path = data_dir / filename
    
    df = load_csv(file_path)
    
    # Preprocess numeric columns
    if 'total_joiners' in df.columns:
        df['total_joiners'] = preprocess_numeric_column(df, 'total_joiners').astype(int)
    if 'joiners' in df.columns:
        df['joiners'] = preprocess_numeric_column(df, 'joiners').astype(int)
    
    return df


def load_leavers_data(data_dir=None, filename='gphc-registrants-leavers.csv'):
    """
    Load and preprocess the leavers data.
    
    Args:
        data_dir: Optional data directory path. If None, uses default project structure.
        filename: Name of the CSV file to load
    
    Returns:
        pd.DataFrame: Preprocessed dataframe with leavers data
    """
    data_dir = get_data_dir(data_dir)
    file_path = data_dir / filename
    
    df = load_csv(file_path)
    
    # Preprocess numeric columns
    if 'total_leavers' in df.columns:
        df['total_leavers'] = preprocess_numeric_column(df, 'total_leavers').astype(int)
    if 'leavers' in df.columns:
        df['leavers'] = preprocess_numeric_column(df, 'leavers').astype(int)
    
    return df


def validate_registrants_data(df):
    """
    Validate registrants dataframe for required columns and data quality.
    
    Args:
        df: DataFrame to validate
    
    Returns:
        tuple: (is_valid, error_messages)
    """
    errors = []
    required_columns = ['profession', 'registrants', 'month', 'year']
    
    # Check required columns
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    # Check for null values in required columns
    for col in required_columns:
        if col in df.columns and df[col].isnull().any():
            null_count = df[col].isnull().sum()
            errors.append(f"Column '{col}' has {null_count} null values")
    
    # Check for negative registrants
    if 'registrants' in df.columns:
        if (df['registrants'] < 0).any():
            errors.append("Found negative values in 'registrants' column")
    
    # Check month and year ranges
    if 'month' in df.columns:
        invalid_months = df[(df['month'] < 1) | (df['month'] > 12)]
        if not invalid_months.empty:
            errors.append(f"Found {len(invalid_months)} rows with invalid month values")
    
    is_valid = len(errors) == 0
    return is_valid, errors

