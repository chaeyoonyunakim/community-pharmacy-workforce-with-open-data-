"""
NHS Business Services Authority (NHSBSA) Consolidated Pharmaceutical List Data Extraction.

This module automates the extraction of pharmacy data in England using the NHSBSA Open Data Portal API.
It retrieves the total number of pharmacies and calculates total pharmacy operation hours (open to close)
for all pharmacies in a specified financial year quarter.

The Consolidated Pharmaceutical List includes NHS pharmacies, appliance contractors, and Local
Pharmaceutical Services (LPS) contractors registered in England.

Data Source:
    Consolidated Pharmaceutical List
    https://opendata.nhsbsa.net/dataset/consolidated-pharmaceutical-list

API Documentation:
    https://opendata.nhsbsa.net/pages/api

Usage:
    This script queries the NHSBSA Open Data Portal API to retrieve pharmacy data including
    opening hours for a specified financial year quarter. The resource_id should be updated
    to reflect the desired quarter (e.g., 'CONSOL_PHARMACY_LIST_202526Q1FINAL').

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
import re
from pathlib import Path
import urllib.request

# Add src directory to path to import utility functions
project_root = Path(__file__).parent.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

from utils import calendar_to_financial_year
import config


class DataTransformer:
    """
    Handles data transformation operations.
    
    This class provides methods to transform raw pharmacy data into
    analysis-ready formats with proper validation and cleaning.
    """
    
    # Configuration for time parsing
    TRANSFORM_CONFIG = {
        'time_patterns': {
            'closed_indicators': ['closed', 'n/a', 'na', '', 'none'],
            'single_range': r'(\d{1,2}):(\d{2})-(\d{1,2}):(\d{2})'
        }
    }
    
    def parse_time_string(self, time_string):
        """
        Parse time string into decimal hours.
        
        This method handles the complexity of pharmacy opening hours, which can
        include multiple time ranges, overnight hours, and various formats.
        
        Examples:
        - "09:00-17:00" → 8.0 hours
        - "09:00-12:00,14:00-17:00" → 6.0 hours (split day)
        - "22:00-06:00" → 8.0 hours (overnight)
        - "Closed" → 0.0 hours
        
        Args:
            time_string: Time range string
            
        Returns:
            Decimal hours the pharmacy is open (0.0 if closed or invalid)
        """
        if config.pd.isna(time_string) or time_string is None:
            return 0.0
        
        time_string = str(time_string).strip()
        
        # Handle closed or empty cases
        if time_string.lower() in self.TRANSFORM_CONFIG['time_patterns']['closed_indicators']:
            return 0.0
        
        # Handle multiple time ranges (split days)
        if ',' in time_string:
            total_hours = 0.0
            for time_range in time_string.split(','):
                total_hours += self._parse_single_time_range(time_range.strip())
            return total_hours
        
        return self._parse_single_time_range(time_string)
    
    def _parse_single_time_range(self, time_range):
        """
        Parse a single time range and return hours.
        
        This helper method handles the core logic of converting time strings
        to decimal hours, including overnight periods.
        
        Args:
            time_range: Single time range like "09:00-17:00"
            
        Returns:
            Decimal hours for this time range
        """
        try:
            time_pattern = self.TRANSFORM_CONFIG['time_patterns']['single_range']
            match = re.match(time_pattern, time_range.strip())
            
            if match:
                start_hour, start_min, end_hour, end_min = map(int, match.groups())
                
                # Convert to minutes for easier calculation
                start_minutes = start_hour * 60 + start_min
                end_minutes = end_hour * 60 + end_min
                
                # Handle overnight hours (e.g., 22:00-06:00)
                if end_minutes < start_minutes:
                    end_minutes += 24 * 60  # Add 24 hours
                
                total_minutes = end_minutes - start_minutes
                return total_minutes / 60.0
            
            return 0.0
            
        except (ValueError, AttributeError):
            return 0.0
    
    def calculate_weekly_hours(self, df):
        """
        Calculate weekly opening hours for each pharmacy.
        
        This method processes all daily opening hour columns and sums them
        to create a comprehensive weekly total. It handles missing data
        gracefully.
        
        Args:
            df: Raw pharmacy data from the API
            
        Returns:
            DataFrame with added weekly hours calculations
        """
        if df.empty:
            return df
        
        df_processed = df.copy()
        
        # Find all opening hours columns
        opening_hours_columns = [
            col for col in df_processed.columns 
            if col.startswith('PHARMACY_OPENING_HOURS_')
        ]
        
        if not opening_hours_columns:
            print("Warning: No opening hours columns found in data")
            return df_processed
        
        # Process each day's hours
        daily_hours = {}
        for column in opening_hours_columns:
            day_name = column.replace('PHARMACY_OPENING_HOURS_', '')
            hours_column_name = f'{day_name}_CALCULATED_HOURS'
            
            df_processed[hours_column_name] = df_processed[column].apply(self.parse_time_string)
            daily_hours[day_name] = hours_column_name
        
        # Calculate total weekly hours
        df_processed['weekly_hours'] = sum(df_processed[col] for col in daily_hours.values())
        
        return df_processed


def fetch_all_pharmacy_data(resource_id, api_root_path):
    """
    Fetch all pharmacy records from the NHSBSA API.
    
    The API has a limit per request, so this function handles pagination
    to retrieve all records.
    
    Args:
        resource_id: Resource ID for the dataset
        api_root_path: Base API URL
        
    Returns:
        List of all pharmacy records
    """
    all_records = []
    limit = 32000  # Maximum records per request
    offset = 0
    
    while True:
        api_request = f'{api_root_path}?resource_id={resource_id}&limit={limit}&offset={offset}'
        
        with urllib.request.urlopen(api_request) as response:
            if response.status == 200:
                data = response.read().decode('utf-8')
                result = json.loads(data)
                
                records = result['result']['records']
                if not records:
                    break
                
                all_records.extend(records)
                offset += len(records)
                
                # Check if we've retrieved all records
                if len(records) < limit:
                    break
            else:
                print(f"Error: API returned status code {response.status}")
                break
    
    return all_records


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

# Extract Financial Year
# Parse the calendar year from the resource_id string format (YYYYQQ or YYYYQQFINAL)
# The first 4 digits represent the calendar year that starts the financial year
# This works for both formats: 'CONSOL_PHARMACY_LIST_202223Q4' and 'CONSOL_PHARMACY_LIST_202526Q1FINAL'
# Example: '202526Q1FINAL' -> extract '2025' -> convert to '2025/26'
resource_year_str = resource_id.split('_')[-1][:4]
calendar_year = int(resource_year_str)
financial_year = calendar_to_financial_year(calendar_year)

# Fetch all pharmacy data
all_records = fetch_all_pharmacy_data(resource_id, api_root_path)

if not all_records:
    print("No pharmacy records found.")
    sys.exit(1)

# Convert to DataFrame
df = config.pd.DataFrame(all_records)

# Calculate weekly hours for each pharmacy
transformer = DataTransformer()
df_with_hours = transformer.calculate_weekly_hours(df)

# Calculate total operation hours across all pharmacies
if 'weekly_hours' in df_with_hours.columns:
    total_pharmacies = len(df_with_hours)
    total_weekly_hours = df_with_hours['weekly_hours'].sum()
    average_weekly_hours = df_with_hours['weekly_hours'].mean()
    
    print(f"\nTotal number of pharmacies in {financial_year}: {total_pharmacies:,}")
    print(f"Total pharmacy operation hours (weekly) in {financial_year}: {total_weekly_hours:,.2f} hours")
    print(f"Average weekly hours per pharmacy: {average_weekly_hours:.2f} hours")
else:
    print("Warning: Could not calculate weekly hours. Opening hours columns may not be present in the dataset.")
