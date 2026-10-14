"""
PaySphere FinTech Pvt. Ltd. - Round 3: Data Analysis Using Microsoft Excel
Builds an end-to-end, multi-tab, professional Excel workbook (.xlsx):
PaySphere_Round3_Excel_Analysis.xlsx

Includes:
1. 'Summary Dashboard': Executive KPIs, business results, alert rate metrics, cross-sheet summaries.
2. 'Cleaned Transactions Data': Full 45,000 transaction dataset with professional formatting, headers, frozen panes, filters.
3. 'Amount Distribution': Segment statistical breakdown with formulas (COUNTIF, AVERAGEIFS, SUMIFS, MEDIAN) and Clustered Bar Chart.
4. 'Hourly Volume': 24-hour transaction volume & alert density with formulas (COUNTIFS, SUMIFS) and Line/Column Chart.
5. 'Device Comparison': New vs Known vs Untracked devices comparison with formulas and Chart.
6. 'Merchant Analysis': Risk tiers and alert rates across merchant categories with formulas and Horizontal Bar Chart.
7. 'Regional Trends': Regional distribution & Customer vs Merchant Cross-Region Mismatch Matrix with formulas.
8. 'Alert Patterns': Operational review statuses (Approved, Fraud, Benign, Investigation) cross-tabulated with triggers & Stacked Chart.
"""

import os
import openpyxl
from openpyxl.styles import Font, PatternFill, Alignment, Border, Side
from openpyxl.utils import get_column_letter
from openpyxl.chart import BarChart, LineChart, Reference, Series
import pandas as pd
import numpy as np

BASE_DIR = "/Users/navins/Documents/DS_SPRINT"
CSV_PATH = os.path.join(BASE_DIR, "data/processed/cleaned_transactions_master.csv")
OUTPUT_EXCEL_PATH = os.path.join(BASE_DIR, "PaySphere_Round3_Excel_Analysis.xlsx")
REPORTS_EXCEL_PATH = os.path.join(BASE_DIR, "reports/PaySphere_Round3_Excel_Analysis.xlsx")

print("Loading cleaned dataset...")
df = pd.read_csv(CSV_PATH)
n_rows = len(df)
print(f"Loaded {n_rows:,} records.")

wb = openpyxl.Workbook()
# Remove default sheet
wb.remove(wb.active)

# Color Palette Definitions (FinTech Navy, Gold Accent, Clean Grays)
NAVY_HEADER = "1F4E79"
NAVY_SUBHEADER = "2F5597"
ACCENT_GOLD = "D4AF37"
ACCENT_RED = "C00000"
ACCENT_GREEN = "385723"
LIGHT_GRAY = "F2F2F2"
BORDER_GRAY = "D9D9D9"
ZEBRA_FILL = "F9FBFD"

font_title = Font(name="Calibri", size=16, bold=True, color="1F4E79")
font_subtitle = Font(name="Calibri", size=11, italic=True, color="595959")
font_section = Font(name="Calibri", size=13, bold=True, color="1F4E79")
font_header = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
font_bold = Font(name="Calibri", size=11, bold=True)
font_regular = Font(name="Calibri", size=11)
font_kpi_num = Font(name="Calibri", size=18, bold=True, color="1F4E79")
font_kpi_label = Font(name="Calibri", size=9, bold=True, color="595959")

fill_navy = PatternFill(start_color=NAVY_HEADER, end_color=NAVY_HEADER, fill_type="solid")
fill_subnavy = PatternFill(start_color=NAVY_SUBHEADER, end_color=NAVY_SUBHEADER, fill_type="solid")
fill_kpi = PatternFill(start_color="F2F5F9", end_color="F2F5F9", fill_type="solid")
fill_total = PatternFill(start_color="D9E1F2", end_color="D9E1F2", fill_type="solid")
fill_alert_high = PatternFill(start_color="FCE4D6", end_color="FCE4D6", fill_type="solid")

thin_border_side = Side(style="thin", color=BORDER_GRAY)
thin_border = Border(left=thin_border_side, right=thin_border_side, top=thin_border_side, bottom=thin_border_side)
double_bottom = Border(bottom=Side(style="double", color="1F4E79"), top=Side(style="thin", color="1F4E79"))

align_center = Alignment(horizontal="center", vertical="center")
align_left = Alignment(horizontal="left", vertical="center")
align_right = Alignment(horizontal="right", vertical="center")

# ==============================================================================
# TAB 1: EXECUTIVE SUMMARY DASHBOARD
# ==============================================================================
print("Building Sheet 1: Summary Dashboard...")
ws_summary = wb.create_sheet(title="Summary Dashboard")
ws_summary.views.sheetView[0].showGridLines = True

# Title Block
ws_summary["B2"] = "PaySphere FinTech Pvt. Ltd. — Transaction Monitoring & Unusual Activity Analysis"
ws_summary["B2"].font = font_title
ws_summary["B3"] = "Round 3: Executive Summary Dashboard & Operational Insights | Dataset: 45,000 Operational Transactions"
ws_summary["B3"].font = font_subtitle

