# Bike Rental Demand Forecasting

**Does a lag-based model improve next-day rental estimates over a weekly seasonal baseline?**

An independent portfolio case study using real public data, built with AI assistance. It is not an employer project or a claim of commercial delivery.

![Results](reports/forecast.svg)

## Evidence and findings

Read [measured findings and recommendations](reports/FINDINGS.md), [metrics](reports/metrics.json), and the generated CSV reports in [reports](reports/). Results come from executing the committed analysis; no business impact is invented.

## Reproduce

Python 3.12 was used for validation. In a virtual environment:

```bash
python -m venv .venv
# macOS/Linux
source .venv/bin/activate
# Windows PowerShell: .venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python download_data.py
python analysis.py
python -m unittest discover -s tests -v
```

The download script accesses the official UCI archive and verifies the extracted file's SHA-256. It writes only to this project's data directory. No account or private data is needed. Runtime libraries are pinned; Python and operating-system differences can still cause small numerical variation.

## Method

- Loads the UCI daily bike-rental series and checks date continuity and target reconciliation.
- Creates lagged demand and a strictly shifted seven-day rolling mean, plus calendar encodings and a time trend.
- Excludes same-day weather and the `casual`/`registered` components of the target to prevent unavailable information and direct target leakage.
- Uses an initial training period, 90 validation days, and the final 90 days as an untouched test set.
- Chooses between Ridge and histogram gradient boosting using validation MAE. The trained model stays frozen for test evaluation.
- Compares with lag-7 demand and reports MAE, RMSE, monthly residual errors, a seven-day block-bootstrap difference interval, and coverage of a validation-residual band.

## Data provenance

See [DATA_SOURCE.md](DATA_SOURCE.md) for creators, DOI, CC BY 4.0 attribution, source URL, and checksum. Original raw data is downloaded rather than committed. [source.json](source.json) records the exact extraction configuration.

## Interpretation and limitations

Evaluation is rolling one-step-ahead: previous test-day actuals become available before the next forecast. It is not a 90-day-ahead forecast from a single origin. The residual band is an empirical diagnostic, not a guaranteed conformal interval. Only one city and two years are observed; structural changes and extreme weather remain unmodelled.

## Files

| File | Purpose |
| --- | --- |
| `analysis.py` | Reproducible analysis and report generation |
| `common.py` | Local output and chart helpers |
| `download_data.py` | Verified public dataset acquisition |
| `reports/` | Measured results, figures, and findings |
| `tests/` | Output integrity and methodological invariants |

## Skills demonstrated

Python, pandas, data validation, reproducibility, evaluation design, visualisation, and evidence-based communication, leakage prevention and baseline comparison.

Code is [MIT licensed](LICENSE); dataset terms remain separate.
