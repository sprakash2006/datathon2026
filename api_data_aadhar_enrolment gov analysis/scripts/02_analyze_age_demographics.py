import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_age():
    print("Loading data for Age Analysis...")
    df = pd.read_parquet(DATA_FILE)

    # Calculate Totals
    total_0_5 = df['age_0_5'].sum()
    total_5_17 = df['age_5_17'].sum()
    total_18_plus = df['age_18_greater'].sum()
    
    # 1. Overall Age Distribution (Pie Chart)
    print("Generating Age Distribution Pie Chart...")
    labels = ['0-5 Years', '5-17 Years', '18+ Years']
    sizes = [total_0_5, total_5_17, total_18_plus]
    explode = (0.1, 0, 0)  # explode 1st slice for emphasis (infants)

    fig, ax = plt.subplots(figsize=(10, 8))
    ax.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
            shadow=True, startangle=140, colors=[utils.COLORS['primary'], utils.COLORS['secondary'], utils.COLORS['tertiary']])
    ax.set_title("Overall Age Group Distribution of Enrolments")
    utils.save_plot(fig, "04_age_group_distribution_pie.png")

    # 2. Age Group Contribution by State (Stacked Bar - Top 10 States by Volume)
    print("Generating Age Stacked Bar Chart...")
    # Get top 10 states
    top_states = df.groupby('state')['total_enrolment'].sum().sort_values(ascending=False).head(10).index
    
    # Aggregate age columns by state
    age_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    state_age = df[df['state'].isin(top_states)].groupby('state')[age_cols].sum()
    # Sort by total
    state_age['total'] = state_age.sum(axis=1)
    state_age = state_age.sort_values('total', ascending=False).drop(columns='total')

    # Plot
    fig, ax = plt.subplots(figsize=(14, 8))
    state_age.plot(kind='bar', stacked=True, ax=ax, width=0.8, color=[utils.COLORS['primary'], utils.COLORS['secondary'], utils.COLORS['tertiary']])
    ax.set_title("Age Group Composition in Top 10 States")
    ax.set_ylabel("Number of Enrolments")
    ax.set_xlabel("State")
    ax.legend(["0-5 Years", "5-17 Years", "18+ Years"])
    utils.save_plot(fig, "05_age_composition_by_state.png")

    # 3. Trends in Infant Enrolment (0-5) over Time (Monthly)
    print("Generating Infant Enrolment Trend...")
    # Group by month
    # We need to reconstruct date if month_year is object/period
    if 'month_year' not in df.columns or not pd.api.types.is_period_dtype(df['month_year']):
         df['month_year'] = df['date'].dt.to_period('M')
    
    monthly_trend = df.groupby('month_year')['age_0_5'].sum()
    monthly_trend.index = monthly_trend.index.astype(str) # convert to string for plotting

    fig, ax = plt.subplots(figsize=(14, 6))
    sns.lineplot(x=monthly_trend.index, y=monthly_trend.values, marker='o', linewidth=2.5, color=utils.COLORS['primary'], ax=ax)
    plt.xticks(rotation=45)
    ax.set_title("Monthly Trend of Infant Enrolments (0-5 Years)")
    ax.set_ylabel("Enrolments")
    ax.set_xlabel("Month")
    ax.grid(True, linestyle='--', alpha=0.7)
    utils.save_plot(fig, "06_infant_enrolment_trend.png")

if __name__ == "__main__":
    analyze_age()
