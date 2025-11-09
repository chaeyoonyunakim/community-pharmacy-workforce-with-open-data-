"""
Community Pharmacy Workforce Survey (CPWS) Baseline Data Configuration.

This module provides examples for setting baseline workforce data for the
workforce projection model using data from the Community Pharmacy Workforce Survey.

The CPWS is published by Health Education England (HEE) and provides comprehensive
workforce data for community pharmacy services across England, including full-time
equivalent (FTE) counts for pharmacists and pharmacy technicians by region.

Data Source:
    Community Pharmacy Workforce Survey
    https://www.data.gov.uk/dataset/09aa8f38-547a-46b7-a117-2cb710ad939b/
    https://www.hee.nhs.uk/our-work/pharmacy/community-pharmacy-workforce-survey

Usage:
    This module demonstrates two approaches for setting baseline data:
    1. Database query method (when CPWS data is available in a database)
    2. Manual configuration method (when using extracted data files)

Note:
    Baseline values should reflect the most recent available CPWS data and
    align with the financial year used in the projection model configuration.
"""

# Database Query Method
# If CPWS data is available in a database, use this SQL query to retrieve
# aggregated baseline workforce data by NHS region.

# Note: This query aggregates data at regional level.
sql_query = """
    SELECT ref.[Region] AS [region]
    , SUM(cpws.[All-PHARMACISTS_FTE]) AS [baseline_pharmacists]
    , SUM(cpws.[ALL-Pharmacy Technicians_FTE]) AS [baseline_technicians]
    FROM
        [Pharmacy].[dbo].[Community_Pharmacy] AS cpws
    JOIN
        [Pharmacy].[dbo].[mapping pharmacy_ICB] AS ref ON cpws.[ICB_Name] = ref.[ICB]
    WHERE
        cpws.[Year] = 2024
    GROUP BY
        ref.[Region];
"""

# Manual Configuration Method
# If database access is not available, set baseline values manually using
# data extracted from CPWS Excel files or other published sources.

# Note: These values represent aggregated FTE counts at national level.
baseline_pharmacists = 18926.58922
baseline_technicians = 4290.735455
