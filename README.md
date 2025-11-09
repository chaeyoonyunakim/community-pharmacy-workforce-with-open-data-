# community-pharmacy-workforce-with-open-data
This workforce projection model supports NHS workforce planning for community pharmacy services, with a focus on two GPhC-regulated professions: pharmacists and pharmacy technicians.

## Folder Structure

```
community-pharmacy-workforce-with-open-data/
├── data/                          # Data files
│   ├── cpws.py
│   ├── gphc-total-number-of-pharmacy-registrants.csv
│   ├── gphc-registrants-joiners.csv
│   └── gphc-registrants-leavers.csv
├── src/                           # Source code
│   ├── config.py                 # Configuration settings
│   ├── input_data.py              # Data loading and preprocessing
│   ├── main.py                    # Main entry point for projections
│   ├── project_workforce.py      # Workforce projection functions
│   ├── utils.py                   # Utility functions
│   └── visualize_projections.py   # Visualization functions
├── LICENSE
├── workforce_projection_chart.png # Generated visualization output
├── README.md
└── requirements.txt

```

## Data sources
- Baseline: [Community Pharmacy Workforce Survey (CPWS)](https://www.data.gov.uk/dataset/09aa8f38-547a-46b7-a117-2cb710ad939b/)
    - **Unit**: Both Headcount and Full-time equivalent (FTE) figures are available
    - **Care setting**: High-street pharmacies only
    - **Survey data**: CPWS 2024 published on 27 June 2025
- Growth rates: [GPhC registers data](https://www.pharmacyregulation.org/about-us/publications-and-insights/research-data-and-insights/gphc-registers-data)
    - **Unit**: Headcount only (total number of registered professionals)
    - **Care setting**: All (Hospital, Community, Primary care, and Pharmacy sector)
    - **Snapshot data**: Annual snapshot data (March) for England from 2018 to 2025
    - **Growth rates**: Compound Annual Growth Rate (CAGR) calculated from 7-year historical data (2018-2025)
- Pharmacy operation hours: [NHSBSA Consolidated Pharmaceutical List](https://opendata.nhsbsa.net/dataset/consolidated-pharmaceutical-list)
    - **Data**: Total number of pharmacies and opening hours in England, available by financial year quarter (e.g., 2025/26 Q1)
    - **Care setting**: All NHS pharmacies, appliance contractors, and Local Pharmaceutical Services (LPS) contractors
    - **Example output (2025/26 Q1)**: 
        - Total number of pharmacies: 10,525
        - Total pharmacy operation hours (weekly): 546,264.13 hours
        - Average weekly hours per pharmacy: 51.92 hours

### Example Output

The model generates workforce projections and visualizations:

![Workforce Projection Chart](workforce_projection_chart.png)

The visualization shows 10-year projections for both Pharmacist and Pharmacy Technician professions across three scenarios (baseline, optimistic, pessimistic) based on CPWS baseline data and GPhC growth rates.

```
============================================================
Baseline and Annual Growth Rates (CAGR)
============================================================
Growth Rate Calculation Period: 7 year(s) (2018-2025)
Projection Period: 10 years
Note: Annual Growth Rate = Compound Annual Growth Rate (CAGR)

Pharmacist:
  Baseline: 18,926.58922
  CAGR (Average Annual Growth Rate): 2.80%
  Annual Change Estimate: 1,399 registrants/year
Pharmacy Technician:
  Baseline: 4,290.735455
  CAGR (Average Annual Growth Rate): 2.00%
  Annual Change Estimate: 414 registrants/year
============================================================
```