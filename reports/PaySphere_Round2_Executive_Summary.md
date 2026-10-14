# PaySphere FinTech Pvt. Ltd. — Round 2 Report
## Digital Payment Insight: EDA & Feature Engineering
**Sector:** FinTech  
**Author / Team:** Data Science Sprint Team  
**Deliverable Stage:** Round 2 (30 Marks)  
**Evaluation Scope:** Complete Data Audit, Cleaning, Multi-Table Integration, Exploratory Data Analysis, Feature Engineering, Feature Selection, and PCA Dimensionality Reduction.

---

## 1. Executive Summary & Business Context
PaySphere FinTech processes high-velocity digital payment transactions spanning four distinct customer segments (`Retail`, `Student/Gig`, `Premium`, and `Corporate`). The operational objective of this engagement is to address the core business question:

> **Core Business Question:**  
> *Which transaction patterns differ from normal customer behaviour and deserve operational review?*

Through rigorous exploratory data analysis, feature engineering, and statistical modeling, we have isolated the multi-dimensional signatures of unusual transactional behaviour. Normal customers execute predictable transaction values during diurnal business hours on authenticated, registered devices. Conversely, transactions warranting operational review are strongly characterized by:
1. **Device Discontinuities**: Transactions occurring on newly bound devices (<7 days old) exhibit a **19.07% alert rate**—a **2.75x risk premium** over trusted devices (6.95%).
2. **Circadian Off-Hours Spikes**: While general transaction volume declines at night, the window between **01:00 AM and 04:00 AM** experiences a surge in high-risk anomalies, reaching an operational alert rate of **17.98%**.
3. **Cross-Region Geographic Mismatches**: When a customer's registered region diverges from the merchant processing region—especially on high amounts—the alert incidence escalates markedly.
4. **Category Exposure**: High-risk, pseudonymous, or easily liquidated merchant categories (**Luxury Goods** at 15.68% alert rate and **Crypto & Gaming** at 14.87%) generate significantly higher operational review demand than everyday spending categories (Groceries at 7.14%).
5. **Customer & Segment Baselines Over Absolute Thresholds**: Transactions that deviate from an individual's historical mean (`amount_to_cust_mean_ratio` and `cust_amount_zscore`) provide substantially stronger predictive power than static currency caps.

---

## 2. Dataset Architecture & Data Quality Audit

### 2.1 Entity Relationship Schema
The PaySphere data architecture integrates five operational datasets:
- **`transactions.csv`** (45,000 unique records): Primary transaction log capturing `transaction_id`, `customer_id`, `merchant_id`, `device_id`, `timestamp`, `amount`, `merchant_category`, and `channel`.
- **`customers.csv`** (4,000 records): Customer demographic baseline capturing `customer_segment`, `region`, and `tenure_months`.
- **`devices.csv`** (5,000 records): Hardware profile capturing `device_id`, `customer_id`, `device_type`, and `new_device_flag`.
- **`merchants.csv`** (600 records): Merchant partner registry capturing `merchant_name`, `merchant_category`, and `region`.
- **`alerts.csv`** (3,740 records): Operational queue capturing `alert_id`, `transaction_id`, `alert_timestamp`, `review_status`, and `reason_category`.

### 2.2 Data Quality Audit Findings & Cleaning Resolution

