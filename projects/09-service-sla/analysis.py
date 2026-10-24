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

n=2200
queue=rng.choice(['Payments','Accounts','Technical'],n)
scale=np.select([queue=='Payments',queue=='Accounts'],[12,16],default=25)
opened=pd.Timestamp('2025-01-01')+pd.to_timedelta(rng.integers(0,8000,n),unit='h')
df=pd.DataFrame({'queue':queue,'opened':opened,'hours':rng.exponential(scale)})
df['resolved']=df.opened+pd.to_timedelta(df.hours,unit='h');df['breach']=df.hours>24
summary=df.groupby('queue').agg(tickets=('hours','size'),median_hours=('hours','median'),p90_hours=('hours',lambda s:s.quantile(.9)),breach_rate=('breach','mean'))
assert summary.tickets.sum()==n
metrics={'tickets':n,'overall_breach_rate':float(df.breach.mean()),'worst_queue':summary.breach_rate.idxmax()}
summary.breach_rate.plot.bar(ax=ax,title='24-hour resolution SLA breaches',ylabel='Breach share')
summary.to_csv(out/'queue_summary.csv')

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
