"""
Workforce Projection Module

Provides functions for calculating growth rates and projecting workforce changes
for Pharmacist and Pharmacy Technician professions based on actual registration data
for England only.
"""

import config
from input_data import (
    load_registrants_data,
    calculate_annual_growth_rates,
    create_scenarios,
    get_baseline
)
from utils import add_financial_year_column


def _project_scenarios(baseline_value, growth_rate_pct, scenarios, duration):
    """
    Core projection logic shared by supply and ops projections.
    
    Projects a baseline value forward using growth rates adjusted by scenarios.
    
    Args:
        baseline_value: Starting value for projection
        growth_rate_pct: Base growth rate percentage
        scenarios: Dictionary of scenario adjustments (from create_scenarios)
        duration: Number of years to project
    
    Returns:
        dict: Projections by scenario name
    """
    projections = {}
    
    for scenario_name, adjustment in scenarios.items():
        # Adjust growth rate based on scenario
        adjusted_growth_rate = growth_rate_pct * adjustment
        
        # Project year by year starting from baseline period
        current_total = baseline_value
        projection = []
        
        for year in range(duration + 1):
            if year == 0:
                projection.append({
                    'year': config.START_PROJECTION_YEAR + year,
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
                    'year': config.START_PROJECTION_YEAR + year,
                    'total': current_total,
                    'change': change,
                    'scenario': scenario_name
                })
        
        projections[scenario_name] = projection
    
    return projections


def project_workforce_supply(baseline, growth_rates, duration=config.DURATION):
    """
    Project workforce over specified years based on baseline and Compound Annual Growth Rate (CAGR).
    
    Uses the provided baseline values and calculated CAGR (average annual growth rate) to project
    future workforce numbers. The CAGR is applied annually with compounding effects.
    
    Args:
        baseline: Dictionary from get_baseline() with baseline values per profession
        growth_rates: Dictionary from calculate_annual_growth_rates() with CAGR data per profession
        duration: Number of years to project (default: config.DURATION)
    
    Returns:
        dict: Projections by profession and scenario
    """
    scenarios = create_scenarios(growth_rates)
    projections = {}
    
    for profession in growth_rates.keys():
        if profession not in baseline:
            print(f"Warning: No baseline data for {profession}. Skipping projections.")
            continue
        
        rate_data = growth_rates[profession]
        baseline_total = baseline[profession]
        
        # Use shared projection logic
        projections[profession] = _project_scenarios(
            baseline_total,
            rate_data['annual_growth_rate_pct'],
            scenarios,
            duration
        )
    
    return projections


def project_pharmacy_ops(baseline_ops_fte, duration=config.DURATION):
    """
    Project pharmacy operations FTE over specified years based on baseline and fixed growth rate.
    
    Uses the provided baseline workforce operation FTE and applies a fixed annual growth rate (0.1%)
    to project future operations FTE requirements.
    
    Args:
        baseline_ops_fte: Baseline workforce operation FTE (from calculate_workforce_ops_fte)
        duration: Number of years to project (default: config.DURATION)
    
    Returns:
        dict: Projections by scenario with baseline and projected values
    """
    # Use fixed growth rate from config
    growth_rate_pct = config.OPS_GROWTH_RATE_PCT
    
    # Use same scenario creation as supply projections
    # Pass empty dict to get default scenarios (baseline: 1.0, optimistic: 1.2, pessimistic: 0.8)
    scenarios = create_scenarios({})
    
    # Use shared projection logic
    return _project_scenarios(baseline_ops_fte, growth_rate_pct, scenarios, duration)


def format_projections(projections, ops_projections=None):
    """
    Format projections into DataFrames with financial year column.
    
    Handles both supply projections (by profession) and ops projections (by scenario).
    Converts calculated values (5 decimal precision) to integers for display.
    Optionally calculates gap analysis when both supply and ops projections are provided.
    
    Args:
        projections: Dict of projections - either:
            - Supply: {profession: {scenario: [data]}}
            - Ops: {scenario: [data]}
        ops_projections: Optional dict of ops projections. If provided along with supply
            projections, gap analysis will be calculated and returned.
    
    Returns:
        dict or pd.DataFrame: 
            - If ops_projections is None: Formatted DataFrames by profession (supply) or 'ops' key
            - If ops_projections is provided: Gap analysis DataFrame with columns:
              financial_year, scenario, supply, ops, gap
    """
    formatted = {}
    
    # Check if this is ops projections (scenarios at top level) or supply projections (professions at top level)
    # Ops projections have scenario names like 'baseline', 'optimistic', 'pessimistic'
    # Supply projections have profession names like 'Pharmacist', 'Pharmacy Technician'
    first_key = list(projections.keys())[0]
    is_ops = first_key in ['baseline', 'optimistic', 'pessimistic']
    
    if is_ops:
        # Ops projections: {scenario: [data]}
        rows = []
        for scenario_name, data in projections.items():
            for point in data:
                rows.append({
                    'year': point['year'],
                    'total_ops_fte': int(round(point['total'])),
                    'annual_change': int(round(point['change'])),
                    'scenario': scenario_name
                })
        
        df = config.pd.DataFrame(rows)
        # Add financial year column
        df = add_financial_year_column(df)
        formatted['ops'] = df
    else:
        # Supply projections: {profession: {scenario: [data]}}
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
            
            df = config.pd.DataFrame(rows)
            # Add financial year column
            df = add_financial_year_column(df)
            formatted[profession] = df
    
    # If ops_projections is provided, calculate gap analysis
    if ops_projections is not None and not is_ops:
        # ops_projections should already be a formatted dict with 'ops' key
        # If it's a DataFrame, wrap it in a dict
        if isinstance(ops_projections, config.pd.DataFrame):
            ops_df = ops_projections
        elif isinstance(ops_projections, dict) and 'ops' in ops_projections:
            ops_df = ops_projections['ops']
        else:
            # If it's raw projections dict, format it first
            ops_formatted = format_projections(ops_projections)
            ops_df = ops_formatted['ops']
        
        # Combine all supply professions into total supply
        supply_rows = []
        for profession, df in formatted.items():
            for _, row in df.iterrows():
                supply_rows.append({
                    'year': row['year'],
                    'financial_year': row['financial_year'],
                    'scenario': row['scenario'],
                    'total_registrants': row['total_registrants']
                })
        
        # Sum supply by year, financial_year, and scenario
        supply_combined = config.pd.DataFrame(supply_rows)
        supply_total = supply_combined.groupby(['year', 'financial_year', 'scenario'])['total_registrants'].sum().reset_index()
        supply_total.rename(columns={'total_registrants': 'supply'}, inplace=True)
        
        # Prepare ops data
        ops_prepared = ops_df[['year', 'financial_year', 'scenario', 'total_ops_fte']].copy()
        ops_prepared.rename(columns={'total_ops_fte': 'ops'}, inplace=True)
        
        # Merge supply and ops
        gap_df = supply_total.merge(ops_prepared, on=['year', 'financial_year', 'scenario'], how='inner')
        
        # Calculate gap
        gap_df['gap'] = gap_df['supply'] - gap_df['ops']
        
        # Select and order columns, sort by scenario and year
        gap_df = gap_df.sort_values(['scenario', 'year']).reset_index(drop=True)
        
        # Select final columns (keep year for plotting)
        gap_df = gap_df[['year', 'financial_year', 'scenario', 'supply', 'ops', 'gap']].copy()
        
        return gap_df
    
    return formatted