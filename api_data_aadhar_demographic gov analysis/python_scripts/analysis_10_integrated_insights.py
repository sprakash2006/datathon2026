import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 10: Integrated National Insights...")
    
    # 1. Multivariate Correlation Matrix
    # We need to aggregate data to a Granular Level (e.g., District Level) to do correlation
    # Features per district: Total Vol, Avg Latency, Failure Rate, Youth %, Female %
    
    dist_stats = df.groupby('district').agg({
        'response_time_ms': 'mean',
        'auth_status': lambda x: (x == 'Failure').mean(),
        'demo_age_5_17': 'sum',
        'gender': lambda x: (x == 'Female').mean()
    }).rename(columns={
        'response_time_ms': 'Avg_Latency',
        'auth_status': 'Failure_Rate',
        'demo_age_5_17': 'Youth_Vol',
        'gender': 'Female_Pct'
    })
    
    # Add Total Vol
    dist_stats['Total_Vol'] = df.groupby('district').size()
    
    corr = dist_stats.corr()
    
    fig, ax = utils.setup_plot("Holistic Analysis: Multivariate Correlation Matrix", "", "")
    sns.heatmap(corr, annot=True, cmap="coolwarm", center=0, ax=ax)
    utils.save_plot(fig, "10_multivariate_correlation.png")
    
    # 2. Digital Inclusion Map (Identify Bottom 50 Districts - The 'Dark Zones')
    bottom_50 = dist_stats.sort_values('Total_Vol').head(20)
    
    fig, ax = utils.setup_plot("Digital Inclusion Gaps: Districts with Lowest Footprint", "Total Transactions", "District")
    sns.barplot(x=bottom_50['Total_Vol'], y=bottom_50.index, hue=bottom_50.index, palette="Greys_r", legend=False, ax=ax)
    utils.save_plot(fig, "10_inclusion_gaps_bottom_districts.png")
    
    utils.save_data(dist_stats, "10_district_integrated_profile.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
