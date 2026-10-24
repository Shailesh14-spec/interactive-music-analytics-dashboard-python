"""Reproducible educational portfolio analysis. See README for provenance and limitations."""
from pathlib import Path
import json
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from scipy import stats
from sklearn.model_selection import train_test_split
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import LogisticRegression, Ridge
from sklearn.dummy import DummyClassifier
from sklearn.metrics import (roc_auc_score, average_precision_score, roc_curve,
 precision_recall_curve, precision_score, recall_score, mean_absolute_error, f1_score)
rng = np.random.default_rng(42)
out = Path(__file__).resolve().parent / 'outputs'
out.mkdir(exist_ok=True)
fig, ax = plt.subplots(figsize=(8, 5))

n=6000
df=pd.DataFrame({'customer_id':rng.integers(1,601,n),'date':pd.Timestamp('2025-01-01')+pd.to_timedelta(rng.integers(0,365,n),unit='D'),'revenue':rng.gamma(3,20,n)})
reference=pd.Timestamp('2026-01-01')
rfm=df.groupby('customer_id').agg(last_order=('date','max'),frequency=('date','size'),monetary=('revenue','sum'))
rfm['recency']=(reference-rfm.last_order).dt.days
rfm['r_score']=np.ceil((1-rfm.recency.rank(pct=True))*4).clip(1,4).astype(int)
rfm['f_score']=np.ceil(rfm.frequency.rank(pct=True)*4).clip(1,4).astype(int)
rfm['m_score']=np.ceil(rfm.monetary.rank(pct=True)*4).clip(1,4).astype(int)
rfm['segment']=np.select([(rfm.r_score>=3)&(rfm.f_score>=3)&(rfm.m_score>=3),rfm.r_score==1],['High engagement','Lapsed'],default='Developing')
counts=rfm.segment.value_counts(); counts.plot.bar(ax=ax,title='RFM customer segments',ylabel='Customers')
metrics={'customers':len(rfm),'transactions':n,'total_revenue':float(df.revenue.sum()),'segments':counts.to_dict()}
assert rfm.frequency.sum()==n
rfm.to_csv(out/'customer_segments.csv')

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
