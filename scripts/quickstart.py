"""One command runs synthetic demo (optional), ETL, SQL, model and reports."""
import argparse
from pathlib import Path
import sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT))
from src import pipeline,modeling,database,reports
from scripts.generate_demo import generate

def main():
    p=argparse.ArgumentParser();p.add_argument('--demo',action='store_true',help='Generate clearly labeled synthetic sample data');p.add_argument('--n-orders',type=int,default=6200)
    a=p.parse_args();raw=ROOT/'data/raw'; processed=ROOT/'data/processed'
    if a.demo:
        print('Generating SYNTHETIC DEMO rows (not real Olist)...',flush=True);generate(raw,a.n_orders)
    elif (raw/'SYNTHETIC_DEMO_DATA.txt').exists():
        raise SystemExit('Synthetic marker found. To analyze original data, replace demo CSVs AND delete data/raw/SYNTHETIC_DEMO_DATA.txt; then rerun.')
    print('ETL...',flush=True);print(pipeline.build(raw,processed),flush=True)
    print('SQLite SQL queries...',flush=True);database.build(processed,ROOT/'data/commercepulse.sqlite',ROOT/'sql',ROOT/'reports')
    print('Temporal ML evaluation...',flush=True);print(modeling.train(processed,ROOT/'models'),flush=True)
    print('Business report & interactive HTML...',flush=True);print(reports.build(processed,ROOT/'reports'),flush=True)
    pb=ROOT/'data/powerbi';pb.mkdir(exist_ok=True,parents=True)
    for file in processed.glob('*.csv'):
        (pb/file.name).write_bytes(file.read_bytes())
    pred=ROOT/'models/out_of_time_predictions.csv'
    if pred.exists(): (pb/pred.name).write_bytes(pred.read_bytes())
    print(f'\nDONE. Open {ROOT/"reports/interactive_dashboard.html"} in a browser, or run: streamlit run app/dashboard.py')
    print('Power BI-ready CSVs: data/powerbi/   |   DAX and build guide: powerbi/')

if __name__=='__main__':main()
