"""
Main entry point for workforce projection script.

Projects workforce changes for Pharmacist and Pharmacy Technician professions
based on actual registration data for England (total registrants over time).

Usage:
    python main.py [scenario]
    
    scenario: Optional. One of 'baseline', 'optimistic', or 'pessimistic'. 
              Default is 'baseline'.
"""

import config
import sys
from input_data import (
    get_baseline_supply,
    load_registrants_data,
    calculate_annual_growth_rates,
    calculate_workforce_ops_fte
)
from project_workforce import (
    project_workforce_supply,
    project_pharmacy_ops,
    format_projections
)
from visualize_projections import create_visualizations


def main(scenario='baseline'):
    """Main execution function.
    
    Args:
        scenario: Scenario to display ('baseline', 'optimistic', or 'pessimistic'). Default is 'baseline'.
    
    Returns:
        pd.DataFrame: Gap analysis DataFrame with columns: financial_year, scenario, supply, ops, gap
    """
    # Validate scenario
    valid_scenarios = ['baseline', 'optimistic', 'pessimistic']
    if scenario not in valid_scenarios:
        raise ValueError(f"Scenario must be one of {valid_scenarios}, got '{scenario}'")
    
    # Get CPWS data
    baseline = get_baseline_supply(source='cpws')
    
    # Calculate growth rates from GPhC historical data
    total_df = load_registrants_data()
    growth_rates = calculate_annual_growth_rates(total_df)
    
    # Calculate pharmacy operations baseline (from NHSBSA data)
    # Values from 2025/26 Q1: average_weekly_hours=51.92, total_pharmacies=10525
    average_weekly_hours = 51.92
    total_pharmacies = 10525
    baseline_ops_fte = calculate_workforce_ops_fte(average_weekly_hours, total_pharmacies)
    
    # Project supply
    supply_projections = project_workforce_supply(baseline, growth_rates)
    
    # Project ops
    ops_projections = project_pharmacy_ops(baseline_ops_fte)
    ops_projections_df = format_projections(ops_projections)
    
    # Format supply projections and calculate gap analysis
    gap_analysis_df = format_projections(supply_projections, ops_projections_df)
    
    # Filter to selected scenario
    scenario_df = gap_analysis_df[gap_analysis_df['scenario'] == scenario].copy()
    
    # Create visualizations (only for selected scenario)
    create_visualizations(scenario_df, baseline_source='cpws')
    
    # Print filtered results
    print(scenario_df)
    
    return scenario_df

if __name__ == '__main__':
    # Allow scenario selection via command-line argument
    scenario = 'baseline'  # default
    if len(sys.argv) > 1:
        scenario = sys.argv[1].lower()
    
    main(scenario=scenario)

