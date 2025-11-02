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
    - actuals: September 2025
    - estimates: March and June 2025 registrant counts are derived by applying monthly average rates to the 9-month joiners/leavers totals (through September 2025), with March representing 3 months of change and June representing 6 months of change.
