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
    def test_sql_reconciliation_and_intervals(self):
        m=json.loads((ROOT/'reports/metrics.json').read_text())
        for name in ['visitor_type','month','traffic','weekend']:
            d=pd.read_csv(ROOT/'reports'/f'{name}.csv')
            self.assertEqual(d.sessions.sum(),m['sessions'])
            self.assertEqual(d.conversions.sum(),m['conversions'])
            self.assertTrue(d.ci_low.ge(0).all())
            self.assertTrue(d.ci_high.le(1).all())
            np.testing.assert_allclose(d.conversions/d.sessions,d.conversion_rate)
