"""
Configuration file for workforce projection model.

Define baseline period and projection parameters here.
"""

# Import libraries
import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt
from utils import calendar_to_financial_year

# Baseline period configuration
BASELINE_YEAR = 2025
BASELINE_MONTH = 3  # March 2025 (annual snapshot month)

# Convert baseline year to financial year format (2025 -> '2025/26')
CURRENT_FINANCIAL_YEAR = calendar_to_financial_year(BASELINE_YEAR)  # 2025/26

# Projection parameters
DURATION = 10  # Number of years to project forward
START_PROJECTION_YEAR = 2025  # Year to start projections from

# Workforce utilisation rate
# Accounts for time off per FTE: 27 days annual leave + 8 days bank holidays + 15 days training/sick leave
UTILISATION_RATE = 0.8077

# Standard FTE working hours per week
FTE_WEEKLY_HOURS = 40

# Pharmacy operations growth rate
OPS_GROWTH_RATE_PCT = 0.1  # 0.1% annual growth rate for pharmacy operations