
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

sns.set_theme(style="white", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def get_zone(state):
    north = ['Jammu and Kashmir', 'Himachal Pradesh', 'Punjab', 'Chandigarh', 'Uttarakhand', 'Haryana', 'Delhi', 'Uttar Pradesh', 'Ladakh']
    south = ['Andhra Pradesh', 'Karnataka', 'Kerala', 'Tamil Nadu', 'Telangana', 'Lakshadweep', 'Puducherry']
    east = ['Bihar', 'Jharkhand', 'West Bengal', 'Odisha', 'Andaman and Nicobar Islands']
    west = ['Rajasthan', 'Gujarat', 'Maharashtra', 'Goa', 'Dadra and Nagar Haveli and Daman and Diu']
    central = ['Madhya Pradesh', 'Chhattisgarh']
    n_east = ['Assam', 'Arunachal Pradesh', 'Manipur', 'Meghalaya', 'Mizoram', 'Nagaland', 'Sikkim', 'Tripura']
    
    if state in north: return 'North'
    if state in south: return 'South'
    if state in east: return 'East'
    if state in west: return 'West'
    if state in central: return 'Central'
    if state in n_east: return 'North-East'
    return 'Other'

def analyze_zones():
    df = load_gov_dataset()
    df['Zone'] = df['state'].apply(get_zone)
    
    # 13. Zonal Market Share
    zone_totals = df.groupby('Zone')['total_transactions'].sum()
    plt.figure(figsize=(10, 10))
    # Custom exploded pie
    explode = [0.05] * len(zone_totals)
    plt.pie(zone_totals, labels=zone_totals.index, autopct='%1.1f%%', startangle=140, pctdistance=0.85, explode=explode, colors=sns.color_palette('pastel'))
    # Draw circle
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig = plt.gcf()
    fig.gca().add_artist(centre_circle)
    plt.title("Federal Zone Distribution: Where is the Volume?", fontsize=18, weight='bold')
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/05_zonal_share_donut.png")
    plt.close()

    # 14. Zonal Growth Trends
    daily_zone = df.groupby(['date', 'Zone'])['total_transactions'].sum().unstack()
    plt.figure(figsize=(16, 8))
    for column in daily_zone.columns:
        plt.plot(daily_zone.index, daily_zone[column].rolling(7).mean(), label=column, linewidth=2)
    plt.title("Regional Velocity: Zonal Growth Trajectories (7-Day MA)", fontsize=18)
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/05_zonal_trends_line.png")
    plt.close()

    # 15. North vs South Gap
    gap_df = daily_zone[['North', 'South']].fillna(0)
    gap_df['Gap'] = gap_df['North'] - gap_df['South']
    
    plt.figure(figsize=(14, 6))
    plt.fill_between(gap_df.index, gap_df['Gap'], where=(gap_df['Gap'] > 0), color='green', alpha=0.3, label='North Leads')
    plt.fill_between(gap_df.index, gap_df['Gap'], where=(gap_df['Gap'] < 0), color='blue', alpha=0.3, label='South Leads')
    plt.plot(gap_df.index, gap_df['Gap'], color='black', alpha=0.2)
    plt.title("The North-South Divide: Daily Volume Difference", fontsize=18)
    plt.axhline(0, color='black', linewidth=1)
    plt.legend(loc='upper left')
    plt.savefig(f"{OUTPUT_DIR}/05_zonal_north_south_gap.png")
    plt.close()
    print("Module 5 Complete")

if __name__ == "__main__":
    analyze_zones()
