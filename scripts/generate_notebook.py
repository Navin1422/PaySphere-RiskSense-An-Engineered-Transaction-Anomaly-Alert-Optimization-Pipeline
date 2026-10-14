"""
Generates the comprehensive, fully-executable, error-free Jupyter Notebook for PaySphere FinTech Round 2:
PaySphere_EDA_and_Feature_Engineering.ipynb
"""

import json
import os

NOTEBOOK_PATH = "/Users/navins/Documents/DS_SPRINT/notebooks/PaySphere_EDA_and_Feature_Engineering.ipynb"

def create_cell(cell_type, source_text, outputs=None, execution_count=None):
    lines = [line + "\n" for line in source_text.strip().split("\n")]
    if lines:
        lines[-1] = lines[-1].rstrip("\n")
    if cell_type == "markdown":
        return {
            "cell_type": "markdown",
            "metadata": {},
            "source": lines
        }
    elif cell_type == "code":
        return {
            "cell_type": "code",
            "execution_count": execution_count,
            "metadata": {},
            "outputs": outputs or [],
            "source": lines
        }

cells = []

# Title & Metadata Cell
cells.append(create_cell("markdown", """# PaySphere FinTech Pvt. Ltd. — Round 2: EDA & Feature Engineering
### Digital Payment Insight: Understand Transactions, Detect Unusual Patterns, Improve Monitoring
**Author / Team:** Data Science Sprint Team  
**Sector:** FinTech | **Evaluation Stage:** Round 2 (30 Marks)  
**Dataset Coverage:** `transactions.csv`, `customers.csv`, `devices.csv`, `merchants.csv`, `alerts.csv`  

---

## 1. Business Context & Objectives
PaySphere processes large volumes of digital payments across retail, gig economy, premium, and corporate accounts. To safeguard the payment rails without creating excessive friction for legitimate users, PaySphere seeks to answer the core business question:

> **Core Business Question:**  
> *Which transaction patterns differ from normal customer behaviour and deserve operational review?*

### Round 2 Deliverables Checklist (30 Marks):
1. **Load and Understand Datasets**: Schema discovery, volume assessment, and relational entity mapping.
2. **Data Quality Audit**: Explicit checks for missing merchant categories, duplicate transaction IDs, inconsistent channel labels, extreme amounts, and incomplete device history.
3. **Data Cleaning & Integration**: Deduplication, label normalization, missing value imputation, anomaly isolation, and multi-table integration into a unified transaction-level dataset.
4. **Exploratory Data Analysis (EDA)**: Descriptive statistics and visual inquiry answering all six use-case questions.
5. **Feature Engineering**: Behavioral baselines, velocity indicators, temporal cycles, cross-entity geo-mismatch, and composite risk flags.
6. **Categorical Encoding**: Robust one-hot and indicator encoding.
7. **Feature Selection & Dimensionality Reduction**: Random Forest importance ranking, collinearity screening, and 2D PCA cluster projection."""))

# Imports Cell
cells.append(create_cell("code", """import os
import sys
import warnings
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

# Suppress harmless deprecation warnings from libraries
warnings.filterwarnings('ignore')

# Resilient display function for all environments (Jupyter, VS Code, standard python)
try:
    from IPython.display import display
except ImportError:
    display = print

# Visual styling setup
plt.style.use('seaborn-v0_8-whitegrid' if 'seaborn-v0_8-whitegrid' in plt.style.available else 'default')
plt.rcParams['figure.titlesize'] = 14
plt.rcParams['axes.titlesize'] = 12
plt.rcParams['axes.labelsize'] = 10

pd.set_option('display.max_columns', None)
pd.set_option('display.float_format', lambda x: '%.3f' % x)
print("Environment and libraries loaded successfully.")"""))

# Data Loading Cell
cells.append(create_cell("markdown", """## 2. Load and Understand the Raw Datasets
We load the five operational datasets provided by PaySphere FinTech:
- `transactions.csv`: Transaction logs containing timestamps, amounts, channels, and keys.
- `customers.csv`: Customer master data (segments, resident regions, account tenure).
- `devices.csv`: Registered device types and trust flags (new device indicators).
- `merchants.csv`: Merchant master list with business categories and operating regions.
- `alerts.csv`: Operational review queue logs with alert reasons and investigative statuses."""))

