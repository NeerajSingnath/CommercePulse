"""CommercePulse | Streamlit multi-page executive analytics dashboard."""
from pathlib import Path
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import streamlit as st

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'data/processed'; REPORTS=ROOT/'reports'; MODELS=ROOT/'models'
st.set_page_config(page_title='CommercePulse | E-commerce analytics',page_icon='📊',layout='wide',initial_sidebar_state='expanded')
st.markdown('''<style>
.block-container{padding-top:1.4rem;padding-bottom:3rem}.kpi-label{color:#a5b4d4;font-size:13px;font-weight:650}
.kpi-number{color:#f2f7ff;font-size:28px;font-weight:800;margin-top:3px}.kpi-note{color:#64748b;font-size:12px}
.kpi{border:1px solid #283858;border-radius:14px;padding:17px 18px;background:#111c30}
.header-sub{color:#9aaccc;margin-bottom:18px}.stTabs [data-baseweb="tab"]{font-weight:600}
</style>''',unsafe_allow_html=True)

@st.cache_data(show_spinner=False)
def get_data():
    if not (DATA/'fact_orders.csv').exists():return None
    return (pd.read_csv(DATA/'fact_orders.csv',parse_dates=['purchased_at']),
            pd.read_csv(DATA/'fact_items.csv'),pd.read_csv(DATA/'dim_customers.csv'),
            json.loads((DATA/'quality_checks.json').read_text()))

loaded=get_data()
if loaded is None:
    st.error('Run `python scripts/quickstart.py --demo` or import Olist and run `python scripts/quickstart.py` first.');st.stop()
orders,items,customers,quality=loaded
st.title('◈ CommercePulse')
st.markdown('<div class="header-sub">E-commerce intelligence • Revenue · Customers · Logistics · Predictive risk</div>',unsafe_allow_html=True)
if quality['dataset_kind']=='SYNTHETIC DEMO':
    st.warning('SYNTHETIC DEMO DATA — For pipeline testing and preview only. Replace with the original Olist dataset before presenting findings as real business insights.',icon='⚠️')

with st.sidebar:
    st.markdown('## ◈ Filters')
    selected_states=st.multiselect('Customer state',sorted(orders['state'].dropna().unique().tolist()),default=[])
    months=sorted(orders['order_month'].dropna().unique().tolist())
    start_month,end_month=st.select_slider('Order month range',options=months,value=(months[0],months[-1]))
    delivered_only=st.checkbox('Delivered orders only',value=True)
    st.divider()
    st.caption(f"Data origin: {quality['dataset_kind']}")
    st.caption('BRL amounts; merchandise GMV excludes freight and undelivered orders.')
    st.caption('Full RFM segments are historical lifetime cohorts, not recomputed within date filters.')

mask=orders['order_month'].between(start_month,end_month)
if selected_states:mask&=orders['state'].isin(selected_states)
if delivered_only:mask&=orders['is_delivered'].eq(1)
o=orders.loc[mask].copy()
i=items[items['order_id'].isin(o['order_id'])].copy()
if o.empty:st.warning('No orders match the selected filters.');st.stop()

def money(x):return f'R$ {x:,.0f}'
def line_fig(df,x,y,title,color='#13b5a6'):
    fig=px.line(df,x=x,y=y,markers=True,title=title)
    fig.update_traces(line_color=color,line_width=3)
    fig.update_layout(template='plotly_dark',height=350,margin=dict(l=10,r=15,t=50,b=10),paper_bgcolor='#0b1120',plot_bgcolor='#131f33')
    return fig

def bar_fig(df,x,y,title,orientation='v',color='#4f8cff'):
    fig=px.bar(df,x=x,y=y,orientation='h' if orientation=='h' else 'v',title=title)
    fig.update_traces(marker_color=color)
    fig.update_layout(template='plotly_dark',height=360,margin=dict(l=10,r=15,t=50,b=10),paper_bgcolor='#0b1120',plot_bgcolor='#131f33')
    return fig

