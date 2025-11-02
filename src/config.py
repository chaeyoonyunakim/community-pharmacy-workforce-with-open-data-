"""
Configuration file for workforce projection model.

Define baseline period and projection parameters here.
"""

# Baseline period configuration
BASELINE_YEAR = 2025
BASELINE_MONTH = 3  # March 2025

# Current period configuration (for calculating growth rates)
CURRENT_YEAR = 2025
CURRENT_MONTH = 9  # September 2025

# Projection parameters
PROJECTION_YEARS = 10  # Number of years to project forward
START_PROJECTION_YEAR = 2025  # Year to start projections from

# Scenario adjustments
SCENARIOS = {
    'baseline': 1.0,  # Current trend continues
    'optimistic': 1.2,  # 20% higher growth rate
    'pessimistic': 0.8  # 20% lower growth rate
}