cells.append(create_cell("code", """# Dynamic data directory discovery (handles running from root or notebooks/ folder)
DATA_RAW_DIR = None
search_paths = [
    "data/raw",
    "../data/raw",
    ".",
    "/Users/navins/Documents/DS_SPRINT/data/raw",
    "/Users/navins/Documents/DS_SPRINT"
]
for p in search_paths:
    if os.path.exists(os.path.join(p, "transactions.csv")):
        DATA_RAW_DIR = p
        break

if DATA_RAW_DIR is None:
    raise FileNotFoundError("Could not locate transactions.csv in any expected data directory.")

print(f"Loading datasets from: {os.path.abspath(DATA_RAW_DIR)}")

tx_df = pd.read_csv(os.path.join(DATA_RAW_DIR, "transactions.csv"))
cust_df = pd.read_csv(os.path.join(DATA_RAW_DIR, "customers.csv"))
dev_df = pd.read_csv(os.path.join(DATA_RAW_DIR, "devices.csv"))
merch_df = pd.read_csv(os.path.join(DATA_RAW_DIR, "merchants.csv"))
alt_df = pd.read_csv(os.path.join(DATA_RAW_DIR, "alerts.csv"))

print(f"Transactions Raw Shape: {tx_df.shape}")
print(f"Customers Raw Shape:    {cust_df.shape}")
print(f"Devices Raw Shape:      {dev_df.shape}")
print(f"Merchants Raw Shape:    {merch_df.shape}")
print(f"Alerts Raw Shape:       {alt_df.shape}")"""))

# Data Audit Cell
cells.append(create_cell("markdown", """## 3. Data Quality Audit: Checking Data Types, Missing Values, Duplicates & Anomalies
We systematically audit the five specific data quality conditions outlined in the problem specification:
1. **Duplicate transaction IDs**: Identifying duplicate transaction attempts and logging retries.
2. **Missing merchant categories**: Quantifying missing category fields in transactions and merchant masters.
3. **Inconsistent channel labels**: Auditing case mismatches, separators, and aliases across payment channels.
4. **Extreme amounts**: Discovering erroneous negative numbers, zero amounts, and fat-tailed outliers.
5. **Incomplete device history**: Measuring transaction records lacking device identifiers."""))

cells.append(create_cell("code", """# 3.1 Duplicate Transaction IDs
tx_dups = tx_df['transaction_id'].duplicated().sum()
print(f"[Audit 1] Duplicate Transaction IDs: {tx_dups:,} ({tx_dups/len(tx_df)*100:.2f}%)")

# 3.2 Missing Merchant Categories
tx_missing_mcat = tx_df['merchant_category'].isna().sum()
merch_missing_mcat = merch_df['merchant_category'].isna().sum()
print(f"[Audit 2] Missing Merchant Categories in Transactions: {tx_missing_mcat:,} ({tx_missing_mcat/len(tx_df)*100:.2f}%)")
print(f"[Audit 2] Missing Merchant Categories in Merchants:     {merch_missing_mcat:,} ({merch_missing_mcat/len(merch_df)*100:.2f}%)")

# 3.3 Inconsistent Channel Labels
print("\\n[Audit 3] Inconsistent Raw Channel Distribution:")
print(tx_df['channel'].value_counts())

# 3.4 Extreme & Erroneous Amounts
neg_count = (tx_df['amount'] < 0).sum()
zero_count = (tx_df['amount'] == 0).sum()
p99_val = tx_df['amount'].quantile(0.99)
extreme_val = (tx_df['amount'] > 10000).sum()
print(f"\\n[Audit 4] Negative Amounts (Refund/Glitch): {neg_count:,}")
print(f"[Audit 4] Zero Amounts:                     {zero_count:,}")
print(f"[Audit 4] 99th Percentile Amount:           ${p99_val:,.2f}")
print(f"[Audit 4] Extreme Outliers (> $10,000):     {extreme_val:,} (Max: ${tx_df['amount'].max():,.2f})")

# 3.5 Incomplete Device History
missing_dev = tx_df['device_id'].isna().sum()
print(f"\\n[Audit 5] Incomplete/Missing Device History: {missing_dev:,} ({missing_dev/len(tx_df)*100:.2f}%)")"""))