| Data Quality Condition | Observed Issue in Raw Data | Operational Cleaning Resolution Applied |
| :--- | :--- | :--- |
| **Duplicate Transaction IDs** | 900 duplicate records (2.0% duplication rate) caused by payment retry loops and upstream logging retries. | Deduplicated via `drop_duplicates(subset=['transaction_id'], keep='first')` to retain authoritative original attempt. |
| **Missing Merchant Categories** | 3,259 records (7.2%) had `NaN` in `transactions.csv`; 24 records had `NaN` in `merchants.csv`. | Harmonized via cross-table lookup from `merchants.csv` using `merchant_id`. Residual unmapped merchants imputed with `'Uncategorized / Other'`. |
| **Inconsistent Channel Labels** | Fragmented casing and delimiters (`'mobile_app'`, `'MOBILE_APP'`, `'Mobile-App'`, `'web'`, `'WEB'`, `'Web'`, `'pos'`, `'POS'`). | Canonical mapping applied: normalized into four clean categories: `Mobile App`, `Web Portal`, `POS Terminal`, and `API Gateway`. |
| **Extreme Amounts** | Heavy right skew (max: $184,952.12; 99th percentile: $59,320.38) alongside 14 negative amounts (-$5.00 to -$150.00) and 27 zero amounts. | Flagged errors (`is_negative_amount`, `is_zero_amount`, `is_extreme_amount`). Quantitatively converted to absolute magnitudes (`amount_clean`) and stabilized via log1p transformation (`amount_log`). |
| **Incomplete Device History** | 16,925 transactions (37.6%) lacked linked device identifiers due to legacy channels, guest checkouts, or uninstrumented POS. | Filled with explicit surrogate key `'DEV_UNTRACKED'`. Created binary flag `has_device_history` and coded `new_device_flag` as -1 (Untracked), 0 (Known), and 1 (New). |

---

## 3. Answers to Use-Case-Specific Analytical Questions

### Q1: What are normal amount ranges by segment?
Each customer segment possesses a distinct financial baseline. Standardizing by segment is essential to prevent false positives on corporate accounts and missed anomalies on retail/gig accounts.

| Customer Segment | Record Count | Mean Amount ($) | Median Amount ($) | IQR (P25 - P75) ($) | 5th - 95th Percentile Range ($) | 99th Percentile ($) |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| **Student/Gig** | 9,095 | $1,290.94 | **$33.86** | $22.21 – $50.91 | $11.75 – $96.95 | $56,418.65 |
| **Retail** | 24,712 | $1,497.20 | **$81.39** | $50.49 – $132.19 | $24.77 – $286.69 | $59,320.38 |
| **Premium** | 6,896 | $1,661.57 | **$330.45** | $197.00 – $584.47 | $88.68 – $1,391.99 | $37,486.96 |
| **Corporate** | 4,297 | $3,288.92 | **$1,324.47** | $727.92 – $2,556.97 | $286.05 – $6,755.06 | $51,804.30 |

*Operational Insight:* A $1,200 transaction is standard operating behavior for a Corporate entity (within IQR), yet represents an extreme statistical outlier (>99th percentile) for a Student/Gig customer that mandates automated review.

---

### Q2: Which hours show unusual volume and alert rates?
* Diurnal Peak Hours: Peak legitimate transaction volume occurs between **08:00 and 20:00**, peaking at 18:00 (3,151 transactions). The baseline alert rate during daytime is steady at **6.5% – 8.1%**.
* Off-Hours Surge Window: Between **01:00 AM and 04:00 AM**, total volume drops to ~1,050 transactions per hour, yet the operational alert rate surges to **15.2% – 18.0%**.
* Operational Implication: Transactions initiated during midnight and pre-dawn hours (01:00–04:00) possess double the anomaly propensity of daytime transactions, representing off-hours travel, compromised credentials, or automated exploitation scripts.

---

### Q3: How do new devices differ from known devices?

| Device Trust Status | Transactions | Mean Amount ($) | Median Amount ($) | Operational Alerts | Alert Rate (%) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Known Trusted Device** | 23,238 | $1,670.06 | $87.90 | 1,615 | **6.95%** |
| **Untracked / Incomplete History** | 16,592 | $1,682.17 | $91.12 | 1,139 | **6.86%** |
| **New Device (< 7 days registered)** | 5,170 | $1,472.19 | $88.29 | 986 | **19.07%** |

*Operational Insight:* Transactions initiated on newly bound devices exhibit an alert rate **nearly three times higher** (19.07% vs. 6.95%). Attackers commonly access compromised credentials on newly provisioned hardware and execute immediate transactions before detection.

---

### Q4: Which merchant categories show more alerts?

