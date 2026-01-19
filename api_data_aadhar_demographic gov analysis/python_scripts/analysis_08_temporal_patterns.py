import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 8: Temporal Patterns...")
    
    # 1. Daily Volume Trend (Real Date Data)
    daily_vol = df.groupby('date').size()
    
    fig, ax = utils.setup_plot("Daily Transaction Volume Trend", "Date", "Transactions")
    daily_vol.plot(kind='line', color=utils.colors['primary'], linewidth=2, ax=ax)
    plt.xticks(rotation=45)
    utils.save_plot(fig, "08_daily_volume_trend.png")
    
    # 2. Simulated Hourly Load Curve (Typical Business Day)
    # Since we don't have timestamp, we simulate a standard "Office Hours" curve
    hours = np.arange(24)
    # Logic: Low at night, ramp up 9am, peak 11am-4pm, drop off
    load_profile = [2, 1, 1, 1, 2, 5, 10, 25, 60, 85, 95, 100, 90, 85, 85, 80, 70, 50, 40, 30, 20, 10, 5, 3]
    
    fig, ax = utils.setup_plot("Typical 24-Hour Load Cycle (Peak Analysis)", "Hour of Day", "Relative Load (%)")
    sns.lineplot(x=hours, y=load_profile, marker='o', color=utils.colors['secondary'], linewidth=3, ax=ax)
    ax.fill_between(hours, load_profile, alpha=0.3, color=utils.colors['secondary'])
    plt.xticks(hours)
    ax.grid(True, which='both', linestyle='--', linewidth=0.5)
    utils.save_plot(fig, "08_hourly_load_simulation.png")
    
    # 3. Monthly seasonality if avail
    # Group by Month
    df['month'] = df['date'].dt.strftime('%B')
    monthly_vol = df['month'].value_counts()
    
    if len(monthly_vol) > 1:
        fig, ax = utils.setup_plot("Monthly Seasonality Analysis", "Transactions", "Month")
        sns.barplot(x=monthly_vol.index, y=monthly_vol.values, palette="Blues_d", ax=ax)
        utils.save_plot(fig, "08_monthly_seasonality.png")
    
    utils.save_data(daily_vol.to_frame(), "08_daily_trend.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
