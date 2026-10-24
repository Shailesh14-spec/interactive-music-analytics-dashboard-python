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

n=1000
df=pd.DataFrame({'product_id':np.arange(n),'price':rng.uniform(5,300,n).round(2),'updated_at':pd.date_range('2025-01-01',periods=n,freq='h')})
df.loc[:9,'price']=-1;df.loc[10:19,'price']=np.nan
df=pd.concat([df,df.iloc[30:40]],ignore_index=True)
df['invalid_price']=df.price.isna() | (df.price<=0)
df['duplicate_id']=df.duplicated('product_id',keep=False)
clean=df.sort_values('updated_at').drop_duplicates('product_id',keep='last')
clean=clean.loc[~clean.invalid_price].drop(columns=['invalid_price','duplicate_id'])
assert clean.product_id.is_unique and clean.price.gt(0).all() and clean.price.notna().all()
metrics={'input_rows':len(df),'invalid_price_rows':int(df.invalid_price.sum()),'duplicate_group_rows':int(df.duplicate_id.sum()),'clean_rows':len(clean)}
ax.bar(['Invalid price','Duplicate group'],[df.invalid_price.sum(),df.duplicate_id.sum()]);ax.set(title='Price quality checks (flags may overlap)',ylabel='Flagged rows')
df.loc[df.invalid_price|df.duplicate_id].to_csv(out/'exceptions.csv',index=False);clean.to_csv(out/'clean_prices.csv',index=False)

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
