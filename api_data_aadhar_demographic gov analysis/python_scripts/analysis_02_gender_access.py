import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 2: Gender Distribution...")
    
    # 1. National Gender Split
    gender_counts = df['gender'].value_counts()
    
    fig, ax = utils.setup_plot("National Gender Distribution", "Gender", "Count")
    sns.barplot(x=gender_counts.index, y=gender_counts.values, hue=gender_counts.index,palette="pastel", legend=False, ax=ax)
    utils.save_plot(fig, "02_national_gender_split.png")
    
    # 2. State-wise Gender Parity (Stacked Bar)
    # Filter top 5 states for clarity
    top_states = df['state'].value_counts().head(5).index
    state_gender = df[df['state'].isin(top_states)].groupby(['state', 'gender']).size().unstack()
    
    # Normalize to percentage
    state_gender_pct = state_gender.div(state_gender.sum(axis=1), axis=0) * 100
    
    fig, ax = utils.setup_plot("Gender Accessibility by Top States (%)", "Proportion (%)", "State")
    state_gender_pct.plot(kind='bar', stacked=True, color=['#ff9999', '#66b3ff', '#99ff99'], ax=ax)
    plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
    utils.save_plot(fig, "02_state_gender_parity.png")
    
    # Save Data
    utils.save_data(state_gender, "02_state_gender_summary.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
