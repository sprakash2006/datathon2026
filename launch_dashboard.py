"""
Quick Launcher for Aadhar Dashboard
Handles compatibility and provides clear startup messages
"""

import sys
import os

# Add paths
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'components'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'analytics'))

print("=" * 80)
print("🇮🇳 AADHAR GOVERNMENT DASHBOARD - INITIALIZING")
print("=" * 80)
print(f"Python Version: {sys.version}")
print(f"Working Directory: {os.getcwd()}")
print("=" * 80)

try:
    print("\n[1/5] Importing dependencies...")
    import dash
    from dash import dcc, html
    import dash_bootstrap_components as dbc
    import plotly.graph_objects as go
    import pandas as pd
    import numpy as np
    print("✓ Dependencies loaded successfully")
    
    print("\n[2/5] Loading data pipeline...")
    from data_pipeline import IntegratedAadharDataPipeline
    print("✓ Data pipeline module loaded")
    
    print("\n[3/5] Initializing data (10% sample for fast startup)...")
    pipeline = IntegratedAadharDataPipeline()
    biometric_df, demographic_df, enrolment_df = pipeline.load_all(sample_frac=0.1)
    integrated_df = pipeline.create_integrated_view()
    kpis = pipeline.get_national_kpis()
    print("✓ Data loaded successfully")
    
    print("\n[4/5] Dashboard Statistics:")
    print(f"  • Biometric records: {len(biometric_df):,}")
    print(f"  • Demographic records: {len(demographic_df):,}")
    print(f"  • Enrolment records: {len(enrolment_df):,}")
    print(f"  • Total data points: {kpis['total_data_points']:,}")
    print(f"  • Auth success rate: {kpis['national_auth_success_rate']:.1f}%")
    print(f"  • Active states: {kpis['active_states_biometric']}")
    
    print("\n[5/5] Starting dashboard server...")
    print("\n" + "=" * 80)
    print("✅ DASHBOARD READY!")
    print("=" * 80)
    print("\n📊 Access the dashboard at:")
    print("   🔗 http://127.0.0.1:8050")
    print("\n⚙️  Features available:")
    print("   • Executive KPIs (8 cards)")
    print("   • Strategic Overview (Zonal distribution, State performance)")
    print("   • Operational Monitoring (Modality, Errors, Latency, Temporal)")
    print("   • Geographic Deep-Dive (Lorenz curve, Inclusion gaps)")
    print("   • Predictive Analytics (Anomalies, Forecasts, Correlations)")
    print("\n💡 Tip: Press Ctrl+C to stop the server")
    print("=" * 80 + "\n")
    
    # Now import and run the full app
    exec(open('app.py').read())
    
except ImportError as e:
    print(f"\n❌ ERROR: Missing dependency")
    print(f"   {str(e)}")
    print("\n💡 Solution: Install requirements")
    print("   pip install -r requirements.txt")
    sys.exit(1)
    
except FileNotFoundError as e:
    print(f"\n❌ ERROR: Data files not found")
    print(f"   {str(e)}")
    print("\n💡 Solution: Ensure CSV files are in the correct directories")
    sys.exit(1)
    
except Exception as e:
    print(f"\n❌ ERROR: {type(e).__name__}")
    print(f"   {str(e)}")
    print("\n💡 Check the error details above")
    import traceback
    traceback.print_exc()
    sys.exit(1)
