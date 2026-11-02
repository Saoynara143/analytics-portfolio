"""Reproducible analytics: CSV -> validation -> aggregations -> charts/report."""
from pathlib import Path
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent
DATA = HERE.parent / '01_marketplace_sql' / 'data' / 'orders.csv'

def main():
    df = pd.read_csv(DATA, parse_dates=['order_date'])
    assert df['order_id'].is_unique, 'Duplicated order_id'
    assert not df[['order_date', 'price_rub', 'purchase_cost_rub', 'order_status']].isna().any().any()
    assert (df['quantity'] > 0).all()
    valid = {'delivered', 'cancelled', 'returned'}
    assert set(df['order_status']) <= valid
    delivered = df.loc[df['order_status'] == 'delivered'].copy()
    delivered['revenue'] = delivered['quantity'] * delivered['price_rub']
    delivered['contribution_profit'] = (
        delivered['revenue'] - delivered['quantity'] * delivered['purchase_cost_rub']
        - delivered[['commission_rub', 'logistics_rub', 'acquiring_rub', 'tax_rub', 'ads_rub']].sum(axis=1)
    )
    delivered['month'] = delivered['order_date'].dt.to_period('M').astype(str)
    monthly = delivered.groupby('month', as_index=False)[['revenue', 'contribution_profit']].sum()
    category = (delivered.groupby('category', as_index=False)[['revenue', 'contribution_profit']]
                .sum().sort_values('contribution_profit', ascending=False))
    month_ax = monthly.plot(x='month', y=['revenue', 'contribution_profit'], kind='bar', figsize=(10, 5),
                            title='Revenue vs contribution profit | synthetic marketplace', rot=0)
    month_ax.set_ylabel('RUB')
    month_ax.figure.tight_layout()
    month_ax.figure.savefig(HERE / 'charts' / 'monthly.png', dpi=145)
    plt.close(month_ax.figure)
    fig, ax = plt.subplots(figsize=(10, 5))
    ax.barh(range(len(category)), category['contribution_profit'])
    ax.set_yticks(range(len(category)), category['category'])
    ax.invert_yaxis()
    ax.set_xlabel('Contribution profit, RUB')
    ax.set_title('Contribution profit by category | synthetic dataset')
    fig.tight_layout()
    fig.savefig(HERE / 'charts' / 'categories.png', dpi=145)
    plt.close(fig)

    revenue = delivered['revenue'].sum()
    profit = delivered['contribution_profit'].sum()
    status_shares = df['order_status'].value_counts(normalize=True)
    best_category = category.iloc[0]
    worst_month = monthly.loc[monthly['contribution_profit'].idxmin()]
    best_month = monthly.loc[monthly['contribution_profit'].idxmax()]
    report = f"""# Отчёт по синтетическим заказам

"""
    report += f"""- Всего заказов в файле: **{len(df):,}**; доставлено: **{len(delivered):,}**.
"""
    report += f"""- Выручка доставленных заказов: **{revenue:,.0f} ₽**.
"""
    report += f"""- Маржинальный доход (contribution profit): **{profit:,.0f} ₽**; маржа: **{profit/revenue*100:.1f}%**.
"""
    report += f"""- Доля возвращённых заказов: **{status_shares.get('returned', 0)*100:.1f}%**; доля отменённых: **{status_shares.get('cancelled', 0)*100:.1f}%**.
"""
    report += f"""- Категория-лидер по маржинальному доходу: **{best_category['category']}** ({best_category['contribution_profit']:,.0f} ₽).
"""
    report += f"""- Наибольший contribution profit за месяц: **{best_month['month']}** ({best_month['contribution_profit']:,.0f} ₽); наименьший: **{worst_month['month']}** ({worst_month['contribution_profit']:,.0f} ₽).
"""
    report += """
## Что делать дальше

1. Проверить рентабельность и возвраты на уровне SKU, а не только категории.
2. Уточнить правила признания расходов по возвращённым заказам и добавить фиксированные расходы.
3. Сравнить категории по вложенному оборотному капиталу, а не только по абсолютному маржинальному доходу.

*Все данные искусственные, выводы не относятся к реальному магазину.*
"""
    (HERE / 'report.md').write_text(report, encoding='utf-8')
    print(report)

if __name__ == '__main__':
    main()
