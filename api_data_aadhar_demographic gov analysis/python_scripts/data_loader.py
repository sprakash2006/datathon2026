import os
import pandas as pd
import numpy as np
import random
from datetime import datetime

class AadhaarDataLoader:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.raw_df = None
        self.master_df = None

    def load_raw_data(self):
        """Loads and merges all 5 CSV files."""
        files = [f for f in os.listdir(self.data_dir) if f.endswith(".csv") and "api_data_aadhar" in f]
        print(f"Loading {len(files)} data files...")
        
        dfs = []
        for f in files:
            path = os.path.join(self.data_dir, f)
            try:
                # Optimized loading: Specify types to save memory if needed
                df = pd.read_csv(path)
                dfs.append(df)
                print(f" - Loaded {f}: {len(df)} rows")
            except Exception as e:
                print(f"Error loading {f}: {e}")
        
        if dfs:
            self.raw_df = pd.concat(dfs, ignore_index=True)
            print(f"Total raw records loaded: {len(self.raw_df)}")
        else:
            raise Exception("No data files loaded!")

    def _generate_synthetic_attributes(self, row):
        """
        Helper to generate synthetic attributes based on logic.
        This enables the structural analysis for missing fields.
        """
        # 1. Gender Simulation (approx 52% Male, 48% Female in India)
        gender = np.random.choice(['Male', 'Female', 'Other'], p=[0.51, 0.48, 0.01])
        
        # 2. Biometric Modal (Fingerprint is dominant, then Iris, then OTP)
        bio_type = np.random.choice(['Fingerprint', 'Iris', 'Face', 'OTP'], p=[0.60, 0.20, 0.05, 0.15])
        
        # 3. Authentication Status & Error Codes
        # 88% Success, 12% Failure
        auth_status = np.random.choice(['Success', 'Failure'], p=[0.88, 0.12])
        error_code = '000'
        if auth_status == 'Failure':
            # Common UIDAI error codes simulation
            errors = ['300 (Biometric Mismatch)', '510 (Invalid XML)', '998 (Technical Error)', '502 (Invalid PID)']
            error_code = np.random.choice(errors, p=[0.6, 0.1, 0.2, 0.1])
            
        # 4. API Latency (Log-normal distribution to simulate real network traffic)
        # Avg around 200ms, but with long tail
        latency = int(np.random.lognormal(mean=5.3, sigma=0.6)) # ~200ms median
        if latency > 5000: latency = 5000 # Cap at 5s
        
        return pd.Series([gender, bio_type, auth_status, error_code, latency])

    def enrich_data(self):
        """
        Adds synthetic columns to the real demographic backbone.
        """
        if self.raw_df is None:
            self.load_raw_data()
            
        print("Starting synthetic data enrichment (this may take a moment)...")
        
        # Vectorized generation for performance (much faster than apply)
        n = len(self.raw_df)
        
        # Gender
        self.raw_df['gender'] = np.random.choice(['Male', 'Female', 'Other'], size=n, p=[0.51, 0.48, 0.01])
        
        # Biometric Type
        self.raw_df['auth_modality'] = np.random.choice(['Fingerprint', 'Iris', 'Face', 'OTP'], size=n, p=[0.60, 0.20, 0.05, 0.15])
        
        # Auth Status
        self.raw_df['auth_status'] = np.random.choice(['Success', 'Failure'], size=n, p=[0.88, 0.12])
        
        # Error Codes (Only for failures)
        # Initialize with '000 (Success)'
        self.raw_df['error_code'] = '000 (Success)'
        
        failure_mask = self.raw_df['auth_status'] == 'Failure'
        fail_count = failure_mask.sum()
        
        if fail_count > 0:
            errors = ['300 (Biometric Mismatch)', '510 (Invalid XML)', '998 (Technical Error)', '570 (Invalid Key)']
            self.raw_df.loc[failure_mask, 'error_code'] = np.random.choice(errors, size=fail_count, p=[0.5, 0.1, 0.3, 0.1])
            
        # API Latency (ms)
        self.raw_df['response_time_ms'] = np.random.lognormal(mean=5.3, sigma=0.6, size=n).astype(int)
        
        # Standardize Date
        self.raw_df['date'] = pd.to_datetime(self.raw_df['date'], format='%d-%m-%Y', errors='coerce')
        
        # Create 'Age_Group' dominance column (Categorical from the two counts)
        # If demo_age_5_17 > demo_age_17_ -> 'Child/Teen', else 'Adult'
        # This is a simplification for categorical analysis
        self.raw_df['dominant_age_group'] = np.where(self.raw_df['demo_age_5_17'] > self.raw_df['demo_age_17_'], '5-17', '18+')

        self.master_df = self.raw_df
        print("Enrichment complete.")
        return self.master_df

if __name__ == "__main__":
    # Test run
    loader = AadhaarDataLoader("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic")
    df = loader.enrich_data()
    print("\nMaster Dataframe Head:")
    print(df.head())
    print(f"\nFinal Shape: {df.shape}")
    print("\nColumn Types:")
    print(df.dtypes)
    
    # Save a small sample for verification
    df.head(100).to_csv("d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_demographic/enriched_sample.csv", index=False)
    print("\nSaved enriched_sample.csv for inspection.")
