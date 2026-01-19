
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np
import os
import sys

# Add current directory to path for data_loader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_loader import load_gov_dataset

# Set style
sns.set_theme(style="whitegrid", context="talk")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_catchment():
    """
    Analyze geographical concentration at Pincode level (Catchment Area).
    """
    print("--- Starting Module 13: Hyperlocal Catchment ---")
    df = load_gov_dataset()
    
    # 1. Pincode Aggregation
    pin_df = df.groupby('pincode')['total_transactions'].sum().reset_index()
    pin_df = pin_df.sort_values('total_transactions', ascending=False)
    
    # 2. Cumulative Calculation (Lorenz Curve Data)
    pin_df['cumulative_vol'] = pin_df['total_transactions'].cumsum()
    pin_df['cumulative_perc'] = pin_df['cumulative_vol'] / pin_df['total_transactions'].sum()
    
    n_pincodes = len(pin_df)
    pin_df['pincode_rank'] = np.arange(1, n_pincodes + 1)
    pin_df['pincode_perc'] = pin_df['pincode_rank'] / n_pincodes
    
    # 3. Visualization
    plt.figure(figsize=(10, 8))
    
    # Plot Actual Curve
    plt.plot(pin_df['pincode_perc'], pin_df['cumulative_perc'], 
             color='darkred', linewidth=3, label='Actual Distribution')
    
    # Plot Perfect Equality Line
    plt.plot([0, 1], [0, 1], color='gray', linestyle='--', label='Perfect Equality (Ideal)')
    
    # Annotations
    top_10_perc = pin_df[pin_df['pincode_perc'] <= 0.1]['cumulative_perc'].max()
    plt.annotate(f'Top 10% Pincodes control {top_10_perc:.0%} volume', 
                 xy=(0.1, top_10_perc), xytext=(0.2, 0.6),
                 arrowprops=dict(facecolor='black', shrink=0.05))
    
    plt.title('Hyperlocal Catchment Inequality (Pincode Lorenz Curve)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Cumulative Share of Pincodes (Ranked)', fontsize=12)
    plt.ylabel('Cumulative Share of Volume', fontsize=12)
    plt.legend()
    plt.grid(True, alpha=0.3)
    
    output_path = os.path.join(OUTPUT_DIR, "13_catchment_inequality.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    analyze_catchment()
