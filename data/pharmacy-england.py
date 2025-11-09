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
    should be updated to reflect the desired quarter (e.g., 'CONSOL_PHARMACY_LIST_202223Q4').

Note:
    The resource_id format follows: 'CONSOL_PHARMACY_LIST_YYYYQQ' where:
    - YYYY: Financial year start (e.g., 2022 for 2022/23)
    - QQ: Quarter identifier (Q1, Q2, Q3, Q4)
"""

import json
import urllib.request

# API Configuration
# Root URL for the NHSBSA Open Data Portal API
api_root_path = 'https://opendata.nhsbsa.net/api/3/action/datastore_search'

# Dataset Configuration
# Resource ID for the Consolidated Pharmaceutical List dataset
# Format: 'CONSOL_PHARMACY_LIST_YYYYQQ' (e.g., 'CONSOL_PHARMACY_LIST_202223Q4')
# Dataset available at: https://opendata.nhsbsa.net/dataset/consolidated-pharmaceutical-list
resource_id = 'CONSOL_PHARMACY_LIST_202223Q4'

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
# Parse the financial year from the resource_id string format (YYYYQQ)
# Example: '202223Q4' -> '2022/23'
resource_year = resource_id.split('_')[-1][:6]
financial_year = f"{resource_year[:4]}/{resource_year[4:]}"

# Extract and Display Results
# Retrieve the total count of pharmacies from the API response
total_pharmacies = result['result']['total']
print(f"Total number of pharmacies in {financial_year}: {total_pharmacies}")
