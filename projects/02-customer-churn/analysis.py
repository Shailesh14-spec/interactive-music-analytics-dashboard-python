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

n = 3000
df = pd.DataFrame({'tenure': rng.integers(1,72,n), 'monthly_charge': rng.uniform(20,120,n), 'support_calls': rng.poisson(2,n)})
logit = -2.5 - .035*df.tenure + .023*df.monthly_charge + .35*df.support_calls
y = rng.binomial(1, 1/(1+np.exp(-logit)))
xtr,xte,ytr,yte = train_test_split(df,y,test_size=.25,stratify=y,random_state=42)
model = make_pipeline(StandardScaler(),LogisticRegression(random_state=42)).fit(xtr,ytr)
probs = model.predict_proba(xte)[:,1]
baseline = DummyClassifier(strategy='prior').fit(xtr,ytr).predict_proba(xte)[:,1]
metrics = {'test_roc_auc': roc_auc_score(yte,probs), 'test_average_precision': average_precision_score(yte,probs), 'baseline_average_precision': average_precision_score(yte,baseline), 'test_rows': len(yte)}
fpr,tpr,_ = roc_curve(yte,probs)
ax.plot(fpr,tpr,label='Logistic regression'); ax.plot([0,1],[0,1],'--',label='Random baseline'); ax.set(xlabel='False positive rate',ylabel='True positive rate',title='Held-out churn classification'); ax.legend()
pd.DataFrame({'actual':yte,'probability':probs}).to_csv(out/'test_predictions.csv',index=False)

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
