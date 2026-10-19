"""
PaySphere FinTech Pvt. Ltd. - Round 2: Data Cleaning, Merging & Exploratory Data Analysis
Addresses:
1. Data Audits: Check types, missing values, duplicates, unusual values.
2. Cleaning & Combining:
   - Deduplicate transaction IDs
   - Standardize channel labels
   - Impute/harmonize missing merchant categories
   - Address extreme/invalid amounts (negatives, zeroes, extreme outliers)
   - Handle incomplete device history
   - Combine all 5 datasets at transaction level
3. Exploratory Data Analysis & Visualizations addressing the 6 specific analytical questions:
   - Normal amount ranges by segment
   - Hourly transaction volume and unusual spikes
   - New devices vs known devices
   - Merchant categories and alert prevalence
   - Regional spikes and cross-region patterns
   - Patterns preceding manual review
"""
   
import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# Set overall plotting styling
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['font.sans-serif'] = 'Helvetica, Arial, DejaVu Sans'
plt.rcParams['axes.edgecolor'] = '#CCCCCC'
plt.rcParams['axes.linewidth'] = 0.8

BASE_DIR = "/Users/navins/Documents/DS_SPRINT"
RAW_DIR = os.path.join(BASE_DIR, "data/raw")
PROC_DIR = os.path.join(BASE_DIR, "data/processed")
FIG_DIR = os.path.join(BASE_DIR, "reports/figures")

os.makedirs(PROC_DIR, exist_ok=True)
os.makedirs(FIG_DIR, exist_ok=True)

print("="*70)
print("STEP 1: LOADING RAW DATASETS")
print("="*70)

tx_df = pd.read_csv(os.path.join(RAW_DIR, "transactions.csv"))
cust_df = pd.read_csv(os.path.join(RAW_DIR, "customers.csv"))
dev_df = pd.read_csv(os.path.join(RAW_DIR, "devices.csv"))
merch_df = pd.read_csv(os.path.join(RAW_DIR, "merchants.csv"))
alt_df = pd.read_csv(os.path.join(RAW_DIR, "alerts.csv"))

print(f"Transactions Raw Shape: {tx_df.shape}")
print(f"Customers Raw Shape:    {cust_df.shape}")
print(f"Devices Raw Shape:      {dev_df.shape}")
print(f"Merchants Raw Shape:    {merch_df.shape}")
print(f"Alerts Raw Shape:       {alt_df.shape}")

print("\n" + "="*70)
print("STEP 2: DATA AUDIT - QUALITY CONDITIONS CHECK")
print("="*70)

# 2.1 Duplicate Transaction IDs
tx_dups = tx_df['transaction_id'].duplicated().sum()
print(f"[Audit] Duplicate Transaction IDs: {tx_dups:,} ({tx_dups/len(tx_df)*100:.2f}%)")

# 2.2 Missing Merchant Categories
tx_missing_mcat = tx_df['merchant_category'].isna().sum()
merch_missing_mcat = merch_df['merchant_category'].isna().sum()
print(f"[Audit] Missing Merchant Categories in Transactions: {tx_missing_mcat:,} ({tx_missing_mcat/len(tx_df)*100:.2f}%)")
print(f"[Audit] Missing Merchant Categories in Merchants:     {merch_missing_mcat:,} ({merch_missing_mcat/len(merch_df)*100:.2f}%)")

# 2.3 Inconsistent Channel Labels
raw_channels = tx_df['channel'].value_counts()
print("\n[Audit] Raw Channel Distribution (Notice casing/formatting inconsistencies):")
for ch, cnt in raw_channels.items():
    print(f"   - {ch:<16}: {cnt:,}")

# 2.4 Extreme Amounts
neg_amounts = (tx_df['amount'] < 0).sum()
zero_amounts = (tx_df['amount'] == 0).sum()
p99_amount = tx_df['amount'].quantile(0.99)
extreme_high = (tx_df['amount'] > 10000).sum()
print(f"\n[Audit] Negative Amounts (Refund/Glitch): {neg_amounts:,}")
print(f"[Audit] Zero Amounts:                     {zero_amounts:,}")
print(f"[Audit] 99th Percentile Amount:            ${p99_amount:,.2f}")
print(f"[Audit] Extreme Outliers (> $10,000):      {extreme_high:,} (Max: ${tx_df['amount'].max():,.2f})")

