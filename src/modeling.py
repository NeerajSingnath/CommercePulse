"""Out-of-time risk model: predict late delivery from checkout-time information only."""
from __future__ import annotations
import json
from pathlib import Path
import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder,StandardScaler
from sklearn.pipeline import Pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score,average_precision_score,precision_score,recall_score,f1_score,confusion_matrix

NUMERIC=['order_value_brl','freight_brl','item_count','promised_days','month','day_of_week']
CATEGORICAL=['state','payment_method']

def train(processed:Path,models:Path,seed:int=42)->dict:
    models.mkdir(parents=True,exist_ok=True)
    df=pd.read_csv(processed/'fact_orders.csv',parse_dates=['purchased_at'])
    df=df[(df['is_delivered']==1)&df['promised_days'].notna() & (df['promised_days']>=0)].sort_values('purchased_at').copy()
    for x in NUMERIC:df[x]=pd.to_numeric(df[x],errors='coerce').fillna(0)
    for x in CATEGORICAL:df[x]=df[x].fillna('Unknown').astype(str)
    split=max(1,min(len(df)-1,int(len(df)*.8)))
    a,b=df.iloc[:split],df.iloc[split:]
    if a['is_late'].nunique()<2 or b['is_late'].nunique()<2:raise ValueError('Both classes required in temporal train/test splits; use more representative data')
    prep=ColumnTransformer([('numeric',StandardScaler(),NUMERIC),('categories',OneHotEncoder(handle_unknown='ignore'),CATEGORICAL)])
    model=Pipeline([('features',prep),('classifier',LogisticRegression(class_weight='balanced',max_iter=1000,random_state=seed))])
    model.fit(a[NUMERIC+CATEGORICAL],a['is_late'])
    prob=model.predict_proba(b[NUMERIC+CATEGORICAL])[:,1]
    pred=(prob>=.5).astype(int)
    metrics={'training_examples':len(a),'test_examples':len(b),'train_late_rate':float(a['is_late'].mean()),'test_late_rate':float(b['is_late'].mean()),
        'roc_auc':float(roc_auc_score(b['is_late'],prob)),'average_precision':float(average_precision_score(b['is_late'],prob)),
        'precision_at_05':float(precision_score(b['is_late'],pred,zero_division=0)), 'recall_at_05':float(recall_score(b['is_late'],pred,zero_division=0)),
        'f1_at_05':float(f1_score(b['is_late'],pred,zero_division=0)), 'confusion_matrix':confusion_matrix(b['is_late'],pred).tolist(),
        'temporal_test_start':str(b['purchased_at'].min()),'temporal_test_end':str(b['purchased_at'].max()),
        'target':'Late delivery among orders known to be delivered (historical retrospective evaluation)',
        'excluded_leakage_features':['delivery_days','delay_days','delivered_at','review_score','is_late'],
        'caveat':'Historical test only; not a live forecasting or causality claim.'}
    joblib.dump(model,models/'late_delivery_model.joblib')
    (models/'metrics.json').write_text(json.dumps(metrics,indent=2))
    predictions=b[['order_id','is_late','purchased_at','state']].copy()
    predictions['late_probability']=np.round(prob,5)
    predictions['risk_tier']=pd.cut(prob,[-.01,.3,.6,1.001],labels=['Low','Medium','High'])
    predictions.to_csv(models/'out_of_time_predictions.csv',index=False)
    return metrics

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--processed',default='data/processed');p.add_argument('--models',default='models');a=p.parse_args()
    print(json.dumps(train(Path(a.processed),Path(a.models)),indent=2))
