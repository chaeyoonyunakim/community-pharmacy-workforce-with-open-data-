"""
Workforce Projection Module

Provides functions for calculating growth rates and projecting workforce changes
for Pharmacist and Pharmacy Technician professions based on actual registration data
for England only.
"""

import pandas as pd
from config import (
    DURATION, START_PROJECTION_YEAR
)
from input_data import (
    load_registrants_data,
    calculate_annual_growth_rates,
    create_scenarios
)
from utils import add_financial_year_column


def load_registration_data(data_dir=None):
    """Load registration data from CSV files."""
    return load_registrants_data(data_dir)


def project_workforce(rates, duration=DURATION):
    """
    Project workforce over specified years based on Compound Annual Growth Rate (CAGR).
    
    Uses the calculated CAGR (average annual growth rate) to project future workforce
    numbers. The CAGR is applied annually with compounding effects.
    
    Args:
        rates: Dictionary from calculate_annual_growth_rates() with CAGR data
        duration: Number of years to project (default: DURATION from config)
    
    Returns:
        dict: Projections by profession and scenario
    """
    scenarios = create_scenarios(rates)
    
    projections = {}
    
    for profession, rate_data in rates.items():
        projections[profession] = {}
        
        for scenario_name, adjustment in scenarios.items():
            # Adjust growth rate based on scenario
            adjusted_growth_rate = rate_data['annual_growth_rate_pct'] * adjustment
            
            # Project year by year starting from baseline period (baseline_year = current_year)
            current_total = rate_data['baseline_total']
            projection = []
            
            for year in range(duration + 1):
                if year == 0:
                    projection.append({
                        'year': START_PROJECTION_YEAR + year,
                        'total': current_total,
                        'change': 0,
                        'scenario': scenario_name
                    })
                else:
                    # Apply compound annual growth rate
                    # Keep precision to 5 decimal places during calculation
                    change = round(current_total * (adjusted_growth_rate / 100), 5)
                    current_total = round(current_total + change, 5)
                    projection.append({
                        'year': START_PROJECTION_YEAR + year,
                        'total': current_total,
                        'change': change,
                        'scenario': scenario_name
                    })
            
            projections[profession][scenario_name] = projection
    
    return projections


def format_projections(projections):
    """
    Format projections into DataFrames with financial year column.
    
    Converts calculated values (5 decimal precision) to integers for display.
    """
    formatted = {}
    
    for profession, scenarios in projections.items():
        rows = []
        for scenario_name, data in scenarios.items():
            for point in data:
                rows.append({
                    'profession': profession,
                    'year': point['year'],
                    'total_registrants': int(round(point['total'])),
                    'annual_change': int(round(point['change'])),
                    'scenario': scenario_name
                })
        
        df = pd.DataFrame(rows)
        # Add financial year column
        df = add_financial_year_column(df)
        formatted[profession] = df
    
    return formatted

