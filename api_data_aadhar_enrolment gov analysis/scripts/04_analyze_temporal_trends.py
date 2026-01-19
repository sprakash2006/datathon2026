import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_temporal():
    print("Loading data for Temporal Analysis...")
    df = pd.read_parquet(DATA_FILE)
    
    # 1. Daily Enrolment Trend (Line Chart)
    print("Generating Daily Trend Chart...")
    daily_counts = df.groupby('date')['total_enrolment'].sum()
    # Calculate 7-day rolling average to smooth out weekends
    rolling_7d = daily_counts.rolling(window=7).mean()

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=daily_counts, label='Daily Volume', alpha=0.3, color='gray', ax=ax)
    sns.lineplot(data=rolling_7d, label='7-Day Moving Average', linewidth=2, color=utils.COLORS['primary'], ax=ax)
    ax.set_title("Daily Aadhaar Enrolment Trends with Moving Average")
    ax.set_ylabel("Total Enrolments")
    ax.set_xlabel("Date")
    ax.legend()
    utils.save_plot(fig, "09_daily_enrolment_trends.png")

    # 2. Day of Week Analysis (Bar Chart)
    # Check for operational consistency
    print("Generating Day of Week Chart...")
    df['day_name'] = df['date'].dt.day_name()
    day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    dow_counts = df.groupby('day_name')['total_enrolment'].mean().reindex(day_order)

    fig, ax = plt.subplots(figsize=(10, 6))
    sns.barplot(x=dow_counts.index, y=dow_counts.values, palette="Blues_d", ax=ax)
    ax.set_title("Average Daily Enrolments by Day of Week")
    ax.set_ylabel("Average Enrolments")
    ax.set_xlabel("Day of Week")
    utils.save_plot(fig, "10_day_of_week_efficiency.png")

    # 3. Monthly Seasonality (Line Chart - Year over Year if data allows, else simple monthly)
    # We have data from 2024 to end of 2025 roughly.
    print("Generating Monthly Seasonality Chart...")
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    
    monthly_pivot = df.pivot_table(index='month', columns='year', values='total_enrolment', aggfunc='sum')
    
    fig, ax = plt.subplots(figsize=(12, 6))
    monthly_pivot.plot(kind='line', marker='o', linewidth=2, ax=ax)
    ax.set_title("Monthly Enrolment Comparision (Year over Year)")
    ax.set_ylabel("Total Enrolments")
    ax.set_xlabel("Month (1=Jan, 12=Dec)")
    ax.set_xticks(range(1, 13))
    utils.save_plot(fig, "11_monthly_seasonality.png")

if __name__ == "__main__":
    analyze_temporal()
