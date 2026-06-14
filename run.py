import subprocess, sys

print("\n" + "="*50)
print("Sales KPI Dashboard — Superstore Data")
print("="*50)

print("\nStep 1: Running ETL pipeline...")
result = subprocess.run([sys.executable, "src/etl.py"], capture_output=False)
if result.returncode != 0:
    print("ETL failed — check superstore.csv is in data/ folder")
    sys.exit(1)

print("\nStep 2: Computing KPIs...")
subprocess.run([sys.executable, "src/kpis.py"], capture_output=False)

print("\nStep 3: Starting dashboard...")
print("Open browser at: http://127.0.0.1:8050")
print("="*50 + "\n")
subprocess.run([sys.executable, "app.py"])