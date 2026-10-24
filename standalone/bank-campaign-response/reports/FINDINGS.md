# Findings

The validation-selected model is **random_forest**. On the untouched final 8,238 rows, average precision is **0.310** against a prevalence baseline of **0.308**. ROC AUC is 0.477.

The validation threshold flags 23.5% of test contacts, with 33.2% precision and 25.3% recall. This is an offline prioritisation benchmark, not incremental campaign uplift. Threshold drift matters: a validation 10% review budget is not guaranteed to remain 10% later.

Recommendation: do not deploy this model. Test ROC AUC is below 0.5 and average precision is close to the prevalence baseline, so this benchmark does not establish useful future-period ranking. Diagnose response-rate and economic-regime drift, obtain recent data, and rerun a pre-specified evaluation before considering a pilot. An observational response model cannot establish who would benefit from being contacted. No profit, cost savings, or deployment claim is made.

The bootstrap interval is an IID sensitivity calculation. Repeated contacts may share clients and time periods; this interval can understate uncertainty. Source identifiers do not support a client-grouped split.
