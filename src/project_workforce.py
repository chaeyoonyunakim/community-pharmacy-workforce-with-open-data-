"""
Workforce Projection Module

Provides functions for calculating growth rates and projecting workforce changes
for Pharmacist and Pharmacy professions based on actual registration data.
"""

import pandas as pd
from config import (
    BASELINE_YEAR, BASELINE_MONTH,
    CURRENT_YEAR, CURRENT_MONTH,
    PROJECTION_YEARS, START_PROJECTION_YEAR,
    SCENARIOS
)
from input_data import load_registrants_data


def load_registration_data(data_dir=None):
    """Load registration data from CSV files."""
    return load_registrants_data(data_dir)


def calculate_annual_growth_rates(total_df):
    """Calculate annual growth rates from actual registrant data."""
    data = {}
    
    # Get profession names dynamically from the data
    professions = total_df['profession'].unique()
    
    # Calculate months elapsed from config
    months_per_year = 12
    if BASELINE_YEAR == CURRENT_YEAR:
        months_elapsed = CURRENT_MONTH - BASELINE_MONTH
    else:
        months_elapsed = (12 - BASELINE_MONTH) + ((CURRENT_YEAR - BASELINE_YEAR - 1) * 12) + CURRENT_MONTH
    
    for profession in professions:
        profession_df = total_df[total_df['profession'] == profession].copy()
        profession_df = profession_df.sort_values(['year', 'month'])
        
        # Get baseline and current periods from config
        baseline = profession_df[(profession_df['year'] == BASELINE_YEAR) & (profession_df['month'] == BASELINE_MONTH)]
        current = profession_df[(profession_df['year'] == CURRENT_YEAR) & (profession_df['month'] == CURRENT_MONTH)]
        
        if baseline.empty or current.empty:
            print(f"Warning: Missing data for {profession}")
            print(f"  Looking for baseline: {BASELINE_YEAR}-{BASELINE_MONTH:02d}, current: {CURRENT_YEAR}-{CURRENT_MONTH:02d}")
            continue
        
        start_total = int(baseline['registrants'].values[0])
        end_total = int(current['registrants'].values[0])
        
        # Calculate growth from baseline to current period
        # Annualize: ((end/start)^(12/months_elapsed) - 1) * 100
        growth_factor = end_total / start_total
        annual_growth_rate_pct = ((growth_factor ** (months_per_year / months_elapsed)) - 1) * 100
        
        # Calculate absolute change over the period
        change_period = end_total - start_total
        annual_change_estimate = (change_period / months_elapsed) * months_per_year
        
        data[profession] = {
            'baseline_total': start_total,
            'current_total': end_total,
            'annual_growth_rate_pct': round(annual_growth_rate_pct, 2),
            'annual_change_estimate': round(annual_change_estimate, 1),
            'change_period': change_period,
            'months_elapsed': months_elapsed
        }
    
    return data


def project_workforce(rates, years=None, scenarios=None):
    """
    Project workforce over specified years based on annual growth rates.
    
    scenarios: dict with scenario names and rate adjustments
    e.g., {'baseline': 1.0, 'growth': 1.1, 'decline': 0.9}
    """
    if years is None:
        years = PROJECTION_YEARS
    if scenarios is None:
        scenarios = SCENARIOS
    
    projections = {}
    
    for profession, rate_data in rates.items():
        projections[profession] = {}
        
        for scenario_name, adjustment in scenarios.items():
            # Adjust growth rate based on scenario
            adjusted_growth_rate = rate_data['annual_growth_rate_pct'] * adjustment
            
            # Project year by year starting from current period (treated as projection baseline)
            current_total = rate_data['current_total']
            projection = []
            
            for year in range(years + 1):
                if year == 0:
                    projection.append({
                        'year': START_PROJECTION_YEAR + year,
                        'total': current_total,
                        'change': 0,
                        'scenario': scenario_name
                    })
                else:
                    # Apply compound annual growth rate
                    change = current_total * (adjusted_growth_rate / 100)
                    current_total = current_total + change
                    projection.append({
                        'year': START_PROJECTION_YEAR + year,
                        'total': round(current_total),
                        'change': round(change),
                        'scenario': scenario_name
                    })
            
            projections[profession][scenario_name] = projection
    
    return projections


def format_projections(projections):
    """Format projections into DataFrames for easy export."""
    formatted = {}
    
    for profession, scenarios in projections.items():
        rows = []
        for scenario_name, data in scenarios.items():
            for point in data:
                rows.append({
                    'profession': profession,
                    'year': point['year'],
                    'total_registrants': point['total'],
                    'annual_change': point['change'],
                    'scenario': scenario_name
                })
        
        formatted[profession] = pd.DataFrame(rows)
    
    return formatted

