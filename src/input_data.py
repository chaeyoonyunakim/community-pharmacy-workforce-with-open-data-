"""
Input data loading and preprocessing functions.

Handles reading CSV files and preprocessing data for workforce projections.
"""

import pandas as pd
from pathlib import Path
from utils import get_data_dir
from config import BASELINE_YEAR, BASELINE_MONTH


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
    Load and preprocess annual snapshot data for England only.
    
    Filters data to:
    - England only (country='England')
    - Annual snapshot data only (month=3, March)
    
    This ensures only yearly snapshot data is loaded, excluding monthly actuals.
    
    Args:
        data_dir: Optional data directory path. If None, uses default project structure.
        filename: Name of the CSV file to load
    
    Returns:
        pd.DataFrame: Preprocessed dataframe with annual snapshot data for England only
    """
    data_dir = get_data_dir(data_dir)
    file_path = data_dir / filename
    
    # Load CSV
    df = load_csv(file_path)
    
    # Filter for England data only if country column exists
    if 'country' in df.columns:
        df = df[df['country'] == 'England'].copy()
        if df.empty:
            raise ValueError("No England data found in the CSV file. Please ensure country='England' rows exist.")
    
    # Filter for annual snapshot data only (month=3, March)
    df['month'] = pd.to_numeric(df['month'])
    df = df[df['month'] == BASELINE_MONTH].copy()
    
    if df.empty:
        raise ValueError(f"No snapshot data found for month {BASELINE_MONTH}. Ensure annual snapshot data exists.")
    
    # Preprocess registrants column (handle commas, quotes, etc.)
    df['registrants'] = preprocess_numeric_column(df, 'registrants').astype(int)
    
    # Convert year to numeric for proper sorting
    df['year'] = pd.to_numeric(df['year'])
    
    # Sort by profession and year for consistency
    df = df.sort_values(['profession', 'year']).reset_index(drop=True)
    
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


def calculate_annual_growth_rates(total_df):
    """
    Calculate Compound Annual Growth Rate (CAGR) from yearly snapshot data (2018 to 2025).
    
    Calculates the 7-year Compound Annual Growth Rate (CAGR) from the earliest
    available year (2018) to the baseline year (2025). CAGR represents the
    average annual growth rate over the period, accounting for compounding effects.
    
    Note: Average growth rate = CAGR (Compound Annual Growth Rate)
    
    Formula: CAGR = ((End/Start)^(1/Years) - 1) * 100
    
    Args:
        total_df: DataFrame with annual snapshot registrants data (month=3, England only)
    
    Returns:
        dict: Growth rate data by profession with keys:
            - baseline_total: Registrants at baseline year (March 2025 snapshot)
            - annual_growth_rate_pct: CAGR percentage (7-year average annual growth rate)
            - annual_change_estimate: Estimated annual absolute change
            - change_period: Total change over the 7-year period
            - years_elapsed: Number of years used for calculation (7 years: 2018-2025)
    """
    data = {}
    
    # Get profession names dynamically from the data
    professions = total_df['profession'].unique()
    
    for profession in professions:
        profession_df = total_df[total_df['profession'] == profession].copy()
        profession_df = profession_df.sort_values('year')
        
        # Get available years
        available_years = sorted(profession_df['year'].unique())
        
        if len(available_years) < 2:
            print(f"Warning: Insufficient snapshot data for {profession}. Need at least 2 years of data.")
            continue
        
        # Use baseline year from config (baseline_year = current_year)
        baseline_year = BASELINE_YEAR
        
        # Check if baseline year exists in data
        if baseline_year not in available_years:
            print(f"Warning: Baseline year {baseline_year} not found for {profession}. Using most recent year.")
            baseline_year = max(available_years)
        
        # Get baseline snapshot (baseline_year is used as both baseline and current)
        baseline = profession_df[profession_df['year'] == baseline_year]
        
        if baseline.empty:
            print(f"Warning: Missing snapshot data for {profession} at year {baseline_year}")
            continue
        
        baseline_total = int(baseline['registrants'].values[0])
        
        # Calculate growth rate from earliest available year to baseline year
        # This uses all available historical data for a more stable growth rate
        earliest_year = min(available_years)
        
        if earliest_year == baseline_year:
            # If baseline is the only year, cannot calculate growth rate
            print(f"Warning: Only one year of data for {profession}. Cannot calculate growth rate.")
            continue
        
        earliest = profession_df[profession_df['year'] == earliest_year]
        
        if earliest.empty:
            print(f"Warning: Missing snapshot data for {profession} at year {earliest_year}")
            continue
        
        earliest_total = int(earliest['registrants'].values[0])
        
        # Calculate years elapsed from earliest year to baseline year
        years_elapsed = baseline_year - earliest_year
        
        # Calculate annual growth rate using yearly intervals
        # Formula: ((end/start)^(1/years_elapsed) - 1) * 100
        growth_factor = baseline_total / earliest_total
        annual_growth_rate_pct = ((growth_factor ** (1 / years_elapsed)) - 1) * 100
        
        # Calculate absolute change over the period
        change_period = baseline_total - earliest_total
        annual_change_estimate = change_period / years_elapsed
        
        data[profession] = {
            'baseline_total': baseline_total,
            'annual_growth_rate_pct': round(annual_growth_rate_pct, 2),
            'annual_change_estimate': round(annual_change_estimate, 1),
            'change_period': change_period,
            'years_elapsed': years_elapsed
        }
    
    return data


def create_scenarios(rates_dict):
    """
    Create scenario adjustments based on calculated annual growth rates.
    
    Creates three scenarios:
    - baseline: Uses the calculated annual growth rate (multiplier 1.0)
    - optimistic: Higher growth rate (calculated rate + adjustment)
    - pessimistic: Lower growth rate (calculated rate - adjustment)
    
    Args:
        rates_dict: Dictionary from calculate_annual_growth_rates() with structure:
            {
                'profession': {
                    'annual_growth_rate_pct': float,
                    ...
                }
            }
    
    Returns:
        dict: Scenario adjustments with keys 'baseline', 'optimistic', 'pessimistic'
              Values are multipliers to apply to growth rates
    """
    if not rates_dict:
        # Default scenarios if no rates available
        return {
            'baseline': 1.0,
            'optimistic': 1.2,
            'pessimistic': 0.8
        }
    
    # Baseline: Use calculated growth rate as-is (1.0 multiplier)
    # Optimistic: 20% higher growth rate (1.2 multiplier)
    # Pessimistic: 20% lower growth rate (0.8 multiplier)
    return {
        'baseline': 1.0,      # Calculated growth rate
        'optimistic': 1.2,     # Plus 20% (higher growth)
        'pessimistic': 0.8     # Minus 20% (lower growth)
    }


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