| Merchant Category | Total Transactions | Total Volume ($) | Alerted Transactions | Alert Rate (%) | Risk Tier |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Luxury Goods** | 2,678 | $5,331,801.02 | 420 | **15.68%** | Critical High |
| **Crypto & Gaming** | 3,483 | $5,664,669.78 | 518 | **14.87%** | Critical High |
| **Uncategorized / Other** | 114 | $524,069.28 | 11 | **9.65%** | Elevated |
| **Travel & Airlines** | 4,010 | $7,730,150.99 | 314 | **7.83%** | Moderate |
| **Dining & Entertainment** | 10,442 | $17,052,184.63 | 795 | **7.61%** | Baseline |
| **Groceries & Supermarkets** | 13,747 | $21,476,275.95 | 982 | **7.14%** | Baseline |
| **Utilities & Bill Payments** | 3,215 | $4,367,257.69 | 223 | **6.94%** | Baseline |
| **Healthcare & Pharma** | 2,011 | $3,581,684.35 | 133 | **6.61%** | Baseline |
| **Electronics & Gadgets** | 5,300 | $8,602,573.41 | 344 | **6.49%** | Baseline |

*Operational Insight:* Luxury Goods and Crypto & Gaming constitute the highest-risk merchant vectors due to high liquidity, rapid transferability, and high resale value.

---

### Q5: Which regions have unusual spikes and cross-region mismatches?
* In-Region vs. Cross-Region Dynamics: Approximately 73.2% of transactions occur with merchants operating in a different geographic region from the customer's resident state (e.g. centralized e-commerce or digital merchants in West/South).
* Regional Alert Rates:
  - Central: 9.13% alert rate (highest mismatch proportion at 93.8%)
  - East: 8.91% alert rate
  - West: 8.80% alert rate
  - North: 7.98% alert rate
  - South: 7.93% alert rate
* Operational Implication: Regional mismatch alone is frequent in digital commerce, but when coupled with high amounts or off-hours timestamps, it serves as an acute anomaly amplifier.

---

### Q6: What patterns appear before manual review?
Analysis of review outcomes (`Approved`, `Closed_Benign`, `Flagged_Fraud`, `Under_Investigation`) against primary trigger reasons reveals:
1. **High Amount Anomalies**: Transactions triggered for high amount anomalies average **~$91,000**, with median values exceeding **$70,000–$90,000**.
2. **New Device Spikes**: 100% of New Device Spike reviews originate from new devices, with higher concentrations under `Flagged_Fraud` and `Under_Investigation`.
3. **Off-Hours Travel**: 100% of these cases occur between 00:00 and 05:00 AM, frequently involving cross-region travel or rapid merchant transitions.
4. **Fraud Concentration**: Over **42%** of confirmed fraudulent transactions combine two or more concurrent triggers (e.g. New Device + Night Hours or High Amount + Crypto Merchant).

---

## 4. Feature Engineering Architecture

We engineered **30 high-signal analytical features** grouped into five strategic pillars:

1. **Customer Historical Baselines**:
   - `amount_to_cust_mean_ratio`: Ratio of current transaction amount to the customer's historical mean spending.
   - `cust_amount_zscore`: Number of standard deviations current amount deviates from the customer's profile.
   - `cust_total_txns`: Customer's overall engagement volume.
2. **Segment Benchmark Indicators**:
   - `amount_to_seg_median_ratio`: Magnitude relative to peer segment typical transaction size.
   - `is_amount_above_seg_p95`: Binary indicator if transaction exceeds 95th percentile of the customer's peer group.
3. **Velocity & Timing Dynamics**:
   - `time_since_prev_tx_mins`: Minutes elapsed since the customer's preceding transaction.
   - `is_burst_velocity`: Binary flag for rapid succession transactions (< 10 minutes apart).
   - `hour_sin`, `hour_cos`: Continuous periodic representation of diurnal cycles.
   - `is_night_hours`: Binary indicator for the 00:00–05:00 AM risk window.
4. **Cross-Entity Consistency & Risk Flags**:
   - `is_region_mismatch`: Geographic divergence between customer and merchant.
   - `is_new_device_bin`: Device trust indicator.
   - `is_untracked_device`: Missing device telemetry indicator.
   - `is_high_risk_mcat`: High-risk merchant exposure flag.
5. **Multi-Factor Interaction Risk Combos**:
   - `risk_combo_new_dev_night`: Concurrency of new device login during off-hours (01:00–05:00 AM).
   - `risk_combo_new_dev_high_risk_mcat`: Concurrency of new device at high-risk merchant.
   - `risk_combo_mismatch_high_amount`: Geo mismatch on amounts exceeding segment 95th percentile.

