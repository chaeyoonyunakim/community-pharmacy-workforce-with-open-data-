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
│   ├── input-data.py             # Data loading and preprocessing
│   ├── main.py                   # Main entry point for projections
│   ├── project_workforce.py      # Workforce projection functions
│   └── utils.py                  # Utility functions
├── viz/                           # Visualization
│   ├── plot.py                   # Entry point for visualizations
│   ├── visualize-projections.py   # Visualization functions
│   ├── workforce_projection_chart.png
│   └── workforce_projection_combined.png
├── LICENSE
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