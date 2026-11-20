"""Synthetic Olist-shaped data for a runnable demo. Never represent as real Olist data."""
from __future__ import annotations
import argparse
from pathlib import Path
import numpy as np
import pandas as pd

STATES = ['SP','RJ','MG','RS','PR','SC','BA','DF','PE','CE','GO','ES']
CITIES = {'SP':'sao paulo','RJ':'rio de janeiro','MG':'belo horizonte','RS':'porto alegre','PR':'curitiba','SC':'florianopolis','BA':'salvador','DF':'brasilia','PE':'recife','CE':'fortaleza','GO':'goiania','ES':'vitoria'}
CATEGORIES = ['health_beauty','computers_accessories','bed_bath_table','sports_leisure','furniture_decor','housewares','watches_gifts','telephony','toys','auto','books_general_interest','fashion_bags_accessories']

def generate(folder: Path, n_orders: int=6200, seed: int=42):
    folder.mkdir(parents=True,exist_ok=True)
    rng=np.random.default_rng(seed)
    n_customers=max(500,int(n_orders*.72))
    customer_uids=np.array([f'unique_{i:06d}' for i in range(n_customers)])
    # Returning-customer draw: 20% of shoppers account for more orders.
    weights=np.ones(n_customers); weights[:int(n_customers*.22)]=4.0; weights=weights/weights.sum()
    unique_ids=rng.choice(customer_uids,size=n_orders,replace=True,p=weights)
    state_probs=np.array([.39,.13,.12,.07,.065,.055,.055,.035,.025,.025,.035,.03]); state_probs/=state_probs.sum()
    state_by_uid={uid:rng.choice(STATES,p=state_probs) for uid in customer_uids}
    state_by_order=[state_by_uid[x] for x in unique_ids]
    all_days=pd.date_range('2017-01-01','2018-08-25',freq='D')
    day_weights=np.linspace(.5,1.4,len(all_days));day_weights*=np.where(all_days.month.isin([11,12]),1.45,1.0);day_weights/=day_weights.sum()
    purchase_days=rng.choice(all_days,size=n_orders,p=day_weights)
    purchase_time=pd.to_datetime(purchase_days)+pd.to_timedelta(rng.integers(7,23,n_orders),unit='h')+pd.to_timedelta(rng.integers(0,60,n_orders),unit='m')
    order_ids=[f'order_{i:07d}' for i in range(n_orders)]
    customer_ids=[f'customer_{i:07d}' for i in range(n_orders)]
    statuses=rng.choice(['delivered','canceled','shipped','unavailable','processing'],n_orders,p=[.945,.023,.017,.005,.01])
    expected_days=rng.integers(7,27,n_orders)+np.where(np.array(state_by_order)=='SP',-2,2)
    expected_days=np.maximum(expected_days,4)
    delay_bias=np.where(np.array(state_by_order)=='SP',-.9,2.5)
    actual_days=np.maximum(1,(expected_days+rng.normal(-3.5+delay_bias,6,n_orders)).round().astype(int))
    delivered_dates=purchase_time+pd.to_timedelta(actual_days,unit='D')
    est_dates=purchase_time+pd.to_timedelta(expected_days,unit='D')
    delivered_dates=pd.Series(delivered_dates).where(statuses=='delivered',pd.NaT)
    orders=pd.DataFrame({'order_id':order_ids,'customer_id':customer_ids,'order_status':statuses,
        'order_purchase_timestamp':purchase_time,
        'order_approved_at':purchase_time+pd.to_timedelta(1,unit='h'),
        'order_delivered_carrier_date':purchase_time+pd.to_timedelta(2,unit='D'),
        'order_delivered_customer_date':delivered_dates,
        'order_estimated_delivery_date':est_dates})
    customers=pd.DataFrame({'customer_id':customer_ids,'customer_unique_id':unique_ids,
        'customer_zip_code_prefix':rng.integers(10000,99999,n_orders),
        'customer_city':[CITIES[s] for s in state_by_order],'customer_state':state_by_order})
    n_products=280
    products=pd.DataFrame({'product_id':[f'product_{i:05d}' for i in range(n_products)],
        'product_category_name':rng.choice(CATEGORIES,size=n_products),
        'product_name_lenght':rng.integers(12,65,n_products),
        'product_description_lenght':rng.integers(100,1600,n_products),
        'product_photos_qty':rng.integers(1,7,n_products),
        'product_weight_g':rng.integers(100,4500,n_products),
        'product_length_cm':rng.integers(10,70,n_products),
        'product_height_cm':rng.integers(3,45,n_products),
        'product_width_cm':rng.integers(7,60,n_products)})
    items=[]; payments=[]; reviews=[]
    prices=np.round(rng.lognormal(4.5,.65,n_products),2)
    item_counts=rng.choice([1,2,3,4],n_orders,p=[.72,.19,.07,.02])
    payment_methods=['credit_card','boleto','voucher','debit_card']
    for i,oid in enumerate(order_ids):
        total=0.
        for j in range(item_counts[i]):
            pi=int(rng.integers(0,n_products)); price=float(max(8,prices[pi]*rng.uniform(.83,1.2))); freight=float(rng.uniform(7,36)); total+=price+freight
            items.append((oid,j+1,f'product_{pi:05d}',f'seller_{rng.integers(0,110):04d}',purchase_time[i]+pd.Timedelta(days=3),round(price,2),round(freight,2)))
        method=rng.choice(payment_methods,p=[.74,.18,.05,.03]); payments.append((oid,1,method,int(rng.integers(1,7)) if method=='credit_card' else 1,round(total,2)))
        if statuses[i]=='delivered':
            late=actual_days[i]>expected_days[i]
            review=int(rng.choice([1,2,3,4,5],p=[.18,.17,.24,.26,.15] if late else [.035,.045,.09,.27,.56]))
            reviews.append((f'review_{i:07d}',oid,review,'','',delivered_dates.iloc[i]+pd.Timedelta(days=2),delivered_dates.iloc[i]+pd.Timedelta(days=3)))
    item_df=pd.DataFrame(items,columns=['order_id','order_item_id','product_id','seller_id','shipping_limit_date','price','freight_value'])
    payments_df=pd.DataFrame(payments,columns=['order_id','payment_sequential','payment_type','payment_installments','payment_value'])
    reviews_df=pd.DataFrame(reviews,columns=['review_id','order_id','review_score','review_comment_title','review_comment_message','review_creation_date','review_answer_timestamp'])
    translations=pd.DataFrame({'product_category_name':CATEGORIES,'product_category_name_english':[x.replace('_',' ').title() for x in CATEGORIES]})
    sheets={'olist_orders_dataset.csv':orders,'olist_customers_dataset.csv':customers,'olist_order_items_dataset.csv':item_df,
        'olist_order_payments_dataset.csv':payments_df,'olist_order_reviews_dataset.csv':reviews_df,
        'olist_products_dataset.csv':products,'product_category_name_translation.csv':translations}
    for fn,df in sheets.items():df.to_csv(folder/fn,index=False)
    (folder/'SYNTHETIC_DEMO_DATA.txt').write_text('SYNTHETIC DEMO DATA ONLY. Generated by CommercePulse; not the actual Olist dataset.\n')
    return {x:len(y) for x,y in sheets.items()}

if __name__=='__main__':
    p=argparse.ArgumentParser(); p.add_argument('--folder',default='data/raw');p.add_argument('--n-orders',type=int,default=6200);p.add_argument('--seed',type=int,default=42)
    a=p.parse_args(); print(generate(Path(a.folder),a.n_orders,a.seed))
