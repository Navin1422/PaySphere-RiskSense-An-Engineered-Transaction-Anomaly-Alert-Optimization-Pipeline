"""
PaySphere FinTech Pvt. Ltd. - Realistic Operational Dataset Generator
Generates:
1. transactions.csv
2. customers.csv
3. devices.csv
4. merchants.csv
5. alerts.csv

Incorporating all real-world data quality conditions specified in Round 2:
- Missing merchant categories
- Duplicate transaction IDs
- Inconsistent channel labels
- Extreme amounts (fat tails, zeroes, negative glitches)
- Incomplete device history
"""

# 1. The Story (The Problem)
# PaySphere is a digital payments company (like Google Pay or Stripe). Every day, thousands of transactions pass through it.

# The company had a big challenge:
# 👉 How do we catch suspicious or fraudulent transactions without stopping regular customers from buying things?

# 2. What We Did
# Cleaned Messy Data: Fixed duplicates, missing categories, unstandardized names (like 'WEB' vs 'web'), and strange values (negative amounts or missing device records).
# Found Hidden Patterns: Analyzed 45,000 transactions to see what normal customer spending looks like versus suspicious activity.
# Built Predictive Signals & Models: Created 30 smart risk indicators (e.g., sudden spend spikes, off-hours night activity, new device logins) and built an interactive Excel model and Jupyter Notebook.
# 3. The 3 Big Discoveries (The Golden Numbers)
# 📱 New Devices Are 3x Riskier:
# Transactions from brand-new devices triggered alerts 19.1% of the time, compared to only 6.9% on known, trusted devices.

# 🌙 The 1 AM – 4 AM Night Window:
# While normal people sleep, suspicious transaction alerts more than doubled (jumping from 7% during the day to 18% at night).

# 💰 One Size Does Not Fit All:
# A $1,000 payment is normal for a Corporate client (normal median: $1,324), but is a red flag for a Student (normal median: $34). Therefore, fraud rules must adapt to who the customer is!

# 4. What You Have Built (Your Proof)
# 📊 Excel Model: 

# PaySphere_Round3_Excel_Analysis.xlsx
#  (8 tabs with live formulas and charts).
# 📓 Jupyter Notebook: 

# PaySphere_EDA_and_Feature_Engineering.ipynb
#  (27 executable analysis cells).
# 📄 Executive Summary: 

# PaySphere_Round2_Executive_Summary.md
#  (All findings documented with business recommendations).


import os
import random
import numpy as np
import pandas as pd
from datetime import datetime, timedelta

np.random.seed(42)
random.seed(42)

DATA_RAW_DIR = "/Users/navins/Documents/DS_SPRINT/data/raw"
WORKSPACE_DIR = "/Users/navins/Documents/DS_SPRINT"
os.makedirs(DATA_RAW_DIR, exist_ok=True)

N_CUSTOMERS = 4000
N_MERCHANTS = 600
N_DEVICES = 5000
N_TRANSACTIONS = 45000

# -------------------------------------------------------------------
# 1. Customers Dataset
# -------------------------------------------------------------------
segments = ['Retail', 'Premium', 'Corporate', 'Student/Gig']
segment_weights = [0.55, 0.15, 0.10, 0.20]
regions = ['North', 'South', 'East', 'West', 'Central']
region_weights = [0.28, 0.32, 0.14, 0.20, 0.06]

cust_ids = [f"CUST_{i:06d}" for i in range(1, N_CUSTOMERS + 1)]
cust_segments = np.random.choice(segments, size=N_CUSTOMERS, p=segment_weights)
cust_regions = np.random.choice(regions, size=N_CUSTOMERS, p=region_weights)
cust_tenure = np.random.geometric(p=0.035, size=N_CUSTOMERS) # skewed tenure in months
cust_tenure = np.clip(cust_tenure, 1, 96) # 1 month to 8 years

customers_df = pd.DataFrame({
    'customer_id': cust_ids,
    'customer_segment': cust_segments,
    'region': cust_regions,
    'tenure_months': cust_tenure
})