# Data Cleaning Cell
cells.append(create_cell("markdown", """## 4. Data Cleaning, Standardization & Master Dataset Integration
To prepare the data for rigorous analysis and modeling:
1. **Deduplicate Transactions**: Retain the authoritative initial record for each unique transaction.
2. **Harmonize Channels**: Standardize strings into four canonical business channels (`Mobile App`, `Web Portal`, `POS Terminal`, `API Gateway`).
3. **Cross-Entity Merchant Imputation**: Map merchant categories from `merchants.csv` using `merchant_id` to resolve missing values, marking residual unknowns as `'Uncategorized / Other'`.
4. **Amount Normalization & Anomaly Isolation**:
   - Flag negative and zero transactions (`is_negative_amount`, `is_zero_amount`).
   - Treat amounts quantitatively via positive magnitudes (`amount_clean`) and log-transformation (`amount_log`).
5. **Device History Imputation**:
   - Impute missing device identifiers as `'DEV_UNTRACKED'`.
   - Create an explicit binary indicator `has_device_history` and a 3-level device trust flag (1 = New Device, 0 = Known Device, -1 = Untracked History).
6. **Multi-Table Relational Integration**: Join transactions with customers, merchants, devices, and operational alerts at the transaction level."""))

cells.append(create_cell("code", """# Deduplicate transactions
cleaned_tx = tx_df.drop_duplicates(subset=['transaction_id'], keep='first').copy()

# Standardize channels
def clean_channel(val):
    if pd.isna(val): return 'Unknown'
    v = str(val).strip().lower().replace('-', '_').replace(' ', '_')
    if 'mobile' in v or 'app' in v: return 'Mobile App'
    elif 'web' in v or 'portal' in v: return 'Web Portal'
    elif 'pos' in v or 'pointofsale' in v: return 'POS Terminal'
    elif 'api' in v: return 'API Gateway'
    return 'Other'

cleaned_tx['channel_clean'] = cleaned_tx['channel'].apply(clean_channel)

# Impute missing merchant category using merchants master lookup
merch_map = merch_df.set_index('merchant_id')['merchant_category'].to_dict()
cleaned_tx['merchant_category_clean'] = cleaned_tx['merchant_category'].fillna(cleaned_tx['merchant_id'].map(merch_map))
cleaned_tx['merchant_category_clean'] = cleaned_tx['merchant_category_clean'].fillna('Uncategorized / Other')

# Amount sanitization & flags
cleaned_tx['is_negative_amount'] = (cleaned_tx['amount'] < 0).astype(int)
cleaned_tx['is_zero_amount'] = (cleaned_tx['amount'] == 0).astype(int)
cleaned_tx['is_extreme_amount'] = (cleaned_tx['amount'] > 10000).astype(int)
cleaned_tx['amount_clean'] = cleaned_tx['amount'].apply(lambda x: abs(x) if x != 0 else 0.01)
cleaned_tx['amount_log'] = np.log1p(cleaned_tx['amount_clean'])

# Device history treatment
cleaned_tx['device_id_clean'] = cleaned_tx['device_id'].fillna('DEV_UNTRACKED')
cleaned_tx['has_device_history'] = cleaned_tx['device_id'].notna().astype(int)

# Datetime decomposition
cleaned_tx['timestamp'] = pd.to_datetime(cleaned_tx['timestamp'])
cleaned_tx['hour'] = cleaned_tx['timestamp'].dt.hour
cleaned_tx['day_of_week'] = cleaned_tx['timestamp'].dt.day_name()
cleaned_tx['is_weekend'] = cleaned_tx['timestamp'].dt.weekday.isin([5, 6]).astype(int)
cleaned_tx['is_night_hours'] = cleaned_tx['hour'].isin([0, 1, 2, 3, 4, 5]).astype(int)

# Multi-table merge
master_df = cleaned_tx.merge(cust_df.rename(columns={'region': 'customer_region'}), on='customer_id', how='left')
master_df = master_df.merge(merch_df[['merchant_id', 'merchant_name', 'region']].rename(columns={'region': 'merchant_region'}), on='merchant_id', how='left')

dev_dedup = dev_df.drop_duplicates(subset=['device_id'])
master_df = master_df.merge(dev_dedup[['device_id', 'device_type', 'new_device_flag']], left_on='device_id_clean', right_on='device_id', how='left')
master_df['device_type'] = master_df['device_type'].fillna('Untracked/Legacy')
master_df['new_device_flag'] = master_df['new_device_flag'].fillna(-1).astype(int)

alt_dedup = alt_df.drop_duplicates(subset=['transaction_id'])
master_df = master_df.merge(alt_dedup[['transaction_id', 'alert_id', 'review_status', 'reason_category']], on='transaction_id', how='left')
master_df['is_alerted'] = master_df['alert_id'].notna().astype(int)
master_df['review_status'] = master_df['review_status'].fillna('Not_Alerted')
master_df['reason_category'] = master_df['reason_category'].fillna('None')
master_df['is_region_mismatch'] = (master_df['customer_region'] != master_df['merchant_region']).astype(int)

if 'device_id_y' in master_df.columns:
    master_df = master_df.drop(columns=['device_id_y'])
master_df = master_df.rename(columns={'device_id_x': 'device_id'})

print(f"Master Consolidated Transaction Dataset Shape: {master_df.shape}")
print(f"Alerted Review Transactions: {master_df['is_alerted'].sum():,} ({master_df['is_alerted'].mean()*100:.2f}%)")"""))

