import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_geo():
    print("Loading data for Geographic Analysis...")
    df = pd.read_parquet(DATA_FILE)

    # 1. State-wise Average Daily Enrolment Heatmap Lookalike (Bar plot sorted logic)
    # Since we don't have geospatial shapefiles readily available to plot a real map without external heavy libs (geopandas),
    # we will use a heatmap representation of "State vs Month" to show density over time and space.
    
    print("Generating State-Month Heatmap...")
    # Prepare matrix: Rows=State (Top 20), Cols=Month, Value=Total Enrolments
    
    # Filter top 20 states by volume for readability
    top_states = df.groupby('state')['total_enrolment'].sum().sort_values(ascending=False).head(20).index
    df_top = df[df['state'].isin(top_states)].copy()
    
    # Ensure month_year is proper
    df_top['month_str'] = df_top['date'].dt.strftime('%Y-%m')
    
    pivot_table = df_top.pivot_table(index='state', columns='month_str', values='total_enrolment', aggfunc='sum', fill_value=0)
    
    # Normalize by row (State) to see PEAK months per state, or raw values. 
    # Let's do raw values but widely scaled.
    
    fig, ax = plt.subplots(figsize=(16, 12))
    sns.heatmap(pivot_table, cmap="YlGnBu", linewidths=.5, annot=False, ax=ax)
    ax.set_title("Heatmap: Monthly Enrolment Intensity by State (Top 20)")
    ax.set_xlabel("Month")
    ax.set_ylabel("State")
    utils.save_plot(fig, "07_state_monthly_heatmap.png")

    # 2. District-level Variability Boxplot for Top 10 States
    # Show how spread out the enrolment is within a state's districts
    print("Generating District Variability Chart...")
    # Get district totals
    district_totals = df.groupby(['state', 'district'])['total_enrolment'].sum().reset_index()
    # Filter for top 10 states
    district_totals_top = district_totals[district_totals['state'].isin(top_states[:10])]
    
    fig, ax = plt.subplots(figsize=(14, 8))
    sns.boxplot(x='total_enrolment', y='state', data=district_totals_top, palette="Set2", ax=ax, order=top_states[:10])
    ax.set_title("Variability of District Enrolments within Top 10 States")
    ax.set_xlabel("Total Enrolments per District")
    ax.set_ylabel("State")
    utils.save_plot(fig, "08_district_variability_boxplot.png")

if __name__ == "__main__":
    analyze_geo()
