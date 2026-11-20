"""Olist ETL with explicit grain control. A payment or review row NEVER multiplies items."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd

TABLES={'orders':'olist_orders_dataset.csv','customers':'olist_customers_dataset.csv','items':'olist_order_items_dataset.csv',
        'payments':'olist_order_payments_dataset.csv','reviews':'olist_order_reviews_dataset.csv','products':'olist_products_dataset.csv'}

def load(raw:Path)->dict[str,pd.DataFrame]:
    data={}
    for key,fn in TABLES.items():
        path=raw/fn
        if not path.exists():raise FileNotFoundError(f'Missing {path}; download Olist or run scripts/quickstart.py --demo')
        data[key]=pd.read_csv(path,low_memory=False)
    tr=raw/'product_category_name_translation.csv'
    data['translation']=pd.read_csv(tr) if tr.exists() else pd.DataFrame(columns=['product_category_name','product_category_name_english'])
    return data

def build(raw:Path,output:Path)->dict:
    output.mkdir(parents=True,exist_ok=True)
    t=load(raw)
    orders=t['orders'].copy(); customers=t['customers'].copy(); items=t['items'].copy(); payments=t['payments'].copy(); reviews=t['reviews'].copy(); products=t['products'].copy()
    for col in ['order_purchase_timestamp','order_delivered_customer_date','order_estimated_delivery_date']:
        orders[col]=pd.to_datetime(orders[col],errors='coerce')
    orders=orders.drop_duplicates('order_id')
    customers=customers.drop_duplicates('customer_id')
    products=products.drop_duplicates('product_id')
    if len(t['translation']):
        products=products.merge(t['translation'][['product_category_name','product_category_name_english']].drop_duplicates('product_category_name'),on='product_category_name',how='left',validate='m:1')
    else:products['product_category_name_english']=products['product_category_name'].fillna('Unknown')
    products['category']=products['product_category_name_english'].fillna(products['product_category_name']).fillna('Unknown').str.replace('_',' ',regex=False).str.title()
    item_totals=items.groupby('order_id',as_index=False).agg(item_count=('order_item_id','size'),order_value_brl=('price','sum'),freight_brl=('freight_value','sum'))
    # Payments can have multiple rows per order. Aggregate before joining to order grain.
    payment_totals=payments.groupby('order_id',as_index=False).agg(payment_value_brl=('payment_value','sum'),payment_count=('payment_sequential','size'))
    method=(payments.sort_values('payment_sequential').drop_duplicates('order_id')[['order_id','payment_type','payment_installments']].rename(columns={'payment_type':'payment_method'}))
    review_totals=reviews.groupby('order_id',as_index=False).agg(review_score=('review_score','mean'),review_count=('review_id','size'))
    fact=orders.merge(customers[['customer_id','customer_unique_id','customer_state','customer_city']],on='customer_id',how='left',validate='m:1')
    for x in (item_totals,payment_totals,method,review_totals):fact=fact.merge(x,on='order_id',how='left',validate='1:1')
    for col in ['item_count','order_value_brl','freight_brl','payment_value_brl','payment_count','review_count']:
        fact[col]=fact[col].fillna(0)
    fact['is_delivered']=fact['order_status'].eq('delivered') & fact['order_delivered_customer_date'].notna()
    fact['is_late']=fact['is_delivered'] & (fact['order_delivered_customer_date']>fact['order_estimated_delivery_date'])
    fact['delivery_days']=(fact['order_delivered_customer_date']-fact['order_purchase_timestamp']).dt.total_seconds()/86400
    fact['promised_days']=(fact['order_estimated_delivery_date']-fact['order_purchase_timestamp']).dt.total_seconds()/86400
    fact['delay_days']=(fact['order_delivered_customer_date']-fact['order_estimated_delivery_date']).dt.total_seconds().div(86400).clip(lower=0)
    fact['gmv_brl']=np.where(fact['is_delivered'],fact['order_value_brl'],0.0)
    fact['order_total_brl']=fact['order_value_brl']+fact['freight_brl']
    fact['order_date']=fact['order_purchase_timestamp'].dt.strftime('%Y-%m-%d')
    fact['order_month']=fact['order_purchase_timestamp'].dt.strftime('%Y-%m')
    fact['year']=fact['order_purchase_timestamp'].dt.year
    fact['month']=fact['order_purchase_timestamp'].dt.month
    fact['day_of_week']=fact['order_purchase_timestamp'].dt.dayofweek
    fact=fact.rename(columns={'customer_state':'state','customer_city':'city','order_purchase_timestamp':'purchased_at','order_estimated_delivery_date':'estimated_delivery_at','order_delivered_customer_date':'delivered_at','order_status':'status'})
    for col in ['purchased_at','estimated_delivery_at','delivered_at']:
        fact[col]=fact[col].dt.strftime('%Y-%m-%d %H:%M:%S')
    fact['is_delivered']=fact['is_delivered'].astype(int);fact['is_late']=fact['is_late'].astype(int)
    item_fact=items.merge(products[['product_id','category']],on='product_id',how='left',validate='m:1')
    item_fact=item_fact.merge(fact[['order_id','purchased_at','order_date','order_month','state','is_delivered','customer_unique_id']],on='order_id',how='left',validate='m:1')
    item_fact['category']=item_fact['category'].fillna('Unknown')
    item_fact['gmv_brl']=np.where(item_fact['is_delivered'].eq(1),item_fact['price'],0.0)
    item_fact=item_fact.rename(columns={'freight_value':'item_freight_brl'})
    # Lifetime customer dimension; distinguishes persistent unique ID from one-order customer ID.
    c=fact.sort_values('purchased_at').groupby('customer_unique_id',dropna=True).agg(
        customer_state=('state','first'),customer_city=('city','first'),lifetime_orders=('order_id','size'),
        lifetime_delivered_orders=('is_delivered','sum'),lifetime_gmv_brl=('gmv_brl','sum'),
        first_order=('order_date','min'),last_order=('order_date','max')).reset_index()
    anchor=pd.to_datetime(fact['order_date']).max()+pd.Timedelta(days=1)
    c['recency_days']=(anchor-pd.to_datetime(c['last_order'])).dt.days
    # RFM based on historical data; quintile rankings (high scores = better business value).
    c['r_score']=pd.qcut(c['recency_days'].rank(method='first',ascending=False),5,labels=False).add(1).astype(int)
    c['f_score']=pd.qcut(c['lifetime_delivered_orders'].rank(method='first'),5,labels=False).add(1).astype(int)
    c['m_score']=pd.qcut(c['lifetime_gmv_brl'].rank(method='first'),5,labels=False).add(1).astype(int)
    c['rfm_score']=c['r_score']+c['f_score']+c['m_score']
    c['segment']=np.select([(c['lifetime_delivered_orders']>=2)&(c['rfm_score']>=12),(c['lifetime_delivered_orders']>=2),
        (c['recency_days']<=90)&(c['lifetime_delivered_orders']==1),(c['recency_days']>180)],
        ['Champions','Loyal','New / Recent','At Risk'],default='Occasional')
    dates=pd.date_range(pd.to_datetime(fact['order_date']).min(),pd.to_datetime(fact['order_date']).max(),freq='D')
    dim_date=pd.DataFrame({'date':dates.strftime('%Y-%m-%d'),'year':dates.year,'quarter':dates.quarter,'month':dates.month,'month_name':dates.strftime('%b'),'year_month':dates.strftime('%Y-%m'),'day_of_week':dates.dayofweek})
    outs={'fact_orders.csv':fact,'fact_items.csv':item_fact,'dim_customers.csv':c,'dim_products.csv':products[['product_id','category','product_category_name']],'dim_date.csv':dim_date}
    for name,df in outs.items():df.to_csv(output/name,index=False)
    quality={
        'dataset_kind':'SYNTHETIC DEMO' if (raw/'SYNTHETIC_DEMO_DATA.txt').exists() else 'OLIST ORIGINAL',
        'raw_rows':{k:len(v) for k,v in t.items()},'processed_rows':{k:len(v) for k,v in outs.items()},
        'unique_order_ids':int(fact['order_id'].nunique()),'duplicate_order_ids':int(fact['order_id'].duplicated().sum()),
        'orphan_item_orders':int((~items['order_id'].isin(orders['order_id'])).sum()),
        'missing_customer_share_pct':float(fact['customer_unique_id'].isna().mean()*100),
        'missing_review_share_pct':float(fact['review_score'].isna().mean()*100),
        'delivered_orders':int(fact['is_delivered'].sum()),
        'order_gmv_matches_item_gmv':bool(np.isclose(fact['gmv_brl'].sum(),item_fact['gmv_brl'].sum(),atol=.02))
    }
    (output/'quality_checks.json').write_text(json.dumps(quality,indent=2))
    if not quality['order_gmv_matches_item_gmv']:raise AssertionError('GMV order/item grain mismatch')
    return quality

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--raw',default='data/raw');p.add_argument('--output',default='data/processed');a=p.parse_args()
    print(json.dumps(build(Path(a.raw),Path(a.output)),indent=2))