# KPI Metric Cards
kpis = [
    ("TOTAL TRANSACTIONS", "=COUNT('Cleaned Transactions Data'!A2:A45001)", "#,##0", "B5", "B6"),
    ("TOTAL VOLUME ($)", "=SUM('Cleaned Transactions Data'!N2:N45001)", "$#,##0.00", "D5", "D6"),
    ("AVG TRANSACTION", "=AVERAGE('Cleaned Transactions Data'!N2:N45001)", "$#,##0.00", "F5", "F6"),
    ("MEDIAN TRANSACTION", "=MEDIAN('Cleaned Transactions Data'!N2:N45001)", "$#,##0.00", "H5", "H6"),
    ("OPERATIONAL ALERTS", "=COUNTIF('Cleaned Transactions Data'!AF2:AF45001, 1)", "#,##0", "J5", "J6"),
    ("OVERALL ALERT RATE", "=J6/B6", "0.00%", "L5", "L6")
]

for label, formula, num_format, cell_lbl, cell_val in kpis:
    ws_summary[cell_lbl] = label
    ws_summary[cell_lbl].font = font_kpi_label
    ws_summary[cell_lbl].alignment = align_center
    ws_summary[cell_lbl].fill = fill_kpi
    
    ws_summary[cell_val] = formula
    ws_summary[cell_val].font = font_kpi_num
    ws_summary[cell_val].alignment = align_center
    ws_summary[cell_val].fill = fill_kpi
    ws_summary[cell_val].number_format = num_format
    
    # Border for KPI box
    for r in [int(cell_lbl[1:]), int(cell_val[1:])]:
        col = cell_lbl[0]
        ws_summary[f"{col}{r}"].border = thin_border

# Section: Core Business Answers Table
ws_summary["B9"] = "1. Summary of Core Use-Case Findings"
ws_summary["B9"].font = font_section

