"""
NHS Business Services Authority (NHSBSA) Consolidated Pharmaceutical List Data Extraction.

This module automates the extraction of the total number of pharmacies in England
using the NHSBSA Open Data Portal API. The Consolidated Pharmaceutical List includes
NHS pharmacies, appliance contractors, and Local Pharmaceutical Services (LPS)
contractors registered in England.

Data Source:
    Consolidated Pharmaceutical List
    https://opendata.nhsbsa.net/dataset/consolidated-pharmaceutical-list

API Documentation:
    https://opendata.nhsbsa.net/pages/api

Usage:
    This script queries the NHSBSA Open Data Portal API to retrieve the total
    count of pharmacies for a specified financial year quarter. The resource_id
    should be updated to reflect the desired quarter (e.g., 'CONSOL_PHARMACY_LIST_202526Q1FINAL').

Note:
    The resource_id format follows: 'CONSOL_PHARMACY_LIST_YYYYQQ' or 
    'CONSOL_PHARMACY_LIST_YYYYQQFINAL' where:
    - YYYY: Financial year start (e.g., 2025 for 2025/26)
    - QQ: Quarter identifier (Q1, Q2, Q3, Q4)
    - FINAL: Optional suffix indicating finalised data (e.g., 'CONSOL_PHARMACY_LIST_202526Q1FINAL')
    
    Resource ID name variations exist - some datasets include the 'FINAL' suffix
    while others do not. Both formats are valid and should be checked in the
    NHSBSA Open Data Portal for the specific dataset version.
"""

import json
import sys
from pathlib import Path
import urllib.request

# Add src directory to path to import utility functions
project_root = Path(__file__).parent.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

from utils import calendar_to_financial_year

# API Configuration
# Root URL for the NHSBSA Open Data Portal API
api_root_path = 'https://opendata.nhsbsa.net/api/3/action/datastore_search'

# Dataset Configuration
# Resource ID for the Consolidated Pharmaceutical List dataset
# Format: 'CONSOL_PHARMACY_LIST_YYYYQQ' or 'CONSOL_PHARMACY_LIST_YYYYQQFINAL'
# Examples: 'CONSOL_PHARMACY_LIST_202526Q1FINAL' (2025/26 Q1) or 'CONSOL_PHARMACY_LIST_202223Q4' (2022/23 Q4)
# Note: Some resource IDs include a 'FINAL' suffix, while others do not
# Dataset available at: https://opendata.nhsbsa.net/dataset/consolidated-pharmaceutical-list
resource_id = 'CONSOL_PHARMACY_LIST_202526Q1FINAL'

# Query Parameters
# Setting 'limit' to 0 retrieves only the total count without individual records,
# which is more efficient when only the aggregate count is required
params = {
    'resource_id': resource_id,
    'limit': 0,
}

# API Request
# Construct the full API request URL with query parameters
api_request = f'{api_root_path}?resource_id={params["resource_id"]}&limit={params["limit"]}'

# Execute API Request
with urllib.request.urlopen(api_request) as response:
    # Validate successful response (HTTP status code 200)
    if response.status == 200:
        data = response.read().decode('utf-8')
        result = json.loads(data)

# Extract Financial Year
# Parse the calendar year from the resource_id string format (YYYYQQ or YYYYQQFINAL)
# The first 4 digits represent the calendar year that starts the financial year
# This works for both formats: 'CONSOL_PHARMACY_LIST_202223Q4' and 'CONSOL_PHARMACY_LIST_202526Q1FINAL'
# Example: '202526Q1FINAL' -> extract '2025' -> convert to '2025/26'
resource_year_str = resource_id.split('_')[-1][:4]
calendar_year = int(resource_year_str)
financial_year = calendar_to_financial_year(calendar_year)

# Extract and Display Results
# Retrieve the total count of pharmacies from the API response
total_pharmacies = result['result']['total']
print(f"Total number of pharmacies in {financial_year}: {total_pharmacies}")
