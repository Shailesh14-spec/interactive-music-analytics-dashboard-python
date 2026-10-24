# Findings

Validation selected **ridge**. Test MAE is **977.7 rentals/day**, compared with **1,450.5** for last week's demand (32.6% improvement; negative means worse).

A seven-day moving-block bootstrap estimates the model-minus-baseline MAE difference interval as [-820.1151116028254, -138.16034355087456]. This is a dependence-aware sensitivity analysis, not evidence across multiple cities or future years.

The absolute validation-residual band covers 81.1% of test actuals. Distribution shift and correlated errors prevent treating this as a guaranteed 90% prediction interval.

Recommendation: retain the seasonal baseline unless the model's error reduction is operationally useful and stable. Investigate large residuals and backtest additional seasons before staffing or inventory decisions. No financial impact is estimated.
