
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

sns.set_theme(style="whitegrid", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_clustering():
    df = load_gov_dataset()
    
    # Aggregate Metrics per State
    # 1. Volume (Total)
    # 2. Consistency (CV - Coeff of Variation)
    state_stats = df.groupby('state')['total_transactions'].agg(['sum', 'mean', 'std'])
    state_stats['CV'] = state_stats['std'] / state_stats['mean']
    state_stats = state_stats.fillna(0)
    
    # 25. Quadrant Analysis (Volume vs Consistency)
    plt.figure(figsize=(14, 10))
    sns.scatterplot(data=state_stats, x='sum', y='CV', s=100)
    
    # Add quadrants
    mid_x = state_stats['sum'].median()
    mid_y = state_stats['CV'].median()
    plt.axvline(mid_x, color='gray', linestyle='--')
    plt.axhline(mid_y, color='gray', linestyle='--')
    
    plt.text(state_stats['sum'].max(), 0, "High Vol / Consistent", ha='right', va='bottom', color='green', fontsize=12)
    plt.text(0, state_stats['CV'].max(), "Low Vol / Erratic", ha='left', va='top', color='red', fontsize=12)
    
    for i, row in state_stats.iterrows():
        if row['sum'] > mid_x or row['CV'] > mid_y: # Label interesting ones
            plt.text(row['sum'], row['CV'], i, fontsize=9)
            
    plt.title("State Performance Matrix: Volume vs Consistency", fontsize=18)
    plt.xlabel("Total Volume")
    plt.ylabel("Volatility (Coefficient of Variation)")
    plt.xscale('log')
    plt.savefig(f"{OUTPUT_DIR}/09_cluster_quadrant.png")
    plt.close()

    # 26. Growth vs Volume Scatter
    # Calculate MoM growth for last month available vs first month
    months = df.pivot_table(index='state', columns=df['date'].dt.to_period('M'), values='total_transactions', aggfunc='sum')
    if months.shape[1] > 1:
        first_col = months.iloc[:, 0]
        last_col = months.iloc[:, -1]
        growth = (last_col - first_col) / first_col * 100
        state_stats['Growth'] = growth
        
        plt.figure(figsize=(14, 10))
        sns.regplot(data=state_stats, x='sum', y='Growth', scatter_kws={'s': 80})
        for i, row in state_stats.iterrows():
             if row['sum'] > mid_x:
                plt.text(row['sum'], row['Growth'], i, fontsize=9)
        plt.title("Growth Potential: Is Large Volume Slowing Down?", fontsize=18)
        plt.xlabel("Total Scale")
        plt.ylabel("Growth Rate (%)")
        plt.xscale('log')
        plt.savefig(f"{OUTPUT_DIR}/09_cluster_growth_matrix.png")
        plt.close()
    
    # 27. "Watchlist" (Low Volume, High Volatility)
    watchlist = state_stats[(state_stats['sum'] < mid_x) & (state_stats['CV'] > mid_y)]
    fig, ax = plt.subplots(figsize=(8, len(watchlist)/2 + 2))
    ax.axis('off')
    table_data = [[idx, f"{row['sum']:,.0f}", f"{row['CV']:.2f}"] for idx, row in watchlist.iterrows()]
    if table_data:
        tbl = plt.table(cellText=table_data, colLabels=["State", "Volume", "Volatility"], loc='center')
        tbl.auto_set_font_size(False)
        tbl.set_fontsize(12)
        tbl.scale(1, 1.5)
        plt.title("Priority Watchlist: Low Performing Regions", fontsize=16)
        plt.savefig(f"{OUTPUT_DIR}/09_cluster_watchlist.png")
    else:
        plt.text(0.5, 0.5, "No Critical Watchlist Items", ha='center')
        plt.savefig(f"{OUTPUT_DIR}/09_cluster_watchlist.png")
    plt.close()
    print("Module 9 Complete")

if __name__ == "__main__":
    analyze_clustering()