def kpi(lbl,val,note=''):
    st.markdown(f'<div class="kpi"><div class="kpi-label">{lbl}</div><div class="kpi-number">{val}</div><div class="kpi-note">{note}</div></div>',unsafe_allow_html=True)

# KPIs ALWAYS use delivered subset even when filter shows non-delivered statuses.
d=o[o['is_delivered']==1]
gmv=d['gmv_brl'].sum(); n_orders=len(d); late=d['is_late'].mean() if n_orders else 0
k1,k2,k3,k4=st.columns(4)
with k1:kpi('MERCHANDISE GMV',money(gmv),'Delivered items · excludes freight')
with k2:kpi('DELIVERED ORDERS',f'{n_orders:,}','Unique order IDs')
with k3:kpi('AVERAGE ORDER VALUE',money(gmv/n_orders if n_orders else 0),'Merchandise only')
with k4:kpi('ON-TIME DELIVERY',f'{(1-late)*100:.1f}%','Delivered orders only')
st.write('')

t1,t2,t3,t4,t5=st.tabs(['📈 Executive overview','🛍️ Revenue & products','👥 Customer intelligence','🚚 Delivery & reviews','🤖 Risk prediction'])
with t1:
    monthly=d.groupby('order_month',as_index=False).agg(gmv_brl=('gmv_brl','sum'),orders=('order_id','nunique'))
    state=d.groupby('state',as_index=False).agg(gmv_brl=('gmv_brl','sum'),late_rate=('is_late','mean')).sort_values('gmv_brl',ascending=False)
    a,b=st.columns(2)
    with a:st.plotly_chart(line_fig(monthly,'order_month','gmv_brl','Monthly merchandise GMV'),use_container_width=True)
    with b:st.plotly_chart(bar_fig(state.head(12),'state','gmv_brl','GMV by state'),use_container_width=True)
    c,d2=st.columns(2)
    with c:
        statuses=o.groupby('status',as_index=False).size()
        pie=px.pie(statuses,names='status',values='size',hole=.65,title='Order status distribution',color_discrete_sequence=px.colors.qualitative.Set2)
        pie.update_layout(template='plotly_dark',paper_bgcolor='#0b1120',height=350);st.plotly_chart(pie,use_container_width=True)
    with d2:
        payment=d.groupby('payment_method',dropna=False,as_index=False)['order_id'].nunique().sort_values('order_id',ascending=False)
        st.plotly_chart(bar_fig(payment,'payment_method','order_id','Payment method by orders',color='#a78bfa'),use_container_width=True)

with t2:
    cat=i.groupby('category',as_index=False).agg(gmv_brl=('gmv_brl','sum'),items=('order_item_id','count')).sort_values('gmv_brl',ascending=False)
    a,b=st.columns(2)
    with a:st.plotly_chart(bar_fig(cat.head(12).iloc[::-1],'gmv_brl','category','Top categories by GMV','h'),use_container_width=True)
    with b:
        state_rev=i.groupby('state',as_index=False)['gmv_brl'].sum().sort_values('gmv_brl',ascending=False)
        st.plotly_chart(bar_fig(state_rev,'state','gmv_brl','Product GMV by customer state',color='#22c4a8'),use_container_width=True)
    st.markdown('### Category performance')
    st.dataframe(cat.rename(columns={'category':'Category','gmv_brl':'GMV (BRL)','items':'Line items'}),use_container_width=True,hide_index=True)
    st.download_button('Download filtered item-level data',i.to_csv(index=False).encode(),'commercepulse_items.csv','text/csv')

