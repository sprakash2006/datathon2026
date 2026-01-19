"""
Production Server for Aadhar Dashboard (Windows)
Uses Waitress to serve the Dash/Flask application securely on the local network.
"""

from waitress import serve
from app import server, load_data_on_startup
import os

if __name__ == "__main__":
    # 1. Load data (10% sample by default, change to None for full data)
    print("Initializing data pipeline...")
    load_data_on_startup(sample_frac=0.1)
    
    # 2. Start Waitress Server
    port = int(os.environ.get("PORT", 8050))
    print(f"\n================================================================================")
    print(f"🚀 PRODUCTION SERVER STARTING")
    print(f"📡 Serving on: http://0.0.0.0:{port}")
    print(f"💡 Access it using your computer's IP address on the local network.")
    print(f"================================================================================\n")
    
    serve(server, host="0.0.0.0", port=port, threads=4)
