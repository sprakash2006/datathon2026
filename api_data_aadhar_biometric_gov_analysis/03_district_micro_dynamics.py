
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from data_loader import load_gov_dataset

sns.set_theme(style="darkgrid", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_district_dynamics():
    df = load_gov_dataset()
    dist_df = df.groupby(['state', 'district'])['total_transactions'].sum().reset_index()
    dist_df = dist_df.sort_values('total_transactions', ascending=False)
    
    # 7. Top 20 Districts National Heatmap (represented as Bar for clarity in static img)
    top_20 = dist_df.head(20).sort_values('total_transactions', ascending=True)
    plt.figure(figsize=(12, 10))
    plt.barh(top_20['district'] + " (" + top_20['state'] + ")", top_20['total_transactions'], color='#8e44ad')
    plt.title("Grassroots Heroes: Top 20 Districts Nationwide", fontsize=18)
    plt.xlabel("Volume")
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/03_micro_top_districts.png")
    plt.close()

    # 8. Lorenz Curve of Equality
    values = np.sort(dist_df['total_transactions'].values)
    lorenz = np.cumsum(values) / values.sum()
    lorenz = np.insert(lorenz, 0, 0)
    
    plt.figure(figsize=(10, 10))
    plt.plot(np.linspace(0, 1, len(lorenz)), lorenz, drawstyle='steps-post', color='red', linewidth=3, label='Actual Distribution')
    plt.plot([0, 1], [0, 1], color='black', linestyle='--', label='Perfect Equality Line')
    plt.title("Service Penetration Inequality (Lorenz Curve)", fontsize=18)
    plt.xlabel("Cumulative Share of Districts")
    plt.ylabel("Cumulative Share of Transactions")
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/03_micro_lorenz_inequality.png")
    plt.close()

    # 9. State vs District Dominance Scatter
    state_stats = df.groupby('state').agg(
        Total_State_Vol=('total_transactions', 'sum'),
        Max_District_Vol=('total_transactions', lambda x: dist_df[dist_df['state'] == x.name]['total_transactions'].max() if not dist_df[dist_df['state'] == x.name].empty else 0)
    ).reset_index()
    
    plt.figure(figsize=(12, 10))
    sns.scatterplot(data=state_stats, x='Total_State_Vol', y='Max_District_Vol', size='Total_State_Vol', sizes=(100, 1000), hue='State', legend=False)
    
    # Annotate significant points
    for i, row in state_stats.nlargest(8, 'Total_State_Vol').iterrows():
        plt.text(row['Total_State_Vol'], row['Max_District_Vol'], row['State'], fontsize=10)
        
    plt.title("Centralization Index: Are States Dependent on One Mega-District?", fontsize=16)
    plt.xlabel("Total State Volume")
    plt.ylabel("Volume of Largest District (Anchor District)")
    plt.xscale('log')
    plt.yscale('log')
    plt.savefig(f"{OUTPUT_DIR}/03_micro_centralization_scatter.png")
    plt.close()
    print("Module 3 Complete")

if __name__ == "__main__":
    analyze_district_dynamics()
