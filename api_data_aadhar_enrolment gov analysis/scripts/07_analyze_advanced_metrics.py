import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_advanced():
    print("Loading data for Advanced Metrics...")
    df = pd.read_parquet(DATA_FILE)
    
    # 1. Monthly Growth Rate % (National)
    print("Generating Growth Rate Chart...")
    if 'month_year' not in df.columns:
         df['month_year'] = df['date'].dt.to_period('M')
    
    monthly_total = df.groupby('month_year')['total_enrolment'].sum()
    pct_change = monthly_total.pct_change() * 100
    
    # Filter valid percent changes (drop NaNs or infs)
    pct_change = pct_change.dropna()
    pct_change.index = pct_change.index.astype(str)

    fig, ax = plt.subplots(figsize=(14, 6))
    colors = ['g' if x >= 0 else 'r' for x in pct_change.values]
    sns.barplot(x=pct_change.index, y=pct_change.values, palette=colors, ax=ax)
    ax.set_title("Month-over-Month Enrolment Growth Rate (%)")
    ax.set_ylabel("Growth Rate (%)")
    ax.set_xlabel("Month")
    ax.axhline(0, color='black', linewidth=1)
    utils.save_plot(fig, "17_monthly_growth_rate.png")

    # 2. Weekday vs Weekend Comparison
    print("Generating Weekday vs Weekend Chart...")
    df['is_weekend'] = df['date'].dt.dayofweek >= 5
    weekend_counts = df.groupby('is_weekend')['total_enrolment'].mean()
    weekend_counts.index = ['Weekday (Mon-Fri)', 'Weekend (Sat-Sun)']
    
    fig, ax = plt.subplots(figsize=(8, 6))
    sns.barplot(x=weekend_counts.index, y=weekend_counts.values, palette="Pastel1", ax=ax)
    ax.set_title("Average Daily Enrolments: Weekday vs Weekend")
    ax.set_ylabel("Average Enrolments")
    utils.save_plot(fig, "18_weekday_vs_weekend_avg.png")

    # 3. Cumulative Enrolment Curve
    print("Generating Cumulative Curve...")
    daily = df.groupby('date')['total_enrolment'].sum().cumsum()
    
    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(data=daily, linewidth=3, color=utils.COLORS['secondary'], ax=ax)
    ax.fill_between(daily.index, daily.values, color=utils.COLORS['secondary'], alpha=0.1)
    ax.set_title("Cumulative Total Enrolments Observed in Dataset")
    ax.set_ylabel("Cumulative Enrolments")
    ax.set_xlabel("Date")
    utils.save_plot(fig, "19_cumulative_growth_curve.png")

if __name__ == "__main__":
    analyze_advanced()
