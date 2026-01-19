import matplotlib.pyplot as plt
import seaborn as sns
import os

# Configuration for "Government-Grade" Aesthetics
def setup_style():
    sns.set_theme(style="whitegrid")
    plt.rcParams['font.family'] = 'sans-serif'
    plt.rcParams['font.sans-serif'] = ['Arial', 'DejaVu Sans', 'Liberation Sans', 'Bitstream Vera Sans', 'sans-serif']
    plt.rcParams['axes.titlesize'] = 16
    plt.rcParams['axes.titleweight'] = 'bold'
    plt.rcParams['axes.labelsize'] = 12
    plt.rcParams['xtick.labelsize'] = 10
    plt.rcParams['ytick.labelsize'] = 10
    plt.rcParams['legend.fontsize'] = 10
    plt.rcParams['figure.figsize'] = (12, 8)
    plt.rcParams['savefig.dpi'] = 300
    plt.rcParams['savefig.bbox'] = 'tight'

def save_plot(fig, filename, output_dir=r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment\visualizations"):
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    path = os.path.join(output_dir, filename)
    fig.savefig(path)
    print(f"Saved plot to {path}")
    plt.close(fig)

COLORS = {
    'primary': '#1f77b4',      # Blue
    'secondary': '#ff7f0e',    # Orange
    'tertiary': '#2ca02c',     # Green
    'quaternary': '#d62728',   # Red
    'neutral': '#7f7f7f',      # Gray
    'palette_diverging': 'coolwarm',
    'palette_categorical': 'tab10',
    'palette_sequential': 'Blues'
}
