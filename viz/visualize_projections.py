"""
Visualize Workforce Projections Module

Provides functions for creating charts for workforce projections based on annual growth rates
calculated from actual registrant data.
"""

import sys
from pathlib import Path
import pandas as pd
import matplotlib.pyplot as plt

# Add src directory to path to import modules
script_dir = Path(__file__).parent
project_root = script_dir.parent
src_dir = project_root / 'src'
sys.path.insert(0, str(src_dir))

from config import PROJECTION_YEARS, START_PROJECTION_YEAR
from project_workforce import (
    load_registration_data,
    calculate_annual_growth_rates,
    project_workforce,
    format_projections
)


def create_visualizations(output_dir=None):
    """Create visualization charts for projections."""
    # Default to viz folder for output
    if output_dir is None:
        output_dir = script_dir
    else:
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Generate projections data
    print("Loading registration data...")
    total_df = load_registration_data()
    
    print("Calculating annual growth rates...")
    rates = calculate_annual_growth_rates(total_df)
    
    print(f"Creating {PROJECTION_YEARS}-year projections...")
    projections = project_workforce(rates, years=PROJECTION_YEARS)
    
    print("Formatting projections...")
    projections_df = format_projections(projections)
    
    # Combine all profession dataframes into one
    df = pd.concat(projections_df.values(), ignore_index=True)
    
    # Get unique professions dynamically
    professions = df['profession'].unique()
    num_professions = len(professions)
    
    # Create figure with subplots (one per profession)
    end_year = START_PROJECTION_YEAR + PROJECTION_YEARS
    fig, axes = plt.subplots(num_professions, 1, figsize=(12, 6 * num_professions))
    if num_professions == 1:
        axes = [axes]  # Make it iterable if only one profession
    fig.suptitle(f'{PROJECTION_YEARS}-Year Workforce Projection ({START_PROJECTION_YEAR}-{end_year})', 
                 fontsize=16, fontweight='bold')
    
    scenarios = ['baseline', 'optimistic', 'pessimistic']
    colors = {'baseline': '#1f77b4', 'optimistic': '#2ca02c', 'pessimistic': '#d62728'}
    
    # Plot each profession
    for idx, profession in enumerate(professions):
        ax = axes[idx]
        for scenario in scenarios:
            data = df[(df['profession'] == profession) & (df['scenario'] == scenario)]
            ax.plot(data['year'], data['total_registrants'], 
                    marker='o', label=scenario.capitalize(), 
                    color=colors[scenario], linewidth=2, markersize=4)
        
        ax.set_title(f'{profession} Workforce Projection', fontsize=12, fontweight='bold')
        ax.set_xlabel('Year')
        ax.set_ylabel('Number of Registrants')
        ax.legend()
        ax.grid(True, alpha=0.3)
        ax.set_xlim(START_PROJECTION_YEAR - 1, end_year + 1)
    
    plt.tight_layout()
    
    # Save figure
    output_path = output_dir / 'workforce_projection_chart.png'
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved visualization: {output_path}")
    
    # Create combined comparison chart
    fig2, ax = plt.subplots(figsize=(12, 6))
    
    # Get professions dynamically
    professions = df['profession'].unique()
    
    for profession in professions:
        for scenario in scenarios:
            data = df[(df['profession'] == profession) & (df['scenario'] == scenario)]
            label = f"{profession} - {scenario.capitalize()}"
            linestyle = '-' if scenario == 'baseline' else ('--' if scenario == 'optimistic' else ':')
            ax.plot(data['year'], data['total_registrants'], 
                   marker='o', label=label, linewidth=2, markersize=3, linestyle=linestyle)
    
    ax.set_title(f'{PROJECTION_YEARS}-Year Workforce Projection: All Professions and Scenarios', 
                 fontsize=14, fontweight='bold')
    ax.set_xlabel('Year')
    ax.set_ylabel('Number of Registrants')
    ax.legend(loc='upper left', fontsize=9)
    ax.grid(True, alpha=0.3)
    ax.set_xlim(START_PROJECTION_YEAR - 1, end_year + 1)
    
    plt.tight_layout()
    
    combined_path = output_dir / 'workforce_projection_combined.png'
    plt.savefig(combined_path, dpi=300, bbox_inches='tight')
    print(f"✓ Saved combined visualization: {combined_path}")
    
    plt.close('all')

