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

observation=11; records=[]; n=1600
signup=rng.integers(0,12,n)
for customer,cohort in enumerate(signup):
 for age in range(observation-cohort+1):
  if age==0 or rng.random()<np.exp(-age/5): records.append((customer,int(cohort),age))
a=pd.DataFrame(records,columns=['customer','cohort','age'])
sizes=pd.Series(signup).value_counts().sort_index()
counts=a.groupby(['cohort','age']).customer.nunique().unstack().reindex(index=range(12),columns=range(12)).fillna(0)
retention=counts.div(sizes,axis=0)
for cohort in range(12): retention.loc[cohort,observation-cohort+1:]=np.nan
assert np.allclose(retention[0],1)
assert retention.max().max()<=1
metrics={'customers':n,'cohorts':12,'month_1_retention_observed_cohorts':float(retention[1].dropna().mean())}
im=ax.imshow(retention,aspect='auto',vmin=0,vmax=1,cmap='Blues');fig.colorbar(im,ax=ax,label='Active share');ax.set(xlabel='Months since signup',ylabel='Signup cohort index',title='Cohort retention (future months masked)')
retention.to_csv(out/'retention.csv')

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
