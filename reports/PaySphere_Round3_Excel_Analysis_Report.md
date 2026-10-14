# PaySphere FinTech Pvt. Ltd. — Round 3 Report
## Data Analysis Using Microsoft Excel | 30 Marks

**Sector:** FinTech  
**Author / Team:** Data Science Sprint Team  
**Deliverable File:** `PaySphere_Round3_Excel_Analysis.xlsx` (Available in workspace root and `reports/`)  
**Scope:** Full Excel Data Import, Table Formatting, Dynamic Statistical Formulas, Pivot Summaries, Native Visual Charts, and Master Executive Summary Dashboard.

---

## 1. Executive Summary & Workbook Architecture

The cleaned operational dataset (`cleaned_transactions_master.csv`) of **45,000 transactions** was imported into a multi-tab Microsoft Excel workbook: **`PaySphere_Round3_Excel_Analysis.xlsx`**.

The workbook is structured into **8 dedicated sheets**:
1. **`Summary Dashboard`**: The single primary summary sheet containing high-level KPI cards (`Total Transactions`, `Total Volume`, `Average Amount`, `Median Amount`, `Alert Count`, `Alert Rate %`), executive business answers, and segment snapshots.
2. **`Cleaned Transactions Data`**: Complete 45,000-row master database with frozen header rows, active filter controls, currency formatting (`$#,##0.00`), integer formatting, and centered indicators.
3. **`Amount Distribution`**: Statistical distribution model across customer segments using `COUNTIF`, `AVERAGEIFS`, `SUMIFS`, median, IQR, P25, P75, P95, and an embedded Clustered Column Chart.
4. **`Hourly Volume`**: 24-hour diurnal cycle analysis using `COUNTIF`, `COUNTIFS`, `SUMIFS`, alert rate %, volume share, with off-hours night spikes (01:00 AM–04:00 AM) highlighted and an embedded Line Chart.
5. **`Device Comparison`**: Hardware trust profiling (Known Trusted, New Device <7d, Untracked History) with alert rates, extreme transaction counts, and a Clustered Column Chart.
6. **`Merchant Analysis`**: Sector-by-sector risk tiering (Luxury Goods, Crypto & Gaming, Groceries, Dining, etc.) with alert rates, volume %, and a Horizontal Bar Chart.
7. **`Regional Trends`**: Customer region distribution, cross-border mismatch analysis, and a 2D Customer Region vs. Merchant Processing Region Alert Rate Matrix.
8. **`Alert Patterns`**: Operational review determinations (`Approved`, `Closed_Benign`, `Flagged_Fraud`, `Under_Investigation`) cross-tabulated with trigger reasons (`High Amount Anomaly`, `Merchant Mismatch`, `New Device Spike`, `Off-Hours Travel`) and an embedded Stacked Column Chart.

---

## 2. Minimum Excel Analysis Coverage & Formula Inventory

### 2.1 Amount Distribution Analysis
- **Excel Tab:** `Amount Distribution`
- **Business Question Answered:** *What are normal amount ranges by segment?*
- **Formulas Implemented:**
  - Count: `=COUNTIF('Cleaned Transactions Data'!$V$2:$V$45001, B6)`
  - Mean Spend: `=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$V$2:$V$45001, B6)`
  - Total Volume: `=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$V$2:$V$45001, B6)`
  - Statistical Spread: P25, Median, P75, IQR, P95, and P99 percentiles calibrated per segment.
- **Embedded Chart:** Native Excel Clustered Column Chart comparing Median vs. P75 vs. P95 spend by segment.

### 2.2 Hourly Volume Analysis
- **Excel Tab:** `Hourly Volume`
- **Business Question Answered:** *Which hours show unusual volume and alert rates?*
- **Formulas Implemented:**
  - Total Hourly Transactions: `=COUNTIF('Cleaned Transactions Data'!$R$2:$R$45001, B6)`
  - Volume Share %: `=C6/$C$30`
  - Alerted Transactions: `=COUNTIFS('Cleaned Transactions Data'!$R$2:$R$45001, B6, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)`
  - Alert Rate %: `=E6/C6`
  - Total Hourly Volume: `=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$R$2:$R$45001, B6)`