with t3:
    # Overall customer segments shown for customers present in current order selection.
    cust=customers[customers['customer_unique_id'].isin(o['customer_unique_id'])].copy()
    st.info('RFM is measured over the complete historical dataset; date/state filters select which customers to display, but do not recalculate lifetime RFM.')
    a,b=st.columns(2)
    with a:
        seg=cust.groupby('segment',as_index=False).agg(customers=('customer_unique_id','count'),total_gmv=('lifetime_gmv_brl','sum')).sort_values('customers',ascending=False)
        st.plotly_chart(bar_fig(seg,'segment','customers','Customer segments',color='#7c5cff'),use_container_width=True)
    with b:
        ret=cust['lifetime_delivered_orders'].clip(upper=6).value_counts().sort_index().reset_index()
        ret.columns=['Historical delivered orders','Customers']
        st.plotly_chart(bar_fig(ret,'Historical delivered orders','Customers','Order frequency (6 = 6+)',color='#13b5a6'),use_container_width=True)
    st.markdown('### RFM customer segments')
    st.dataframe(cust[['customer_unique_id','segment','recency_days','lifetime_delivered_orders','lifetime_gmv_brl','rfm_score']].sort_values('lifetime_gmv_brl',ascending=False).head(500),use_container_width=True,hide_index=True)

with t4:
    delivered=o[o['is_delivered']==1]
    if len(delivered):
        state_q=delivered.groupby('state',as_index=False).agg(orders=('order_id','size'),late_rate=('is_late','mean'),avg_review=('review_score','mean')).sort_values('late_rate',ascending=False)
        a,b=st.columns(2)
        with a:
            st.plotly_chart(bar_fig(state_q,'state','late_rate','Late-delivery fraction by state',color='#fb7185'),use_container_width=True)
        with b:
            review=delivered.dropna(subset=['review_score']).groupby('is_late',as_index=False)['review_score'].mean()
            review['delivery'] = review['is_late'].map({0:'On time',1:'Late'})
            st.plotly_chart(bar_fig(review,'delivery','review_score','Mean review: on time vs late',color='#f59e0b'),use_container_width=True)
        st.markdown('### State-level delivery reliability')
        state_q['late_rate']=state_q['late_rate'].round(3)
        st.dataframe(state_q,use_container_width=True,hide_index=True)
        st.caption('Differences in reviews are observational; they do not demonstrate causation.')

with t5:
    metrics_path=MODELS/'metrics.json'; preds_path=MODELS/'out_of_time_predictions.csv'
    if metrics_path.exists() and preds_path.exists():
        m=json.loads(metrics_path.read_text());preds=pd.read_csv(preds_path)
        preds=preds[preds['order_id'].isin(o['order_id'])]
        a,b,c=st.columns(3)
        with a:st.metric('Out-of-time ROC-AUC',f"{m['roc_auc']:.3f}")
        with b:st.metric('Average precision',f"{m['average_precision']:.3f}")
        with c:st.metric('Temporal test orders',f"{m['test_examples']:,}")
        st.caption('Retrospective performance on later historical delivered orders. Predictions are NOT available for every order, and this is NOT a live deployed model.')
        if len(preds):
            r=preds.groupby('risk_tier',as_index=False).agg(orders=('order_id','size'),observed_late_rate=('is_late','mean'))
            st.plotly_chart(bar_fig(r,'risk_tier','observed_late_rate','Observed late share by predicted risk tier',color='#fb7185'),use_container_width=True)
            st.dataframe(preds.sort_values('late_probability',ascending=False).head(300),use_container_width=True,hide_index=True)
        st.markdown('**Method:** Logistic regression with class weighting, one-hot state/payment encoding, and chronological 80/20 split. No review, delivered date or realized delivery duration is used as a feature.')
        st.download_button('Download evaluation predictions',preds.to_csv(index=False).encode(),'delivery_risk_predictions.csv','text/csv')
    else:st.info('Run quickstart to train and evaluate the model.')

st.divider()
st.caption('CommercePulse | Analytical prototype • For interview demonstration • No profit, returns, ad-spend or causal metrics inferred.')
