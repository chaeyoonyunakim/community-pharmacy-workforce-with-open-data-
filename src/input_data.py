"""
Input data loading and preprocessing functions.

Handles reading CSV files and preprocessing data for workforce projections.
"""

from utils import get_data_dir
from config import BASELINE_YEAR, BASELINE_MONTH, pd, sys, Path


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


def get_baseline_from_gphc(data_dir=None, filename='gphc-total-number-of-pharmacy-registrants.csv'):
    """
    Extract baseline data from GPhC registrants CSV file.
    
    Extracts baseline values for March of the baseline year from the GPhC data.
    Returns values in consistent format: baseline_pharmacists and baseline_technicians.
    
    Args:
        data_dir: Optional data directory path. If None, uses default project structure.
        filename: Name of the CSV file to load
    
    Returns:
        dict: Dictionary with keys 'baseline_pharmacists' and 'baseline_technicians'
    """
    # Load registrants data filtered for baseline year and month
    df = load_registrants_data(data_dir, filename)
    
    # Filter for baseline year
    df = df[df['year'] == BASELINE_YEAR].copy()
    
    # Extract baseline values by profession
    baseline_data = {}
    for profession in df['profession'].unique():
        profession_df = df[df['profession'] == profession]
        if not profession_df.empty:
            baseline_value = int(profession_df['registrants'].values[0])
            # Map profession names to consistent variable names
            if 'Pharmacist' in profession:
                baseline_data['baseline_pharmacists'] = baseline_value
            elif 'Pharmacy Technician' in profession or 'Technician' in profession:
                baseline_data['baseline_technicians'] = baseline_value
    
    return baseline_data


def get_baseline_from_cpws():
    """
    Load baseline data from CPWS configuration file.
    
    Imports baseline_pharmacists and baseline_technicians from data/cpws.py.
    Returns values in consistent format.
    
    Returns:
        dict: Dictionary with keys 'baseline_pharmacists' and 'baseline_technicians'
    """
    # Add data directory to path to import cpws module
    project_root = Path(__file__).parent.parent
    data_dir = project_root / 'data'
    sys.path.insert(0, str(data_dir))
    
    import cpws
    baseline_data = {
        'baseline_pharmacists': cpws.baseline_pharmacists,
        'baseline_technicians': cpws.baseline_technicians
    }
    return baseline_data


def get_baseline(source='cpws', data_dir=None):
    """
    Get baseline workforce data per profession.
    
    Retrieves baseline values from either CPWS (default) or GPhC data source.
    Returns baseline values in a consistent format per profession.
    
    Args:
        source: Data source selection - 'cpws' (default) or 'gphc'
        data_dir: Optional data directory path for GPhC CSV (only used if source='gphc')
    
    Returns:
        dict: Baseline data by profession with keys:
            - 'Pharmacist': baseline value
            - 'Pharmacy Technician': baseline value
    
    Raises:
        ValueError: If source is not 'cpws' or 'gphc'
    """
    # Select baseline data source
    if source.lower() == 'cpws':
        baseline_dict = get_baseline_from_cpws()
    elif source.lower() == 'gphc':
        baseline_dict = get_baseline_from_gphc(data_dir)
    else:
        raise ValueError(f"Invalid source '{source}'. Must be 'cpws' or 'gphc'")
    
    # Map to profession names used in the data
    baseline_data = {}
    if 'baseline_pharmacists' in baseline_dict:
        baseline_data['Pharmacist'] = baseline_dict['baseline_pharmacists']
    if 'baseline_technicians' in baseline_dict:
        baseline_data['Pharmacy Technician'] = baseline_dict['baseline_technicians']
    
    return baseline_data


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
