
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

sns.set_theme(style="white", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_seasonality():
    df = load_gov_dataset()
    df['Month'] = df['date'].dt.month_name()
    df['DayOfWeek'] = df['date'].dt.day_name()
    
    # Order definitions
    days_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    months_order = ['January', 'February', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    
    # 19. Operational Heatmap
    heatmap_data = df.pivot_table(index='DayOfWeek', columns='Month', values='total_transactions', aggfunc='mean')
    # Reindex
    heatmap_data = heatmap_data.reindex(index=days_order, columns=[m for m in months_order if m in heatmap_data.columns])
    
    plt.figure(figsize=(16, 8))
    sns.heatmap(heatmap_data, cmap="YlGnBu", linewidths=.5, annot=False)
    plt.title("Operational Cadence Heatmap (Avg Daily Volume)", fontsize=18)
    plt.savefig(f"{OUTPUT_DIR}/07_temp_heatmap.png")
    plt.close()

    # 20. The Sunday Effect
    day_stats = df.groupby('DayOfWeek')['total_transactions'].mean().reindex(days_order)
    plt.figure(figsize=(10, 6))
    colors = ['#34495e'] * 6 + ['#e74c3c'] # Red for Sunday
    sns.barplot(x=day_stats.index, y=day_stats.values, palette=colors)
    plt.title("The 'Sunday Effect': Operational Drop-off", fontsize=18)
    plt.xticks(rotation=45)
    plt.savefig(f"{OUTPUT_DIR}/07_temp_sunday_effect.png")
    plt.close()

    # 21. Monthly Growth Rates
    monthly = df.set_index('date').resample('M')['total_transactions'].sum()
    pct_change = monthly.pct_change() * 100
    
    plt.figure(figsize=(12, 6))
    # Color bars based on growth/decline
    colors = ['red' if x < 0 else 'green' for x in pct_change.fillna(0)]
    plt.bar(monthly.index, pct_change, color=colors, width=20)
    plt.title("Month-over-Month Growth Volatility (%)", fontsize=18)
    plt.axhline(0, color='black', linewidth=1)
    plt.ylabel("Growth Rate %")
    plt.savefig(f"{OUTPUT_DIR}/07_temp_monthly_growth.png")
    plt.close()
    print("Module 7 Complete")

if __name__ == "__main__":
    analyze_seasonality()
