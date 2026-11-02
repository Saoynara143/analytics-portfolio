"""A/B analysis with conversion, two-proportion z-test, CI and SRM guardrail."""
from pathlib import Path
from math import sqrt, erfc
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

HERE = Path(__file__).resolve().parent

def two_proportion_test(success_a, n_a, success_b, n_b):
    pa, pb = success_a / n_a, success_b / n_b
    pooled = (success_a + success_b) / (n_a + n_b)
    pooled_se = sqrt(pooled * (1 - pooled) * (1/n_a + 1/n_b))
    z = (pb - pa) / pooled_se if pooled_se else 0
    p_value = erfc(abs(z) / sqrt(2))  # 2-sided normal-tail p-value
    unpooled_se = sqrt(pa*(1-pa)/n_a + pb*(1-pb)/n_b)
    ci_low, ci_high = (pb-pa)-1.96*unpooled_se, (pb-pa)+1.96*unpooled_se
    return pa, pb, z, p_value, ci_low, ci_high

def main():
    df = pd.read_csv(HERE / 'data' / 'experiment.csv')
    assert df['user_id'].is_unique
    assert set(df['variant']) == {'A', 'B'}
    assert set(df['started'].unique()) <= {0, 1}
    assert set(df['completed'].unique()) <= {0, 1}
    assert (df['completed'] <= df['started']).all()
    by_variant = df.groupby('variant').agg(users=('user_id','count'), started=('started','sum'),
                                           completed=('completed','sum'))
    a,b = by_variant.loc['A'],by_variant.loc['B']
    p_a,p_b,z,p_value,ci_low,ci_high = two_proportion_test(a['completed'],a['users'],b['completed'],b['users'])
    n_a,n_b=int(a['users']),int(b['users'])
    total=n_a+n_b
    # SRM check: normal approximation to a binomial 50/50 assignment.
    srm_z=(n_b-total/2)/sqrt(total*0.25)
    srm_p=erfc(abs(srm_z)/sqrt(2))
    start_a,start_b,_,start_p,_,_ = two_proportion_test(a['started'],n_a,b['started'],n_b)
    fig,ax=plt.subplots(figsize=(7.4,4.5))
    rates=[p_a*100,p_b*100]
    bars=ax.bar(['A: контроль','B: изменение'],rates, color=['#94A3B8','#2563EB'],width=0.55)
    ax.set_ylabel('Registration completion, %')
    ax.set_ylim(0,max(rates)*1.30)
    for bar,value in zip(bars,rates):
        ax.text(bar.get_x()+bar.get_width()/2,value+0.4,f'{value:.2f}%',ha='center')
    ax.set_title('A/B registration: synthetic data')
    fig.tight_layout();fig.savefig(HERE/'charts'/'conversion.png',dpi=150);plt.close(fig)
    signal = p_value < 0.05
    report = f"""# Результат учебного A/B-теста (синтетические данные)

"""
    report += f"""| Показатель | A (контроль) | B (изменение) |
|---|---:|---:|
"""
    report += f"""| Рандомизированные пользователи | {n_a:,} | {n_b:,} |
"""
    report += f"""| Завершили регистрацию | {int(a['completed']):,} | {int(b['completed']):,} |
"""
    report += f"""| Конверсия в завершение | {p_a*100:.2f}% | {p_b*100:.2f}% |
"""
    report += f"""| Конверсия в начало | {start_a*100:.2f}% | {start_b*100:.2f}% |

"""
    report += f"""- **Абсолютная разница B − A:** {(p_b-p_a)*100:+.2f} процентных пункта.
"""
    report += f"""- **Относительный uplift:** {(p_b/p_a-1)*100:+.2f}%.
"""
    report += f"""- **95% ДИ для абсолютной разницы (B − A):** [{ci_low*100:+.2f}; {ci_high*100:+.2f}] п.п.
"""
    report += f"""- **z-тест основной метрики, двусторонний:** z={z:.3f}, p={p_value:.2e}.
"""
    report += f"""- **SRM (ожидаемое распределение 50/50):** p={srm_p:.5f}; {'подозрение на дисбаланс' if srm_p<0.01 else 'критического дисбаланса не обнаружено'} (порог 0.01).
"""
    report += f"""- **Вторичная метрика (начало регистрации):** A={start_a*100:.2f}%, B={start_b*100:.2f}%, p={start_p:.2e} (exploratory; без поправки на множественные проверки).

"""
    report += f"""## Интерпретация

"""
    report += ("""На синтетических данных разница по основной метрике статистически значима при α=0.05. """ if signal else """На синтетических данных не найдено статистически значимой разницы при α=0.05. """)
    report += """Это **не рекомендация выкатывать изменение в реальный продукт**: отсутствуют заранее заданный размер выборки, подтверждённая длительность, проверка guardrail-метрик и реальный экспериментальный контекст.

## Методология

ITT: в знаменатель включены все рандомизированные пользователи, без фильтрации по тем, кто начал регистрацию. Для основной метрики — pooled z-test для p-value, нормальный unpooled ДИ разницы; для SRM — проверка отклонения от ожидаемого 50/50.
"""
    (HERE/'report.md').write_text(report,encoding='utf-8')
    print(report)

if __name__ == '__main__':
    main()
