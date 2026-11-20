"""Materialize the star schema as SQLite and run reproducible analytical SQL."""
from pathlib import Path
import sqlite3
import pandas as pd

def build(processed:Path, db:Path, sql_dir:Path, reports:Path):
    db.parent.mkdir(parents=True,exist_ok=True);reports.mkdir(parents=True,exist_ok=True)
    with sqlite3.connect(db) as conn:
        for table in ['fact_orders','fact_items','dim_customers','dim_products','dim_date']:
            pd.read_csv(processed/f'{table}.csv').to_sql(table,conn,if_exists='replace',index=False,chunksize=5000)
        conn.executescript('''CREATE UNIQUE INDEX IF NOT EXISTS idx_orders_pk ON fact_orders(order_id);
CREATE INDEX IF NOT EXISTS idx_items_order ON fact_items(order_id);
CREATE INDEX IF NOT EXISTS idx_orders_month ON fact_orders(order_month);
CREATE INDEX IF NOT EXISTS idx_orders_customer ON fact_orders(customer_unique_id);
CREATE INDEX IF NOT EXISTS idx_items_product ON fact_items(product_id);''')
        for file in sorted(sql_dir.glob('*.sql')):
            result=pd.read_sql_query(file.read_text(),conn)
            result.to_csv(reports/(file.stem+'.csv'),index=False)

if __name__=='__main__':
    build(Path('data/processed'),Path('data/commercepulse.sqlite'),Path('sql'),Path('reports'))