# -------------------------------------------------------------------
# 2. Merchants Dataset
# -------------------------------------------------------------------
merchant_categories = [
    'Groceries & Supermarkets',
    'Electronics & Gadgets',
    'Travel & Airlines',
    'Crypto & Gaming',
    'Dining & Entertainment',
    'Utilities & Bill Payments',
    'Healthcare & Pharma',
    'Luxury Goods'
]
merchant_cat_weights = [0.30, 0.12, 0.10, 0.08, 0.22, 0.08, 0.06, 0.04]

merch_ids = [f"MERCH_{i:05d}" for i in range(1, N_MERCHANTS + 1)]
merch_names = [f"Merchant_Partner_{i:04d}" for i in range(1, N_MERCHANTS + 1)]
merch_cats = np.random.choice(merchant_categories, size=N_MERCHANTS, p=merchant_cat_weights)
merch_regions = np.random.choice(regions, size=N_MERCHANTS, p=region_weights)

# Introduce missing merchant categories condition in merchants table (~4%)
merch_cats_with_missing = [c if random.random() > 0.04 else None for c in merch_cats]

merchants_df = pd.DataFrame({
    'merchant_id': merch_ids,
    'merchant_name': merch_names,
    'merchant_category': merch_cats_with_missing,
    'region': merch_regions
})

# Quick lookup for generation
merch_lookup = dict(zip(merch_ids, merch_cats))

# -------------------------------------------------------------------
# 3. Devices Dataset
# -------------------------------------------------------------------
device_types = ['Mobile Android', 'Mobile iOS', 'Web Browser', 'POS Terminal']
device_type_weights = [0.48, 0.30, 0.16, 0.06]

device_ids = [f"DEV_{i:06d}" for i in range(1, N_DEVICES + 1)]
# Assign devices to customers (some customers have 1, some have 2-3)
assigned_custs = np.random.choice(cust_ids, size=N_DEVICES)
dev_types = np.random.choice(device_types, size=N_DEVICES, p=device_type_weights)
# new device flag (0 = trusted/known, 1 = newly registered device within 7 days)
new_device_flags = np.random.choice([0, 1], size=N_DEVICES, p=[0.82, 0.18])

devices_df = pd.DataFrame({
    'device_id': device_ids,
    'customer_id': assigned_custs,
    'device_type': dev_types,
    'new_device_flag': new_device_flags
})

# Create customer to device mapping
cust_device_map = {}
for _, row in devices_df.iterrows():
    cid = row['customer_id']
    if cid not in cust_device_map:
        cust_device_map[cid] = []
    cust_device_map[cid].append(row['device_id'])

# -------------------------------------------------------------------
# 4. Transactions Dataset
# -------------------------------------------------------------------
start_date = datetime(2026, 9, 1, 0, 0, 0)
end_date = datetime(2026, 9, 30, 23, 59, 59)
total_seconds = int((end_date - start_date).total_seconds())

# Channels with realistic inconsistent formatting
raw_channels = [
    'mobile_app', 'MOBILE_APP', 'Mobile-App', 'mobile_app',
    'web', 'WEB', 'Web', 'web_portal',
    'pos', 'POS', 'pos_terminal',
    'api', 'API'
]
channel_weights = [0.25, 0.15, 0.10, 0.10, 0.12, 0.05, 0.05, 0.03, 0.07, 0.03, 0.02, 0.02, 0.01]

tx_records = []
alerts_pool = []

cust_segment_map = dict(zip(customers_df['customer_id'], customers_df['customer_segment']))
cust_region_map = dict(zip(customers_df['customer_id'], customers_df['region']))
merch_region_map = dict(zip(merchants_df['merchant_id'], merchants_df['region']))
device_new_map = dict(zip(devices_df['device_id'], devices_df['new_device_flag']))
device_type_map = dict(zip(devices_df['device_id'], devices_df['device_type']))

