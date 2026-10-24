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

n=10000
y=rng.binomial(1,.025,n)
df=pd.DataFrame({'amount':rng.lognormal(3+.7*y,1,n),'velocity':rng.poisson(2+3*y,n),'distance':rng.exponential(10+30*y,n)})
xdev,xte,ydev,yte=train_test_split(df,y,test_size=.2,stratify=y,random_state=42)
xtr,xv,ytr,yv=train_test_split(xdev,ydev,test_size=.25,stratify=ydev,random_state=42)
model=make_pipeline(StandardScaler(),LogisticRegression(random_state=42)).fit(xtr,ytr)
threshold=float(np.quantile(model.predict_proba(xv)[:,1],.95))
p=model.predict_proba(xte)[:,1]; flagged=p>=threshold
metrics={'test_average_precision':average_precision_score(yte,p),'prevalence_baseline':float(yte.mean()),'validation_threshold':threshold,'test_review_rate':float(flagged.mean()),'precision':precision_score(yte,flagged,zero_division=0),'recall':recall_score(yte,flagged,zero_division=0)}
precision,recall,_=precision_recall_curve(yte,p)
ax.plot(recall,precision); ax.axhline(yte.mean(),linestyle='--'); ax.set(xlabel='Recall',ylabel='Precision',title='Fraud review: held-out precision–recall')
pd.DataFrame({'actual':yte,'score':p,'flagged':flagged}).to_csv(out/'review_queue.csv',index=False)

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