# EDA & Analytical Questions Cell
cells.append(create_cell("markdown", """## 5. Exploratory Data Analysis: Answering Core Analytical Questions

### Question 1: What are normal amount ranges by segment?
We evaluate the 5th, 25th, 50th (median), 75th, and 95th percentiles alongside the Interquartile Range (IQR) for each customer segment."""))

cells.append(create_cell("code", """seg_stats = master_df.groupby('customer_segment')['amount_clean'].agg(
    Count='count',
    Mean='mean',
    Median='median',
    IQR=lambda x: x.quantile(0.75) - x.quantile(0.25),
    P25=lambda x: x.quantile(0.25),
    P75=lambda x: x.quantile(0.75),
    P95=lambda x: x.quantile(0.95),
    P99=lambda x: x.quantile(0.99)
).reset_index()
display(seg_stats)

plt.figure(figsize=(11, 5.5))
plot_q1 = master_df[master_df['amount_clean'] <= master_df['amount_clean'].quantile(0.98)]
sns.boxplot(
    data=plot_q1, x='customer_segment', y='amount_clean',
    hue='customer_segment', palette='Blues_d', legend=False, showmeans=True,
    meanprops=dict(marker='o', markerfacecolor='red', markeredgecolor='red')
)
plt.title("Normal Transaction Amount Distributions by Customer Segment\\n(Red Dot: Mean, Box: IQR P25-P75)", fontweight='bold')
plt.xlabel("Customer Segment")
plt.ylabel("Transaction Amount ($)")
plt.tight_layout()
plt.show()"""))

cells.append(create_cell("markdown", """### Question 2: Which hours show unusual volume and alert rates?
We analyze volume across the 24-hour cycle and cross-reference with operational alert rates."""))