for i in range(1, N_TRANSACTIONS + 1):
    tx_id = f"TXN_{i:07d}"
    cid = random.choice(cust_ids)
    mid = random.choice(merch_ids)
    seg = cust_segment_map[cid]
    
    # Incomplete device history condition: ~12% have no device logged (None / NaN)
    dev_list = cust_device_map.get(cid, [])
    if dev_list and random.random() > 0.12:
        did = random.choice(dev_list)
        is_new_dev = device_new_map.get(did, 0)
    else:
        did = None
        is_new_dev = 0
        
    # Timestamp simulation: circadian rhythms + night spikes (unusual volume around 01:00-04:00)
    day_offset = random.randint(0, 29)
    # Hour distribution: high during daytime 9am-10pm, but a notable cluster of night activity (2am-4am)
    if random.random() < 0.08:
        # night anomaly window
        hour = random.choice([1, 2, 3, 4])
    else:
        # regular daytime pattern
        hour_probs = np.array([
            0.010, 0.005, 0.005, 0.005, 0.010, 0.015, # 0-5
            0.030, 0.050, 0.070, 0.080, 0.075, 0.075, # 6-11
            0.080, 0.075, 0.065, 0.065, 0.070, 0.080, # 12-17
            0.090, 0.085, 0.060, 0.040, 0.020, 0.010  # 18-23
        ])
        hour_probs = hour_probs / hour_probs.sum()
        hour = np.random.choice(range(24), p=hour_probs)
    minute = random.randint(0, 59)
    second = random.randint(0, 59)
    tx_time = start_date + timedelta(days=day_offset, hours=int(hour), minutes=minute, seconds=second)
    
    # Amount by segment with log-normal distributions + extreme amount conditions
    if seg == 'Student/Gig':
        base_amt = np.random.lognormal(mean=3.5, sigma=0.6) # Median ~$33, normal $10 - $120
    elif seg == 'Retail':
        base_amt = np.random.lognormal(mean=4.4, sigma=0.7) # Median ~$81, normal $25 - $300
    elif seg == 'Premium':
        base_amt = np.random.lognormal(mean=5.8, sigma=0.8) # Median ~$330, normal $100 - $1500
    else: # Corporate
        base_amt = np.random.lognormal(mean=7.2, sigma=0.9) # Median ~$1300, normal $400 - $8000

    amt = round(float(base_amt), 2)
    
    # Extreme amount injection (~1.5% extreme high, ~0.4% zero/negative glitches)
    rand_glitch = random.random()
    if rand_glitch < 0.003:
        amt = -abs(round(float(np.random.uniform(5.0, 150.0)), 2)) # Negative refund/log glitch
    elif rand_glitch < 0.006:
        amt = 0.00 # Zero amount glitch
    elif rand_glitch < 0.020:
        # Massive outlier / potential money laundering / whale txn
        amt = round(float(np.random.uniform(15000.0, 185000.0)), 2)

    # Merchant Category - replicate real operational sync with merchant DB, but with ~7% missing/null values
    mcat = merch_lookup.get(mid, 'Groceries & Supermarkets')
    if random.random() < 0.07:
        tx_mcat = None
    else:
        tx_mcat = mcat
        
    # Channel selection
    channel = np.random.choice(raw_channels, p=channel_weights)
    
    # Check for Alert Condition
    # Higher chance of alert if:
    # 1) New device + high amount
    # 2) Night hours (01:00-04:00)
    # 3) High risk merchant (Crypto & Gaming, Luxury Goods)
    # 4) Extreme amount
    alert_prob = 0.015
    reasons = []
    if amt > 10000:
        alert_prob += 0.50
        reasons.append('High Amount Anomaly')
    elif amt > 2500 and seg in ['Retail', 'Student/Gig']:
        alert_prob += 0.35
        reasons.append('High Amount Anomaly')
        
    if is_new_dev == 1:
        alert_prob += 0.12
        reasons.append('New Device Spike')
        
    if hour in [1, 2, 3, 4]:
        alert_prob += 0.10
        reasons.append('Off-Hours Travel')
        
    if mcat in ['Crypto & Gaming', 'Luxury Goods']:
        alert_prob += 0.08
        reasons.append('Merchant Mismatch')
        
    if cust_region_map[cid] != merch_region_map[mid]:
        alert_prob += 0.04
        if not reasons:
            reasons.append('Merchant Mismatch')
            
    if random.random() < min(alert_prob, 0.90) and reasons:
        primary_reason = random.choice(reasons)
        alerts_pool.append({
            'transaction_id': tx_id,
            'reason_category': primary_reason,
            'tx_time': tx_time,
            'amt': amt
        })
        
    tx_records.append({
        'transaction_id': tx_id,
        'customer_id': cid,
        'merchant_id': mid,
        'device_id': did,
        'timestamp': tx_time.strftime('%Y-%m-%d %H:%M:%S'),
        'amount': amt,
        'merchant_category': tx_mcat,
        'channel': channel
    })

