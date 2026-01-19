
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
from data_loader import load_gov_dataset

OUTPUT_DIR = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/gov_analysis/output"

def create_dashboard_assets():
    df = load_gov_dataset()
    daily = df.groupby('date')['total_transactions'].sum()
    
    # 28. "30-Day Pulse" (Last 30 days Sparkline)
    last_30 = daily.tail(30)
    plt.figure(figsize=(10, 2))
    plt.plot(last_30.values, color='#27ae60', linewidth=3)
    plt.fill_between(range(30), last_30.values, color='#27ae60', alpha=0.3)
    plt.axis('off') # Sparkline style
    plt.tight_layout()
    plt.savefig(f"{OUTPUT_DIR}/10_dashboard_sparkline.png", transparent=True)
    plt.close()

    # 29. "Victory Gauge" (Progress Assessment)
    # Hypothetical Target: 100M transactions
    current = df['total_transactions'].sum()
    target = 100_000_000
    
    plt.figure(figsize=(6, 6))
    ax = plt.subplot(111, polar=True)
    val = (current / target) * 180 # Map to 180 degrees
    # Background
    ax.barh(0, np.radians(180), color='lightgray', height=1)
    # Value
    ax.barh(0, np.radians(val), color='#f1c40f', height=1)
    ax.set_theta_zero_location('W')
    ax.set_theta_direction(-1)
    ax.set_rlabel_position(0)
    ax.set_yticks([])
    ax.set_xticks([])
    plt.text(0, -0.2, f"{current/1_000_000:.1f}M / {target/1_000_000:.0f}M", ha='center', fontsize=20, transform=ax.transAxes)
    plt.title("Annual Target Progress", y=0.8)
    plt.savefig(f"{OUTPUT_DIR}/10_dashboard_gauge.png", transparent=True)
    plt.close()

    # 30. Info Card High-Res Text (Summary)
    fig, ax = plt.subplots(figsize=(6, 4))
    ax.axis('off')
    ax.text(0.5, 0.7, "TOTAL VOLUME", ha='center', va='center', fontsize=15, color='gray')
    ax.text(0.5, 0.4, f"{current:,.0f}", ha='center', va='center', fontsize=35, weight='bold', color='#2c3e50')
    plt.savefig(f"{OUTPUT_DIR}/10_dashboard_infocard.png")
    plt.close()
    
    print("Module 10 Complete")

if __name__ == "__main__":
    create_dashboard_assets()
