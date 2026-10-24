"""SQL conversion scorecard with denominator checks and Wilson intervals."""
from common import *
import sqlite3
from scipy.stats import chi2_contingency
raw=pd.read_csv(ROOT/'data/online_shoppers_intention.csv')
required=['Revenue','VisitorType','Month','TrafficType','Weekend']
assert set(required).issubset(raw)
assert not raw[required].isna().any().any()
assert set(raw.Revenue.unique())=={True,False}
df=raw.copy();df['Revenue']=df.Revenue.astype(int)
# No user or session identifier exists. Identical feature rows are preserved.
queries={
 'visitor_type':'''SELECT VisitorType AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY VisitorType ORDER BY sessions DESC''',
 'month':'''SELECT Month AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY Month ORDER BY sessions DESC''',
 'traffic':'''SELECT TrafficType AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY TrafficType ORDER BY sessions DESC''',
 'weekend':'''SELECT Weekend AS segment,COUNT(*) AS sessions,SUM(Revenue) AS conversions,AVG(Revenue) AS conversion_rate FROM sessions GROUP BY Weekend ORDER BY sessions DESC'''}
def wilson(k,n,z=1.96):
 p=k/n;den=1+z*z/n;centre=(p+z*z/(2*n))/den
 half=z*np.sqrt(p*(1-p)/n+z*z/(4*n*n))/den
 return np.clip(centre-half,0,1),np.clip(centre+half,0,1)
reports={}
with sqlite3.connect(':memory:') as conn:
 df.to_sql('sessions',conn,index=False)
 for key,query in queries.items():
  report=pd.read_sql_query(query,conn)
  assert report.sessions.sum()==len(raw)
  assert report.conversions.sum()==int(raw.Revenue.sum())
  report['ci_low'],report['ci_high']=wilson(report.conversions,report.sessions)
  assert report.ci_low.ge(0).all() and report.ci_high.le(1).all()
  report.to_csv(OUT/(key+'.csv'),index=False);reports[key]=report
(ROOT/'analysis.sql').write_text('\n\n'.join('-- '+k+'\n'+q+';' for k,q in queries.items())+'\n')
table=pd.crosstab(raw.VisitorType,raw.Revenue);chi,pvalue,dof,expected=chi2_contingency(table)
cramers_v=float(np.sqrt(chi/(table.to_numpy().sum()*min(table.shape[0]-1,table.shape[1]-1))))
rate=float(raw.Revenue.mean());quality={'rows':len(raw),'missing_cells':int(raw.isna().sum().sum()),'exact_duplicate_feature_rows':int(raw.duplicated().sum()),'duplicate_policy':'preserve: no session identifier available','revenue_is_boolean_not_money':True}
save_json('data_audit.json',quality)
metrics={'sessions':len(raw),'conversions':int(raw.Revenue.sum()),'overall_conversion_rate':rate,'visitor_type_chi_square':float(chi),'visitor_type_p_value':float(pvalue),'visitor_type_cramers_v':cramers_v,'chi_square_min_expected_cell':float(expected.min()),'overall_wilson_95_ci':list(wilson(int(raw.Revenue.sum()),len(raw)))}
save_json('metrics.json',metrics)
r=reports['visitor_type'];fig,ax=plt.subplots(figsize=(9,5));ax.bar(r.segment,r.conversion_rate,color='#2364aa');ax.errorbar(r.segment,r.conversion_rate,yerr=[r.conversion_rate-r.ci_low,r.ci_high-r.conversion_rate],fmt='none',color='black',capsize=5);ax.axhline(rate,ls='--',color='#d97706',label='Overall');ax.set(ylabel='Converting session share',title='Visitor conversion with 95% Wilson intervals');ax.legend();save_chart(fig,'visitor_conversion')
sub=r.loc[r.sessions>=100].sort_values('conversion_rate',ascending=False);best=sub.iloc[0]
(OUT/'FINDINGS.md').write_text(f'''# Findings\n\n**{len(raw):,} sessions** contain **{int(raw.Revenue.sum()):,} conversions**, an overall rate of **{rate:.2%}**. Among visitor groups with at least 100 sessions, **{best.segment}** has the highest observed conversion rate ({best.conversion_rate:.2%}; n={int(best.sessions):,}).\n\nVisitor type has an observed association with conversion: Cramer's V={cramers_v:.3f}, chi-square p={pvalue:.3g}. This comparison is descriptive. It does not establish that changing visitor type changes conversion, or that any channel has a causal effect. The p-value does not adjust for the other exploratory segment tables.\n\nRecommendation: use the scorecard to identify hypotheses for a separately randomised experiment. Check audience mix, acquisition source, and season before changing budgets. Revenue is a Boolean label: this analysis cannot estimate sales value, ROAS, or profit. Month categories are not complete dates and cannot support chronological retention cohorts.\n\nAll SQL segment totals reconcile to the original row and conversion totals. Wilson intervals quantify sampling uncertainty under independent-session assumptions; they do not correct selection or measurement bias.\n''')
print(json.dumps(metrics,indent=2))