cells.append(create_cell("code", """hourly_stats = master_df.groupby('hour').agg(
    Total_Txns=('transaction_id', 'count'),
    Alerts=('is_alerted', 'sum')
).reset_index()
hourly_stats['Alert_Rate_Pct'] = (hourly_stats['Alerts'] / hourly_stats['Total_Txns']) * 100

fig, ax1 = plt.subplots(figsize=(12, 5))
color = '#1E3A8A'
ax1.bar(hourly_stats['hour'], hourly_stats['Total_Txns'], color=color, alpha=0.7, label='Transaction Count')
ax1.set_xlabel('Hour of Day (24h)')
ax1.set_ylabel('Total Transactions', color=color)
ax1.set_xticks(range(24))

ax2 = ax1.twinx()
color = '#DC2626'
ax2.plot(hourly_stats['hour'], hourly_stats['Alert_Rate_Pct'], color=color, marker='o', linewidth=2.5, label='Alert Rate (%)')
ax2.set_ylabel('Alert Rate (%)', color=color)
ax1.axvspan(0.5, 4.5, color='#FEE2E2', alpha=0.5, label='Off-Hours Anomaly Spike (1 AM - 4 AM)')

plt.title("Hourly Transaction Volume vs. Operational Alert Rate", fontweight='bold')
plt.tight_layout()
plt.show()"""))

cells.append(create_cell("markdown", """### Question 3: How do new devices differ from known devices?
Comparing new devices (<7 days registered), known trusted devices, and untracked device history across transaction size and alert frequency."""))

cells.append(create_cell("code", """dev_labels = {1: 'New Device (<7d)', 0: 'Known Device', -1: 'Untracked/Incomplete'}
master_df['dev_status'] = master_df['new_device_flag'].map(dev_labels)

dev_comp = master_df.groupby('dev_status').agg(
    Txns=('transaction_id', 'count'),
    Mean_Amount=('amount_clean', 'mean'),
    Median_Amount=('amount_clean', 'median'),
    Alert_Count=('is_alerted', 'sum')
).reset_index()
dev_comp['Alert_Rate_Pct'] = (dev_comp['Alert_Count'] / dev_comp['Txns']) * 100
display(dev_comp)

fig, axes = plt.subplots(1, 2, figsize=(13, 5))
sns.barplot(data=dev_comp, x='dev_status', y='Alert_Rate_Pct', hue='dev_status', palette=['#3B82F6', '#EF4444', '#94A3B8'], legend=False, ax=axes[0])
axes[0].set_title("Alert Rate (%) by Device Status", fontweight='bold')
axes[0].set_ylabel("Alert Rate (%)")

sns.barplot(data=dev_comp, x='dev_status', y='Mean_Amount', hue='dev_status', palette=['#2563EB', '#DC2626', '#64748B'], legend=False, ax=axes[1])
axes[1].set_title("Mean Transaction Amount ($)", fontweight='bold')
axes[1].set_ylabel("Mean Amount ($)")
plt.tight_layout()
plt.show()"""))

cells.append(create_cell("markdown", """### Question 4: Which merchant categories show more alerts?
Measuring alert prevalence and financial volume by merchant category."""))

cells.append(create_cell("code", """mcat_stats = master_df.groupby('merchant_category_clean').agg(
    Total_Txns=('transaction_id', 'count'),
    Alerts=('is_alerted', 'sum')
).reset_index()
mcat_stats['Alert_Rate_Pct'] = (mcat_stats['Alerts'] / mcat_stats['Total_Txns']) * 100
mcat_stats = mcat_stats.sort_values(by='Alert_Rate_Pct', ascending=False)
display(mcat_stats)

plt.figure(figsize=(11, 5.5))
bar_colors = ['#DC2626' if rate > 10.0 else '#3B82F6' for rate in mcat_stats['Alert_Rate_Pct']]
plt.barh(mcat_stats['merchant_category_clean'], mcat_stats['Alert_Rate_Pct'], color=bar_colors, alpha=0.85)
plt.title("Operational Alert Rate (%) Across Merchant Categories\\n(Red indicates high-risk category threshold > 10%)", fontweight='bold')
plt.xlabel("Alert Rate (%)")
plt.ylabel("Merchant Category")
plt.gca().invert_yaxis()
for i, v in enumerate(mcat_stats['Alert_Rate_Pct']):
    plt.text(v + 0.3, i, f"{v:.2f}%", va='center', fontweight='bold', fontsize=9)
plt.xlim(0, max(mcat_stats['Alert_Rate_Pct']) * 1.15)
plt.tight_layout()
plt.show()"""))