# 2.5 Incomplete Device History
missing_dev = tx_df['device_id'].isna().sum()
print(f"[Audit] Incomplete/Missing Device History: {missing_dev:,} ({missing_dev/len(tx_df)*100:.2f}%)")

print("\n" + "="*70)
print("STEP 3: DATA CLEANING & STANDARDIZATION")
print("="*70)

# 3.1 Deduplicate Transactions (Keep first occurrence)
cleaned_tx = tx_df.drop_duplicates(subset=['transaction_id'], keep='first').copy()
print(f"[Clean] Deduplicated transactions: {len(tx_df):,} -> {len(cleaned_tx):,}")

# 3.2 Standardize Channel Labels
def standardize_channel(val):
    if pd.isna(val):
        return 'Unknown'
    v = str(val).strip().lower().replace('-', '_').replace(' ', '_')
    if 'mobile' in v or 'app' in v:
        return 'Mobile App'
    elif 'web' in v or 'portal' in v:
        return 'Web Portal'
    elif 'pos' in v or 'pointofsale' in v:
        return 'POS Terminal'
    elif 'api' in v:
        return 'API Gateway'
    else:
        return 'Other'

cleaned_tx['channel_clean'] = cleaned_tx['channel'].apply(standardize_channel)
print("[Clean] Standardized Channel Labels:")
print(cleaned_tx['channel_clean'].value_counts())

# 3.3 Harmonize & Impute Missing Merchant Categories
# Map merchant categories from merchants.csv where missing in transactions.csv
merch_clean_lookup = merch_df.set_index('merchant_id')['merchant_category'].to_dict()
cleaned_tx['merchant_category_clean'] = cleaned_tx['merchant_category'].fillna(
    cleaned_tx['merchant_id'].map(merch_clean_lookup)
)
# Impute any residual unmapped categories with 'Uncategorized / Other'
cleaned_tx['merchant_category_clean'] = cleaned_tx['merchant_category_clean'].fillna('Uncategorized / Other')
print(f"[Clean] Missing Merchant Categories after harmonization: {cleaned_tx['merchant_category_clean'].isna().sum()}")

# 3.4 Handle Extreme & Erroneous Amounts
# Record amount anomaly flags
cleaned_tx['is_negative_amount'] = (cleaned_tx['amount'] < 0).astype(int)
cleaned_tx['is_zero_amount'] = (cleaned_tx['amount'] == 0).astype(int)
cleaned_tx['is_extreme_amount'] = (cleaned_tx['amount'] > 10000).astype(int)

# For quantitative modelling: convert negative amounts to absolute magnitude with flag
cleaned_tx['amount_clean'] = cleaned_tx['amount'].apply(lambda x: abs(x) if x != 0 else 0.01)

# Log-transformed amount for stabilization
cleaned_tx['amount_log'] = np.log1p(cleaned_tx['amount_clean'])

# 3.5 Handle Incomplete Device History
cleaned_tx['device_id_clean'] = cleaned_tx['device_id'].fillna('DEV_UNTRACKED')
cleaned_tx['has_device_history'] = (cleaned_tx['device_id'].notna()).astype(int)

# 3.6 Parse Timestamps
cleaned_tx['timestamp'] = pd.to_datetime(cleaned_tx['timestamp'])
cleaned_tx['hour'] = cleaned_tx['timestamp'].dt.hour
cleaned_tx['day_of_week'] = cleaned_tx['timestamp'].dt.day_name()
cleaned_tx['is_weekend'] = cleaned_tx['timestamp'].dt.weekday.isin([5, 6]).astype(int)
cleaned_tx['is_night_hours'] = cleaned_tx['hour'].isin([0, 1, 2, 3, 4, 5]).astype(int)

print("\n" + "="*70)
print("STEP 4: COMBINING DATASETS AT TRANSACTION LEVEL")
print("="*70)

