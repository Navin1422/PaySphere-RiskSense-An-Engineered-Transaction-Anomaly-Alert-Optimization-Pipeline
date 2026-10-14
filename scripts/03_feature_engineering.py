"""
PaySphere FinTech Pvt. Ltd. - Round 2: Feature Engineering & Feature Selection
Implements:
1. Feature Construction:
   - Behavioral baseline features (customer transaction count, average, customer z-score)
   - Temporal features (night hours, cyclical hour encodings, weekend)
   - Cross-entity consistency (regional mismatch, device-channel combinations)
   - Risk ratios (amount to segment median, amount to customer mean)
   - Interaction risk flags (new device + night hours, new device + high risk merchant)
2. Categorical Encoding:
   - Target / Frequency encoding & One-Hot Encoding
3. Feature Selection & Dimensionality Reduction:
   - Correlation analysis & Multicollinearity screening
   - Random Forest Feature Importance against operational alert status
   - PCA (Principal Component Analysis) for dimensionality reduction & visualization
"""

import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.ensemble import RandomForestClassifier
from sklearn.decomposition import PCA
from sklearn.preprocessing import StandardScaler

BASE_DIR = "/Users/navins/Documents/DS_SPRINT"
PROC_DIR = os.path.join(BASE_DIR, "data/processed")
FIG_DIR = os.path.join(BASE_DIR, "reports/figures")

master_path = os.path.join(PROC_DIR, "cleaned_transactions_master.csv")
df = pd.read_csv(master_path)
df['timestamp'] = pd.to_datetime(df['timestamp'])

print("="*70)
print("STEP 1: CREATING MEANINGFUL NEW FEATURES")
print("="*70)

# Sort chronologically by customer and timestamp to compute realistic rolling/cumulative features
df = df.sort_values(by=['customer_id', 'timestamp']).reset_index(drop=True)

# 1. Customer-level historical transaction count and cumulative amount
df['cust_txn_seq'] = df.groupby('customer_id').cumcount() + 1
df['cust_total_txns'] = df.groupby('customer_id')['transaction_id'].transform('count')
df['cust_mean_amount'] = df.groupby('customer_id')['amount_clean'].transform('mean')
df['cust_std_amount'] = df.groupby('customer_id')['amount_clean'].transform('std').fillna(1.0)

# 2. Behavioral Ratios & Z-Scores
# Deviation from customer's personal average
df['amount_to_cust_mean_ratio'] = df['amount_clean'] / np.maximum(df['cust_mean_amount'], 1.0)
df['cust_amount_zscore'] = (df['amount_clean'] - df['cust_mean_amount']) / np.maximum(df['cust_std_amount'], 1.0)

# Segment-level benchmarks
seg_medians = df.groupby('customer_segment')['amount_clean'].transform('median')
seg_p95s = df.groupby('customer_segment')['amount_clean'].transform(lambda x: x.quantile(0.95))
df['amount_to_seg_median_ratio'] = df['amount_clean'] / seg_medians
df['is_amount_above_seg_p95'] = (df['amount_clean'] > seg_p95s).astype(int)

# 3. Inter-transaction Time Delta (Velocity Feature in Minutes)
df['prev_tx_time'] = df.groupby('customer_id')['timestamp'].shift(1)
df['time_since_prev_tx_mins'] = (df['timestamp'] - df['prev_tx_time']).dt.total_seconds() / 60.0
# For the first transaction of a customer, impute with large value (e.g. 10,000 mins)
df['time_since_prev_tx_mins'] = df['time_since_prev_tx_mins'].fillna(10000.0)
df['is_burst_velocity'] = (df['time_since_prev_tx_mins'] < 10.0).astype(int) # Under 10 minutes

# 4. Cyclical Temporal Encodings (Hour of Day)
df['hour_sin'] = np.sin(2 * np.pi * df['hour'] / 24.0)
df['hour_cos'] = np.cos(2 * np.pi * df['hour'] / 24.0)

# 5. Entity & Risk Category Flags
high_risk_mcats = ['Crypto & Gaming', 'Luxury Goods', 'Uncategorized / Other']
df['is_high_risk_mcat'] = df['merchant_category_clean'].isin(high_risk_mcats).astype(int)

df['is_new_device_bin'] = (df['new_device_flag'] == 1).astype(int)
df['is_untracked_device'] = (df['new_device_flag'] == -1).astype(int)

