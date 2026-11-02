"""Create a fully synthetic, reproducible A/B funnel dataset."""
import csv
from pathlib import Path
import numpy as np

HERE = Path(__file__).resolve().parent

def main():
    rng = np.random.default_rng(20261102)
    n = 24000
    variants = rng.choice(['A', 'B'], size=n, p=[0.5, 0.5])
    segment = rng.choice(['new', 'returning'], size=n, p=[0.78, 0.22])
    device = rng.choice(['mobile', 'desktop'], size=n, p=[0.72, 0.28])
    # User-level funnel: registration completed implies started.
    start_prob = 0.55 + 0.025 * (variants == 'B') + 0.04 * (device == 'desktop')
    started = rng.random(n) < start_prob
    finish_prob = 0.32 + 0.045 * (variants == 'B') + 0.04 * (segment == 'returning')
    completed = started & (rng.random(n) < finish_prob)
    output = HERE / 'data' / 'experiment.csv'
    with output.open('w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(['user_id', 'variant', 'user_type', 'device', 'started', 'completed'])
        for i in range(n):
            writer.writerow([f'U-{i+1:06d}',variants[i],segment[i],device[i],int(started[i]),int(completed[i])])
    print(f'Generated {n} synthetic users: {output}')

if __name__ == '__main__':
    main()
