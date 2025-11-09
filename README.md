# community-pharmacy-workforce-with-open-data
This workforce projection model supports NHS workforce planning for community pharmacy services, with a focus on two GPhC-regulated professions: pharmacists and pharmacy technicians.

## Folder Structure

```
community-pharmacy-workforce-with-open-data/
├── data/                          # Data files
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
- [GPhC registers data](https://www.pharmacyregulation.org/about-us/publications-and-insights/research-data-and-insights/gphc-registers-data)
    - **Snapshot data**: Annual snapshot data (March) for England from 2018 to 2025
    - **Growth rates**: Compound Annual Growth Rate (CAGR) calculated from 7-year historical data (2018-2025)
    - The model uses the 7-year average annual growth rate (CAGR) to project workforce changes over a 10-year period
