"""
Main entry point for workforce projection script.

Projects workforce changes for Pharmacist and Pharmacy Technician professions
based on actual registration data for England (total registrants over time).

Usage:
    python main.py
"""

from config import DURATION, BASELINE_YEAR
from project_workforce import (
    load_registration_data,
    calculate_annual_growth_rates,
    project_workforce,
    format_projections
)


def main():
    """Main execution function."""
    total_df = load_registration_data()
    rates = calculate_annual_growth_rates(total_df)
    
    print("\n" + "="*60)
    print("Baseline and Annual Growth Rates (CAGR)")
    print("="*60)
    print(f"Growth Rate Calculation Period: {list(rates.values())[0]['years_elapsed']} year(s) (2018-2025)")
    print(f"Projection Period: {DURATION} years")
    print("Note: Annual Growth Rate = Compound Annual Growth Rate (CAGR)")
    print()
    for profession, rate_data in rates.items():
        print(f"{profession}:")
        print(f"  Baseline (March {BASELINE_YEAR}): {rate_data['baseline_total']:,} registrants")
        print(f"  CAGR (Average Annual Growth Rate): {rate_data['annual_growth_rate_pct']:.2f}%")
        print(f"  Annual Change Estimate: {rate_data['annual_change_estimate']:,.0f} registrants/year")
    print("="*60 + "\n")
    
    print(f"Creating {DURATION}-year projections...")
    projections = project_workforce(rates)
    
    print("Formatting projections...")
    projections_df = format_projections(projections)
    
    print("\n✅ Projection complete!")


if __name__ == '__main__':
    main()

