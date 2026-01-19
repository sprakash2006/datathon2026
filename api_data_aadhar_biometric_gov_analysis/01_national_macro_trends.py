
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

# Setup
sns.set_theme(style="whitegrid", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_macro_trends():
    df = load_gov_dataset()
    daily_vol = df.groupby('date')['total_transactions'].sum().sort_index()
    
    # 1. Cumulative Growth (S-Curve Analysis)
    cumulative = daily_vol.cumsum()
    plt.figure(figsize=(14, 8))
    plt.fill_between(cumulative.index, cumulative.values, color="skyblue", alpha=0.4)
    plt.plot(cumulative.index, cumulative.values, color="SlateBlue", linewidth=3)
    plt.title("National Biometric Update Trajectory (Cumulative)", fontsize=20, weight='bold')
    plt.ylabel("Total Transactions (Millions)")
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.savefig(f"{OUTPUT_DIR}/01_macro_cumulative_growth.png")
    plt.close()

    # 2. Daily Volatility
    plt.figure(figsize=(16, 6))
    plt.plot(daily_vol.index, daily_vol.values, color='#34495e', linewidth=1.5, label='Daily Volume')
    plt.title("Daily Operational Volatility", fontsize=18)
    plt.axhline(daily_vol.mean(), color='red', linestyle='--', label=f'Avg: {daily_vol.mean():,.0f}')
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/01_macro_daily_volatility.png")
    plt.close()

    # 3. Moving Method (Trend Smoothing)
    ma7 = daily_vol.rolling(window=7).mean()
    ma30 = daily_vol.rolling(window=30).mean()
    
    plt.figure(figsize=(16, 8))
    plt.plot(daily_vol.index, daily_vol.values, color='lightgrey', alpha=0.5, label='Raw Data')
    plt.plot(daily_vol.index, ma7, color='#2ecc71', linewidth=2, label='7-Day Trend')
    plt.plot(daily_vol.index, ma30, color='#e74c3c', linewidth=2.5, linestyle='-', label='30-Day Trend')
    plt.title("Short vs Long Term Trend Analysis", fontsize=18)
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/01_macro_moving_averages.png")
    plt.close()
    print("Module 1 Complete")

if __name__ == "__main__":
    analyze_macro_trends()
