
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

sns.set_theme(style="ticks", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def is_tier1(district):
    metros = ['Mumbai', 'Delhi', 'Bangalore', 'Bengaluru', 'Hyderabad', 'Ahmedabad', 'Chennai', 'Kolkata', 'Pune']
    s = str(district).lower()
    for m in metros:
        if m.lower() in s: return True
    return False

def analyze_urban_rural():
    df = load_gov_dataset()
    df['Type'] = df['district'].apply(lambda x: 'Metro/Tier-1' if is_tier1(x) else 'Rest of India')
    
    # 16. Tier 1 vs RoI Volume
    type_stats = df.groupby('Type')['total_transactions'].sum()
    plt.figure(figsize=(8, 8))
    plt.bar(type_stats.index, type_stats.values, color=['#95a5a6', '#8e44ad'])
    plt.title("Urban Core vs Hinterland Volume", fontsize=18)
    plt.ylabel("Total Transactions")
    plt.savefig(f"{OUTPUT_DIR}/06_urban_tier1_volume.png")
    plt.close()

    # 17. High-Density Pincode Clusters
    top_pins = df.groupby('pincode')['total_transactions'].sum().nlargest(15)
    plt.figure(figsize=(14, 8))
    top_pins.plot(kind='bar', color='#e74c3c')
    plt.title("Hyper-Local Hotspots: Top 15 Pincodes", fontsize=18)
    plt.xlabel("Pincode")
    plt.xticks(rotation=45)
    plt.savefig(f"{OUTPUT_DIR}/06_urban_pincode_clusters.png")
    plt.close()

    # 18. Volatility Analysis (Stability)
    daily_type = df.groupby(['date', 'Type'])['total_transactions'].sum().unstack()
    daily_type_pct_change = daily_type.pct_change().dropna()
    
    plt.figure(figsize=(10, 6))
    sns.kdeplot(daily_type_pct_change['Metro/Tier-1'], fill=True, label='Metro Stability', color='purple')
    sns.kdeplot(daily_type_pct_change['Rest of India'], fill=True, label='Rural/RoI Stability', color='gray')
    plt.title("Operational Stability: Day-to-Day Volatility Distribution", fontsize=16)
    plt.xlabel("Daily % Change (Closer to 0 is more stable)")
    plt.xlim(-1, 1) # Limit extreme outliers
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/06_urban_volatility_kde.png")
    plt.close()
    print("Module 6 Complete")

if __name__ == "__main__":
    analyze_urban_rural()
