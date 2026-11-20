"""Automated executive metrics + interactive standalone Plotly HTML overview."""
from __future__ import annotations
import json
from pathlib import Path
import numpy as np
import pandas as pd
import plotly.graph_objects as go
from plotly.subplots import make_subplots

def build(processed:Path,reports:Path)->dict:
    reports.mkdir(parents=True,exist_ok=True)
    o=pd.read_csv(processed/'fact_orders.csv'); i=pd.read_csv(processed/'fact_items.csv'); c=pd.read_csv(processed/'dim_customers.csv')
    d=o[o['is_delivered']==1]; total=float(d['gmv_brl'].sum());n=len(d)
    monthly=d.groupby('order_month',as_index=False).agg(gmv=('gmv_brl','sum'),orders=('order_id','nunique'))
    category=i.groupby('category',as_index=False)['gmv_brl'].sum().sort_values('gmv_brl',ascending=False).head(10)
    state=d.groupby('state',as_index=False)['gmv_brl'].sum().sort_values('gmv_brl',ascending=False).head(12)
    score=o[o['review_score'].notna()].groupby('is_late',as_index=False)['review_score'].mean()
    late_rate=float(d['is_late'].mean()) if n else 0
    avg_on_time=float(d.loc[d['is_late']==0,'review_score'].mean());avg_late=float(d.loc[d['is_late']==1,'review_score'].mean())
    metrics={'dataset_kind':json.loads((processed/'quality_checks.json').read_text())['dataset_kind'],
        'delivered_orders':n,'gross_merchandise_value_brl':round(total,2),'aov_ex_shipping_brl':round(total/max(1,n),2),
        'unique_customers':int(c['customer_unique_id'].nunique()),'late_delivery_rate_pct':round(100*late_rate,2),
        'average_review_score':round(float(d['review_score'].mean()),2),
        'repeat_buyer_share_pct':round(float((c['lifetime_delivered_orders']>=2).mean()*100),2),
        'review_on_time':round(avg_on_time,2),'review_late':round(avg_late,2),
        'top_category':category.iloc[0]['category'] if len(category) else None,
        'top_state':state.iloc[0]['state'] if len(state) else None}
    (reports/'metrics.json').write_text(json.dumps(metrics,indent=2))
    fig=make_subplots(rows=2,cols=2,subplot_titles=('Delivered GMV trend (BRL)','Top product categories by GMV','GMV by customer state','Review score: on-time vs late'),
        specs=[[{'type':'xy'},{'type':'xy'}],[{'type':'xy'},{'type':'xy'}]],horizontal_spacing=.17,vertical_spacing=.17)
    fig.add_trace(go.Scatter(x=monthly['order_month'],y=monthly['gmv'],mode='lines+markers',line=dict(color='#13b5a6',width=3),fill='tozeroy',name='Delivered GMV'),1,1)
    fig.add_trace(go.Bar(x=category['gmv_brl'].iloc[::-1],y=category['category'].iloc[::-1],orientation='h',marker_color='#4f8cff',name='Categories'),1,2)
    fig.add_trace(go.Bar(x=state['state'],y=state['gmv_brl'],marker_color='#7c5cff',name='States'),2,1)
    fig.add_trace(go.Bar(x=['On time' if k==0 else 'Late' for k in score['is_late']],y=score['review_score'],marker_color=['#13b5a6','#fb7185'],name='Average review'),2,2)
    fig.update_layout(title=dict(text='COMMERCEPULSE | Executive BI overview'+(' — SYNTHETIC DEMO' if metrics['dataset_kind']=='SYNTHETIC DEMO' else ''),font=dict(size=22)),
        template='plotly_dark',height=900,showlegend=False,paper_bgcolor='#0b1120',plot_bgcolor='#111b2f',margin=dict(l=110,r=80,t=115,b=90))
    fig.add_annotation(text=f"Delivered GMV: R$ {total:,.0f}   •   Delivered orders: {n:,}   •   Late: {late_rate:.1%}   •   Avg review: {metrics['average_review_score']:.2f}/5",xref='paper',yref='paper',x=.5,y=1.055,showarrow=False,font=dict(size=13,color='#d8e1f0'))
    fig.write_html(reports/'interactive_dashboard.html',include_plotlyjs=True,full_html=True)
    # A short defendable management note; observational associations, not causal claims.
    note=f'''# CommercePulse — Executive Summary\n\n**Data:** {metrics['dataset_kind']}. These numbers are from this project's current processed data. **Historical order coverage only**; no causal claims.\n\n## Key business indicators\n\n- Delivered merchandise GMV (excluding freight): **R$ {total:,.2f}**\n- Delivered orders: **{n:,}**; AOV: **R$ {metrics['aov_ex_shipping_brl']:,.2f}**\n- Observed late delivery rate: **{metrics['late_delivery_rate_pct']}%** of delivered orders\n- Average customer review: **{metrics['average_review_score']}/5**\n- Repeat buyer share (2+ delivered orders; full dataset): **{metrics['repeat_buyer_share_pct']}%**\n- Highest-GMV category: **{metrics['top_category']}**; leading state: **{metrics['top_state']}**\n\n## Hypotheses to validate\n\n1. Target higher-delay states with seller SLA monitoring and carrier diagnostics. Late orders have an observed review average of {avg_late:.2f}, versus {avg_on_time:.2f} for on-time deliveries. This is association, **not proof** that lateness causes lower reviews.\n2. Improve repeat purchases with targeted campaigns for customers with a single purchase, then test incremental lift against a holdout group.\n3. Track category GMV and freight costs separately; do not confuse payment totals with merchandise GMV, and do not call GMV net revenue or profit.\n\n## Data and modeling caveats\n\n- This dataset has no purchase cost, return/refund truth, marketing spend, or reliable profits.\n- Customer inactivity is not proof of churn; RFM is descriptive.\n- Delivery risk ML is retrospective, uses checkout-time features, and is evaluated on a later chronological holdout.\n- If demo data were used, **replace with original Olist data before describing results as real-world findings**.\n'''
    (reports/'executive_summary.md').write_text(note)
    return metrics

if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('--processed',default='data/processed');p.add_argument('--reports',default='reports');a=p.parse_args()
    print(json.dumps(build(Path(a.processed),Path(a.reports)),indent=2))