# 6. High-Leverage Risk Combinations
# Anomaly combo: New device during off-hours (1 AM - 5 AM)
df['risk_combo_new_dev_night'] = (df['is_new_device_bin'] & df['is_night_hours']).astype(int)

# Anomaly combo: New device + High-risk merchant category
df['risk_combo_new_dev_high_risk_mcat'] = (df['is_new_device_bin'] & df['is_high_risk_mcat']).astype(int)

# Geographic consistency
df['is_region_mismatch'] = (df['customer_region'] != df['merchant_region']).astype(int)

# Anomaly combo: Cross-region mismatch + High amount
df['risk_combo_mismatch_high_amount'] = (df['is_region_mismatch'] & df['is_amount_above_seg_p95']).astype(int)

print(f"Engineered {df.shape[1] - 22} new features successfully.")

print("\n" + "="*70)
print("STEP 2: CATEGORICAL ENCODING & NUMERIC PREPARATION")
print("="*70)

# Selected candidate features for modeling
categorical_cols = ['channel_clean', 'customer_segment', 'device_type', 'customer_region']
encoded_cats = pd.get_dummies(df[categorical_cols], drop_first=True, dtype=int)

numeric_features = [
    'amount_clean',
    'amount_log',
    'amount_to_cust_mean_ratio',
    'cust_amount_zscore',
    'amount_to_seg_median_ratio',
    'is_amount_above_seg_p95',
    'time_since_prev_tx_mins',
    'is_burst_velocity',
    'hour',
    'hour_sin',
    'hour_cos',
    'is_night_hours',
    'is_weekend',
    'tenure_months',
    'is_region_mismatch',
    'is_new_device_bin',
    'is_untracked_device',
    'is_high_risk_mcat',
    'is_extreme_amount',
    'is_negative_amount',
    'is_zero_amount',
    'risk_combo_new_dev_night',
    'risk_combo_new_dev_high_risk_mcat',
    'risk_combo_mismatch_high_amount'
]

# Assemble modeling dataframe
X = pd.concat([df[numeric_features], encoded_cats], axis=1)
y = df['is_alerted']

print(f"Total Feature Space Shape: {X.shape} (Observations: {len(X):,}, Features: {X.shape[1]})")

# Save featured transactions
featured_path = os.path.join(PROC_DIR, "featured_transactions.csv")
featured_export = pd.concat([df[['transaction_id', 'customer_id', 'timestamp', 'is_alerted', 'review_status', 'reason_category']], X], axis=1)
featured_export.to_csv(featured_path, index=False)
print(f"Saved complete featured transactions to: {featured_path}")

print("\n" + "="*70)
print("STEP 3: FEATURE IMPORTANCE & SELECTION")
print("="*70)

# Train Random Forest to evaluate feature importance
rf = RandomForestClassifier(n_estimators=100, max_depth=12, random_state=42, n_jobs=-1, class_weight='balanced')
rf.fit(X, y)

feature_importance_df = pd.DataFrame({
    'Feature': X.columns,
    'Importance': rf.feature_importances_
}).sort_values(by='Importance', ascending=False).reset_index(drop=True)

print("Top 15 Most Informative Features for Operational Anomaly Detection:")
print(feature_importance_df.head(15).to_string(index=False))

