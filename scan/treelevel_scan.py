'''Stage A: tree-level scan for electroweakino spectra that can fit LZ and soft-2L.

For each sampled (tanb, mu, M_other) find every value of the scanned gaugino mass
(M1 or M2) at which the lightest CP-even and CP-odd neutralinos cross, i.e. where
N1 and N2 are exactly degenerate. Any keV splitting delta is then obtained by
moving slightly off the crossing, so delta is effectively a free parameter here.

Criteria (see README):
  LZ      : m(N1) >= 100 GeV and |O_12| >= 0.1 (Z-mediated N1 -> N2 upscatter)
  soft-2L : some N_k (k >= 3) with 10 <= m(N_k) - m(N1) <= 20 GeV that couples to
            N1 or N2 via the Z (|O_k1| or |O_k2| >= 0.1), and m(N1) <= 300 GeV

Usage: python treelevel_scan.py [n_samples_per_mode] [outfile.csv]
'''

import sys
import numpy as np
import pandas as pd
from scipy.optimize import brentq

from neutralino import (neutralinos, chargino_masses, crossing_function, z_coupling,
                        h_coupling, composition)

rng = np.random.default_rng(20261102)
N = int(sys.argv[1]) if len(sys.argv) > 1 else 20000
OUT = sys.argv[2] if len(sys.argv) > 2 else 'results/treelevel_crossings.csv'

# grid for the solved-for gaugino mass, both signs
half = np.geomspace(20, 5000, 500)
GRID = np.concatenate([-half[::-1], half])


def describe(M1, M2, mu, tb, mode):
    w, v = neutralinos(M1, M2, mu, tb)
    m = np.abs(w)
    row = dict(mode=mode, tanb=tb, M1=M1, M2=M2, mu=mu,
               mN1=m[0], mN2=m[1], mN3=m[2], mN4=m[3],
               mC1=chargino_masses(M2, mu, tb)[0], mC2=chargino_masses(M2, mu, tb)[1],
               O12=abs(z_coupling(v, 0, 1)), hN1=h_coupling(v, 0, tb))
    for i in range(3):
        for k, val in composition(v, i).items():
            row[f'N{i+1}_{k}'] = val
    # heavier neutralinos that could give the soft-2L signal
    best = None
    for k in (2, 3):
        gap = m[k] - m[0]
        zc = max(abs(z_coupling(v, k, 0)), abs(z_coupling(v, k, 1)))
        if best is None or abs(gap - 15) < abs(best[0] - 15):
            best = (gap, zc, k + 1)
    row['dm_2L'], row['Z_2L'], row['k_2L'] = best
    row['sign_M1mu'] = int(np.sign(M1 * mu))
    row['sign_M2mu'] = int(np.sign(M2 * mu))
    return row


def scan(mode):
    rows = []
    tb = np.exp(rng.uniform(np.log(1.0), np.log(60), N))
    mu = rng.uniform(100, 800, N) * rng.choice([-1, 1], N)
    other = rng.uniform(100, 5000, N) * rng.choice([-1, 1], N)
    for t, u, o in zip(tb, mu, other):
        if mode == 'M1':
            f, ok = crossing_function(GRID, o, u, t)
            fun = lambda x: crossing_function(x, o, u, t)[0]
        else:
            f, ok = crossing_function(o, GRID, u, t)
            fun = lambda x: crossing_function(o, x, u, t)[0]
        idx = np.where((np.sign(f[:-1]) != np.sign(f[1:])) & ok[:-1] & ok[1:]
                       & (np.sign(GRID[:-1]) == np.sign(GRID[1:])))[0]
        for i in idx:
            try:
                x = brentq(fun, GRID[i], GRID[i + 1], xtol=1e-10)
            except ValueError:
                continue
            M1, M2 = (x, o) if mode == 'M1' else (o, x)
            r = describe(M1, M2, u, t, mode)
            if r['mN2'] - r['mN1'] < 1e-4:     # genuine crossing of N1/N2
                rows.append(r)
    return rows


if __name__ == '__main__':
    rows = scan('M1') + scan('M2')
    df = pd.DataFrame(rows)
    df['LZ'] = (df.mN1 >= 100) & (df.O12 >= 0.1)
    df['soft2L'] = (df.dm_2L >= 10) & (df.dm_2L <= 20) & (df.Z_2L >= 0.1) & (df.mN1 <= 300)
    df.to_csv(OUT, index=False)
    print(f"{len(df)} crossings; LZ-capable: {df.LZ.sum()}; LZ+soft2L: {(df.LZ & df.soft2L).sum()}")
