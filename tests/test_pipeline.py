from pathlib import Path
import pandas as pd
import numpy as np
from scripts.generate_demo import generate
from src.pipeline import build

def test_grains_and_gmv(tmp_path:Path):
    raw,processed=tmp_path/'raw',tmp_path/'processed'
    generate(raw,n_orders=750,seed=7)
    q=build(raw,processed)
    o=pd.read_csv(processed/'fact_orders.csv'); i=pd.read_csv(processed/'fact_items.csv')
    assert q['duplicate_order_ids']==0
    assert len(o)==750
    assert len(i)>=len(o)
    assert q['order_gmv_matches_item_gmv']
    assert np.isclose(o['gmv_brl'].sum(),i['gmv_brl'].sum(),atol=.02)
    assert len(pd.read_csv(processed/'dim_customers.csv'))==o['customer_unique_id'].nunique()
    assert ((o['is_late']==1)&(o['is_delivered']==0)).sum()==0

def test_duplicate_reviews_dont_multiply_orders(tmp_path:Path):
    raw,out=tmp_path/'raw',tmp_path/'out'
    generate(raw,n_orders=550,seed=16)
    r=pd.read_csv(raw/'olist_order_reviews_dataset.csv')
    r=pd.concat([r,r.head(20)],ignore_index=True);r.to_csv(raw/'olist_order_reviews_dataset.csv',index=False)
    build(raw,out)
    o=pd.read_csv(out/'fact_orders.csv');assert len(o)==550
    assert o['order_id'].is_unique

def test_duplicate_payments_dont_multiply_orders(tmp_path:Path):
    raw,out=tmp_path/'raw',tmp_path/'out'
    generate(raw,n_orders=550,seed=13)
    p=pd.read_csv(raw/'olist_order_payments_dataset.csv')
    p=pd.concat([p,p.head(10)],ignore_index=True);p.to_csv(raw/'olist_order_payments_dataset.csv',index=False)
    build(raw,out)
    o=pd.read_csv(out/'fact_orders.csv');assert len(o)==550
    assert o['order_id'].is_unique
