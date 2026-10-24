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

from types import SimpleNamespace
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics import ConfusionMatrixDisplay
vocabulary = {
    'billing': ['invoice', 'payment', 'refund', 'charge', 'receipt', 'balance'],
    'technical': ['network', 'software', 'connection', 'error', 'device', 'installation'],
    'delivery': ['parcel', 'shipment', 'courier', 'address', 'tracking', 'dispatch'],
}
documents, labels = [], []
for label, words in enumerate(vocabulary.values()):
    for i in range(120):
        selected = rng.choice(words, size=3, replace=False)
        documents.append('Please help with ' + ' '.join(selected) + rng.choice([' today', ' for my account', ' as soon as possible']))
        labels.append(label)
corpus = SimpleNamespace(data=documents, target=np.array(labels), target_names=np.array(list(vocabulary)))
x=corpus.data; y=corpus.target
xtr,xte,ytr,yte=train_test_split(x,y,test_size=.3,stratify=y,random_state=42)
model=make_pipeline(TfidfVectorizer(),LogisticRegression(max_iter=1000,random_state=42)).fit(xtr,ytr)
p=model.predict(xte);baseline=DummyClassifier(strategy='most_frequent').fit(np.zeros((len(ytr),1)),ytr).predict(np.zeros((len(yte),1)))
metrics={'macro_f1':f1_score(yte,p,average='macro'),'baseline_macro_f1':f1_score(yte,baseline,average='macro'),'train_documents':len(ytr),'test_documents':len(yte)}
ConfusionMatrixDisplay.from_predictions(yte,p,display_labels=corpus.target_names,ax=ax,colorbar=False);ax.set_title('Held-out topic classification')
pd.DataFrame({'actual':corpus.target_names[yte],'predicted':corpus.target_names[p]}).to_csv(out/'predictions.csv',index=False)

fig.tight_layout()
fig.savefig(out/'chart.svg',dpi=150)
plt.close(fig)
(out/'metrics.json').write_text(json.dumps(metrics,indent=2,default=lambda x:x.item())+'\n')
print(json.dumps(metrics,indent=2,default=lambda x:x.item()))
