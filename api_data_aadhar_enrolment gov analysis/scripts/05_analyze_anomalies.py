import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils
import numpy as np

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_anomalies():
    print("Loading data for Anomaly Analysis...")
    df = pd.read_parquet(DATA_FILE)
    
    # 1. Detect Sudden Volume Spikes in District-Level Daily Data
    # Z-score method per district might be too heavy. Let's look at global outliers or specific high-variance districts.
    
    print("Calculating Daily Enrolment Anomalies...")
    # Group by District and Date
    daily_district = df.groupby(['district', 'date'])['total_enrolment'].sum().reset_index()
    
    # Define Anomaly: > 3 Std Dev from the District's Mean
    daily_district['mean'] = daily_district.groupby('district')['total_enrolment'].transform('mean')
    daily_district['std'] = daily_district.groupby('district')['total_enrolment'].transform('std')
    daily_district['z_score'] = (daily_district['total_enrolment'] - daily_district['mean']) / daily_district['std']
    
    anomalies = daily_district[daily_district['z_score'] > 3].sort_values('z_score', ascending=False)
    
    print(f"Found {len(anomalies)} anomalous days across all districts.")
    
    # Visualizing Top 5 Anomalous Districts over time
    top_anomalous_districts = anomalies['district'].unique()[:5]
    
    if len(top_anomalous_districts) > 0:
        subset = daily_district[daily_district['district'].isin(top_anomalous_districts)]
        
        fig, ax = plt.subplots(figsize=(14, 8))
        sns.lineplot(data=subset, x='date', y='total_enrolment', hue='district', ax=ax)
        # Highlight anomalies
        anom_subset = anomalies[anomalies['district'].isin(top_anomalous_districts)]
        sns.scatterplot(data=anom_subset, x='date', y='total_enrolment', color='red', s=100, marker='X', label='Anomaly (>3 STD)', ax=ax, zorder=5)
        
        ax.set_title("Time-Series of Top 5 Districts with Enrolment Spikes (Anomalies)")
        ax.set_xlabel("Date")
        ax.set_ylabel("Daily Enrolments")
        utils.save_plot(fig, "12_anomalous_spikes_districts.png")
    
    # 2. Distribution of "Unusual" High Volume Days (Histogram of Z-Scores)
    print("Generating Anomaly Distribution...")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(daily_district['z_score'].dropna(), bins=100, kde=False, log_scale=(False, True), color=utils.COLORS['quaternary'], ax=ax)
    ax.axvline(3, color='red', linestyle='--', label='Threshold (3 STD)')
    ax.set_title("Distribution of Enrolment Spikes (Z-Scores across Districts)")
    ax.set_xlabel("Z-Score (Standard Deviations from Mean)")
    ax.legend()
    utils.save_plot(fig, "13_anomaly_distribution_log.png")

if __name__ == "__main__":
    analyze_anomalies()