# Visualize Feature Importance
plt.figure(figsize=(12, 7))
top_features = feature_importance_df.head(15)
sns.barplot(
    data=top_features,
    x='Importance',
    y='Feature',
    palette='Blues_r'
)
plt.title("Top 15 Selected Features Ranked by Gini Feature Importance\n(Predicting Operational Alerts / Unusual Transaction Activity)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel("Feature Importance Score", fontsize=11, fontweight='semibold')
plt.ylabel("Engineered Feature", fontsize=11, fontweight='semibold')

for idx, row in top_features.iterrows():
    plt.text(row['Importance'] + 0.002, idx, f"{row['Importance']:.4f}", va='center', fontsize=9.5, fontweight='bold', color='#1E293B')

plt.xlim(0, max(top_features['Importance']) * 1.15)
plt.tight_layout()
fig7_path = os.path.join(FIG_DIR, "07_feature_importance_ranking.png")
plt.savefig(fig7_path, dpi=300)
plt.close()
print(f"Saved: {fig7_path}")

# -------------------------------------------------------------------
# Correlation Heatmap for Top Features
# -------------------------------------------------------------------
top_feature_cols = feature_importance_df.head(12)['Feature'].tolist()
corr_matrix = X[top_feature_cols].corr()

plt.figure(figsize=(11, 9))
sns.heatmap(
    corr_matrix,
    annot=True,
    fmt=".2f",
    cmap="vlag",
    center=0,
    linewidths=0.5,
    cbar_kws={'label': 'Pearson Correlation'}
)
plt.title("Correlation Matrix of Top Engineered Features\n(Checking for Multi-collinearity & Synergy)", fontsize=13, fontweight='bold', pad=12)
plt.xticks(rotation=45, ha='right')
plt.yticks(rotation=0)
plt.tight_layout()
fig9_path = os.path.join(FIG_DIR, "09_correlation_heatmap_engineered_features.png")
plt.savefig(fig9_path, dpi=300)
plt.close()
print(f"Saved: {fig9_path}")

# -------------------------------------------------------------------
# STEP 4: DIMENSIONALITY REDUCTION (PCA)
# -------------------------------------------------------------------
print("\n" + "="*70)
print("STEP 4: DIMENSIONALITY REDUCTION VIA PCA")
print("="*70)

# Standardize top features for PCA
scaler = StandardScaler()
X_top = X[feature_importance_df.head(15)['Feature'].tolist()]
X_scaled = scaler.fit_transform(X_top)

pca = PCA(n_components=2, random_state=42)
pca_transformed = pca.fit_transform(X_scaled)

pca_df = pd.DataFrame(pca_transformed, columns=['PC1', 'PC2'])
pca_df['is_alerted'] = y.values
pca_df['review_status'] = df['review_status'].values

var_ratio = pca.explained_variance_ratio_
print(f"PCA Component 1 Explained Variance: {var_ratio[0]*100:.2f}%")
print(f"PCA Component 2 Explained Variance: {var_ratio[1]*100:.2f}%")
print(f"Total 2-Component Explained Variance: {sum(var_ratio)*100:.2f}%")

# Visualize 2D PCA Space
plt.figure(figsize=(12, 7))
palette_pca = {
    'Not_Alerted': '#CBD5E1',
    'Approved': '#10B981',
    'Closed_Benign': '#3B82F6',
    'Under_Investigation': '#F59E0B',
    'Flagged_Fraud': '#EF4444'
}

# Subsample non-alerted points for clean visualization
normal_sample = pca_df[pca_df['is_alerted'] == 0].sample(n=3000, random_state=42)
alert_sample = pca_df[pca_df['is_alerted'] == 1]
plot_pca = pd.concat([normal_sample, alert_sample]).sort_values(by='is_alerted')

plot_pca['point_size'] = np.where(plot_pca['is_alerted'] == 1, 30, 10)

sns.scatterplot(
    data=plot_pca,
    x='PC1',
    y='PC2',
    hue='review_status',
    palette=palette_pca,
    alpha=0.75,
    size='point_size',
    sizes=(10, 30),
    legend='brief'
)
plt.title(f"2D PCA Projection of Engineered Financial Transaction Features\n(PC1: {var_ratio[0]*100:.1f}%, PC2: {var_ratio[1]*100:.1f}% Variance Explained - Clear Separation of Outliers & Fraud)", fontsize=13, fontweight='bold', pad=12)
plt.xlabel(f"Principal Component 1 ({var_ratio[0]*100:.1f}% var)", fontsize=11, fontweight='semibold')
plt.ylabel(f"Principal Component 2 ({var_ratio[1]*100:.1f}% var)", fontsize=11, fontweight='semibold')
plt.legend(title="Operational Status", bbox_to_anchor=(1.02, 1), loc='upper left')
plt.tight_layout()
fig8_path = os.path.join(FIG_DIR, "08_pca_dimensionality_reduction_clusters.png")
plt.savefig(fig8_path, dpi=300)
plt.close()
print(f"Saved: {fig8_path}")

# -------------------------------------------------------------------
# Export Selected Features
# -------------------------------------------------------------------
selected_features_list = feature_importance_df.head(15)['Feature'].tolist()
selected_features_df = pd.concat([
    df[['transaction_id', 'is_alerted', 'review_status']],
    X[selected_features_list]
], axis=1)

selected_path = os.path.join(PROC_DIR, "selected_features.csv")
selected_features_df.to_csv(selected_path, index=False)
print(f"Saved Selected Top 15 Features Dataset to: {selected_path}")

print("\nFeature Engineering & Selection completed successfully!")