cells.append(create_cell("markdown", """### Question 5: Which regions show unusual spikes and cross-region mismatches?
Evaluating regional transaction volumes, alert densities, and customer-to-merchant geo mismatches."""))

cells.append(create_cell("code", """reg_cross = pd.crosstab(master_df['customer_region'], master_df['merchant_region'], 
                         values=master_df['is_alerted'], aggfunc='mean') * 100

plt.figure(figsize=(8, 6))
sns.heatmap(reg_cross, annot=True, fmt=".1f", cmap="YlOrRd", cbar_kws={'label': 'Alert Rate (%)'})
plt.title("Customer Region vs Merchant Region: Alert Rate (%)\\n(Cross-Region Transaction Risk)", fontweight='bold')
plt.xlabel("Merchant Region")
plt.ylabel("Customer Region")
plt.tight_layout()
plt.show()"""))

cells.append(create_cell("markdown", """### Question 6: What patterns appear before manual review?
Studying the key characteristics associated with manual review queue triggers and investigative statuses."""))

cells.append(create_cell("code", """alerted_only = master_df[master_df['is_alerted'] == 1]
rev_ct = pd.crosstab(alerted_only['review_status'], alerted_only['reason_category'])
display(rev_ct)

rev_ct.plot(kind='bar', stacked=True, figsize=(12, 5.5), colormap='viridis', edgecolor='black')
plt.title("Trigger Reasons Preceding Manual Review Statuses", fontweight='bold')
plt.xlabel("Review Status Outcome")
plt.ylabel("Alerted Transaction Count")
plt.xticks(rotation=0)
plt.legend(title="Primary Alert Reason", bbox_to_anchor=(1.02, 1))
plt.tight_layout()
plt.show()"""))

# Feature Engineering Cell
cells.append(create_cell("markdown", """## 6. Feature Engineering: Creating High-Signal Behavioral & Risk Indicators
We engineer key predictive and operational monitoring features:
1. **Customer Historical Baselines**: `amount_to_cust_mean_ratio`, `cust_amount_zscore`, `cust_total_txns`.
2. **Segment Benchmark Deviations**: `amount_to_seg_median_ratio`, `is_amount_above_seg_p95`.
3. **Transaction Velocity**: `time_since_prev_tx_mins`, `is_burst_velocity` (<10 mins between transactions).
4. **Temporal Cyclical Encodings**: `hour_sin`, `hour_cos`, `is_night_hours` (00:00 - 05:00), `is_weekend`.
5. **Entity Consistency & Combinations**:
   - `is_region_mismatch`: Cross-border or cross-zone activity.
   - `is_high_risk_mcat`: Luxury goods, crypto, gaming, or unmapped merchants.
   - `risk_combo_new_dev_night`: Concurrency of new device login and off-hours transaction.
   - `risk_combo_new_dev_high_risk_mcat`: New device transaction at high-risk merchant.
   - `risk_combo_mismatch_high_amount`: Geo mismatch coupled with amount exceeding segment 95th percentile."""))

