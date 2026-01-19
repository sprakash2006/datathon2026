import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 4: Geographic Variation...")
    
    # 1. District Concentration: How many districts make up 80% of volume?
    district_vols = df.groupby('district').size().sort_values(ascending=False)
    cumsum = district_vols.cumsum()
    total_vol = district_vols.sum()
    pareto_threshold = total_vol * 0.8
    
    top_80_count = cumsum[cumsum <= pareto_threshold].count()
    total_districts = len(district_vols)
    
    print(f"80% of volume comes from {top_80_count} out of {total_districts} districts.")
    
    # Viz 1: Top 20 Busiest Districts National-Level
    top_20_dist = district_vols.head(20)
    fig, ax = utils.setup_plot("Top 20 High-Activity Districts (National)", "Record Count", "District")
    sns.barplot(x=top_20_dist.values, y=top_20_dist.index, hue=top_20_dist.index, palette="rocket", legend=False, ax=ax)
    utils.save_plot(fig, "04_top_20_districts.png")
    
    # 2. State Volatility (Standard Deviation of District Volumes per State)
    # High Std Dev means huge inequality between districts (e.g., one major city dominance)
    state_volatility = df.groupby('state')['district'].value_counts().groupby(level=0).std().sort_values(ascending=False).head(10)
    
    fig, ax = utils.setup_plot("Regional Inequality: States with Highest District Disparity", "Std Dev of District Volume", "State")
    sns.barplot(x=state_volatility.values, y=state_volatility.index, hue=state_volatility.index, palette="coolwarm", legend=False, ax=ax)
    utils.save_plot(fig, "04_regional_disparity.png")
    
    # Save Data
    utils.save_data(district_vols.to_frame(name='count'), "04_district_volumes.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
