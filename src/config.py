"""
Configuration file for workforce projection model.

Define baseline period and projection parameters here.
"""

# Baseline period configuration
BASELINE_YEAR = 2025
BASELINE_MONTH = 3  # March 2025 (annual snapshot month)

# Import financial year conversion function
from utils import calendar_to_financial_year

# Convert baseline year to financial year format (2025 -> '2025/26')
CURRENT_FINANCIAL_YEAR = calendar_to_financial_year(BASELINE_YEAR)  # 2025/26

# Projection parameters
DURATION = 10  # Number of years to project forward
START_PROJECTION_YEAR = 2025  # Year to start projections from