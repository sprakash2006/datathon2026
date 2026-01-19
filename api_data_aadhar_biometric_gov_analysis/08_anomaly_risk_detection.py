
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
import numpy as np
from data_loader import load_gov_dataset

sns.set_theme(style="whitegrid", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_risk():
    df = load_gov_dataset()
    daily_vol = df.groupby('date')['total_transactions'].sum()
    
    # 22. The "July 1st" Spike Deep Dive
    subset = daily_vol['2025-06-15':'2025-07-15']
    plt.figure(figsize=(14, 6))
    plt.plot(subset.index, subset.values, color='#c0392b', marker='o')
    plt.title("Forensic Timeline: The July 1st Anomaly", fontsize=18)
    plt.axvspan(pd.Timestamp('2025-06-30'), pd.Timestamp('2025-07-02'), color='yellow', alpha=0.3, label='Spike Window')
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/08_risk_july_spike.png")
    plt.close()

    # 23. Z-Score Outlier Detection
    mean = daily_vol.mean()
    std = daily_vol.std()
    z_scores = (daily_vol - mean) / std
    outliers = z_scores[abs(z_scores) > 3]
    
    plt.figure(figsize=(14, 8))
    plt.scatter(daily_vol.index, z_scores, c=z_scores, cmap='coolwarm', s=50)
    plt.axhline(3, color='red', linestyle='--', label='Critical Threshold (+3 SD)')
    plt.axhline(-3, color='red', linestyle='--')
    plt.title("Statistical Control Chart (Z-Scores)", fontsize=18)
    plt.ylabel("Standard Deviations from Mean")
    plt.legend()
    for date, val in outliers.items():
        plt.annotate(date.strftime('%Y-%m-%d'), (date, val))
    plt.savefig(f"{OUTPUT_DIR}/08_risk_outlier_detection.png")
    plt.close()

    # 24. Unexpected Lulls (Operational Downtime Risk)
    threshold = mean * 0.1 # 10% of average
    lulls = daily_vol[daily_vol < threshold]
    plt.figure(figsize=(10, 6))
    if not lulls.empty:
        plt.bar(lulls.index, lulls.values, color='black')
        plt.title(f"Operational Blackouts: Days < 10% Capacity ({len(lulls)} days)", fontsize=18)
        plt.savefig(f"{OUTPUT_DIR}/08_risk_downtime_lulls.png")
    else:
        # Create a placeholder if no lulls
        plt.text(0.5, 0.5, "No Critical Downtime Detected", ha='center', fontsize=20)
        plt.savefig(f"{OUTPUT_DIR}/08_risk_downtime_lulls.png")
    plt.close()
    print("Module 8 Complete")

if __name__ == "__main__":
    analyze_risk()
