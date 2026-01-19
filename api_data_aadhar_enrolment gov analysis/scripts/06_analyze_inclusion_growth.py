import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import analysis_utils as utils

# Setup
utils.setup_style()
DATA_FILE = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\processed_aadhar_data.parquet"

def analyze_inclusion():
    print("Loading data for Inclusion/Gap Analysis...")
    df = pd.read_parquet(DATA_FILE)
    
    # 1. Identify Districts with Lowest Total Enrolments (Lagging Regions)
    # Filter out districts with very low/zero data that might be data errors, but here we assume low means low coverage.
    print("Generating Lagging Districts Chart...")
    district_totals = df.groupby(['state', 'district'])['total_enrolment'].sum().reset_index()
    
    # Bottom 20 Districts (excluding 0 if we want, but let's keep them and label)
    bottom_districts = district_totals[district_totals['total_enrolment'] > 0].sort_values('total_enrolment', ascending=True).head(20)
    bottom_districts['label'] = bottom_districts['district'] + " (" + bottom_districts['state'] + ")"
    
    fig, ax = plt.subplots(figsize=(14, 10))
    sns.barplot(x='total_enrolment', y='label', data=bottom_districts, palette="Reds_r", ax=ax)
    ax.set_title("Bottom 20 Districts by Total Enrolments (Inclusion Gaps)")
    ax.set_xlabel("Total Enrolments")
    ax.set_ylabel("District (State)")
    utils.save_plot(fig, "14_bottom_20_districts_gap.png")

    # 2. Correlation between Age Groups (Children vs Adults)
    # Do districts with high adult enrolments also have high child enrolments?
    print("Generating Age Group Correlation...")
    district_age = df.groupby('district')[['age_0_5', 'age_5_17', 'age_18_greater']].sum()
    
    fig, ax = plt.subplots(figsize=(10, 8))
    sns.heatmap(district_age.corr(), annot=True, cmap="coolwarm", vmin=-1, vmax=1, ax=ax)
    ax.set_title("Correlation Matrix of Enrolment Age Groups across Districts")
    utils.save_plot(fig, "15_age_group_correlation_matrix.png")
    
    # 3. Scatter Plot: Infant (0-5) vs Adult (18+) Enrolment
    # Identifying districts focusing on newborn enrolment vs general population
    print("Generating Infant vs Adult Scatter...")
    fig, ax = plt.subplots(figsize=(10, 10))
    sns.scatterplot(data=district_age, x='age_18_greater', y='age_0_5', alpha=0.6, ax=ax, color=utils.COLORS['primary'])
    ax.set_title("District-wise Scatter: Infant (0-5) vs Adult (18+) Enrolments")
    ax.set_xlabel("Adult Enrolments")
    ax.set_ylabel("Infant Enrolments")
    ax.set_xscale('log')
    ax.set_yscale('log')
    ax.grid(True, which="both", ls="--")
    utils.save_plot(fig, "16_infant_vs_adult_scatter.png")

if __name__ == "__main__":
    analyze_inclusion()
