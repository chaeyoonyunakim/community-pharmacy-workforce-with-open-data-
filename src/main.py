"""
Main entry point for workforce projection script.

Projects workforce changes for Pharmacist and Pharmacy Technician professions
based on actual registration data for England (total registrants over time).

Usage:
    python main.py
"""

import config
from project_workforce import (
    load_registration_data,
    calculate_annual_growth_rates,
    get_baseline,
    project_workforce,
    format_projections
)


def main():
    """Main execution function."""
    # Get CPWS data
    baseline = get_baseline(source='cpws')
    
    # Calculate growth rates from GPhC historical data
    total_df = load_registration_data()
    growth_rates = calculate_annual_growth_rates(total_df)
    
    print("\n" + "="*60)
    print("Baseline and Annual Growth Rates (CAGR)")
    print("="*60)
    print(f"Growth Rate Calculation Period: {list(growth_rates.values())[0]['years_elapsed']} year(s) (2018-2025)")
    print(f"Projection Period: {config.DURATION} years")
    print("Note: Annual Growth Rate = Compound Annual Growth Rate (CAGR)")
    print()
    for profession in growth_rates.keys():
        if profession in baseline:
            print(f"{profession}:")
            print(f"  Baseline: {baseline[profession]:,}")
            print(f"  CAGR (Average Annual Growth Rate): {growth_rates[profession]['annual_growth_rate_pct']:.2f}%")
            print(f"  Annual Change Estimate: {growth_rates[profession]['annual_change_estimate']:,.0f} registrants/year")
    print("="*60 + "\n")
    
    print(f"Creating {config.DURATION}-year projections...")
    projections = project_workforce(baseline, growth_rates)
    
    print("Formatting projections...")
    projections_df = format_projections(projections)
    
    print("\n✅ Projection complete!")


if __name__ == '__main__':
    main()

