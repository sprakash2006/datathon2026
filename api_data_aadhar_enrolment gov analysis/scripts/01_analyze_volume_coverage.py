import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_volume():
    print("Loading data for Volume Analysis...")
    df = pd.read_parquet(DATA_FILE)

    # 1. Total Enrolment by State (Top 15)
    print("Generating State Volume Chart...")
    state_totals = df.groupby('state')['total_enrolment'].sum().sort_values(ascending=False).head(15)
    
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.barplot(x=state_totals.values, y=state_totals.index, palette=utils.COLORS['palette_sequential'], ax=ax)
    ax.set_title('Top 15 States by Total Aadhaar Enrolments')
    ax.set_xlabel('Total Enrolments')
    ax.set_ylabel('State')
    for i, v in enumerate(state_totals.values):
        ax.text(v + (v*0.01), i, f'{v:,.0f}', va='center', fontsize=10)
    utils.save_plot(fig, "01_top_15_states_volume.png")

    # 2. Total Enrolment by District (Top 20)
    print("Generating District Volume Chart...")
    district_totals = df.groupby(['state', 'district'])['total_enrolment'].sum().reset_index()
    district_totals['label'] = district_totals['district'] + " (" + district_totals['state'] + ")"
    top_districts = district_totals.sort_values('total_enrolment', ascending=False).head(20)

    fig, ax = plt.subplots(figsize=(14, 10))
    sns.barplot(x='total_enrolment', y='label', data=top_districts, palette="viridis", ax=ax)
    ax.set_title('Top 20 Districts by Total Aadhaar Enrolments')
    ax.set_xlabel('Total Enrolments')
    ax.set_ylabel('District (State)')
    utils.save_plot(fig, "02_top_20_districts_volume.png")

    # 3. Rural vs Urban Proxy (using District names that contain 'Rural' or 'Urban' if any, OR simply distribution of volume)
    # Since we don't have explicit R/U flag, we visualize the distribution density of district-level enrolments
    print("Generating Enrolment Distribution Density...")
    fig, ax = plt.subplots(figsize=(12, 6))
    sns.histplot(district_totals['total_enrolment'], bins=50, kde=True, color=utils.COLORS['primary'], ax=ax)
    ax.set_title('Distribution of Enrolment Volumes across Districts')
    ax.set_xlabel('Total Enrolments')
    ax.set_ylabel('Frequency (Number of Districts)')
    utils.save_plot(fig, "03_district_volume_distribution.png")

if __name__ == "__main__":
    analyze_volume()