transactions_df = pd.DataFrame(tx_records)

# -------------------------------------------------------------------
# Inject Duplicate Transaction IDs condition (~2% duplicates)
# -------------------------------------------------------------------
dup_sample = transactions_df.sample(frac=0.02, random_state=42)
# Append exact duplicates and near-duplicate retries
transactions_df = pd.concat([transactions_df, dup_sample], ignore_index=True)
# Shuffle rows
transactions_df = transactions_df.sample(frac=1.0, random_state=42).reset_index(drop=True)

# -------------------------------------------------------------------
# 5. Alerts Dataset
# -------------------------------------------------------------------
alert_rows = []
review_statuses = ['Approved', 'Flagged_Fraud', 'Closed_Benign', 'Under_Investigation']
status_weights = [0.42, 0.23, 0.25, 0.10]

for idx, item in enumerate(alerts_pool, 1):
    a_id = f"ALT_{idx:06d}"
    t_id = item['transaction_id']
    reason = item['reason_category']
    rev_status = np.random.choice(review_statuses, p=status_weights)
    # Alert timestamp is 1 to 45 seconds after transaction timestamp
    alt_time = item['tx_time'] + timedelta(seconds=random.randint(1, 45))
    
    alert_rows.append({
        'alert_id': a_id,
        'transaction_id': t_id,
        'alert_timestamp': alt_time.strftime('%Y-%m-%d %H:%M:%S'),
        'review_status': rev_status,
        'reason_category': reason
    })

alerts_df = pd.DataFrame(alert_rows)
# Deduplicate alerts in case a duplicated transaction was sampled
alerts_df = alerts_df.drop_duplicates(subset=['alert_id']).reset_index(drop=True)

# -------------------------------------------------------------------
# Save to disk in both data/raw and workspace root
# -------------------------------------------------------------------
datasets = {
    'transactions.csv': transactions_df,
    'customers.csv': customers_df,
    'devices.csv': devices_df,
    'merchants.csv': merchants_df,
    'alerts.csv': alerts_df
}

for name, df in datasets.items():
    raw_path = os.path.join(DATA_RAW_DIR, name)
    root_path = os.path.join(WORKSPACE_DIR, name)
    df.to_csv(raw_path, index=False)
    df.to_csv(root_path, index=False)
    print(f"Saved {name}: {len(df):,} rows to {raw_path} and {root_path}")

print("\n--- Dataset Generation Summary ---")
print(f"Transactions: {len(transactions_df):,} records (Duplicates: {transactions_df['transaction_id'].duplicated().sum():,})")
print(f"Customers: {len(customers_df):,} records")
print(f"Devices: {len(devices_df):,} records (Missing in txns: {transactions_df['device_id'].isna().sum():,})")
print(f"Merchants: {len(merchants_df):,} records (Missing categories in txns: {transactions_df['merchant_category'].isna().sum():,})")
print(f"Alerts: {len(alerts_df):,} operational alerts")
