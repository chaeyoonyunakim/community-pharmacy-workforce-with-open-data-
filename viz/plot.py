"""
Main entry point for creating workforce projection visualizations.

Usage:
    python plot.py
"""

from visualize_projections import create_visualizations


if __name__ == '__main__':
    try:
        create_visualizations()
        print("\n✅ Visualizations created successfully!")
    except ImportError:
        print("Error: matplotlib not installed. Install with: pip install matplotlib")
    except Exception as e:
        print(f"Error creating visualizations: {e}")
        import traceback
        traceback.print_exc()

