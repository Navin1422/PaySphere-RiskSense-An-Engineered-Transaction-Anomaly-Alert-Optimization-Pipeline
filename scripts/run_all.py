"""
PaySphere FinTech Pvt. Ltd. - End-to-End Master Execution Pipeline
Executes all steps for Round 2: EDA & Feature Engineering
"""

import subprocess
import sys
import os

SCRIPTS = [
    "01_generate_dataset.py",
    "02_eda_and_cleaning.py",
    "03_feature_engineering.py",
    "generate_notebook.py",
    "04_create_excel_model.py"
]

SCRIPTS_DIR = os.path.dirname(os.path.abspath(__file__))

print("="*80)
print("PAYSPHERE FINTECH - ROUND 2 AUTOMATED PIPELINE EXECUTION")
print("="*80)

for s in SCRIPTS:
    script_path = os.path.join(SCRIPTS_DIR, s)
    print(f"\n>>> Running {s}...")
    res = subprocess.run([sys.executable, script_path], check=True)
    if res.returncode != 0:
        print(f"Error running {s}. Pipeline halted.")
        sys.exit(1)

print("\n" + "="*80)
print("ALL ROUND 2 STAGES EXECUTED SUCCESSFULLY!")
print("Cleaned datasets, features, figures, and Jupyter Notebook are generated.")
print("="*80)
