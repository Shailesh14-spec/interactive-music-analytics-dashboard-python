"""Integrity checks against a completed analysis run."""
from pathlib import Path
import json, unittest
import numpy as np
import pandas as pd
ROOT=Path(__file__).resolve().parents[1]
class ResultsTest(unittest.TestCase):
    def test_outputs_exist(self):
        report=ROOT/'reports'
        metrics=json.loads((report/'metrics.json').read_text())
        self.assertTrue(metrics)
        self.assertTrue(list(report.glob('*.svg')))
        self.assertTrue((report/'FINDINGS.md').is_file())
    def test_temporal_predictions(self):
        p=pd.read_csv(ROOT/'reports/predictions.csv',parse_dates=['dteday'])
        self.assertEqual(len(p),90)
        self.assertTrue(p.dteday.is_monotonic_increasing)
        self.assertTrue(p.dteday.is_unique)
        self.assertTrue(p.prediction.ge(0).all())
        self.assertTrue(p.lower.le(p.upper).all())
        raw=pd.read_csv(ROOT/'data/day.csv')
        np.testing.assert_allclose(p.seasonal_naive.to_numpy(),raw.cnt.shift(7).iloc[-90:].to_numpy())
        m=json.loads((ROOT/'reports/metrics.json').read_text())
        self.assertAlmostEqual(float(np.abs(p.cnt-p.prediction).mean()),m['test_mae'])
