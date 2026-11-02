"""Execute every query on an in-memory SQLite database. No pip dependencies."""
from pathlib import Path
import csv
import sqlite3

HERE = Path(__file__).resolve().parent
COLUMNS = ["order_id", "order_date", "customer_id", "product_id", "category", "quantity",
           "price_rub", "purchase_cost_rub", "commission_rub", "logistics_rub", "acquiring_rub",
           "tax_rub", "ads_rub", "order_status"]
NUMERIC = {"quantity", "price_rub", "purchase_cost_rub", "commission_rub", "logistics_rub", "acquiring_rub", "tax_rub", "ads_rub"}

def main():
    db = sqlite3.connect(':memory:')
    schema = ', '.join(f'{c} {"REAL" if c in NUMERIC else "TEXT"}' for c in COLUMNS)
    db.execute(f'CREATE TABLE orders ({schema})')
    with (HERE / 'data' / 'orders.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    assert rows and set(rows[0]) == set(COLUMNS)
    db.executemany('INSERT INTO orders VALUES (' + ','.join(['?'] * len(COLUMNS)) + ')',
                   [[float(row[c]) if c in NUMERIC else row[c] for c in COLUMNS] for row in rows])
    out = HERE / 'results'
    out.mkdir(exist_ok=True)
    for query_file in sorted((HERE / 'sql').glob('*.sql')):
        cur = db.execute(query_file.read_text(encoding='utf-8'))
        names = [col[0] for col in cur.description]
        results = cur.fetchall()
        with (out / f'{query_file.stem}.csv').open('w', encoding='utf-8', newline='') as f:
            w = csv.writer(f); w.writerow(names); w.writerows(results)
        print(f'{query_file.name}: {len(results)} строк; первая строка: {results[0] if results else "нет"}')
    db.close()

if __name__ == '__main__':
    main()
