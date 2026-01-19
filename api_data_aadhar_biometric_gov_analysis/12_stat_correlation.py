
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os
import sys

# Add current directory to path for data_loader
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from data_loader import load_gov_dataset

# Set style
sns.set_theme(style="white", context="talk")
OUTPUT_DIR = "output"
os.makedirs(OUTPUT_DIR, exist_ok=True)

def analyze_correlations():
    """
    Analyze execution synchronization between major states.
    """
    print("--- Starting Module 12: Statistical Correlation ---")
    df = load_gov_dataset()
    
    # 1. Identify Top 10 States
    top_states = df.groupby('state')['total_transactions'].sum().nlargest(10).index.tolist()
    
    # 2. Pivot Data: Date x State
    # Filter for top states first to reduce data size
    df_top = df[df['state'].isin(top_states)]
    pivot_df = df_top.pivot_table(index='date', columns='state', values='total_transactions', aggfunc='sum').fillna(0)
    
    import numpy as np
    
    # 3. Calculate Correlation Matrix
    corr_matrix = pivot_df.corr(method='pearson')
    
    # 4. Visualization
    plt.figure(figsize=(12, 10))
    
    mask = np.triu(np.ones_like(corr_matrix, dtype=bool))
    
    heatmap = sns.heatmap(corr_matrix, mask=mask, annot=True, fmt=".2f", cmap='coolwarm', 
                          center=0, square=True, linewidths=.5, cbar_kws={"shrink": .5})
    
    plt.title('State-to-State Operational Correlation (Pearson Coeff)', fontsize=16, fontweight='bold', pad=20)
    plt.xticks(rotation=45, ha='right')
    plt.yticks(rotation=0)
    
    output_path = os.path.join(OUTPUT_DIR, "12_state_correlation_matrix.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    analyze_correlations()
