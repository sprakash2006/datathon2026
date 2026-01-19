
import pandas as pd
import glob
import os

DATA_PATH = "d:/Durgesh Projects/Data-Hackethon/api_data_aadhar_biometric/"

def load_gov_dataset():
    """
    Standardized loader for Government Analysis.
    Reads all CSVs, fixes dates, creates 'total_transactions' column.
    Returns: Cleaned DataFrame
    """
    files = glob.glob(os.path.join(DATA_PATH, "*.csv"))
    if not files:
        raise FileNotFoundError(f"No CSV files found in {DATA_PATH}")
    
    print(f"Loading {len(files)} source files...")
    df_list = []
    for f in files:
        try:
            df_chunk = pd.read_csv(f)
            df_list.append(df_chunk)
        except Exception as e:
            print(f"Error reading {f}: {e}")
    
    if not df_list:
        raise ValueError("Failed to load any data.")

    df = pd.concat(df_list, ignore_index=True)
    
    # 1. Date Standardization
    # Sample format: 01-03-2025
    df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
    
    # 2. Numeric Handling
    cols_to_clean = ['bio_age_5_17', 'bio_age_17_']
    for col in cols_to_clean:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
    
    # 3. Derived Columns
    df['total_transactions'] = df['bio_age_5_17'] + df['bio_age_17_']
    
    # 4. Filter Invalid Dates
    df = df.dropna(subset=['date'])
    
    row_count = len(df)
    print(f"Data Loaded Successfully: {row_count} rows, {df['total_transactions'].sum():,.0f} total transactions.")
    return df
