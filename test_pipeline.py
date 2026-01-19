"""Test the data pipeline with a small sample."""

import sys
sys.path.insert(0, 'backend')

from data_pipeline import IntegratedAadharDataPipeline

# Initialize pipeline
pipeline = IntegratedAadharDataPipeline()

# Load with 10% sample for quick test
print("Testing with 10% sample...")
pipeline.load_all(sample_frac=0.1)

# Create integrated view
pipeline.create_integrated_view()

# Get KPIs
kpis = pipeline.get_national_kpis()

print("\n" + "=" * 80)
print("TEST RESULTS - National KPIs")
print("=" * 80)
for key, value in kpis.items():
    if isinstance(value, float):
        print(f"{key:.<50} {value:>12,.2f}")
    else:
        print(f"{key:.<50} {value:>12,}")
print("=" * 80)

print("\n✓ Data pipeline test successful!")