# Merge Customers
master_df = cleaned_tx.merge(
    cust_df.rename(columns={'region': 'customer_region'}),
    on='customer_id',
    how='left'
)

# Merge Merchants
master_df = master_df.merge(
    merch_df[['merchant_id', 'merchant_name', 'region']].rename(columns={'region': 'merchant_region'}),
    on='merchant_id',
    how='left'
)

# Merge Devices
# Note: Deduplicate devices table by device_id in case a device was mapped multiple times
dev_unique = dev_df.drop_duplicates(subset=['device_id']).copy()
master_df = master_df.merge(
    dev_unique[['device_id', 'device_type', 'new_device_flag']],
    left_on='device_id_clean',
    right_on='device_id',
    how='left'
)

# Fill untracked device attributes
master_df['device_type'] = master_df['device_type'].fillna('Untracked/Legacy')
# -1 indicates untracked device history, 0 = known, 1 = new device
master_df['new_device_flag'] = master_df['new_device_flag'].fillna(-1).astype(int)

# Merge Alerts
# Deduplicate alerts by transaction_id (taking the first alert log per transaction)
alt_unique = alt_df.drop_duplicates(subset=['transaction_id']).copy()
master_df = master_df.merge(
    alt_unique[['transaction_id', 'alert_id', 'review_status', 'reason_category']],
    on='transaction_id',
    how='left'
)

# Operational target indicator: Was this transaction alerted for operational review?
master_df['is_alerted'] = master_df['alert_id'].notna().astype(int)
master_df['review_status'] = master_df['review_status'].fillna('Not_Alerted')
master_df['reason_category'] = master_df['reason_category'].fillna('None')

# Drop redundant raw device_id column from merge
if 'device_id_y' in master_df.columns:
    master_df = master_df.drop(columns=['device_id_y'])
master_df = master_df.rename(columns={'device_id_x': 'device_id'})

print(f"Consolidated Master Transactions Shape: {master_df.shape}")
print(f"Total Alerted Transactions: {master_df['is_alerted'].sum():,} ({master_df['is_alerted'].mean()*100:.2f}%)")

# Compute geographic consistency
master_df['is_region_mismatch'] = (master_df['customer_region'] != master_df['merchant_region']).astype(int)

# Save cleaned master dataset
master_clean_path = os.path.join(PROC_DIR, "cleaned_transactions_master.csv")
master_df.to_csv(master_clean_path, index=False)
print(f"Saved Cleaned Master Dataset to: {master_clean_path}")

print("\n" + "="*70)
print("STEP 5: USE-CASE-SPECIFIC ANALYTICAL QUESTIONS & VISUALIZATIONS")
print("="*70)

# Palette definitions for crisp visuals
fintech_palette = ["#1E3A8A", "#0D9488", "#F59E0B", "#EF4444", "#8B5CF6"]
alert_palette = {"Not_Alerted": "#94A3B8", "Approved": "#10B981", "Closed_Benign": "#3B82F6", 
                 "Under_Investigation": "#F59E0B", "Flagged_Fraud": "#EF4444"}

# -------------------------------------------------------------------
# Q1: What are normal amount ranges by segment?
# -------------------------------------------------------------------
print("\n--- Q1: Normal Amount Ranges by Customer Segment ---")
seg_stats = master_df.groupby('customer_segment')['amount_clean'].agg(
    Count='count',
    Mean='mean',
    Std='std',
    Median='median',
    IQR=lambda x: x.quantile(0.75) - x.quantile(0.25),
    P5=lambda x: x.quantile(0.05),
    P25=lambda x: x.quantile(0.25),
    P75=lambda x: x.quantile(0.75),
    P95=lambda x: x.quantile(0.95),
    P99=lambda x: x.quantile(0.99)
).reset_index()
print(seg_stats.to_string(index=False))