- **Embedded Chart:** Native Excel Line Chart highlighting the **15.2% – 18.0% alert spike** between 01:00 AM and 04:00 AM (highlighted with orange cell fills).

### 2.3 Device Trust Comparison
- **Excel Tab:** `Device Comparison`
- **Business Question Answered:** *How do new devices differ from known devices?*
- **Formulas Implemented:**
  - Device Transaction Count: `=COUNTIF('Cleaned Transactions Data'!$AB$2:$AB$45001, C6)`
  - Device Alert Count: `=COUNTIFS('Cleaned Transactions Data'!$AB$2:$AB$45001, C6, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)`
  - Alert Rate %: `=F6/D6`
  - Mean Transaction Amount: `=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$AB$2:$AB$45001, C6)`
  - Extreme Amount Count: `=COUNTIFS('Cleaned Transactions Data'!$AB$2:$AB$45001, C6, 'Cleaned Transactions Data'!$M$2:$M$45001, 1)`
- **Embedded Chart:** Clustered Column Chart proving the **2.75x Risk Multiplier** of new devices (19.07% vs. 6.95%).

### 2.4 Merchant-Category Analysis
- **Excel Tab:** `Merchant Analysis`
- **Business Question Answered:** *Which merchant categories show more alerts?*
- **Formulas Implemented:**
  - Category Transactions: `=COUNTIF('Cleaned Transactions Data'!$J$2:$J$45001, B6)`
  - Total Category Volume: `=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$J$2:$J$45001, B6)`
  - Category Alerts: `=COUNTIFS('Cleaned Transactions Data'!$J$2:$J$45001, B6, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)`
  - Category Alert Rate %: `=F6/D6`
- **Embedded Chart:** Horizontal Bar Chart ranking sectors from Critical High (Luxury Goods: 15.68%, Crypto: 14.87%) to Baseline (Groceries: 7.14%).

### 2.5 Regional Trends & Cross-Region Mismatches
- **Excel Tab:** `Regional Trends`
- **Business Question Answered:** *Which regions have unusual spikes?*
- **Formulas Implemented:**
  - Regional Transaction Count: `=COUNTIF('Cleaned Transactions Data'!$W$2:$W$45001, B6)`
  - Regional Alert Rate: `=E6/C6`
  - Cross-Region Mismatch Count: `=COUNTIFS('Cleaned Transactions Data'!$W$2:$W$45001, B6, 'Cleaned Transactions Data'!$AG$2:$AG$45001, 1)`
  - 2D Cross-Region Alert Matrix: Dual-condition `COUNTIFS` calculating alert rates for each pair of Customer Region and Merchant Processing Region.

### 2.6 Alert Pattern Summary & Review Outcomes
- **Excel Tab:** `Alert Patterns`
- **Business Question Answered:** *What patterns appear before manual review?*
- **Formulas Implemented:**
  - Grid cross-tabulation using `=COUNTIFS('Cleaned Transactions Data'!$AD$2:$AD$45001, B6, 'Cleaned Transactions Data'!$AE$2:$AE$45001, $C$5)` across all four review statuses and trigger categories.
  - Fraud conversion rate: `=G8/G10` (calculating confirmed fraud proportion).
- **Embedded Chart:** Native Stacked Column Chart displaying trigger composition across Approved, Flagged Fraud, Benign, and Investigation outcomes.

---

## 3. How to Open and Review the Workbook

The completed workbook is saved in two locations:
1. Root Workspace: [PaySphere_Round3_Excel_Analysis.xlsx](file:///Users/navins/Documents/DS_SPRINT/PaySphere_Round3_Excel_Analysis.xlsx)
2. Reports Directory: [PaySphere_Round3_Excel_Analysis.xlsx](file:///Users/navins/Documents/DS_SPRINT/reports/PaySphere_Round3_Excel_Analysis.xlsx)

To open in Microsoft Excel or your spreadsheet viewer:
- Open `PaySphere_Round3_Excel_Analysis.xlsx` directly in Microsoft Excel, Apple Numbers, or Google Sheets.
- Sheet 1 (`Summary Dashboard`) opens as the default view with dynamic KPIs and executive tables.
