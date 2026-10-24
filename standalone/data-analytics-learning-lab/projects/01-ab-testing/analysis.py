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

n = 12000
group = rng.integers(0, 2, n)
df = pd.DataFrame({'group': group, 'converted': rng.binomial(1, .12 + .012 * group)})
s = df.groupby('group').converted.agg(['sum', 'count', 'mean'])
a, b = s.loc[0], s.loc[1]
diff = b['mean'] - a['mean']
pooled = s['sum'].sum() / n
se0 = np.sqrt(pooled * (1-pooled) * (1/a['count'] + 1/b['count']))
z = diff / se0
se = np.sqrt(a['mean']*(1-a['mean'])/a['count'] + b['mean']*(1-b['mean'])/b['count'])
pvalue = 2 * stats.norm.sf(abs(z))
metrics = {'control_rate': a['mean'], 'treatment_rate': b['mean'], 'difference_pp': diff*100, 'p_value': pvalue, 'ci_lower_pp': (diff-1.96*se)*100, 'ci_upper_pp': (diff+1.96*se)*100}
s.to_csv(out/'group_summary.csv')
s['mean'].plot.bar(ax=ax, color=['#2364aa','#20a39e'], ylabel='Conversion rate', title='Simulated conversion experiment')

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