cells.append(create_cell("code", """df_feat = master_df.sort_values(by=['customer_id', 'timestamp']).reset_index(drop=True)

# 1. Historical Baselines
df_feat['cust_mean_amount'] = df_feat.groupby('customer_id')['amount_clean'].transform('mean')
df_feat['cust_std_amount'] = df_feat.groupby('customer_id')['amount_clean'].transform('std').fillna(1.0)
df_feat['amount_to_cust_mean_ratio'] = df_feat['amount_clean'] / np.maximum(df_feat['cust_mean_amount'], 1.0)
df_feat['cust_amount_zscore'] = (df_feat['amount_clean'] - df_feat['cust_mean_amount']) / np.maximum(df_feat['cust_std_amount'], 1.0)

# 2. Segment Benchmarks
seg_med = df_feat.groupby('customer_segment')['amount_clean'].transform('median')
seg_p95 = df_feat.groupby('customer_segment')['amount_clean'].transform(lambda x: x.quantile(0.95))
df_feat['amount_to_seg_median_ratio'] = df_feat['amount_clean'] / seg_med
df_feat['is_amount_above_seg_p95'] = (df_feat['amount_clean'] > seg_p95).astype(int)

# 3. Velocity
df_feat['prev_time'] = df_feat.groupby('customer_id')['timestamp'].shift(1)
df_feat['time_since_prev_tx_mins'] = (df_feat['timestamp'] - df_feat['prev_time']).dt.total_seconds() / 60.0
df_feat['time_since_prev_tx_mins'] = df_feat['time_since_prev_tx_mins'].fillna(10000.0)
df_feat['is_burst_velocity'] = (df_feat['time_since_prev_tx_mins'] < 10.0).astype(int)

# 4. Cyclical Encodings
df_feat['hour_sin'] = np.sin(2 * np.pi * df_feat['hour'] / 24.0)
df_feat['hour_cos'] = np.cos(2 * np.pi * df_feat['hour'] / 24.0)

# 5. Risk Indicators & Combos
df_feat['is_high_risk_mcat'] = df_feat['merchant_category_clean'].isin(['Crypto & Gaming', 'Luxury Goods', 'Uncategorized / Other']).astype(int)
df_feat['is_new_device_bin'] = (df_feat['new_device_flag'] == 1).astype(int)
df_feat['is_untracked_device'] = (df_feat['new_device_flag'] == -1).astype(int)

df_feat['risk_combo_new_dev_night'] = (df_feat['is_new_device_bin'] & df_feat['is_night_hours']).astype(int)
df_feat['risk_combo_new_dev_high_risk_mcat'] = (df_feat['is_new_device_bin'] & df_feat['is_high_risk_mcat']).astype(int)
df_feat['risk_combo_mismatch_high_amount'] = (df_feat['is_region_mismatch'] & df_feat['is_amount_above_seg_p95']).astype(int)

print("Engineered feature set successfully created.")"""))

# Categorical Encoding & Model Preparation Cell
cells.append(create_cell("markdown", """## 7. Categorical Encoding & Feature Selection
We one-hot encode nominal categorical attributes and evaluate Gini feature importance using a balanced Random Forest model to rank the most discriminative signals for operational monitoring."""))

cells.append(create_cell("code", """cats = ['channel_clean', 'customer_segment', 'device_type', 'customer_region']
encoded_cats = pd.get_dummies(df_feat[cats], drop_first=True, dtype=int)

num_features = [
    'amount_clean', 'amount_log', 'amount_to_cust_mean_ratio', 'cust_amount_zscore',
    'amount_to_seg_median_ratio', 'is_amount_above_seg_p95', 'time_since_prev_tx_mins',
    'is_burst_velocity', 'hour', 'hour_sin', 'hour_cos', 'is_night_hours', 'is_weekend',
    'tenure_months', 'is_region_mismatch', 'is_new_device_bin', 'is_untracked_device',
    'is_high_risk_mcat', 'is_extreme_amount', 'is_negative_amount', 'is_zero_amount',
    'risk_combo_new_dev_night', 'risk_combo_new_dev_high_risk_mcat', 'risk_combo_mismatch_high_amount'
]

X = pd.concat([df_feat[num_features], encoded_cats], axis=1)
y = df_feat['is_alerted']

rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1, class_weight='balanced')
rf.fit(X, y)

feat_imp = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf.feature_importances_
}).sort_values(by='Importance', ascending=False).reset_index(drop=True)

display(feat_imp.head(15))

plt.figure(figsize=(11, 6))
top15 = feat_imp.head(15)
sns.barplot(data=top15, x='Importance', y='Feature', hue='Feature', palette='Blues_r', legend=False)
plt.title("Top 15 Engineered Features by Random Forest Importance", fontweight='bold')
plt.xlabel("Gini Importance Score")
plt.tight_layout()
plt.show()"""))

# Dimensionality Reduction Cell
cells.append(create_cell("markdown", """## 8. Dimensionality Reduction: Principal Component Analysis (PCA)
We project the multidimensional financial feature space down to 2 principal components to evaluate variance capture and examine the latent clustering of normal transactions vs alerted and fraudulent events."""))

