"""Static layout concept for Power BI page 1 (NOT a screenshot of a .pbix)."""
from pathlib import Path
import json
import pandas as pd
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch

ROOT=Path(__file__).resolve().parents[1]
o=pd.read_csv(ROOT/'data/processed/fact_orders.csv');i=pd.read_csv(ROOT/'data/processed/fact_items.csv')
m=json.loads((ROOT/'reports/metrics.json').read_text());d=o[o['is_delivered']==1]
BG='#0B1120';BOX='#15213A';TXT='#EFF6FF';MUT='#98ACCA';TEAL='#13B5A6';BLUE='#4F8CFF';PURPLE='#7C5CFF';PINK='#FB7185'
plt.rcParams.update({'font.family':'DejaVu Sans','text.color':TXT,'axes.labelcolor':MUT,'xtick.color':MUT,'ytick.color':MUT,'font.size':10})
fig=plt.figure(figsize=(18,10),facecolor=BG)
fig.text(.042,.949,'◈  COMMERCEPULSE',fontsize=25,fontweight='bold',color=TXT)
fig.text(.045,.911,'EXECUTIVE OVERVIEW   /   E-COMMERCE INTELLIGENCE',fontsize=11,color=MUT)
fig.text(.954,.949,'POWER BI LAYOUT CONCEPT',fontsize=10,color=TEAL,ha='right',fontweight='bold')
fig.text(.954,.917,'SYNTHETIC DEMO — NOT ORIGINAL OLIST',fontsize=9,color=PINK,ha='right')

cards=[('MERCHANDISE GMV',f"R$ {m['gross_merchandise_value_brl']/1000:,.1f}K",'Delivered orders only'),
       ('DELIVERED ORDERS',f"{m['delivered_orders']:,}",'Historical transactions'),
       ('AVERAGE ORDER VALUE',f"R$ {m['aov_ex_shipping_brl']:,.0f}",'Excludes freight'),
       ('ON-TIME DELIVERY',f"{100-m['late_delivery_rate_pct']:.1f}%",'Delivery reliability'),
       ('AVERAGE REVIEW',f"{m['average_review_score']:.2f} / 5",'Completed order ratings')]
for n,(label,val,note) in enumerate(cards):
    x=.044+n*.184; y=.756; w=.173;h=.128
    fig.add_artist(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.008,rounding_size=.012',transform=fig.transFigure,facecolor=BOX,edgecolor='#263750',linewidth=1))
    fig.text(x+.012,y+h-.033,label,fontsize=9,color=MUT,weight='bold')
    fig.text(x+.012,y+h-.083,val,fontsize=22,color=TXT,weight='bold')
    fig.text(x+.012,y+.014,note,fontsize=8,color='#8295B6')

def axes(rect,title):
    ax=fig.add_axes(rect,facecolor=BOX);ax.set_title(title,color=TXT,loc='left',fontweight='bold',pad=17,fontsize=13)
    for s in ax.spines.values():s.set_visible(False)
    ax.grid(axis='y',alpha=.11,color='white',zorder=0);ax.tick_params(length=0,labelsize=9,pad=7)
    return ax

monthly=d.groupby('order_month')['gmv_brl'].sum();ax=axes([.055,.402,.412,.293],'Delivered GMV trend   ·   BRL')
x=np.arange(len(monthly));ax.plot(x,monthly.values,color=TEAL,linewidth=2.6,marker='o',markersize=3)
ax.fill_between(x,monthly.values,alpha=.12,color=TEAL)
ax.set_xticks(x[::max(1,len(x)//8)],monthly.index[::max(1,len(x)//8)],rotation=0)
ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,pos:f'{v/1000:.0f}k'))
ax.set_xlim(-.5,len(x)-.5)
category=i.groupby('category')['gmv_brl'].sum().sort_values().tail(7);ax=axes([.535,.402,.421,.293],'Top categories   ·   merchandise GMV')
labels=[x[:20]+'…' if len(x)>20 else x for x in category.index];ys=np.arange(len(category))
ax.barh(ys,category.values,color=BLUE,height=.55);ax.set_yticks(ys,labels);ax.grid(axis='x',alpha=.1,color='white');ax.grid(axis='y',visible=False)
ax.xaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,pos:f'{v/1000:.0f}k'))

states=d.groupby('state')['gmv_brl'].sum().sort_values(ascending=False).head(9);ax=axes([.055,.079,.412,.259],'Geography   ·   leading states')
ax.bar(states.index,states.values,color=PURPLE,width=.68);ax.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v,pos:f'{v/1000:.0f}k'))
review=d.groupby('is_late')['review_score'].mean();ax=axes([.535,.079,.421,.259],'Customer satisfaction   ·   delivery timing')
ax.bar(['On time','Late'],[review.get(0,0),review.get(1,0)],color=[TEAL,PINK],width=.37)
for j,k in enumerate([0,1]):ax.text(j,review.get(k,0)+.1,f'{review.get(k,0):.2f}',color=TXT,ha='center',fontsize=16,weight='bold')
ax.set_ylim(0,5.2);ax.set_ylabel('Avg. review score (1–5)')
fig.text(.055,.022,'Layout preview only • Build actual cross-filtering pages in Power BI Desktop • GMV ≠ revenue or profit',color=MUT,fontsize=9)
name=ROOT/'powerbi/dashboard_layout_concept.png';fig.savefig(name,dpi=150,facecolor=BG,bbox_inches='tight');print(name)
