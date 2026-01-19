import sys
import os
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from data_loader import AadhaarDataLoader
from analysis import analysis_utils as utils

def run_analysis(df):
    print("Running Analysis 5: Biometric Performance...")
    
    # 1. Modality Usage Market Share
    modality_counts = df['auth_modality'].value_counts()
    
    fig, ax = utils.setup_plot("Biometric Modality Usage Share", "", "")
    ax.pie(modality_counts, labels=modality_counts.index, autopct='%1.1f%%', colors=utils.colors['categorical'], startangle=90)
    utils.save_plot(fig, "05_modality_share.png")
    
    # 2. Failure Rate by Modality (Reliability Score)
    # Calculate % Failure for each modality
    metrics = df.groupby('auth_modality')['auth_status'].value_counts(normalize=True).unstack().fillna(0)
    metrics['Failure_Rate_Pct'] = metrics['Failure'] * 100
    metrics = metrics.sort_values('Failure_Rate_Pct', ascending=False)
    
    fig, ax = utils.setup_plot("Reliability Gap: Failure Rate by Modality (%)", "Failure Rate (%)", "Modality")
    sns.barplot(x=metrics.index, y=metrics['Failure_Rate_Pct'], hue=metrics.index, palette="Reds_r", legend=False, ax=ax)
    
    # Add value labels
    for i, v in enumerate(metrics['Failure_Rate_Pct']):
        ax.text(i, v + 0.5, f"{v:.1f}%", ha='center', fontsize=12)
        
    utils.save_plot(fig, "05_modality_failure_rates.png")
    
    # 3. Modality Preference by Age Group (Do Kids use Blue/Iris more?)
    # Group by Dominant Age Group and Modality
    if 'dominant_age_group' in df.columns:
        age_modality = pd.crosstab(df['dominant_age_group'], df['auth_modality'], normalize='index') * 100
        
        fig, ax = utils.setup_plot("Modality Preference by Age Demographics", "Percentage Usage", "Age Group")
        age_modality.plot(kind='bar', stacked=True, colormap='Accent', ax=ax)
        plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
        utils.save_plot(fig, "05_age_modality_preference.png")
        
    utils.save_data(metrics, "05_biometric_performance_summary.csv")

if __name__ == "__main__":
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    run_analysis(df)
