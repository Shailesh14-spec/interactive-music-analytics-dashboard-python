"""Chronological campaign-response benchmark using pre-contact features only."""
from common import *
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.pipeline import make_pipeline
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import average_precision_score,roc_auc_score,brier_score_loss,precision_score,recall_score,precision_recall_curve
from sklearn.calibration import calibration_curve

raw=pd.read_csv(ROOT/'data/bank-additional-full.csv',sep=';')
features=['contact','month','day_of_week','pdays','previous','poutcome','emp.var.rate','cons.price.idx','cons.conf.idx','euribor3m','nr.employed']
assert set(features+['y','duration']).issubset(raw.columns)
assert set(raw.y.unique())=={'yes','no'}
assert not raw[features].isna().any().any()
x=raw[features].copy();x['previously_contacted']=(x.pdays!=999).astype(int)
x['pdays']=x.pdays.replace(999,0)
y=raw.y.eq('yes').astype(int)
n=len(raw);cut1=int(n*.6);cut2=int(n*.8)
a,b,c=slice(0,cut1),slice(cut1,cut2),slice(cut2,n)
assert x.iloc[a].index.max()<x.iloc[b].index.min()<x.iloc[c].index.min()
cat=x.select_dtypes('object').columns.tolist();num=[v for v in x if v not in cat]
def prep():
 return ColumnTransformer([('categorical',OneHotEncoder(handle_unknown='ignore',sparse_output=False),cat),('numeric',StandardScaler(),num)])
models={
 'logistic':make_pipeline(prep(),LogisticRegression(C=1,max_iter=2000,random_state=42)),
 'random_forest':make_pipeline(prep(),RandomForestClassifier(n_estimators=160,max_depth=8,min_samples_leaf=30,n_jobs=2,random_state=42))}
validation=[]
for name,model in models.items():
 model.fit(x.iloc[a],y.iloc[a]);p=model.predict_proba(x.iloc[b])[:,1]
 validation.append({'model':name,'average_precision':average_precision_score(y.iloc[b],p),'brier':brier_score_loss(y.iloc[b],p)})
validation=pd.DataFrame(validation).sort_values('average_precision',ascending=False)
selected=validation.iloc[0].model;model=models[selected]
pv=model.predict_proba(x.iloc[b])[:,1];threshold=float(np.quantile(pv,.9))
# Freeze model and threshold after validation; do not refit or tune on test outcomes.
p=model.predict_proba(x.iloc[c])[:,1];actual=y.iloc[c].to_numpy();flag=p>=threshold
rng=np.random.default_rng(42);aps=[]
for _ in range(250):
 idx=rng.integers(0,len(actual),len(actual))
 if len(np.unique(actual[idx]))==2:aps.append(average_precision_score(actual[idx],p[idx]))
precision=float(precision_score(actual,flag,zero_division=0));rate=float(actual.mean())
metrics={'rows':n,'train_rows':cut1,'validation_rows':cut2-cut1,'test_rows':n-cut2,'selected_model':selected,'test_prevalence':rate,'test_average_precision':average_precision_score(actual,p),'average_precision_bootstrap_95_ci':np.quantile(aps,[.025,.975]).tolist(),'test_roc_auc':roc_auc_score(actual,p),'test_brier':brier_score_loss(actual,p),'constant_prior_brier':brier_score_loss(actual,np.full(len(actual),y.iloc[a].mean())),'validation_90th_percentile_threshold':threshold,'test_review_share':float(flag.mean()),'test_precision_at_threshold':precision,'test_recall_at_threshold':recall_score(actual,flag,zero_division=0),'precision_lift_over_test_prevalence':precision/rate}
save_json('metrics.json',metrics)
validation.to_csv(OUT/'validation_comparison.csv',index=False)
pd.DataFrame([{'split':label,'rows':len(y.iloc[part]),'response_rate':float(y.iloc[part].mean())} for label,part in [('train',a),('validation',b),('test',c)]]).to_csv(OUT/'prevalence_drift.csv',index=False)
pd.DataFrame({'source_row':raw.iloc[c].index,'actual':actual,'score':p,'review':flag}).to_csv(OUT/'test_predictions.csv',index=False)
quality={'missing_cells':int(raw.isna().sum().sum()),'exact_duplicate_rows':int(raw.duplicated().sum()),'duration_excluded':True,'raw_rows_preserved':True,'split':'original chronological row order, 60/20/20'}
save_json('data_audit.json',quality)
fig,axes=plt.subplots(1,2,figsize=(11,4))
pr,re,_=precision_recall_curve(actual,p);axes[0].plot(re,pr,label=selected);axes[0].axhline(rate,ls='--',label='Test prevalence');axes[0].set(xlabel='Recall',ylabel='Precision',title='Future-period precision–recall');axes[0].legend()
frac,mean=calibration_curve(actual,p,n_bins=8,strategy='quantile');axes[1].plot(mean,frac,'o-');axes[1].plot([0,1],[0,1],'--');axes[1].set(xlabel='Mean predicted response',ylabel='Observed response',title='Calibration on held-out period')
save_chart(fig,'evaluation')
text=f'''# Findings\n\nThe validation-selected model is **{selected}**. On the untouched final {len(actual):,} rows, average precision is **{metrics['test_average_precision']:.3f}** against a prevalence baseline of **{rate:.3f}**. ROC AUC is {metrics['test_roc_auc']:.3f}.\n\nThe validation threshold flags {flag.mean():.1%} of test contacts, with {precision:.1%} precision and {metrics['test_recall_at_threshold']:.1%} recall. This is an offline prioritisation benchmark, not incremental campaign uplift. Threshold drift matters: a validation 10% review budget is not guaranteed to remain 10% later.\n\nRecommendation: do not deploy this model. Test ROC AUC is below 0.5 and average precision is close to the prevalence baseline, so this benchmark does not establish useful future-period ranking. Diagnose response-rate and economic-regime drift, obtain recent data, and rerun a pre-specified evaluation before considering a pilot. An observational response model cannot establish who would benefit from being contacted. No profit, cost savings, or deployment claim is made.\n\nThe bootstrap interval is an IID sensitivity calculation. Repeated contacts may share clients and time periods; this interval can understate uncertainty. Source identifiers do not support a client-grouped split.\n'''
(OUT/'FINDINGS.md').write_text(text)
print(json.dumps(metrics,indent=2))
