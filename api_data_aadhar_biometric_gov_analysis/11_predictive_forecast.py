
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

def analyze_forecast():
    """
    Project future trends using linear regression.
    """
    print("--- Starting Module 11: Predictive Forecasting ---")
    df = load_gov_dataset()
    
    # 1. Daily Aggregation
    daily_df = df.groupby('date')['total_transactions'].sum().reset_index()
    daily_df = daily_df.sort_values('date')
    
    # 2. Prepare for Regression
    daily_df['day_ordinal'] = daily_df['date'].map(pd.Timestamp.toordinal)
    
    # Simple Linear Regression
    X = daily_df['day_ordinal'].values
    y = daily_df['total_transactions'].values
    
    # Fit coefficients
    z = np.polyfit(X, y, 1)
    p = np.poly1d(z)
    
    # 3. Forecast next 30 days
    last_date = daily_df['date'].max()
    future_dates = [last_date + pd.Timedelta(days=x) for x in range(1, 31)]
    future_ordinals = [d.toordinal() for d in future_dates]
    future_values = p(future_ordinals)
    
    # Create Forecast DataFrame
    forecast_df = pd.DataFrame({
        'date': future_dates,
        'total_transactions': future_values,
        'type': 'Forecast'
    })
    
    daily_df['type'] = 'Actual'
    combined_df = pd.concat([daily_df[['date', 'total_transactions', 'type']], forecast_df])
    
    # 4. Visualization
    plt.figure(figsize=(14, 7))
    
    # Determine the y-axis limit for potentially cleaner viewing if outliers exist
    # If the max is huge (spike), maybe limit it, but for government report, let's show reality.
    
    sns.lineplot(data=combined_df, x='date', y='total_transactions', hue='type', 
                 palette={'Actual': 'navy', 'Forecast': 'crimson'}, linewidth=2.5)
    
    # Add Trendline to Actuals for clarity
    plt.plot(daily_df['date'], p(X), "k--", label="Linear Trend", alpha=0.6)
    
    plt.title('30-Day Predictive Volume Forecast (Linear Regression)', fontsize=16, fontweight='bold', pad=20)
    plt.xlabel('Date', fontsize=12)
    plt.ylabel('Daily Transactions', fontsize=12)
    plt.legend()
    
    # Ensure current dir exists
    output_path = os.path.join(OUTPUT_DIR, "11_forecast_trend.png")
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    print(f"Generated {output_path}")

if __name__ == "__main__":
    analyze_forecast()