plt.figure(figsize=(12, 6))
# Filter out extreme outliers for clean boxplot visibility
plot_data_q1 = master_df[master_df['amount_clean'] <= master_df['amount_clean'].quantile(0.98)]
ax = sns.boxplot(
    data=plot_data_q1,
    x='customer_segment',
    y='amount_clean',
    palette='Blues_d',
    showmeans=True,
    meanprops={"marker":"o", "markerfacecolor":"red", "markeredgecolor":"red", "markersize":"6"}
)
plt.title("Normal Transaction Amount Distributions by Customer Segment\n(Red Dot = Mean, Central Box = IQR (P25 - P75), Whiskers = 1.5x IQR)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Customer Segment", fontsize=11, fontweight='semibold')
plt.ylabel("Transaction Amount ($)", fontsize=11, fontweight='semibold')
plt.grid(True, linestyle='--', alpha=0.5)

# Annotate normal median ranges
for idx, row in seg_stats.iterrows():
    ax.text(idx, row['P75'] * 1.15, f"Median: ${row['Median']:.1f}\nP25-P75: [${row['P25']:.1f}-${row['P75']:.1f}]", 
            ha='center', fontsize=9, fontweight='semibold', bbox=dict(boxstyle="round,pad=0.3", fc="#EFF6FF", ec="#3B82F6", lw=1))

plt.tight_layout()
fig1_path = os.path.join(FIG_DIR, "01_normal_amount_ranges_by_segment.png")
plt.savefig(fig1_path, dpi=300)
plt.close()
print(f"Saved: {fig1_path}")

# -------------------------------------------------------------------
# Q2: Which hours show unusual volume & alert rates?
# -------------------------------------------------------------------
print("\n--- Q2: Hourly Volume & Alert Rate Patterns ---")
hourly_stats = master_df.groupby('hour').agg(
    Total_Transactions=('transaction_id', 'count'),
    Alerted_Transactions=('is_alerted', 'sum'),
    Total_Volume=('amount_clean', 'sum'),
    Average_Amount=('amount_clean', 'mean')
).reset_index()
hourly_stats['Alert_Rate_Pct'] = (hourly_stats['Alerted_Transactions'] / hourly_stats['Total_Transactions']) * 100
print(hourly_stats[['hour', 'Total_Transactions', 'Alerted_Transactions', 'Alert_Rate_Pct']].to_string(index=False))

fig, ax1 = plt.subplots(figsize=(13, 6))

color = '#1E3A8A'
ax1.set_xlabel('Hour of Day (24h Clock)', fontsize=11, fontweight='semibold')
ax1.set_ylabel('Total Transaction Count', color=color, fontsize=11, fontweight='semibold')
bars = ax1.bar(hourly_stats['hour'], hourly_stats['Total_Transactions'], color=color, alpha=0.75, width=0.6, label='Transaction Count')
ax1.tick_params(axis='y', labelcolor=color)
ax1.set_xticks(range(24))

ax2 = ax1.twinx()
color = '#DC2626'
ax2.set_ylabel('Operational Alert Rate (%)', color=color, fontsize=11, fontweight='semibold')
line = ax2.plot(hourly_stats['hour'], hourly_stats['Alert_Rate_Pct'], color=color, marker='o', linewidth=2.5, label='Alert Rate (%)')
ax2.tick_params(axis='y', labelcolor=color)
ax2.grid(False)

# Highlight unusual midnight window (1:00 AM - 4:00 AM)
ax1.axvspan(0.5, 4.5, color='#FEE2E2', alpha=0.6, label='Unusual Alert Spike Window (1 AM - 4 AM)')

plt.title("Hourly Transaction Volume vs. Operational Alert Rate\n(Significant Alert Risk Spike during Off-Hours: 01:00 - 04:00)", fontsize=13, fontweight='bold', pad=12)
fig.tight_layout()
fig2_path = os.path.join(FIG_DIR, "02_hourly_volume_and_unusual_night_spikes.png")
plt.savefig(fig2_path, dpi=300)
plt.close()
print(f"Saved: {fig2_path}")

