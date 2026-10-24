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

n=420; t=np.arange(n)
df=pd.DataFrame({'date':pd.date_range('2024-01-01',periods=n),'demand':120+.10*t+22*np.sin(2*np.pi*t/7)+rng.normal(0,9,n)})
for lag in [1,7,14]: df[f'lag_{lag}']=df.demand.shift(lag)
df=df.dropna(); train,test=df.iloc[:-60],df.iloc[-60:]
features=['lag_1','lag_7','lag_14']
model=make_pipeline(StandardScaler(),Ridge(alpha=1)).fit(train[features],train.demand)
p=model.predict(test[features]); b=test.lag_7
metrics={'model_mae':mean_absolute_error(test.demand,p),'seasonal_naive_mae':mean_absolute_error(test.demand,b),'holdout_days':60}
ax.plot(test.date,test.demand,label='Actual');ax.plot(test.date,p,label='Ridge');ax.plot(test.date,b,alpha=.5,label='Lag 7');ax.legend();ax.set(title='One-step-ahead demand forecast',ylabel='Units');fig.autofmt_xdate()
test.assign(prediction=p).to_csv(out/'forecast.csv',index=False)

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
