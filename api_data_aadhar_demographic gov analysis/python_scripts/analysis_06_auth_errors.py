import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 6: Authentication Errors...")
    
    # Filter only failures
    failures = df[df['auth_status'] == 'Failure']
    
    if len(failures) == 0:
        print("No failures found to analyze.")
        return

    # 1. Error Code Distribution (Pareto)
    error_counts = failures['error_code'].value_counts()
    
    fig, ax = utils.setup_plot("Top Authentication Failure Reasons", "Count of Failures", "Error Code")
    sns.barplot(x=error_counts.values, y=error_counts.index, hue=error_counts.index, palette="Reds_d", legend=False, ax=ax)
    utils.save_plot(fig, "06_error_code_distribution.png")
    
    # 2. Geographic Failure Hotspots (Which state has most technical errors?)
    # Calculate Failure Rate per State
    state_total = df['state'].value_counts()
    state_fail = failures['state'].value_counts()
    
    fail_rate = (state_fail / state_total * 100).sort_values(ascending=False).head(10)
    
    fig, ax = utils.setup_plot("Operational Risk: States with Highest Failure Rates (%)", "Failure Rate (%)", "State")
    sns.barplot(x=fail_rate.values, y=fail_rate.index, hue=fail_rate.index, palette="OrRd_r", legend=False, ax=ax)
    utils.save_plot(fig, "06_state_failure_hotspots.png")
    
    utils.save_data(error_counts, "06_error_summary.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
