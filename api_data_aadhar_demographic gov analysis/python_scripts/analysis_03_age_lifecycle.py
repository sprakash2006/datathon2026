import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 3: Age-Group Lifecycle...")
    
    # Calculate Youth Ratio per State
    # Youth Ratio = (5-17) / (5-17 + 17+)
    df_state = df.groupby('state')[['demo_age_5_17', 'demo_age_17_']].sum()
    df_state['Total'] = df_state['demo_age_5_17'] + df_state['demo_age_17_']
    df_state['Youth_Ratio'] = df_state['demo_age_5_17'] / df_state['Total']
    
    # Sort for visualization
    df_state_sorted = df_state.sort_values('Youth_Ratio', ascending=False).head(10)
    
    # Viz 1: Top 10 States with Youngest Demographic (High Student/Child population activity)
    fig, ax = utils.setup_plot("States with Highest Share of Youth Activity (5-17 yrs)", "Youth Proportion (0-1)", "State")
    sns.barplot(x=df_state_sorted['Youth_Ratio'], y=df_state_sorted.index, hue=df_state_sorted.index, palette="Blues_r", legend=False, ax=ax)
    ax.axvline(df_state['Youth_Ratio'].mean(), color='red', linestyle='--', label=f"National Avg: {df_state['Youth_Ratio'].mean():.2f}")
    ax.legend()
    utils.save_plot(fig, "03_youth_demographic_hotspots.png")
    
    # Viz 2: Age Correlation with Volume
    # Do larger states have younger or older populations?
    fig, ax = utils.setup_plot("Correlation: Volume vs Youth Ratio", "Total Activity Volume", "Youth Ratio")
    sns.scatterplot(data=df_state, x='Total', y='Youth_Ratio', size='Total', sizes=(20, 500), color=utils.colors['primary'], ax=ax)
    utils.save_plot(fig, "03_volume_age_correlation.png")
    
    # Save Data
    utils.save_data(df_state, "03_state_age_profile.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
