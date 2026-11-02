"""Minimal regression checks for the SQL, Python and A/B projects."""
from pathlib import Path
import csv
import sqlite3
import math
import unittest

ROOT = Path(__file__).resolve().parent

class PortfolioTests(unittest.TestCase):
    def test_synthetic_orders_have_unique_ids(self):
        with (ROOT/'01_marketplace_sql/data/orders.csv').open(encoding='utf-8',newline='') as f:
            rows = list(csv.DictReader(f))
        self.assertEqual(len(rows), 3200)
        self.assertEqual(len({r['order_id'] for r in rows}),len(rows))
        self.assertTrue(all(float(r['quantity']) > 0 for r in rows))

    def test_experiment_is_valid_funnel(self):
        with (ROOT/'03_ab_test/data/experiment.csv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertEqual(len(rows), 24000)
        self.assertEqual(len({r['user_id'] for r in rows}), len(rows))
        self.assertTrue(all(int(r['completed']) <= int(r['started']) for r in rows))

    def test_sql_revenue_equals_python_revenue(self):
        with (ROOT/'01_marketplace_sql/data/orders.csv').open(encoding='utf-8',newline='') as f:
            rows = list(csv.DictReader(f))
        expected=sum(float(r['quantity'])*float(r['price_rub']) for r in rows if r['order_status']=='delivered')
        with (ROOT/'01_marketplace_sql/results/01_kpi.csv').open(encoding='utf-8',newline='') as f:
            result=next(csv.DictReader(f))
        self.assertTrue(math.isclose(expected, float(result['revenue_rub']), rel_tol=1e-9))

    def test_first_month_retention_is_100_percent(self):
        with (ROOT/'01_marketplace_sql/results/05_cohorts.csv').open(encoding='utf-8',newline='') as f:
            rows=list(csv.DictReader(f))
        self.assertTrue(all(float(r['retention_pct'])==100 for r in rows if int(r['month_number'])==0))

if __name__ == '__main__':
    unittest.main()
