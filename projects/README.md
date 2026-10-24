# Data Analytics & Data Science Portfolio

Ten runnable educational projects covering SQL, experimentation, predictive modelling, forecasting, customer analytics, and operations.

**Provenance:** all ten projects generate synthetic data with a fixed random seed. Created with AI assistance. These projects demonstrate methods and are not claims of employment, real-client delivery, or real-world business impact.

## Project directory

| Project | Decision question |
| --- | --- |
| [Conversion A/B Testing](01-ab-testing) | Estimate conversion lift and quantify uncertainty before a rollout. |
| [Customer Churn Classification](02-customer-churn) | Prioritise customers for retention review using information available before churn. |
| [Transaction Fraud Triage](03-fraud-triage) | Evaluate a review queue under strong class imbalance. |
| [Retail Demand Forecasting](04-demand-forecasting) | Compare a lag-based forecast with a weekly seasonal baseline. |
| [Customer RFM Segmentation](05-rfm-segmentation) | Identify customer groups for differentiated engagement. |
| [SQL Sales Performance](06-sql-sales) | Build a monthly category revenue report from relational sales data. |
| [Subscription Cohort Retention](07-cohort-retention) | Track retention using correct exposure windows. |
| [Price Data Quality Audit](08-price-quality) | Flag invalid prices and reconcile duplicate product records. |
| [Service Operations SLA Analysis](09-service-sla) | Identify queues with slow resolution and SLA breaches. |
| [Document Topic Classification](10-document-classifier) | Classify documents using text features with a held-out evaluation. |

## Reproduce all results

Use Python 3.11 or newer, in a virtual environment:

```bash
python -m pip install -r projects/requirements.txt
python projects/run_all.py
```

Each project contains executable analysis, provenance and limitations, measured metrics, a chart, and CSV output. Outputs are deterministic for a fixed software environment. Dependency version ranges are provided rather than an exact environment lock; small numerical differences between versions are possible.

## Portfolio use

Study and customise the analyses, explain tradeoffs, and replace synthetic data with documented public datasets before treating these as mature case studies. All projects are currently in this repository because the connected integration cannot create new repositories.
