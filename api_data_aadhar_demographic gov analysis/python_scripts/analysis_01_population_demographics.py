import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

# Add parent dir to path for imports
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 1: Population & Demographics...")
    
    # 1. Total records (proxy for population interactions in this dataset) by State
    state_counts = df['state'].value_counts().head(10)
    
    # Viz 1: Top 10 States by Interaction Volume
    fig, ax = utils.setup_plot(
        "Top 10 States by Aadhaar Activity Volume",
        "Record Count",
        "State"
    )
    sns.barplot(x=state_counts.values, y=state_counts.index, hue=state_counts.index, palette="viridis", legend=False, ax=ax)
    utils.save_plot(fig, "01_top_states_population.png")
    
    # 2. Age Group Distribution (5-17 vs 18+)
    # We sum the raw counts provided in the dataset
    age_audit = df[['demo_age_5_17', 'demo_age_17_']].sum()
    age_audit.index = ['Age 5-17', 'Age 18+']
    
    # Viz 2: National Age Group Split
    fig, ax = utils.setup_plot("National Demographic Profile: Age Groups", "", "")
    ax.pie(age_audit, labels=age_audit.index, autopct='%1.1f%%', colors=[utils.colors['primary'], utils.colors['secondary']], startangle=140)
    utils.save_plot(fig, "01_age_group_pie.png")
    
    # 3. District-level average activity
    dist_counts = df.groupby('state')['district'].nunique().sort_values(ascending=False).head(15)
    
    # Viz 3: Districts Coverage per State
    fig, ax = utils.setup_plot("Administrative Coverage: Active Districts per State", "Number of Active Districts", "State")
    sns.barplot(x=dist_counts.values, y=dist_counts.index, hue=dist_counts.index, palette="magma", legend=False, ax=ax)
    utils.save_plot(fig, "01_district_coverage.png")
    
    # Save Summary Data
    utils.save_data(state_counts, "01_state_population_summary.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
