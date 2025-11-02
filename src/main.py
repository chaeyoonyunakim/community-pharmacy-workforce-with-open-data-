"""
Main entry point for workforce projection script.

Projects workforce changes for Pharmacist and Pharmacy professions
based on actual registration data (total registrants over time).

Usage:
    python main.py
"""

from config import PROJECTION_YEARS
from project_workforce import (
    load_registration_data,
    calculate_annual_growth_rates,
    project_workforce,
    format_projections
)


def main():
    """Main execution function."""
    print("Loading registration data...")
    total_df = load_registration_data()
    
    print("Calculating annual growth rates from actual data...")
    rates = calculate_annual_growth_rates(total_df)
    
    print(f"Creating {PROJECTION_YEARS}-year projections...")
    projections = project_workforce(rates, years=PROJECTION_YEARS)
    
    print("Formatting projections...")
    projections_df = format_projections(projections)
    
    print("\n✅ Projection complete!")


if __name__ == '__main__':
    main()