---

## 5. Feature Selection & Dimensionality Reduction

### 5.1 Top 15 Selected Features (Random Forest Gini Importance)

| Rank | Selected Feature | Importance Score | Operational Significance |
| :---: | :--- | :---: | :--- |
| **1** | `is_new_device_bin` | **0.1268** | Single highest indicator of operational review necessity. |
| **2** | `is_region_mismatch` | **0.0911** | Cross-region payment processing anomaly. |
| **3** | `is_high_risk_mcat` | **0.0843** | Luxury goods, crypto, or uncategorized merchant exposure. |
| **4** | `amount_log` | **0.0830** | Log-transformed amount stabilizing heavy right-tailed volume. |
| **5** | `amount_clean` | **0.0658** | Raw sanitized monetary value. |
| **6** | `amount_to_cust_mean_ratio` | **0.0626** | Normalized deviation from customer personal historical spending. |
| **7** | `amount_to_seg_median_ratio` | **0.0587** | Deviation from segment peer median. |
| **8** | `cust_amount_zscore` | **0.0571** | Statistical z-score of transaction amount within customer distribution. |
| **9** | `hour` | **0.0523** | Hour of transaction capture (24h format). |
| **10** | `time_since_prev_tx_mins` | **0.0466** | Inter-transaction velocity and spacing. |
| **11** | `tenure_months` | **0.0399** | Customer account age; newer accounts present higher baseline risk. |
| **12** | `is_extreme_amount` | **0.0339** | Indicator for transactions exceeding $10,000. |
| **13** | `is_night_hours` | **0.0332** | Indicator for transactions during off-hours (00:00–05:00 AM). |
| **14** | `hour_cos` | **0.0319** | Cyclical diurnal cosine encoding. |
| **15** | `hour_sin` | **0.0285** | Cyclical diurnal sine encoding. |

### 5.2 Dimensionality Reduction (PCA)
- Standardizing the top 15 features and projecting to 2 principal components captures **42.28% of total variance** (PC1: 26.90%, PC2: 15.38%).
- In the 2D projection, legitimate daily transactions form a dense, central baseline cluster.
- Alerted transactions and confirmed fraud form distinct outer trajectories along PC1 and PC2, corresponding to velocity bursts, extreme amount anomalies, and new-device off-hour interactions.

---

## 6. Actionable Recommendations for PaySphere Operations

1. **Dynamic Risk-Based Step-Up Authentication**:
   - Rather than static transaction limits, trigger 2FA/biometric verification when `amount_to_cust_mean_ratio > 3.5` OR when `is_new_device_bin == 1` combined with `is_night_hours == 1`.
2. **Prioritized Queueing for Operational Review**:
   - Route alerts triggered by composite risk flags (`risk_combo_new_dev_night` and `risk_combo_new_dev_high_risk_mcat`) to Level 2 fraud analysts with a 15-minute SLA.
3. **Automate Benign Whitelisting**:
   - Transactions originating from corporate accounts within normal segment IQR ($727 - $2,556) on trusted devices should bypass manual review to reduce analyst fatigue.
4. **Continuous Telemetry & Data Quality Guardrails**:
   - Mandate device SDK logging across all mobile and web checkouts to eradicate the 37% untracked device gap.
   - Enforce merchant category validation at onboarding to eliminate null category values.

---

## 7. Deliverables & Artifact Inventory
- **Cleaned Master Dataset**: `data/processed/cleaned_transactions_master.csv` (45,000 rows × 24 columns)
- **Engineered Master Dataset**: `data/processed/featured_transactions.csv` (45,000 rows × 44 columns)
- **Selected Top 15 Features Dataset**: `data/processed/selected_features.csv` (45,000 rows × 18 columns)
- **Executable Jupyter Notebook**: `notebooks/PaySphere_EDA_and_Feature_Engineering.ipynb`
- **Visual Evidence Charts**: `reports/figures/01` to `09` (High-resolution PNG charts)
- **Automated Pipeline Runner**: `scripts/run_all.py`
