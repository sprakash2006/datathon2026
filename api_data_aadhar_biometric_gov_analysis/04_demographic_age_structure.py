
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd
from data_loader import load_gov_dataset

sns.set_theme(style="whitegrid", context="talk")
OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def analyze_demographics():
    df = load_gov_dataset()
    
    # 10. National Age Split
    total_5_17 = df['bio_age_5_17'].sum()
    total_17_plus = df['bio_age_17_'].sum()
    
    plt.figure(figsize=(9, 9))
    plt.pie([total_5_17, total_17_plus], labels=['Youth (5-17)', 'Adult (17+)'], autopct='%1.1f%%', colors=['#f1c40f', '#34495e'], startangle=90, explode=(0.05, 0))
    plt.title("National Demographic Split: The Youth Factor", fontsize=18, weight='bold')
    plt.savefig(f"{OUTPUT_DIR}/04_demo_national_split.png")
    plt.close()

    # 11. "Youth Surge" States (Highest % of 5-17)
    state_age = df.groupby('state')[['bio_age_5_17', 'total_transactions']].sum()
    state_age['youth_pct'] = (state_age['bio_age_5_17'] / state_age['total_transactions']) * 100
    top_youth_states = state_age.sort_values('youth_pct', ascending=False).head(15)
    
    plt.figure(figsize=(14, 8))
    sns.barplot(x=top_youth_states['youth_pct'], y=top_youth_states.index, palette="Oranges_r")
    plt.title("Future-Ready States: Highest Youth Enrollment (%)", fontsize=18)
    plt.xlabel("Percentage of Transactions from Age 5-17")
    plt.axvline(50, color='black', linestyle='--')
    plt.savefig(f"{OUTPUT_DIR}/04_demo_youth_surge_states.png")
    plt.close()

    # 12. Age Trend Divergence
    daily_age = df.groupby('date')[['bio_age_5_17', 'bio_age_17_']].sum()
    
    plt.figure(figsize=(14, 8))
    plt.plot(daily_age.index, daily_age['bio_age_5_17'], label='Youth (5-17)', color='#f39c12', linewidth=2)
    plt.plot(daily_age.index, daily_age['bio_age_17_'], label='Adult (17+)', color='#2c3e50', linewidth=2)
    plt.fill_between(daily_age.index, daily_age['bio_age_5_17'], daily_age['bio_age_17_'], color='gray', alpha=0.1)
    plt.title("Demographic Divergence: When do Kids vs Adults Update?", fontsize=18)
    plt.legend()
    plt.savefig(f"{OUTPUT_DIR}/04_demo_trend_divergence.png")
    plt.close()
    print("Module 4 Complete")

if __name__ == "__main__":
    analyze_demographics()
