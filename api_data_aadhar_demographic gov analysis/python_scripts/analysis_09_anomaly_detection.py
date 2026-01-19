import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import numpy as np

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 9: Anomaly Detection...")
    
    # 1. Temporal Anomalies (Spikes in daily volume)
    daily_vol = df.groupby('date').size().reset_index(name='count')
    daily_vol['mean'] = daily_vol['count'].mean()
    daily_vol['std'] = daily_vol['count'].std()
    
    # Z-Score > 2 is an anomaly
    daily_vol['z_score'] = (daily_vol['count'] - daily_vol['mean']) / daily_vol['std']
    anomalies = daily_vol[np.abs(daily_vol['z_score']) > 1.5] # Lower threshold for demo
    
    fig, ax = utils.setup_plot("Anomaly Detection: Daily Transaction Spikes", "Date", "Transaction Count")
    sns.lineplot(x='date', y='count', data=daily_vol, ax=ax, label='Normal Traffic')
    sns.scatterplot(x='date', y='count', data=anomalies, color='red', s=100, ax=ax, label='Anomaly (High Deviation)')
    utils.save_plot(fig, "09_temporal_anomalies.png")
    
    # 2. District Outliers (Boxplot of District Counts per State)
    # Identifying districts that are statistically way bigger than their peers in the same state
    # Filter top 5 states
    top_states = df['state'].value_counts().head(5).index
    df_dist = df[df['state'].isin(top_states)].groupby(['state', 'district']).size().reset_index(name='count')
    
    fig, ax = utils.setup_plot("Geographic Outliers: District Volume Distribution", "State", "Volume per District")
    sns.boxplot(x='state', y='count', data=df_dist, palette="Set3", ax=ax)
    sns.stripplot(x='state', y='count', data=df_dist, color='black', alpha=0.3, ax=ax)
    utils.save_plot(fig, "09_district_outliers.png")
    
    utils.save_data(anomalies, "09_anomaly_report.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
