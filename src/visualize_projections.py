"""
Visualize Workforce Projections Module

Provides functions for creating charts for workforce supply and operations projections
with gap analysis visualization.
"""

import config
from utils import calendar_to_financial_year


def create_visualizations(gap_analysis_df, baseline_source='cpws', output_dir=None):
    """
    Create visualization charts for supply and ops projections with gap analysis.
    
    Args:
        gap_analysis_df: DataFrame from format_projections() with columns:
            year, financial_year, scenario, supply, ops, gap
        baseline_source: Baseline data source ('cpws' or 'gphc'). Default is 'cpws'.
        output_dir: Optional output directory path. If None, uses project root.
    """
    # Default to project root
    if output_dir is None:
        from pathlib import Path
        output_dir = Path(__file__).parent.parent
    else:
        from pathlib import Path
        output_dir = Path(output_dir)
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    # Create figure for the selected scenario
    end_year = config.START_PROJECTION_YEAR + config.DURATION
    start_fy = calendar_to_financial_year(config.START_PROJECTION_YEAR)
    end_fy = calendar_to_financial_year(end_year)
    
    fig, ax1 = config.plt.subplots(1, 1, figsize=(14, 6))
    
    fig.suptitle(f'{config.DURATION}-Year Workforce Supply vs Operations Projection - England ({start_fy} to {end_fy})', 
                 fontsize=16, fontweight='bold')
    
    # Color scheme
    supply_color = '#1f77b4'  # Blue
    ops_color = '#ff7f0e'     # Orange
    gap_color = '#2ca02c'     # Green
    
    # Get scenario name from data (should be a single scenario since data is pre-filtered in main())
    if gap_analysis_df.empty:
        return
    
    # Extract scenario name from the first row (all rows should have the same scenario)
    scenario_name = gap_analysis_df['scenario'].iloc[0]
    scenario_data = gap_analysis_df.copy()
    
    # Verify all rows have the same scenario (safety check)
    unique_scenarios = scenario_data['scenario'].unique()
    if len(unique_scenarios) > 1:
        raise ValueError(f"Expected single scenario in gap_analysis_df, but found: {unique_scenarios}")
    
    # Left y-axis: Supply and Ops lines
    ax1.plot(scenario_data['year'], scenario_data['supply'], 
            marker='o', label='Supply (Total FTE)', 
            color=supply_color, linewidth=2.5, markersize=5, linestyle='-')
    ax1.plot(scenario_data['year'], scenario_data['ops'], 
            marker='s', label='Operations (FTE)', 
            color=ops_color, linewidth=2.5, markersize=5, linestyle='--')
    
    # Set left y-axis labels
    y_label = 'FTE' if baseline_source.lower() == 'cpws' else 'Number of Registrants'
    ax1.set_ylabel(y_label, fontsize=10, color='black')
    ax1.tick_params(axis='y', labelcolor='black')
    ax1.grid(True, alpha=0.3)
    ax1.set_xlim(config.START_PROJECTION_YEAR - 1, end_year + 1)
    
    # Right y-axis: Gap bars
    ax2 = ax1.twinx()
    ax2.bar(scenario_data['year'], scenario_data['gap'], 
           label='Gap (Supply - Ops)', 
           color=gap_color, alpha=0.6, width=0.6)
    
    # Add zero line for gap reference on right axis
    ax2.axhline(y=0, color='gray', linestyle='-', linewidth=0.5, alpha=0.5)
    ax2.set_ylabel('Gap (FTE)', fontsize=10, color=gap_color)
    ax2.tick_params(axis='y', labelcolor=gap_color)
    
    # Set labels and title
    ax1.set_title(f'{scenario_name.capitalize()} Scenario', fontsize=12, fontweight='bold')
    ax1.set_xlabel('Financial Year', fontsize=10)
    
    # Combine legends from both axes
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc='best', fontsize=9)
    
    # Set x-axis ticks and labels to financial years
    tick_positions = range(config.START_PROJECTION_YEAR, end_year + 1)
    tick_labels = [calendar_to_financial_year(year) for year in tick_positions]
    ax1.set_xticks(tick_positions)
    ax1.set_xticklabels(tick_labels, rotation=45, ha='right')
    
    config.plt.tight_layout()
    
    # Save figure
    output_path = output_dir / 'workforce_projection.png'
    config.plt.savefig(output_path, dpi=300, bbox_inches='tight')
    
    config.plt.close('all')

