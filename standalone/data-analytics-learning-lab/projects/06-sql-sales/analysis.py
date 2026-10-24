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

import sqlite3
n=3000
orders=pd.DataFrame({'order_id':np.arange(n),'product_id':rng.integers(1,5,n),'date':pd.Timestamp('2025-01-01')+pd.to_timedelta(rng.integers(0,365,n),unit='D'),'quantity':rng.integers(1,5,n)})
products=pd.DataFrame({'product_id':[1,2,3,4],'category':['Home','Home','Tech','Tech'],'price':[15.,30.,50.,80.]})
query="""WITH monthly AS (
SELECT strftime('%Y-%m',o.date) AS month,p.category,SUM(o.quantity*p.price) AS revenue
FROM orders o JOIN products p ON o.product_id=p.product_id GROUP BY 1,2)
SELECT *,revenue-LAG(revenue) OVER (PARTITION BY category ORDER BY month) AS revenue_change FROM monthly ORDER BY month,category"""
with sqlite3.connect(':memory:') as conn:
 orders.to_sql('orders',conn,index=False);products.to_sql('products',conn,index=False)
 result=pd.read_sql_query(query,conn)
expected=(orders.merge(products,on='product_id').eval('quantity*price')).sum()
assert np.isclose(result.revenue.sum(),expected)
metrics={'orders':n,'revenue':float(expected),'report_rows':len(result)}
result.pivot(index='month',columns='category',values='revenue').plot(ax=ax,title='Monthly category revenue',ylabel='Revenue (simulated units)');ax.tick_params(axis='x',rotation=45)
result.to_csv(out/'monthly_sales.csv',index=False)
(out/'analysis.sql').write_text(query+';\n')

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