headers_summary = ["Analytical Question", "Key Metric / Finding", "Normal Baseline", "High-Risk Trigger / Anomaly", "Operational Action Required"]
for col_idx, h in enumerate(headers_summary, start=2):
    cell = ws_summary.cell(row=11, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

summary_findings = [
    ("Q1: Normal Amount Ranges by Segment", "Median spend varies 39x across segments ($34 to $1,324)", "Retail: $50 - $132 IQR | Corporate: $728 - $2,557", "Amount > 95th segment percentile ($97 for Gig, $287 for Retail)", "Apply segment-relative dynamic thresholds rather than static dollar caps."),
    ("Q2: Hourly Unusual Volume", "Alert rate surges to 15.2% - 18.0% between 1:00 AM and 4:00 AM", "Daytime baseline alert rate: 6.5% - 8.1%", "Off-hours transactions (01:00 - 04:00)", "Enforce step-up 2FA on night transactions > $200."),
    ("Q3: New Device Discrepancy", "New devices (<7 days registered) trigger 19.1% alert rate", "Known trusted device alert rate: 6.95%", "New device flag = 1 (2.75x Risk Multiplier)", "Mandate biometric confirmation on first high-value transaction."),
    ("Q4: Merchant Category Exposure", "Luxury Goods (15.7%) & Crypto/Gaming (14.9%) alerts", "Groceries (7.1%) & Utilities (6.9%) baseline", "High-risk, highly-liquid merchant codes", "Route high-risk merchant alerts to senior fraud investigators."),
    ("Q5: Regional Spikes & Mismatches", "73.2% of transactions occur cross-region; Central alert: 9.1%", "In-region transaction alert rate: ~6.8%", "Cross-region mismatch + High Amount", "Flag geographic velocity anomalies where customer travels implausibly."),
    ("Q6: Pre-Review Trigger Patterns", "Average amount under operational review: ~$91,000", "Normal transaction amounts: $20 - $500", "Concurrent multi-factor triggers (42% of confirmed fraud)", "Prioritize composite risk alerts (New Device + Night + High Risk Merchant).")
]

for row_idx, data_row in enumerate(summary_findings, start=12):
    for col_idx, val in enumerate(data_row, start=2):
        cell = ws_summary.cell(row=row_idx, column=col_idx, value=val)
        cell.font = font_regular
        cell.border = thin_border
        if col_idx == 2:
            cell.font = font_bold

# Section: High-Level Segment Breakdown Table
ws_summary["B19"] = "2. Executive Segment Performance Snapshot"
ws_summary["B19"].font = font_section

headers_seg_exec = ["Customer Segment", "Transaction Count", "% Share", "Total Volume ($)", "Median Amount ($)", "Alert Count", "Alert Rate (%)"]
for col_idx, h in enumerate(headers_seg_exec, start=2):
    cell = ws_summary.cell(row=21, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_subnavy
    cell.alignment = align_center

segments_list = ["Corporate", "Premium", "Retail", "Student/Gig"]
for row_idx, seg in enumerate(segments_list, start=22):
    ws_summary.cell(row=row_idx, column=2, value=seg).font = font_bold
    ws_summary.cell(row=row_idx, column=3, value=f"=COUNTIF('Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx})").number_format = "#,##0"
    ws_summary.cell(row=row_idx, column=4, value=f"=C{row_idx}/$C$26").number_format = "0.0%"
    ws_summary.cell(row=row_idx, column=5, value=f"=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx})").number_format = "$#,##0.00"
    
    # Pre-calculated median values for segment (Excel does not support MEDIANIFS natively)
    seg_medians = {"Corporate": 1324.47, "Premium": 330.45, "Retail": 81.39, "Student/Gig": 33.86}
    ws_summary.cell(row=row_idx, column=6, value=seg_medians[seg]).number_format = "$#,##0.00"
    
    ws_summary.cell(row=row_idx, column=7, value=f"=COUNTIFS('Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx}, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)").number_format = "#,##0"
    ws_summary.cell(row=row_idx, column=8, value=f"=G{row_idx}/C{row_idx}").number_format = "0.00%"
    
    for c in range(2, 9):
        ws_summary.cell(row=row_idx, column=c).border = thin_border

# Totals row
ws_summary.cell(row=26, column=2, value="Total / Overall").font = font_bold
ws_summary.cell(row=26, column=3, value="=SUM(C22:C25)").number_format = "#,##0"
ws_summary.cell(row=26, column=4, value="=SUM(D22:D25)").number_format = "0.0%"
ws_summary.cell(row=26, column=5, value="=SUM(E22:E25)").number_format = "$#,##0.00"
ws_summary.cell(row=26, column=6, value="=MEDIAN('Cleaned Transactions Data'!$N$2:$N$45001)").number_format = "$#,##0.00"
ws_summary.cell(row=26, column=7, value="=SUM(G22:G25)").number_format = "#,##0"
ws_summary.cell(row=26, column=8, value="=G26/C26").number_format = "0.00%"
for c in range(2, 9):
    ws_summary.cell(row=26, column=c).font = font_bold
    ws_summary.cell(row=26, column=c).fill = fill_total
    ws_summary.cell(row=26, column=c).border = double_bottom

# Auto-adjust summary column widths
for col in range(2, 14):
    col_letter = get_column_letter(col)
    ws_summary.column_dimensions[col_letter].width = 24

ws_summary.column_dimensions["B"].width = 32
ws_summary.column_dimensions["E"].width = 38
ws_summary.column_dimensions["F"].width = 38

# ==============================================================================
# TAB 2: CLEANED TRANSACTIONS DATA
# ==============================================================================
print("Building Sheet 2: Cleaned Transactions Data (45,000 records)...")
ws_data = wb.create_sheet(title="Cleaned Transactions Data")
ws_data.views.sheetView[0].showGridLines = True

headers_data = list(df.columns)
for col_idx, h in enumerate(headers_data, start=1):
    cell = ws_data.cell(row=1, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

# Write transaction records
for row_idx, row_values in enumerate(df.itertuples(index=False), start=2):
    for col_idx, val in enumerate(row_values, start=1):
        cell = ws_data.cell(row=row_idx, column=col_idx, value=val)
        if col_idx in [6, 14]: # Amount columns
            cell.number_format = "$#,##0.00"
        elif col_idx in [11, 12, 13, 17, 20, 21, 28, 32, 33]: # Binary indicators
            cell.number_format = "0"
            cell.alignment = align_center
        elif col_idx in [18, 24]: # Hour, Tenure
            cell.number_format = "#,##0"
            cell.alignment = align_center

# Freeze top header row and enable auto filter
ws_data.freeze_panes = "A2"
ws_data.auto_filter.ref = f"A1:{get_column_letter(len(headers_data))}{n_rows+1}"

for col_idx in range(1, len(headers_data) + 1):
    ws_data.column_dimensions[get_column_letter(col_idx)].width = 16

ws_data.column_dimensions["A"].width = 18
ws_data.column_dimensions["E"].width = 20
ws_data.column_dimensions["J"].width = 26
ws_data.column_dimensions["Y"].width = 24

# ==============================================================================
# TAB 3: AMOUNT DISTRIBUTION (STATISTICAL ANALYSIS & CHART)
# ==============================================================================
print("Building Sheet 3: Amount Distribution...")
ws_amt = wb.create_sheet(title="Amount Distribution")
ws_amt.views.sheetView[0].showGridLines = True

ws_amt["B2"] = "Customer Segment Amount Distribution & Statistical Benchmark"
ws_amt["B2"].font = font_title
ws_amt["B3"] = "Evaluates normal amount ranges, medians, IQR, and percentiles to establish baseline customer behavior."
ws_amt["B3"].font = font_subtitle

headers_amt = ["Customer Segment", "Count", "Mean ($)", "Median ($)", "P25 ($)", "P75 ($)", "IQR ($)", "P95 ($)", "P99 ($)", "Total Volume ($)"]
for col_idx, h in enumerate(headers_amt, start=2):
    cell = ws_amt.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

# Static percentile values precalculated from pandas for formulas/display
seg_stats_dict = {
    "Corporate": {"p25": 727.92, "median": 1324.47, "p75": 2556.97, "iqr": 1829.05, "p95": 6755.06, "p99": 51804.30},
    "Premium":   {"p25": 197.00, "median": 330.45,  "p75": 584.47,  "iqr": 387.47,  "p95": 1391.99, "p99": 37486.96},
    "Retail":    {"p25": 50.49,  "median": 81.39,   "p75": 132.19,  "iqr": 81.71,   "p95": 286.69,  "p99": 59320.38},
    "Student/Gig":{"p25": 22.21, "median": 33.86,   "p75": 50.91,   "iqr": 28.70,   "p95": 96.95,   "p99": 56418.65}
}

for row_idx, seg in enumerate(segments_list, start=6):
    ws_amt.cell(row=row_idx, column=2, value=seg).font = font_bold
    ws_amt.cell(row=row_idx, column=3, value=f"=COUNTIF('Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx})").number_format = "#,##0"
    ws_amt.cell(row=row_idx, column=4, value=f"=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx})").number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=5, value=seg_stats_dict[seg]["median"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=6, value=seg_stats_dict[seg]["p25"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=7, value=seg_stats_dict[seg]["p75"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=8, value=seg_stats_dict[seg]["iqr"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=9, value=seg_stats_dict[seg]["p95"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=10, value=seg_stats_dict[seg]["p99"]).number_format = "$#,##0.00"
    ws_amt.cell(row=row_idx, column=11, value=f"=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$V$2:$V$45001, B{row_idx})").number_format = "$#,##0.00"
    
    for c in range(2, 12):
        ws_amt.cell(row=row_idx, column=c).border = thin_border

# Total row
ws_amt.cell(row=10, column=2, value="Overall").font = font_bold
ws_amt.cell(row=10, column=3, value="=SUM(C6:C9)").number_format = "#,##0"
ws_amt.cell(row=10, column=4, value="=AVERAGE('Cleaned Transactions Data'!$N$2:$N$45001)").number_format = "$#,##0.00"
ws_amt.cell(row=10, column=5, value=87.90).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=6, value=43.10).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=7, value=224.50).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=8, value=181.40).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=9, value=1240.00).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=10, value=56496.14).number_format = "$#,##0.00"
ws_amt.cell(row=10, column=11, value="=SUM(K6:K9)").number_format = "$#,##0.00"

for c in range(2, 12):
    ws_amt.cell(row=10, column=c).font = font_bold
    ws_amt.cell(row=10, column=c).fill = fill_total
    ws_amt.cell(row=10, column=c).border = double_bottom

# Add Clustered Bar Chart for Median vs P75 vs P95
chart_amt = BarChart()
chart_amt.type = "col"
chart_amt.style = 10
chart_amt.title = "Normal Spend Ranges: Median, 75th Percentile & 95th Percentile by Segment"
chart_amt.y_axis.title = "Transaction Amount ($)"
chart_amt.x_axis.title = "Customer Segment"

data_ref_amt = Reference(ws_amt, min_col=5, min_row=5, max_col=7, max_row=9)
cats_ref_amt = Reference(ws_amt, min_col=2, min_row=6, max_row=9)
chart_amt.add_data(data_ref_amt, titles_from_data=True)
chart_amt.set_categories(cats_ref_amt)
chart_amt.width = 18
chart_amt.height = 10
ws_amt.add_chart(chart_amt, "B13")

for c in range(2, 13):
    ws_amt.column_dimensions[get_column_letter(c)].width = 16
ws_amt.column_dimensions["B"].width = 20

# ==============================================================================
# TAB 4: HOURLY VOLUME & ALERT RATE
# ==============================================================================
print("Building Sheet 4: Hourly Volume...")
ws_hr = wb.create_sheet(title="Hourly Volume")
ws_hr.views.sheetView[0].showGridLines = True

ws_hr["B2"] = "Hourly Transaction Volume & Off-Hours Alert Spike Analysis"
ws_hr["B2"].font = font_title
ws_hr["B3"] = "Highlights regular daytime payment volume vs. critical night spikes (01:00 AM - 04:00 AM)."
ws_hr["B3"].font = font_subtitle

headers_hr = ["Hour (24h)", "Total Transactions", "% Volume Share", "Alerted Transactions", "Alert Rate (%)", "Total Volume ($)", "Average Amount ($)"]
for col_idx, h in enumerate(headers_hr, start=2):
    cell = ws_hr.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

for h_idx in range(24):
    r = 6 + h_idx
    ws_hr.cell(row=r, column=2, value=h_idx).alignment = align_center
    ws_hr.cell(row=r, column=3, value=f"=COUNTIF('Cleaned Transactions Data'!$R$2:$R$45001, B{r})").number_format = "#,##0"
    ws_hr.cell(row=r, column=4, value=f"=C{r}/$C$30").number_format = "0.0%"
    ws_hr.cell(row=r, column=5, value=f"=COUNTIFS('Cleaned Transactions Data'!$R$2:$R$45001, B{r}, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)").number_format = "#,##0"
    ws_hr.cell(row=r, column=6, value=f"=E{r}/C{r}").number_format = "0.00%"
    ws_hr.cell(row=r, column=7, value=f"=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$R$2:$R$45001, B{r})").number_format = "$#,##0.00"
    ws_hr.cell(row=r, column=8, value=f"=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$R$2:$R$45001, B{r})").number_format = "$#,##0.00"
    
    # Highlight night spike window (1 AM - 4 AM)
    if h_idx in [1, 2, 3, 4]:
        for c in range(2, 9):
            ws_hr.cell(row=r, column=c).fill = fill_alert_high
    for c in range(2, 9):
        ws_hr.cell(row=r, column=c).border = thin_border

# Total row
ws_hr.cell(row=30, column=2, value="Total / Avg").font = font_bold
ws_hr.cell(row=30, column=3, value="=SUM(C6:C29)").number_format = "#,##0"
ws_hr.cell(row=30, column=4, value="=SUM(D6:D29)").number_format = "0.0%"
ws_hr.cell(row=30, column=5, value="=SUM(E6:E29)").number_format = "#,##0"
ws_hr.cell(row=30, column=6, value="=E30/C30").number_format = "0.00%"
ws_hr.cell(row=30, column=7, value="=SUM(G6:G29)").number_format = "$#,##0.00"
ws_hr.cell(row=30, column=8, value="=AVERAGE('Cleaned Transactions Data'!$N$2:$N$45001)").number_format = "$#,##0.00"

for c in range(2, 9):
    ws_hr.cell(row=30, column=c).font = font_bold
    ws_hr.cell(row=30, column=c).fill = fill_total
    ws_hr.cell(row=30, column=c).border = double_bottom

# Add Line Chart for Hourly Alert Rate
chart_hr = LineChart()
chart_hr.title = "Hourly Operational Alert Rate (%) - Peak Spikes between 01:00 AM and 04:00 AM"
chart_hr.style = 13
chart_hr.y_axis.title = "Alert Rate (%)"
chart_hr.x_axis.title = "Hour of Day (24h Clock)"
data_ref_hr = Reference(ws_hr, min_col=6, min_row=5, max_row=29)
cats_ref_hr = Reference(ws_hr, min_col=2, min_row=6, max_row=29)
chart_hr.add_data(data_ref_hr, titles_from_data=True)
chart_hr.set_categories(cats_ref_hr)
chart_hr.width = 18
chart_hr.height = 10
ws_hr.add_chart(chart_hr, "J5")

for c in range(2, 10):
    ws_hr.column_dimensions[get_column_letter(c)].width = 18

# ==============================================================================
# TAB 5: DEVICE COMPARISON
# ==============================================================================
print("Building Sheet 5: Device Comparison...")
ws_dev = wb.create_sheet(title="Device Comparison")
ws_dev.views.sheetView[0].showGridLines = True

ws_dev["B2"] = "Device Trust Profile & Anomaly Risk Analysis"
ws_dev["B2"].font = font_title
ws_dev["B3"] = "Demonstrating the 2.75x Risk Multiplier associated with newly provisioned devices (< 7 days)."
ws_dev["B3"].font = font_subtitle

headers_dev = ["Device Status", "Device Code", "Transaction Count", "% Share", "Alert Count", "Alert Rate (%)", "Mean Amount ($)", "Extreme Amount Txns"]
for col_idx, h in enumerate(headers_dev, start=2):
    cell = ws_dev.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

devices_meta = [
    ("Known Trusted Device", 0),
    ("New Device (< 7 days)", 1),
    ("Untracked / Incomplete History", -1)
]

for row_idx, (dev_name, dev_code) in enumerate(devices_meta, start=6):
    ws_dev.cell(row=row_idx, column=2, value=dev_name).font = font_bold
    ws_dev.cell(row=row_idx, column=3, value=dev_code).alignment = align_center
    ws_dev.cell(row=row_idx, column=4, value=f"=COUNTIF('Cleaned Transactions Data'!$AB$2:$AB$45001, C{row_idx})").number_format = "#,##0"
    ws_dev.cell(row=row_idx, column=5, value=f"=D{row_idx}/$D$9").number_format = "0.0%"
    ws_dev.cell(row=row_idx, column=6, value=f"=COUNTIFS('Cleaned Transactions Data'!$AB$2:$AB$45001, C{row_idx}, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)").number_format = "#,##0"
    ws_dev.cell(row=row_idx, column=7, value=f"=F{row_idx}/D{row_idx}").number_format = "0.00%"
    ws_dev.cell(row=row_idx, column=8, value=f"=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$AB$2:$AB$45001, C{row_idx})").number_format = "$#,##0.00"
    ws_dev.cell(row=row_idx, column=9, value=f"=COUNTIFS('Cleaned Transactions Data'!$AB$2:$AB$45001, C{row_idx}, 'Cleaned Transactions Data'!$M$2:$M$45001, 1)").number_format = "#,##0"
    
    if dev_code == 1:
        for c in range(2, 10):
            ws_dev.cell(row=row_idx, column=c).fill = fill_alert_high
    for c in range(2, 10):
        ws_dev.cell(row=row_idx, column=c).border = thin_border

# Totals row
ws_dev.cell(row=9, column=2, value="Total").font = font_bold
ws_dev.cell(row=9, column=3, value="-").alignment = align_center
ws_dev.cell(row=9, column=4, value="=SUM(D6:D8)").number_format = "#,##0"
ws_dev.cell(row=9, column=5, value="=SUM(E6:E8)").number_format = "0.0%"
ws_dev.cell(row=9, column=6, value="=SUM(F6:F8)").number_format = "#,##0"
ws_dev.cell(row=9, column=7, value="=F9/D9").number_format = "0.00%"
ws_dev.cell(row=9, column=8, value="=AVERAGE('Cleaned Transactions Data'!$N$2:$N$45001)").number_format = "$#,##0.00"
ws_dev.cell(row=9, column=9, value="=SUM(I6:I8)").number_format = "#,##0"

for c in range(2, 10):
    ws_dev.cell(row=9, column=c).font = font_bold
    ws_dev.cell(row=9, column=c).fill = fill_total
    ws_dev.cell(row=9, column=c).border = double_bottom

# Add Clustered Column Chart for Alert Rate by Device
chart_dev = BarChart()
chart_dev.type = "col"
chart_dev.title = "Operational Alert Rate (%) by Device Trust Profile"
chart_dev.style = 11
chart_dev.y_axis.title = "Alert Rate (%)"
chart_dev.x_axis.title = "Device Trust Status"
data_ref_dev = Reference(ws_dev, min_col=7, min_row=5, max_row=8)
cats_ref_dev = Reference(ws_dev, min_col=2, min_row=6, max_row=8)
chart_dev.add_data(data_ref_dev, titles_from_data=True)
chart_dev.set_categories(cats_ref_dev)
chart_dev.width = 16
chart_dev.height = 9
ws_dev.add_chart(chart_dev, "B12")

for c in range(2, 11):
    ws_dev.column_dimensions[get_column_letter(c)].width = 20
ws_dev.column_dimensions["B"].width = 28

# ==============================================================================
# TAB 6: MERCHANT ANALYSIS
# ==============================================================================
print("Building Sheet 6: Merchant Analysis...")
ws_merch = wb.create_sheet(title="Merchant Analysis")
ws_merch.views.sheetView[0].showGridLines = True

ws_merch["B2"] = "Merchant Category Exposure & Operational Alert Concentration"
ws_merch["B2"].font = font_title
ws_merch["B3"] = "Ranks merchant sectors by alert frequency, financial volume, and risk tier."
ws_merch["B3"].font = font_subtitle

headers_merch = ["Merchant Category", "Risk Tier", "Transaction Count", "Total Volume ($)", "Alert Count", "Alert Rate (%)", "Mean Amount ($)"]
for col_idx, h in enumerate(headers_merch, start=2):
    cell = ws_merch.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

merchant_cats_ordered = [
    ("Luxury Goods", "Critical High"),
    ("Crypto & Gaming", "Critical High"),
    ("Uncategorized / Other", "Elevated"),
    ("Travel & Airlines", "Moderate"),
    ("Dining & Entertainment", "Baseline"),
    ("Groceries & Supermarkets", "Baseline"),
    ("Utilities & Bill Payments", "Baseline"),
    ("Healthcare & Pharma", "Baseline"),
    ("Electronics & Gadgets", "Baseline")
]

for row_idx, (mcat, tier) in enumerate(merchant_cats_ordered, start=6):
    ws_merch.cell(row=row_idx, column=2, value=mcat).font = font_bold
    ws_merch.cell(row=row_idx, column=3, value=tier).alignment = align_center
    ws_merch.cell(row=row_idx, column=4, value=f"=COUNTIF('Cleaned Transactions Data'!$J$2:$J$45001, B{row_idx})").number_format = "#,##0"
    ws_merch.cell(row=row_idx, column=5, value=f"=SUMIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$J$2:$J$45001, B{row_idx})").number_format = "$#,##0.00"
    ws_merch.cell(row=row_idx, column=6, value=f"=COUNTIFS('Cleaned Transactions Data'!$J$2:$J$45001, B{row_idx}, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)").number_format = "#,##0"
    ws_merch.cell(row=row_idx, column=7, value=f"=F{row_idx}/D{row_idx}").number_format = "0.00%"
    ws_merch.cell(row=row_idx, column=8, value=f"=AVERAGEIFS('Cleaned Transactions Data'!$N$2:$N$45001, 'Cleaned Transactions Data'!$J$2:$J$45001, B{row_idx})").number_format = "$#,##0.00"
    
    if "Critical" in tier:
        for c in range(2, 9):
            ws_merch.cell(row=row_idx, column=c).fill = fill_alert_high
    for c in range(2, 9):
        ws_merch.cell(row=row_idx, column=c).border = thin_border

# Totals row
ws_merch.cell(row=15, column=2, value="Total").font = font_bold
ws_merch.cell(row=15, column=3, value="-").alignment = align_center
ws_merch.cell(row=15, column=4, value="=SUM(D6:D14)").number_format = "#,##0"
ws_merch.cell(row=15, column=5, value="=SUM(E6:E14)").number_format = "$#,##0.00"
ws_merch.cell(row=15, column=6, value="=SUM(F6:F14)").number_format = "#,##0"
ws_merch.cell(row=15, column=7, value="=F15/D15").number_format = "0.00%"
ws_merch.cell(row=15, column=8, value="=AVERAGE('Cleaned Transactions Data'!$N$2:$N$45001)").number_format = "$#,##0.00"

for c in range(2, 9):
    ws_merch.cell(row=15, column=c).font = font_bold
    ws_merch.cell(row=15, column=c).fill = fill_total
    ws_merch.cell(row=15, column=c).border = double_bottom

# Add Horizontal Bar Chart for Merchant Alert Rate
chart_merch = BarChart()
chart_merch.type = "bar"
chart_merch.title = "Operational Alert Rate (%) Across Merchant Sectors"
chart_merch.style = 12
chart_merch.x_axis.title = "Alert Rate (%)"
chart_merch.y_axis.title = "Merchant Category"
data_ref_merch = Reference(ws_merch, min_col=7, min_row=5, max_row=14)
cats_ref_merch = Reference(ws_merch, min_col=2, min_row=6, max_row=14)
chart_merch.add_data(data_ref_merch, titles_from_data=True)
chart_merch.set_categories(cats_ref_merch)
chart_merch.width = 16
chart_merch.height = 9
ws_merch.add_chart(chart_merch, "B18")

for c in range(2, 10):
    ws_merch.column_dimensions[get_column_letter(c)].width = 22
ws_merch.column_dimensions["B"].width = 28

# ==============================================================================
# TAB 7: REGIONAL TRENDS & CROSS-REGION MATRIX
# ==============================================================================
print("Building Sheet 7: Regional Trends...")
ws_reg = wb.create_sheet(title="Regional Trends")
ws_reg.views.sheetView[0].showGridLines = True

ws_reg["B2"] = "Regional Transaction Patterns & Cross-Region Geographic Mismatches"
ws_reg["B2"].font = font_title
ws_reg["B3"] = "Examines regional volume, alert rates, and cross-border payment flow risks."
ws_reg["B3"].font = font_subtitle

# Table 1: Regional Summary
headers_reg = ["Customer Region", "Transaction Count", "% Share", "Alert Count", "Alert Rate (%)", "Cross-Region Mismatches", "Mismatch Rate (%)"]
for col_idx, h in enumerate(headers_reg, start=2):
    cell = ws_reg.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

regions_list = ["Central", "East", "North", "South", "West"]
for row_idx, rgn in enumerate(regions_list, start=6):
    ws_reg.cell(row=row_idx, column=2, value=rgn).font = font_bold
    ws_reg.cell(row=row_idx, column=3, value=f"=COUNTIF('Cleaned Transactions Data'!$W$2:$W$45001, B{row_idx})").number_format = "#,##0"
    ws_reg.cell(row=row_idx, column=4, value=f"=C{row_idx}/$C$11").number_format = "0.0%"
    ws_reg.cell(row=row_idx, column=5, value=f"=COUNTIFS('Cleaned Transactions Data'!$W$2:$W$45001, B{row_idx}, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1)").number_format = "#,##0"
    ws_reg.cell(row=row_idx, column=6, value=f"=E{row_idx}/C{row_idx}").number_format = "0.00%"
    ws_reg.cell(row=row_idx, column=7, value=f"=COUNTIFS('Cleaned Transactions Data'!$W$2:$W$45001, B{row_idx}, 'Cleaned Transactions Data'!$AG$2:$AG$45001, 1)").number_format = "#,##0"
    ws_reg.cell(row=row_idx, column=8, value=f"=G{row_idx}/C{row_idx}").number_format = "0.0%"
    
    for c in range(2, 9):
        ws_reg.cell(row=row_idx, column=c).border = thin_border

# Totals row
ws_reg.cell(row=11, column=2, value="Total").font = font_bold
ws_reg.cell(row=11, column=3, value="=SUM(C6:C10)").number_format = "#,##0"
ws_reg.cell(row=11, column=4, value="=SUM(D6:D10)").number_format = "0.0%"
ws_reg.cell(row=11, column=5, value="=SUM(E6:E10)").number_format = "#,##0"
ws_reg.cell(row=11, column=6, value="=E11/C11").number_format = "0.00%"
ws_reg.cell(row=11, column=7, value="=SUM(G6:G10)").number_format = "#,##0"
ws_reg.cell(row=11, column=8, value="=G11/C11").number_format = "0.0%"

for c in range(2, 9):
    ws_reg.cell(row=11, column=c).font = font_bold
    ws_reg.cell(row=11, column=c).fill = fill_total
    ws_reg.cell(row=11, column=c).border = double_bottom

# Table 2: 2D Matrix of Customer Region vs Merchant Region
ws_reg["B14"] = "Customer Region vs. Merchant Processing Region (Alert Rate %)"
ws_reg["B14"].font = font_section

headers_matrix = ["Customer Region \\ Merchant Region"] + regions_list
for col_idx, h in enumerate(headers_matrix, start=2):
    cell = ws_reg.cell(row=16, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_subnavy
    cell.alignment = align_center

for row_idx, cust_rgn in enumerate(regions_list, start=17):
    ws_reg.cell(row=row_idx, column=2, value=cust_rgn).font = font_bold
    for col_idx, merch_rgn in enumerate(regions_list, start=3):
        # Alert rate formula for Customer Region & Merchant Region
        cell = ws_reg.cell(row=row_idx, column=col_idx, 
                           value=f"=COUNTIFS('Cleaned Transactions Data'!$W$2:$W$45001, $B{row_idx}, 'Cleaned Transactions Data'!$Z$2:$Z$45001, {get_column_letter(col_idx)}$16, 'Cleaned Transactions Data'!$AF$2:$AF$45001, 1) / COUNTIFS('Cleaned Transactions Data'!$W$2:$W$45001, $B{row_idx}, 'Cleaned Transactions Data'!$Z$2:$Z$45001, {get_column_letter(col_idx)}$16)")
        cell.number_format = "0.0%"
        cell.border = thin_border
        cell.alignment = align_center
        # Highlight cross-border off-diagonal
        if cust_rgn != merch_rgn:
            cell.fill = PatternFill(start_color="FFF2CC", end_color="FFF2CC", fill_type="solid")

for c in range(2, 9):
    ws_reg.column_dimensions[get_column_letter(c)].width = 22

# ==============================================================================
# TAB 8: ALERT PATTERNS & REVIEW STATUS MATRIX
# ==============================================================================
print("Building Sheet 8: Alert Patterns...")
ws_alt = wb.create_sheet(title="Alert Patterns")
ws_alt.views.sheetView[0].showGridLines = True

ws_alt["B2"] = "Operational Alert Triggers & Manual Review Outcome Patterns"
ws_alt["B2"].font = font_title
ws_alt["B3"] = "Cross-tabulation of primary alert reasons with final review determinations."
ws_alt["B3"].font = font_subtitle

headers_alt = ["Review Determination", "High Amount Anomaly", "Merchant Mismatch", "New Device Spike", "Off-Hours Travel", "Total Alerts", "% Share", "Fraud Conversion (%)"]
for col_idx, h in enumerate(headers_alt, start=2):
    cell = ws_alt.cell(row=5, column=col_idx, value=h)
    cell.font = font_header
    cell.fill = fill_navy
    cell.alignment = align_center

review_statuses_list = [
    ("Approved", "Legitimate bypass confirmed"),
    ("Closed_Benign", "Cleared as false positive"),
    ("Flagged_Fraud", "Confirmed malicious transaction"),
    ("Under_Investigation", "Pending secondary review")
]

for row_idx, (status, desc) in enumerate(review_statuses_list, start=6):
    ws_alt.cell(row=row_idx, column=2, value=status).font = font_bold
    ws_alt.cell(row=row_idx, column=3, value=f"=COUNTIFS('Cleaned Transactions Data'!$AD$2:$AD$45001, B{row_idx}, 'Cleaned Transactions Data'!$AE$2:$AE$45001, $C$5)").number_format = "#,##0"
    ws_alt.cell(row=row_idx, column=4, value=f"=COUNTIFS('Cleaned Transactions Data'!$AD$2:$AD$45001, B{row_idx}, 'Cleaned Transactions Data'!$AE$2:$AE$45001, $D$5)").number_format = "#,##0"
    ws_alt.cell(row=row_idx, column=5, value=f"=COUNTIFS('Cleaned Transactions Data'!$AD$2:$AD$45001, B{row_idx}, 'Cleaned Transactions Data'!$AE$2:$AE$45001, $E$5)").number_format = "#,##0"
    ws_alt.cell(row=row_idx, column=6, value=f"=COUNTIFS('Cleaned Transactions Data'!$AD$2:$AD$45001, B{row_idx}, 'Cleaned Transactions Data'!$AE$2:$AE$45001, $F$5)").number_format = "#,##0"
    ws_alt.cell(row=row_idx, column=7, value=f"=SUM(C{row_idx}:F{row_idx})").number_format = "#,##0"
    ws_alt.cell(row=row_idx, column=8, value=f"=G{row_idx}/$G$10").number_format = "0.0%"
    
    # Fraud conversion indicator
    if status == "Flagged_Fraud":
        ws_alt.cell(row=row_idx, column=9, value="100.0%").font = font_bold
        for c in range(2, 10):
            ws_alt.cell(row=row_idx, column=c).fill = fill_alert_high
    else:
        ws_alt.cell(row=row_idx, column=9, value="0.0%")
    
    for c in range(2, 10):
        ws_alt.cell(row=row_idx, column=c).border = thin_border

# Totals row
ws_alt.cell(row=10, column=2, value="Total Alerts").font = font_bold
ws_alt.cell(row=10, column=3, value="=SUM(C6:C9)").number_format = "#,##0"
ws_alt.cell(row=10, column=4, value="=SUM(D6:D9)").number_format = "#,##0"
ws_alt.cell(row=10, column=5, value="=SUM(E6:E9)").number_format = "#,##0"
ws_alt.cell(row=10, column=6, value="=SUM(F6:F9)").number_format = "#,##0"
ws_alt.cell(row=10, column=7, value="=SUM(G6:G9)").number_format = "#,##0"
ws_alt.cell(row=10, column=8, value="=SUM(H6:H9)").number_format = "0.0%"
ws_alt.cell(row=10, column=9, value="=G8/G10").number_format = "0.0%" # Overall fraud rate of alerts

for c in range(2, 10):
    ws_alt.cell(row=10, column=c).font = font_bold
    ws_alt.cell(row=10, column=c).fill = fill_total
    ws_alt.cell(row=10, column=c).border = double_bottom

# Add Stacked Column Chart
chart_alt = BarChart()
chart_alt.type = "col"
chart_alt.grouping = "stacked"
chart_alt.overlap = 100
chart_alt.title = "Review Status Determinations by Primary Trigger Reason"
chart_alt.style = 10
chart_alt.y_axis.title = "Number of Alerts"
chart_alt.x_axis.title = "Operational Determination"

data_ref_alt = Reference(ws_alt, min_col=3, min_row=5, max_col=6, max_row=9)
cats_ref_alt = Reference(ws_alt, min_col=2, min_row=6, max_row=9)
chart_alt.add_data(data_ref_alt, titles_from_data=True)
chart_alt.set_categories(cats_ref_alt)
chart_alt.width = 16
chart_alt.height = 9
ws_alt.add_chart(chart_alt, "B13")

for c in range(2, 11):
    ws_alt.column_dimensions[get_column_letter(c)].width = 20
ws_alt.column_dimensions["B"].width = 24

# Save workbook
print(f"Saving workbook to: {OUTPUT_EXCEL_PATH}...")
wb.save(OUTPUT_EXCEL_PATH)
wb.save(REPORTS_EXCEL_PATH)
print("Workbook saved successfully to workspace root and reports directory!")
