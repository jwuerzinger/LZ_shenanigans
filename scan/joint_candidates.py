'''Targeted tree-level scan for joint LZ + soft-2L candidates (class A), ignoring m_h.

Class A: wino within ~25 GeV of mu with M2*mu < 0, M1*mu > 0, tanb ~ 1-1.4. For each
sample (tanb, mu, M2) solve for M1 at the N1/N2 crossing and keep points with
  m(N1) >= 140 GeV (LZ kinematics), m(C1) > m(N1), a Z-N1-N2 coupling,
  and a neutralino N3/N4 8-25 GeV above N1 that couples to N1/N2 via the Z.

Usage: python joint_candidates.py [n] -> results/joint_candidates.csv
'''

import sys
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from neutralino import crossing_function
from treelevel_scan import describe

rng = np.random.default_rng(7)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 40000
MIN_M = float(sys.argv[2]) if len(sys.argv) > 2 else 140
OUT = sys.argv[3] if len(sys.argv) > 3 else 'results/joint_candidates.csv'
rows = []
for _ in range(N):
    tb = rng.uniform(1.0, 1.4)
    s = rng.choice([-1, 1])
    mu = s * rng.uniform(80 if MIN_M < 140 else 140, 400)
    M2 = -s * (abs(mu) + rng.uniform(-60, 60))
    grid = s * np.geomspace(50, 3000, 300)          # M1 has the sign of mu
    f, ok = crossing_function(grid, M2, mu, tb)
    for i in np.where((np.sign(f[:-1]) != np.sign(f[1:])) & ok[:-1] & ok[1:])[0]:
        try:
            M1 = brentq(lambda x: crossing_function(x, M2, mu, tb)[0], grid[i], grid[i + 1], xtol=1e-10)
        except ValueError:
            continue
        r = describe(M1, M2, mu, tb, 'joint')
        if (r['mN2'] - r['mN1'] < 1e-4 and r['mN1'] >= MIN_M and r['mC1'] > r['mN1']
                and r['O12'] >= 0.1 and 8 <= r['dm_2L'] <= 25 and r['Z_2L'] >= 0.1):
            rows.append(r)
df = pd.DataFrame(rows)
df['dC'] = df.mC1 - df.mN1
df.to_csv(OUT, index=False)
print(len(df), 'candidates')
print(df[['tanb', 'mN1', 'dm_2L', 'dC', 'O12', 'Z_2L', 'hN1']].describe().round(3).to_string())
