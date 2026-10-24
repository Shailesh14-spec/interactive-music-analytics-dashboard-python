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
    def test_leakage_and_split(self):
        audit=json.loads((ROOT/'reports/data_audit.json').read_text())
        self.assertTrue(audit['duration_excluded'])
        m=json.loads((ROOT/'reports/metrics.json').read_text())
        self.assertEqual(m['train_rows']+m['validation_rows']+m['test_rows'],m['rows'])
        p=pd.read_csv(ROOT/'reports/test_predictions.csv')
        self.assertEqual(len(p),m['test_rows'])
        self.assertTrue(p.score.between(0,1).all())
        self.assertGreaterEqual(p.source_row.min(),m['train_rows']+m['validation_rows'])
        self.assertAlmostEqual(p.actual.mean(),m['test_prevalence'])