# -------------------------------------------------------------------
# Q3: How do new devices differ from known devices?
# -------------------------------------------------------------------
print("\n--- Q3: New Devices vs. Known Devices Comparison ---")
# Device status mapping: 1: New Device, 0: Known Device, -1: Untracked / Incomplete History
dev_labels = {1: 'New Device (<7d)', 0: 'Known Trusted Device', -1: 'Untracked/Incomplete History'}
master_df['device_status_label'] = master_df['new_device_flag'].map(dev_labels)

dev_comparison = master_df.groupby('device_status_label').agg(
    Txn_Count=('transaction_id', 'count'),
    Avg_Amount=('amount_clean', 'mean'),
    Median_Amount=('amount_clean', 'median'),
    Alert_Count=('is_alerted', 'sum'),
    Extreme_Txn_Count=('is_extreme_amount', 'sum')
).reset_index()
dev_comparison['Alert_Rate_Pct'] = (dev_comparison['Alert_Count'] / dev_comparison['Txn_Count']) * 100
print(dev_comparison.to_string(index=False))

fig, axes = plt.subplots(1, 2, figsize=(14, 5.5))

# Plot 3A: Alert Rate Comparison
sns.barplot(
    data=dev_comparison,
    x='device_status_label',
    y='Alert_Rate_Pct',
    palette=['#3B82F6', '#EF4444', '#94A3B8'],
    ax=axes[0]
)
axes[0].set_title("Operational Alert Rate by Device Trust Profile", fontsize=12, fontweight='bold')
axes[0].set_ylabel("Alert Rate (%)", fontsize=10, fontweight='semibold')
axes[0].set_xlabel("Device Profile", fontsize=10, fontweight='semibold')
for p in axes[0].patches:
    axes[0].annotate(f"{p.get_height():.2f}%", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight='bold')

# Plot 3B: Average Transaction Amount Comparison
sns.barplot(
    data=dev_comparison,
    x='device_status_label',
    y='Avg_Amount',
    palette=['#2563EB', '#DC2626', '#64748B'],
    ax=axes[1]
)
axes[1].set_title("Mean Transaction Amount by Device Trust Profile", fontsize=12, fontweight='bold')
axes[1].set_ylabel("Mean Amount ($)", fontsize=10, fontweight='semibold')
axes[1].set_xlabel("Device Profile", fontsize=10, fontweight='semibold')
for p in axes[1].patches:
    axes[1].annotate(f"${p.get_height():,.1f}", (p.get_x() + p.get_width() / 2., p.get_height()),
                     ha='center', va='center', xytext=(0, 7), textcoords='offset points', fontweight='bold')

plt.tight_layout()
fig3_path = os.path.join(FIG_DIR, "03_new_device_vs_known_device_risk_profile.png")
plt.savefig(fig3_path, dpi=300)
plt.close()
print(f"Saved: {fig3_path}")

# -------------------------------------------------------------------
# Q4: Which merchant categories show more alerts?
# -------------------------------------------------------------------
print("\n--- Q4: Alerts by Merchant Category ---")
mcat_stats = master_df.groupby('merchant_category_clean').agg(
    Total_Txns=('transaction_id', 'count'),
    Alerted_Txns=('is_alerted', 'sum'),
    Total_Volume=('amount_clean', 'sum'),
    Avg_Amount=('amount_clean', 'mean')
).reset_index()
mcat_stats['Alert_Rate_Pct'] = (mcat_stats['Alerted_Txns'] / mcat_stats['Total_Txns']) * 100
mcat_stats = mcat_stats.sort_values(by='Alert_Rate_Pct', ascending=False)
print(mcat_stats.to_string(index=False))

plt.figure(figsize=(12, 6))
bars = plt.barh(mcat_stats['merchant_category_clean'], mcat_stats['Alert_Rate_Pct'], 
                color=np.where(mcat_stats['Alert_Rate_Pct'] > 10.0, '#DC2626', '#3B82F6'), alpha=0.85)
plt.title("Operational Alert Rate (%) Across Merchant Categories\n(Red: High-Risk Category Exposure)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Alert Rate (%)", fontsize=11, fontweight='semibold')
plt.ylabel("Merchant Category", fontsize=11, fontweight='semibold')
plt.gca().invert_yaxis()

