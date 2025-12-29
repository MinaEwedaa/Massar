"""Analyze why the model is performing poorly."""
import pandas as pd

df = pd.read_csv('../cleaned_transport_dataset.csv')

print("="*60)
print("MODEL PERFORMANCE ANALYSIS")
print("="*60)

print(f"\nDataset Size: {len(df)} rows")
print(f"Training samples (80%): {int(len(df) * 0.8)}")
print(f"Test samples (20%): {int(len(df) * 0.2)}")

print("\n" + "="*60)
print("PROBLEM 1: TOO LITTLE DATA")
print("="*60)
print(f"❌ Only {len(df)} rows is WAY too small for 13 features!")
print("   Rule of thumb: Need 10-20 samples per feature")
print(f"   You have: {len(df)} samples / 13 features = {len(df)/13:.1f} samples per feature")
print("   Recommended: At least 130-260 samples per feature = 1,690-3,380 total rows")

print("\n" + "="*60)
print("PROBLEM 2: POOR MODEL QUALITY")
print("="*60)
print("❌ R² Score: 0.26 (only explains 26% of variance)")
print("   Good models have R² > 0.7")
print("❌ Test RMSE: 221 minutes (average error)")
print("❌ Test MAE: 107 minutes (mean absolute error)")

print("\n" + "="*60)
print("PROBLEM 3: HIGH VARIANCE IN TARGET")
print("="*60)
print(f"Delay range: {df['delay_minutes'].min():.1f} to {df['delay_minutes'].max():.1f} minutes")
print(f"Standard deviation: {df['delay_minutes'].std():.1f} minutes")
print(f"Mean: {df['delay_minutes'].mean():.1f} minutes")
print(f"\nNegative delays (early): {(df['delay_minutes'] < 0).sum()} ({(df['delay_minutes'] < 0).sum()/len(df)*100:.1f}%)")
print(f"Zero delays: {(df['delay_minutes'] == 0).sum()} ({(df['delay_minutes'] == 0).sum()/len(df)*100:.1f}%)")
print(f"Delays > 100 min: {(df['delay_minutes'] > 100).sum()} ({(df['delay_minutes'] > 100).sum()/len(df)*100:.1f}%)")

print("\n" + "="*60)
print("WHY PREDICTIONS ARE ~127 MINUTES")
print("="*60)
print("The model has a huge intercept (953 minutes) and is predicting")
print("near the 75th percentile (119 min) because it can't learn patterns")
print("from such a small, noisy dataset.")

print("\n" + "="*60)
print("SOLUTIONS")
print("="*60)
print("1. ✅ Collect MORE DATA (at least 1,000-5,000 rows)")
print("2. ✅ Try different algorithms (Random Forest, XGBoost)")
print("3. ✅ Feature engineering (remove outliers, normalize)")
print("4. ✅ Use simpler model (just predict median/mean for now)")
print("="*60)

