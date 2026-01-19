
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from data_loader import load_gov_dataset

sns.set_theme(style="white", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_geo_performance():
    df = load_gov_dataset()
    state_perf = df.groupby('state')['total_transactions'].sum().sort_values(ascending=False)
    
    # 4. State Leaderboard (Top 15)
    plt.figure(figsize=(14, 10))
    sns.barplot(x=state_perf.head(15).values, y=state_perf.head(15).index, palette="viridis")
    plt.title("Federal Review: Top 15 High-Performance States", fontsize=18, weight='bold')
    plt.xlabel("Total Transactions")
    plt.savefig(f"{OUTPUT_DIR}/02_geo_state_leaderboard.png")
    plt.close()

    # 5. Performance vs National Average (Diverging Bar)
    top_20 = state_perf.head(20)
    avg_perf = top_20.mean()
    processed_df = pd.DataFrame({'State': top_20.index, 'Volume': top_20.values})
    processed_df['Z_Score'] = (processed_df['Volume'] - avg_perf) / processed_df['Volume'].std()
    processed_df['Color'] = ['red' if x < 0 else 'green' for x in processed_df['Z_Score']]
    
    plt.figure(figsize=(14, 10))
    plt.hlines(y=processed_df.State, xmin=0, xmax=processed_df.Z_Score, color=processed_df.Color, alpha=0.5, linewidth=5)
    plt.title("State Performance Deviations (Normalized Z-Score)", fontsize=18)
    plt.xlabel("Deviation from Top-20 Average (SD)")
    plt.grid(linestyle='--', alpha=0.5)
    plt.savefig(f"{OUTPUT_DIR}/02_geo_diverging_performance.png")
    plt.close()

    # 6. Pareto Analysis (80/20 Rule)
    cumulative_pct = state_perf.cumsum() / state_perf.sum() * 100
    
    fig, ax1 = plt.subplots(figsize=(14, 8))
    ax1.bar(state_perf.index[:15], state_perf.values[:15], color='#3498db')
    ax2 = ax1.twinx()
    ax2.plot(state_perf.index[:15], cumulative_pct.values[:15], color='#c0392b', marker='D', linewidth=2)
    ax2.axhline(80, color='grey', linestyle='--')
    ax2.text(0, 81, '80% Contribution Threshold')
    
    plt.title("Strategic Resource Allocation: The Vital Few (Pareto)", fontsize=18)
    ax1.set_xticklabels(state_perf.index[:15], rotation=45, ha='right')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/02_geo_pareto_states.png")
    plt.close()
    print("Module 2 Complete")

if __name__ == "__main__":
    analyze_geo_performance()
