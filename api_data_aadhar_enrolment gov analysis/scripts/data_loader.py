import pandas as pd
import glob
import os
import datetime

# Configuration
DATA_DIR = r"d:\Durgesh Projects\Data-Hackethon\api_data_aadhar_enrolment"
OUTPUT_FILE = os.path.join(DATA_DIR, "processed_aadhar_data.parquet")

def load_and_process_data():
    print("Searching for CSV files...")
    files = glob.glob(os.path.join(DATA_DIR, "*.csv"))
    
    if not files:
        print("Error: No CSV files found.")
        return

    print(f"Found {len(files)} files. Loading...")
    
    dfs = []
    for f in files:
        try:
            # Read CSV
            df = pd.read_csv(f)
            dfs.append(df)
            print(f"Loaded {os.path.basename(f)}: {len(df)} rows")
        except Exception as e:
            print(f"Error loading {f}: {e}")
    
    if not dfs:
        print("No data loaded.")
        return

    # Merge all dataframes
    full_df = pd.concat(dfs, ignore_index=True)
    print(f"Total raw rows: {len(full_df)}")

    # Standardize Column Names
    full_df.columns = [c.strip().lower() for c in full_df.columns]
    
    # 1. Handle Missing Values
    # Fill numeric NaNs with 0
    numeric_cols = ['age_0_5', 'age_5_17', 'age_18_greater']
    for col in numeric_cols:
        full_df[col] = full_df[col].fillna(0).astype(int)
        
    # Fill text NaNs with 'Unknown'
    text_cols = ['state', 'district']
    for col in text_cols:
        full_df[col] = full_df[col].fillna('Unknown')

    # 2. Date Conversion
    # The 'date' format appears to be YYYY-MM-DD based on inspection or needs robust parsing
    print("Converting dates...")
    full_df['date'] = pd.to_datetime(full_df['date'], errors='coerce')
    
    # Drop rows with invalid dates if any
    invalid_dates = full_df['date'].isnull().sum()
    if invalid_dates > 0:
        print(f"Warning: {invalid_dates} rows have invalid dates. Dropping them.")
        full_df = full_df.dropna(subset=['date'])

    # 3. Derived Metrics
    full_df['total_enrolment'] = full_df['age_0_5'] + full_df['age_5_17'] + full_df['age_18_greater']
    full_df['month_year'] = full_df['date'].dt.to_period('M')
    full_df['year'] = full_df['date'].dt.year

    # 4. Save Processed Data
    print(f"Saving processed data to {OUTPUT_FILE}...")
    full_df.to_parquet(OUTPUT_FILE, index=False)
    print("Data processing complete.")
    
    # Print Summary
    print("\n--- Data Summary ---")
    print(f"Total Rows: {len(full_df)}")
    print(f"Date Range: {full_df['date'].min()} to {full_df['date'].max()}")
    print(f"Total Enrolments: {full_df['total_enrolment'].sum()}")
    print(f"Unique States: {full_df['state'].nunique()}")
    print(f"Unique Districts: {full_df['district'].nunique()}")

if __name__ == "__main__":
    load_and_process_data()
