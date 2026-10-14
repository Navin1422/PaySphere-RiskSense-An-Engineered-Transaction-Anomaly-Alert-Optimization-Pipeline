# PaySphere FinTech — Round 2: EDA & Feature Engineering
> **Digital Payment Insight: Understand Transactions. Detect Unusual Patterns. Improve Monitoring.**

This repository contains the complete implementation, data cleaning pipeline, exploratory data analysis, visual figures, feature engineering, and feature selection for **Round 2 (30 Marks)**.

---

## Directory Structure
```
DS_SPRINT/
├── README.md                                    # Project documentation & execution guide
├── PaySphere_Round3_Excel_Analysis.xlsx         # Master Excel Workbook (8 sheets, formulas, charts)
├── transactions.csv                             # Authoritative raw transactions dataset
├── customers.csv                                # Raw customers master dataset
├── devices.csv                                  # Raw devices dataset
├── merchants.csv                                # Raw merchants dataset
├── alerts.csv                                   # Raw alerts queue dataset
├── data/
│   ├── raw/                                     # Raw datasets storage
│   └── processed/
│       ├── cleaned_transactions_master.csv      # Merged, deduplicated, cleaned master dataset
│       ├── featured_transactions.csv            # Master dataset with 30+ engineered features
│       └── selected_features.csv                # Top 15 selected features for modelling
├── notebooks/
│   └── PaySphere_EDA_and_Feature_Engineering.ipynb  # Documented, fully executable Jupyter Notebook
├── scripts/
│   ├── 01_generate_dataset.py                   # Realistic dataset synthesis with data quality quirks
│   ├── 02_eda_and_cleaning.py                   # Auditing, cleaning, merging, and visual EDA
│   ├── 03_feature_engineering.py                # Feature construction, selection, and PCA
│   ├── 04_create_excel_model.py                 # Automated multi-tab Excel model generator
│   ├── generate_notebook.py                     # Programmatic notebook generator
│   └── run_all.py                               # Single-command end-to-end execution runner
└── reports/
    ├── PaySphere_Round2_Executive_Summary.md    # Full analytical report with business recommendations
    ├── PaySphere_Round3_Excel_Analysis_Report.md# Round 3 Excel analysis documentation
    ├── PaySphere_Round3_Excel_Analysis.xlsx     # Copy of master Excel workbook
    └── figures/
        ├── 01_normal_amount_ranges_by_segment.png
        ├── 02_hourly_volume_and_unusual_night_spikes.png
        ├── 03_new_device_vs_known_device_risk_profile.png
        ├── 04_alerts_by_merchant_category.png
        ├── 05_regional_spikes_and_cross_region_mismatch.png
        ├── 06_patterns_preceding_manual_review.png
        ├── 07_feature_importance_ranking.png
        ├── 08_pca_dimensionality_reduction_clusters.png
        └── 09_correlation_heatmap_engineered_features.png
```

---

## Quickstart & Replication
To re-run the entire pipeline from scratch and reproduce all outputs, datasets, and figures:
```bash
python3 scripts/run_all.py
```

To launch the Jupyter Notebook:
```bash
jupyter notebook notebooks/PaySphere_EDA_and_Feature_Engineering.ipynb
```