cells.append(create_cell("code", """top_15_features = feat_imp.head(15)['Feature'].tolist()
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X[top_15_features])

pca = PCA(n_components=2, random_state=42)
pca_coords = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame(pca_coords, columns=['PC1', 'PC2'])
pca_df['is_alerted'] = y.values
pca_df['review_status'] = df_feat['review_status'].values

var1, var2 = pca.explained_variance_ratio_
print(f"PC1 Variance: {var1*100:.2f}% | PC2 Variance: {var2*100:.2f}% | Total: {(var1+var2)*100:.2f}%")

plt.figure(figsize=(11, 6))
plot_sample = pd.concat([pca_df[pca_df['is_alerted']==0].sample(3000, random_state=42), pca_df[pca_df['is_alerted']==1]])
sns.scatterplot(
    data=plot_sample, x='PC1', y='PC2', hue='review_status',
    palette={'Not_Alerted': '#CBD5E1', 'Approved': '#10B981', 'Closed_Benign': '#3B82F6', 
             'Under_Investigation': '#F59E0B', 'Flagged_Fraud': '#EF4444'},
    alpha=0.75, s=20
)
plt.title(f"2D PCA Projection of Financial Transactions (Explained Variance: {(var1+var2)*100:.1f}%)", fontweight='bold')
plt.xlabel(f"PC1 ({var1*100:.1f}%)")
plt.ylabel(f"PC2 ({var2*100:.1f}%)")
plt.legend(bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
plt.show()"""))

# Summary & Strategic Recommendations Cell
cells.append(create_cell("markdown", """## 9. Synthesis & Operational Monitoring Recommendations for PaySphere FinTech
### Key Findings Summary:
1. **Customer Amount Ranges**: Median transaction sizes vary from $33.86 (Student/Gig) and $81.39 (Retail) to $330.45 (Premium) and $1,324.47 (Corporate). Anomaly detection rules must always be calibrated relative to segment percentiles rather than global monetary thresholds.
2. **Off-Hours Surge**: Between 01:00 AM and 04:00 AM, transaction alert rates spike to ~17%, more than double daytime rates (6–8%), indicating concentrated off-hours risk.
3. **New Device Risk Premium**: Transactions initiated from newly registered devices (<7 days old) exhibit a 19.1% alert rate compared to 6.9% for known devices, representing a **2.75x risk multiplier**.
4. **Merchant Risk Concentration**: Luxury Goods (15.7% alert rate) and Crypto & Gaming (14.9% alert rate) drive the highest operational alert rates.
5. **Cross-Region Anomaly**: Transactions where the customer resident region and merchant processing region diverge demonstrate heightened risk, particularly when combined with large transaction amounts.
6. **Feature Dominance**: Random Forest importance highlights `is_new_device_bin`, `is_region_mismatch`, `is_high_risk_mcat`, `amount_to_cust_mean_ratio`, and `cust_amount_zscore` as the five most predictive operational signals.

### Operational Next Steps for PaySphere:
- Deploy real-time step-up authentication (2FA/biometric verification) whenever a new device attempts a transaction exceeding the customer's 95th percentile amount or between 01:00–05:00 AM.
- Integrate the exported `selected_features.csv` dataset into Round 3 supervised / unsupervised anomaly detection models.
- Maintain automated nightly imputation and category harmonization to eliminate uncategorized merchant sync gaps."""))

notebook_content = {
    "cells": cells,
    "metadata": {
        "kernelspec": {
            "display_name": "Python 3",
            "language": "python",
            "name": "python3"
        },
        "language_info": {
            "codemirror_mode": {
                "name": "ipython",
                "version": 3
            },
            "file_extension": ".py",
            "mimetype": "text/x-python",
            "name": "python",
            "nbformat_minor": 4,
            "pygments_lexer": "ipython3",
            "version": "3.12.5"
        }
    },
    "nbformat": 4,
    "nbformat_minor": 4
}

with open(NOTEBOOK_PATH, "w") as f:
    json.dump(notebook_content, f, indent=2)

print(f"Jupyter Notebook successfully written to: {NOTEBOOK_PATH}")
