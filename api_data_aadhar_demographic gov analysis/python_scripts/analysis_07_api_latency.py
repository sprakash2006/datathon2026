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
    print("Running Analysis 7: API Latency & Performance...")
    
    # 1. Latency Distribution (Histogram with P95/P99 markers)
    latency = df['response_time_ms']
    p95 = np.percentile(latency, 95)
    p99 = np.percentile(latency, 99)
    avg = np.mean(latency)
    
    fig, ax = utils.setup_plot("System Latency Distribution (Response Time)", "Response Time (ms)", "Frequency")
    sns.histplot(latency, bins=50, kde=True, color=utils.colors['primary'], ax=ax)
    ax.axvline(p95, color='orange', linestyle='--', label=f'P95: {p95:.0f}ms')
    ax.axvline(p99, color='red', linestyle='--', label=f'P99: {p99:.0f}ms')
    ax.legend()
    utils.save_plot(fig, "07_latency_distribution.png")
    
    # 2. Latency by State (Infrastructure bottleneck identification)
    # Boxplot to show spread per state
    top_states = df['state'].value_counts().head(10).index
    df_top = df[df['state'].isin(top_states)]
    
    fig, ax = utils.setup_plot("Infrastructure Performance: Latency by State", "State", "Response Time (ms)")
    sns.boxplot(x='state', y='response_time_ms', data=df_top, palette="Set2", showfliers=False, ax=ax)
    plt.xticks(rotation=45)
    utils.save_plot(fig, "07_state_latency_performance.png")
    
    # 3. Latency vs Failure Correlation (Does slow response cause timeout failures?)
    # Compare avg latency of Success vs Failure
    status_perf = df.groupby('auth_status')['response_time_ms'].mean()
    
    fig, ax = utils.setup_plot("Impact of Latency on Authentication Success", "Average Response Time (ms)", "Status")
    sns.barplot(x=status_perf.index, y=status_perf.values, palette=['#e74c3c', '#2ecc71'], ax=ax)
    utils.save_plot(fig, "07_latency_vs_success.png")

    utils.save_data(status_perf.to_frame(), "07_latency_summary.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
