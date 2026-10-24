"""Next-day forecasting evaluated one day at a time with a chronological holdout."""
from common import *
from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler
from sklearn.linear_model import Ridge
from sklearn.ensemble import HistGradientBoostingRegressor
from sklearn.metrics import mean_absolute_error,mean_squared_error
raw=pd.read_csv(ROOT/'data/day.csv',parse_dates=['dteday']).sort_values('dteday').reset_index(drop=True)
assert raw.dteday.is_unique
assert raw.dteday.diff().dropna().eq(pd.Timedelta(days=1)).all()
assert (raw.casual+raw.registered).eq(raw.cnt).all()
df=raw[['dteday','cnt']].copy()
for lag in [1,7,14,28]:df[f'lag_{lag}']=df.cnt.shift(lag)
df['rolling_7']=df.cnt.shift(1).rolling(7).mean()
df['weekday_sin']=np.sin(2*np.pi*df.dteday.dt.dayofweek/7)
df['weekday_cos']=np.cos(2*np.pi*df.dteday.dt.dayofweek/7)
df['annual_sin']=np.sin(2*np.pi*df.dteday.dt.dayofyear/365.25)
df['annual_cos']=np.cos(2*np.pi*df.dteday.dt.dayofyear/365.25)
df['trend']=np.arange(len(df))
df=df.dropna().reset_index(drop=True)
features=[col for col in df if col not in ['dteday','cnt']]
train,val,test=df.iloc[:-180],df.iloc[-180:-90],df.iloc[-90:]
assert train.dteday.max()<val.dteday.min()<test.dteday.min()
models={'ridge':make_pipeline(StandardScaler(),Ridge(alpha=10)), 'gradient_boosting':HistGradientBoostingRegressor(max_iter=150,max_leaf_nodes=10,l2_regularization=10,random_state=42)}
rows=[]
for name,model in models.items():
 model.fit(train[features],train.cnt);pv=np.maximum(model.predict(val[features]),0)
 rows.append({'model':name,'validation_mae':mean_absolute_error(val.cnt,pv)})
comparison=pd.DataFrame(rows).sort_values('validation_mae');name=comparison.iloc[0].model;model=models[name]
pv=np.maximum(model.predict(val[features]),0);q=float(np.quantile(np.abs(val.cnt-pv),.9))
# Keep the validation-selected, training-period fitted model frozen.
p=np.maximum(model.predict(test[features]),0);baseline=test.lag_7.to_numpy();actual=test.cnt.to_numpy()
mae=mean_absolute_error(actual,p);bmae=mean_absolute_error(actual,baseline)
errdiff=np.abs(actual-p)-np.abs(actual-baseline)
rng=np.random.default_rng(42);block_means=[];n=len(test)
for _ in range(500):
 starts=rng.integers(0,n,int(np.ceil(n/7)))
 idx=np.concatenate([(np.arange(s,s+7)%n) for s in starts])[:n]
 block_means.append(errdiff[idx].mean())
metrics={'raw_days':len(raw),'train_days':len(train),'validation_days':90,'test_days':90,'selected_model':name,'test_start':str(test.dteday.min().date()),'test_end':str(test.dteday.max().date()),'test_mae':mae,'seasonal_naive_mae':bmae,'mae_improvement_percent':100*(bmae-mae)/bmae,'test_rmse':float(np.sqrt(mean_squared_error(actual,p))),'mae_difference_7day_block_bootstrap_95_ci':np.quantile(block_means,[.025,.975]).tolist(),'validation_residual_90pct_radius':q,'test_empirical_interval_coverage':float(((actual>=np.maximum(0,p-q))&(actual<=p+q)).mean())}
save_json('metrics.json',metrics);comparison.to_csv(OUT/'validation_comparison.csv',index=False)
pred=test[['dteday','cnt']].assign(prediction=p,seasonal_naive=baseline,lower=np.maximum(0,p-q),upper=p+q);pred.to_csv(OUT/'predictions.csv',index=False)
monthly=pred.assign(month=pred.dteday.dt.to_period('M').astype(str),absolute_error=np.abs(actual-p)).groupby('month').absolute_error.agg(['count','mean']);monthly.to_csv(OUT/'monthly_errors.csv')
fig,axes=plt.subplots(2,1,figsize=(11,7))
axes[0].plot(test.dteday,actual,label='Actual');axes[0].plot(test.dteday,p,label=name);axes[0].plot(test.dteday,baseline,alpha=.4,label='Lag 7');axes[0].fill_between(test.dteday,np.maximum(0,p-q),p+q,alpha=.15,label='Validation residual band');axes[0].legend();axes[0].set(ylabel='Daily rentals',title='One-step-ahead held-out forecasts')
axes[1].axhline(0,color='grey');axes[1].plot(test.dteday,actual-p);axes[1].set(ylabel='Actual minus forecast',title='Residuals over time');fig.autofmt_xdate();save_chart(fig,'forecast')
(OUT/'FINDINGS.md').write_text(f'''# Findings\n\nValidation selected **{name}**. Test MAE is **{mae:,.1f} rentals/day**, compared with **{bmae:,.1f}** for last week's demand ({metrics['mae_improvement_percent']:.1f}% improvement; negative means worse).\n\nA seven-day moving-block bootstrap estimates the model-minus-baseline MAE difference interval as {metrics['mae_difference_7day_block_bootstrap_95_ci']}. This is a dependence-aware sensitivity analysis, not evidence across multiple cities or future years.\n\nThe absolute validation-residual band covers {metrics['test_empirical_interval_coverage']:.1%} of test actuals. Distribution shift and correlated errors prevent treating this as a guaranteed 90% prediction interval.\n\nRecommendation: retain the seasonal baseline unless the model's error reduction is operationally useful and stable. Investigate large residuals and backtest additional seasons before staffing or inventory decisions. No financial impact is estimated.\n''')
print(json.dumps(metrics,indent=2))
