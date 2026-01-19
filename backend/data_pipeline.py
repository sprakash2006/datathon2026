"""
Unified Data Pipeline for Integrated Aadhar Government Dashboard
Loads and integrates all three datasets: Biometric, Demographic, and Enrolment
Total volume: ~4.94M rows across 12 CSV files
"""

import pandas as pd
import numpy as np
import glob
import os
from pathlib import Path
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')


class IntegratedAadharDataPipeline:
    """
    Unified data loader for all three Aadhar datasets with standardization,
    enrichment, and cross-dataset join capabilities.
    """
    
    def __init__(self, base_path=None):
        """
        Initialize the pipeline with base path to data folders.
        
        Args:
            base_path: Base directory containing the three dataset folders
        """
        if base_path is None:
            self.base_path = Path(__file__).parent.parent
        else:
            self.base_path = Path(base_path)
            
        self.biometric_path = self.base_path / "api_data_aadhar_biometric_gov_analysis"
        self.demographic_path = self.base_path / "api_data_aadhar_demographic gov analysis"
        self.enrolment_path = self.base_path / "api_data_aadhar_enrolment gov analysis"
        
        # State to Zone mapping for regional analysis
        self.state_to_zone = {
            'Jammu and Kashmir': 'North', 'Himachal Pradesh': 'North', 'Punjab': 'North',
            'Chandigarh': 'North', 'Uttarakhand': 'North', 'Haryana': 'North',
            'NCT of Delhi': 'North', 'Rajasthan': 'North', 'Uttar Pradesh': 'North',
            'Bihar': 'East', 'Sikkim': 'East', 'Arunachal Pradesh': 'North East',
            'Nagaland': 'North East', 'Manipur': 'North East', 'Mizoram': 'North East',
            'Tripura': 'North East', 'Meghalaya': 'North East', 'Assam': 'North East',
            'West Bengal': 'East', 'Jharkhand': 'East', 'Odisha': 'East',
            'Chhattisgarh': 'Central', 'Madhya Pradesh': 'Central',
            'Gujarat': 'West', 'Daman and Diu': 'West', 'Dadra and Nagar Haveli': 'West',
            'Maharashtra': 'West', 'Goa': 'West',
            'Andhra Pradesh': 'South', 'Karnataka': 'South', 'Kerala': 'South',
            'Tamil Nadu': 'South', 'Puducherry': 'South', 'Lakshadweep': 'South',
            'Andaman and Nicobar Islands': 'South', 'Telangana': 'South',
            'Ladakh': 'North'
        }
        
        self.biometric_df = None
        self.demographic_df = None
        self.enrolment_df = None
        self.integrated_df = None
        
    def load_biometric_data(self, sample_frac=None):
        """
        Load biometric authentication data (~1.86M rows from 4 CSV files).
        
        Args:
            sample_frac: Optional fraction to sample (0-1) for faster testing
            
        Returns:
            pd.DataFrame with biometric data
        """
        print("Loading Biometric Data...")
        
        csv_files = glob.glob(str(self.biometric_path / "api_data_aadhar_biometric_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No biometric CSV files found in {self.biometric_path}")
            
        dfs = []
        for file in csv_files:
            print(f"  Reading: {Path(file).name}")
            df = pd.read_csv(file)
            dfs.append(df)
            
        df = pd.concat(dfs, ignore_index=True)
        
        # Standardize date format
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        
        # Clean numeric columns
        df['bio_age_5_17'] = pd.to_numeric(df['bio_age_5_17'], errors='coerce').fillna(0)
        df['bio_age_17_'] = pd.to_numeric(df['bio_age_17_'], errors='coerce').fillna(0)
        
        # Derive total transactions
        df['total_transactions'] = df['bio_age_5_17'] + df['bio_age_17_']
        
        # Add zone information
        df['zone'] = df['state'].map(self.state_to_zone).fillna('Unknown')
        
        # Add temporal features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month_year'] = df['date'].dt.to_period('M').astype(str)
        
        # Sample if requested
        if sample_frac and 0 < sample_frac < 1:
            df = df.sample(frac=sample_frac, random_state=42)
            
        self.biometric_df = df
        print(f"✓ Loaded {len(df):,} biometric records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Total transactions: {df['total_transactions'].sum():,.0f}")
        
        return df
    
    def load_demographic_data(self, sample_frac=None):
        """
        Load demographic data with synthetic enrichment (~2.07M rows from 5 CSV files).
        
        Args:
            sample_frac: Optional fraction to sample (0-1)
            
        Returns:
            pd.DataFrame with demographic data including synthetic auth metrics
        """
        print("\nLoading Demographic Data...")
        
        csv_files = glob.glob(str(self.demographic_path / "api_data_aadhar_demographic_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No demographic CSV files found in {self.demographic_path}")
            
        dfs = []
        for file in csv_files:
            print(f"  Reading: {Path(file).name}")
            df = pd.read_csv(file)
            dfs.append(df)
            
        df = pd.concat(dfs, ignore_index=True)
        
        # Standardize date format
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        
        # Clean numeric columns
        df['demo_age_5_17'] = pd.to_numeric(df['demo_age_5_17'], errors='coerce').fillna(0)
        df['demo_age_17_'] = pd.to_numeric(df['demo_age_17_'], errors='coerce').fillna(0)
        
        # Derive total demographic count
        df['total_demographic'] = df['demo_age_5_17'] + df['demo_age_17_']
        
        # Synthetic enrichment (vectorized for performance)
        np.random.seed(42)
        n = len(df)
        
        # Gender distribution (51% Male, 48% Female, 1% Other)
        df['gender'] = np.random.choice(['Male', 'Female', 'Other'], 
                                       size=n, p=[0.51, 0.48, 0.01])
        
        # Auth modality (60% Fingerprint, 20% Iris, 5% Face, 15% OTP)
        df['auth_modality'] = np.random.choice(['Fingerprint', 'Iris', 'Face', 'OTP'],
                                               size=n, p=[0.60, 0.20, 0.05, 0.15])
        
        # Auth status (88% Success, 12% Failure)
        df['auth_status'] = np.random.choice(['Success', 'Failure'],
                                            size=n, p=[0.88, 0.12])
        
        # Error codes for failures only
        error_codes = np.random.choice([300, 510, 998, 570], 
                                      size=n, p=[0.45, 0.25, 0.20, 0.10])
        df['error_code'] = np.where(df['auth_status'] == 'Failure', error_codes, np.nan)
        
        # Response time (log-normal distribution, median ~200ms)
        df['response_time_ms'] = np.random.lognormal(mean=5.3, sigma=0.5, size=n).astype(int)
        df['response_time_ms'] = np.clip(df['response_time_ms'], 50, 5000)
        
        # Dominant age group
        df['dominant_age_group'] = np.where(df['demo_age_5_17'] >= df['demo_age_17_'],
                                           '5-17', '18+')
        
        # Add zone information
        df['zone'] = df['state'].map(self.state_to_zone).fillna('Unknown')
        
        # Add temporal features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month_year'] = df['date'].dt.to_period('M').astype(str)
        
        # Sample if requested
        if sample_frac and 0 < sample_frac < 1:
            df = df.sample(frac=sample_frac, random_state=42)
            
        self.demographic_df = df
        print(f"✓ Loaded {len(df):,} demographic records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Auth success rate: {(df['auth_status']=='Success').mean()*100:.1f}%")
        
        return df
    
    def load_enrolment_data(self, sample_frac=None):
        """
        Load enrolment data (~1.01M rows from 3 CSV files).
        
        Args:
            sample_frac: Optional fraction to sample (0-1)
            
        Returns:
            pd.DataFrame with enrolment data
        """
        print("\nLoading Enrolment Data...")
        
        csv_files = glob.glob(str(self.enrolment_path / "api_data_aadhar_enrolment_*.csv"))
        
        if not csv_files:
            raise FileNotFoundError(f"No enrolment CSV files found in {self.enrolment_path}")
            
        dfs = []
        for file in csv_files:
            print(f"  Reading: {Path(file).name}")
            df = pd.read_csv(file)
            dfs.append(df)
            
        df = pd.concat(dfs, ignore_index=True)
        
        # Standardize date format (handle both DD-MM-YYYY and YYYY-MM-DD)
        df['date'] = pd.to_datetime(df['date'], format='%d-%m-%Y', errors='coerce')
        if df['date'].isna().sum() > len(df) * 0.5:
            df['date'] = pd.to_datetime(df['date'], format='%Y-%m-%d', errors='coerce')
        
        # Clean numeric columns
        df['age_0_5'] = pd.to_numeric(df['age_0_5'], errors='coerce').fillna(0)
        df['age_5_17'] = pd.to_numeric(df['age_5_17'], errors='coerce').fillna(0)
        df['age_18_greater'] = pd.to_numeric(df['age_18_greater'], errors='coerce').fillna(0)
        
        # Derive total enrolment
        df['total_enrolment'] = df['age_0_5'] + df['age_5_17'] + df['age_18_greater']
        
        # Add zone information
        df['zone'] = df['state'].map(self.state_to_zone).fillna('Unknown')
        
        # Add temporal features
        df['year'] = df['date'].dt.year
        df['month'] = df['date'].dt.month
        df['day_of_week'] = df['date'].dt.day_name()
        df['week_of_year'] = df['date'].dt.isocalendar().week
        df['month_year'] = df['date'].dt.to_period('M').astype(str)
        
        # Sample if requested
        if sample_frac and 0 < sample_frac < 1:
            df = df.sample(frac=sample_frac, random_state=42)
            
        self.enrolment_df = df
        print(f"✓ Loaded {len(df):,} enrolment records")
        print(f"  Date range: {df['date'].min()} to {df['date'].max()}")
        print(f"  Total enrolments: {df['total_enrolment'].sum():,.0f}")
        print(f"  Infant enrolments (0-5): {df['age_0_5'].sum():,.0f}")
        
        return df
    
    def load_all(self, sample_frac=None):
        """
        Load all three datasets in parallel.
        
        Args:
            sample_frac: Optional fraction to sample for faster testing
            
        Returns:
            tuple: (biometric_df, demographic_df, enrolment_df)
        """
        print("=" * 80)
        print("INTEGRATED AADHAR DATA PIPELINE - LOADING ALL DATASETS")
        print("=" * 80)
        
        self.load_biometric_data(sample_frac)
        self.load_demographic_data(sample_frac)
        self.load_enrolment_data(sample_frac)
        
        print("\n" + "=" * 80)
        print("DATA LOADING SUMMARY")
        print("=" * 80)
        print(f"Biometric records:   {len(self.biometric_df):>12,}")
        print(f"Demographic records: {len(self.demographic_df):>12,}")
        print(f"Enrolment records:   {len(self.enrolment_df):>12,}")
        print(f"{'─' * 40}")
        print(f"TOTAL:               {len(self.biometric_df) + len(self.demographic_df) + len(self.enrolment_df):>12,}")
        print("=" * 80)
        
        return self.biometric_df, self.demographic_df, self.enrolment_df
    
    def create_integrated_view(self):
        """
        Create integrated DataFrame with cross-dataset aggregations by state-date.
        Enables unified analysis across all three data sources.
        
        Returns:
            pd.DataFrame with integrated metrics
        """
        print("\nCreating Integrated View...")
        
        if self.biometric_df is None or self.demographic_df is None or self.enrolment_df is None:
            raise ValueError("Load all datasets first using load_all()")
        
        # Aggregate biometric by state-date
        bio_agg = self.biometric_df.groupby(['state', 'district', 'date']).agg({
            'total_transactions': 'sum',
            'bio_age_5_17': 'sum',
            'bio_age_17_': 'sum',
            'zone': 'first'
        }).reset_index()
        bio_agg.columns = ['state', 'district', 'date', 
                           'bio_transactions', 'bio_youth', 'bio_adult', 'zone']
        
        # Aggregate demographic by state-date
        demo_agg = self.demographic_df.groupby(['state', 'district', 'date']).agg({
            'total_demographic': 'sum',
            'demo_age_5_17': 'sum',
            'demo_age_17_': 'sum',
            'auth_status': lambda x: (x == 'Success').sum() / len(x) * 100,  # Success rate
            'response_time_ms': 'median'
        }).reset_index()
        demo_agg.columns = ['state', 'district', 'date',
                           'demo_total', 'demo_youth', 'demo_adult', 
                           'auth_success_rate', 'median_latency_ms']
        
        # Aggregate enrolment by state-date
        enrol_agg = self.enrolment_df.groupby(['state', 'district', 'date']).agg({
            'total_enrolment': 'sum',
            'age_0_5': 'sum',
            'age_5_17': 'sum',
            'age_18_greater': 'sum'
        }).reset_index()
        enrol_agg.columns = ['state', 'district', 'date',
                            'enrol_total', 'enrol_infant', 'enrol_youth', 'enrol_adult']
        
        # Merge all three datasets
        integrated = bio_agg.merge(demo_agg, on=['state', 'district', 'date'], how='outer')
        integrated = integrated.merge(enrol_agg, on=['state', 'district', 'date'], how='outer')
        
        # Fill NaN values with 0 for numeric columns
        numeric_cols = integrated.select_dtypes(include=[np.number]).columns
        integrated[numeric_cols] = integrated[numeric_cols].fillna(0)
        
        # Add combined metrics
        integrated['total_activity'] = (integrated['bio_transactions'] + 
                                       integrated['demo_total'] + 
                                       integrated['enrol_total'])
        
        # Add temporal features
        integrated['year'] = integrated['date'].dt.year
        integrated['month'] = integrated['date'].dt.month
        integrated['month_year'] = integrated['date'].dt.to_period('M').astype(str)
        
        self.integrated_df = integrated
        print(f"✓ Created integrated view with {len(integrated):,} state-district-date records")
        print(f"  Unique states: {integrated['state'].nunique()}")
        print(f"  Unique districts: {integrated['district'].nunique()}")
        print(f"  Date range: {integrated['date'].min()} to {integrated['date'].max()}")
        
        return integrated
    
    def get_national_kpis(self):
        """
        Calculate top-level national KPIs for executive dashboard.
        
        Returns:
            dict: National-level metrics
        """
        kpis = {}
        
        if self.biometric_df is not None:
            kpis['total_biometric_transactions'] = self.biometric_df['total_transactions'].sum()
            kpis['active_states_biometric'] = self.biometric_df['state'].nunique()
            kpis['active_districts_biometric'] = self.biometric_df['district'].nunique()
            
        if self.demographic_df is not None:
            kpis['total_demographic_records'] = len(self.demographic_df)
            kpis['national_auth_success_rate'] = (
                (self.demographic_df['auth_status'] == 'Success').sum() / len(self.demographic_df) * 100
            )
            kpis['median_latency_ms'] = self.demographic_df['response_time_ms'].median()
            kpis['p95_latency_ms'] = self.demographic_df['response_time_ms'].quantile(0.95)
            kpis['p99_latency_ms'] = self.demographic_df['response_time_ms'].quantile(0.99)
            
        if self.enrolment_df is not None:
            kpis['total_enrolments'] = self.enrolment_df['total_enrolment'].sum()
            kpis['infant_enrolments'] = self.enrolment_df['age_0_5'].sum()
            kpis['active_states_enrolment'] = self.enrolment_df['state'].nunique()
            
        # Combined metrics
        kpis['total_data_points'] = sum([
            len(self.biometric_df) if self.biometric_df is not None else 0,
            len(self.demographic_df) if self.demographic_df is not None else 0,
            len(self.enrolment_df) if self.enrolment_df is not None else 0
        ])
        
        return kpis
    
    def export_to_parquet(self, output_dir=None):
        """
        Export all datasets to Parquet format for 3-5x faster loading.
        
        Args:
            output_dir: Directory to save Parquet files
        """
        if output_dir is None:
            output_dir = self.base_path / "parquet_cache"
        else:
            output_dir = Path(output_dir)
            
        output_dir.mkdir(exist_ok=True)
        
        print("\nExporting to Parquet format...")
        
        if self.biometric_df is not None:
            path = output_dir / "biometric.parquet"
            self.biometric_df.to_parquet(path, compression='snappy')
            print(f"✓ Saved biometric data: {path}")
            
        if self.demographic_df is not None:
            path = output_dir / "demographic.parquet"
            self.demographic_df.to_parquet(path, compression='snappy')
            print(f"✓ Saved demographic data: {path}")
            
        if self.enrolment_df is not None:
            path = output_dir / "enrolment.parquet"
            self.enrolment_df.to_parquet(path, compression='snappy')
            print(f"✓ Saved enrolment data: {path}")
            
        if self.integrated_df is not None:
            path = output_dir / "integrated.parquet"
            self.integrated_df.to_parquet(path, compression='snappy')
            print(f"✓ Saved integrated view: {path}")
            
        print(f"\nParquet files saved to: {output_dir}")


def main():
    """Demo usage of the integrated data pipeline."""
    
    # Initialize pipeline
    pipeline = IntegratedAadharDataPipeline()
    
    # Load all datasets (use sample_frac=0.1 for quick testing)
    pipeline.load_all(sample_frac=None)  # Load full data
    
    # Create integrated view
    pipeline.create_integrated_view()
    
    # Get national KPIs
    kpis = pipeline.get_national_kpis()
    
    print("\n" + "=" * 80)
    print("NATIONAL KPIs - EXECUTIVE SUMMARY")
    print("=" * 80)
    for key, value in kpis.items():
        if isinstance(value, float):
            print(f"{key:.<50} {value:>12,.2f}")
        else:
            print(f"{key:.<50} {value:>12,}")
    print("=" * 80)
    
    # Export to Parquet for faster subsequent loads
    pipeline.export_to_parquet()
    
    print("\n✓ Data pipeline initialization complete!")
    print("  All datasets loaded and ready for dashboard integration.")


if __name__ == "__main__":
    main()
