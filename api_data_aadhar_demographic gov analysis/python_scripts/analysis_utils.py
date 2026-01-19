import matplotlib.pyplot as plt
import seaborn as sns
import os

# Government-Grade Style Configuration
plt.style.use('seaborn-v0_8-whitegrid')
sns.set_context("talk") # Larger fonts for readability in reports

# Official Govt/Report Color Palette
colors = {
    'primary': '#1f77b4', # Blue
    'secondary': '#ff7f0e', # Orange
    'success': '#2ca02c', # Green
    'danger': '#d62728', # Red
    'neutral': '#7f7f7f', # Gray
    'categorical': sns.color_palette("tab10")
}

def setup_plot(title, xlabel, ylabel, figsize=(12, 7)):
    """Standardizes plot setup."""
    fig, ax = plt.subplots(figsize=figsize)
    ax.set_title(title, fontsize=16, fontweight='bold', pad=20)
    ax.set_xlabel(xlabel, fontsize=12, labelpad=10)
    ax.set_ylabel(ylabel, fontsize=12, labelpad=10)
    return fig, ax

def save_plot(fig, filename, subfolder=""):
    """Saves plot to the appropriate output directory."""
    base_dir = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic/output/visualizations"
    target_dir = os.path.join(base_dir, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    path = os.path.join(target_dir, filename)
    fig.tight_layout()
    fig.savefig(path, dpi=300, bbox_inches='tight')
    print(f"Saved visualization: {path}")
    plt.close(fig)

def save_data(df, filename, subfolder=""):
    """Saves analysis summary data."""
    base_dir = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic/output/reports"
    target_dir = os.path.join(base_dir, subfolder)
    os.makedirs(target_dir, exist_ok=True)
    
    path = os.path.join(target_dir, filename)
    df.to_csv(path, index=True)
    print(f"Saved report data: {path}")