for bar in bars:
    w = bar.get_width()
    plt.text(w + 0.3, bar.get_y() + bar.get_height()/2, f"{w:.2f}%", 
             va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

plt.xlim(0, max(mcat_stats['Alert_Rate_Pct']) * 1.15)
plt.tight_layout()
fig4_path = os.path.join(FIG_DIR, "04_alerts_by_merchant_category.png")
plt.savefig(fig4_path, dpi=300)
plt.close()
print(f"Saved: {fig4_path}")

# -------------------------------------------------------------------
# Q5: Which regions have unusual spikes & cross-region mismatch?
# -------------------------------------------------------------------
print("\n--- Q5: Regional Spikes & Cross-Region Geo Mismatch ---")
master_df['is_region_mismatch'] = (master_df['customer_region'] != master_df['merchant_region']).astype(int)

reg_stats = master_df.groupby(['customer_region']).agg(
    Total_Txns=('transaction_id', 'count'),
    Alerts=('is_alerted', 'sum'),
    Mismatch_Txns=('is_region_mismatch', 'sum')
).reset_index()
reg_stats['Alert_Rate_Pct'] = (reg_stats['Alerts'] / reg_stats['Total_Txns']) * 100
reg_stats['Mismatch_Rate_Pct'] = (reg_stats['Mismatch_Txns'] / reg_stats['Total_Txns']) * 100

print(reg_stats.to_string(index=False))

# Crosstab of Customer Region vs Merchant Region
geo_ct = pd.crosstab(master_df['customer_region'], master_df['merchant_region'], values=master_df['is_alerted'], aggfunc='mean') * 100

plt.figure(figsize=(9, 7))
sns.heatmap(geo_ct, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Alert Rate (%)'}, linewidths=0.5)
plt.title("Customer Region vs. Merchant Region: Operational Alert Rate (%)\n(Diagonal = Domestic In-Region, Off-Diagonal = Cross-Region Mismatch)", fontsize=12, fontweight='bold', pad=12)
plt.xlabel("Merchant Region", fontsize=10, fontweight='semibold')
plt.ylabel("Customer Resident Region", fontsize=10, fontweight='semibold')
plt.tight_layout()
fig5_path = os.path.join(FIG_DIR, "05_regional_spikes_and_cross_region_mismatch.png")
plt.savefig(fig5_path, dpi=300)
plt.close()
print(f"Saved: {fig5_path}")

# -------------------------------------------------------------------
# Q6: What patterns appear before manual review?
# -------------------------------------------------------------------
print("\n--- Q6: Patterns Preceding Manual Review Statuses ---")
alerted_cases = master_df[master_df['is_alerted'] == 1].copy()
review_summary = alerted_cases.groupby(['review_status', 'reason_category']).agg(
    Count=('transaction_id', 'count'),
    Mean_Amount=('amount_clean', 'mean'),
    Median_Amount=('amount_clean', 'median'),
    New_Device_Pct=('new_device_flag', lambda x: (x == 1).mean() * 100),
    Night_Hour_Pct=('is_night_hours', lambda x: x.mean() * 100)
).reset_index()
print(review_summary.to_string(index=False))

plt.figure(figsize=(13, 6))
review_reason_ct = pd.crosstab(alerted_cases['review_status'], alerted_cases['reason_category'])
review_reason_ct.plot(kind='bar', stacked=True, figsize=(13, 6), colormap='viridis', edgecolor='black', alpha=0.85)
plt.title("Distribution of Primary Trigger Reasons across Operational Review Outcomes\n(Approved vs. Flagged Fraud vs. Benign vs. Under Investigation)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Operational Review Outcome", fontsize=11, fontweight='semibold')
plt.ylabel("Number of Alerted Transactions", fontsize=11, fontweight='semibold')
plt.xticks(rotation=0)
plt.legend(title="Primary Alert Trigger", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
fig6_path = os.path.join(FIG_DIR, "06_patterns_preceding_manual_review.png")
plt.savefig(fig6_path, dpi=300)
plt.close()
print(f"Saved: {fig6_path}")

print("\nEDA & Visualizations completed successfully!")
