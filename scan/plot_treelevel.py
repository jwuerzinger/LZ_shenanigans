'''Figure for the README: how close can a third neutralino get to a keV-split N1/N2 pair?

Usage: python plot_treelevel.py  (reads results/treelevel_crossings.csv, writes results/gap_vs_tanb.png)
'''

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

SURFACE, INK, INK2, MUTED = '#fcfcfb', '#0b0b0b', '#52514e', '#b9b8b2'
BLUE = '#2a78d6'

df = pd.read_csv('results/treelevel_crossings.csv')
df['dC'] = df.mC1 - df.mN1
ok = df[df.LZ & (df.dC >= -0.25) & (df.mN1 <= 300) & (df.Z_2L >= 0.1)]

edges = np.geomspace(1, 60, 26)
mid, env = [], []
for lo, hi in zip(edges[:-1], edges[1:]):
    sel = ok[(ok.tanb >= lo) & (ok.tanb < hi)]
    if len(sel):
        mid.append(np.sqrt(lo * hi))
        env.append(sel.dm_2L.min())

fig, ax = plt.subplots(figsize=(7.5, 4.2), dpi=160)
fig.patch.set_facecolor(SURFACE)
ax.set_facecolor(SURFACE)
ax.axhspan(10, 20, color=BLUE, alpha=0.10, lw=0)
ax.text(1.03, 15, 'soft-2L window (10–20 GeV)', color=INK2, va='center', fontsize=8.5)
ax.scatter(ok.tanb, ok.dm_2L, s=3, color=MUTED, alpha=0.5, lw=0, rasterized=True)
ax.plot(mid, env, color=BLUE, lw=2, solid_capstyle='round')
ax.text(mid[-1], env[-1] + 6, 'smallest gap found in the scan', color=INK2, ha='right', fontsize=8.5)
ax.axvline(3, color=INK2, lw=1, ls=(0, (3, 3)))
ax.text(3.15, 185, 'm$_h$ = 125 GeV needs tanβ ≳ 3\n(SPheno, stops ≤ 20 TeV)', color=INK2, fontsize=8.5, va='top')
ax.set_xscale('log')
ax.set_xlim(1, 60)
ax.set_ylim(0, 200)
ax.set_xticks([1, 2, 3, 5, 10, 20, 50])
ax.set_xticklabels(['1', '2', '3', '5', '10', '20', '50'])
ax.set_xlabel('tanβ', color=INK2)
ax.set_ylabel('m(N$_k$) − m(N$_1$) for the closest N$_{3,4}$ [GeV]', color=INK2)
ax.set_title('Tree level: keV-split N1/N2 pair (LZ) with a neutral LSP, m(N1) = 100–300 GeV',
             color=INK, fontsize=10, loc='left')
for s in ('top', 'right'):
    ax.spines[s].set_visible(False)
for s in ('left', 'bottom'):
    ax.spines[s].set_color(MUTED)
ax.tick_params(colors=INK2, labelsize=8.5)
ax.grid(axis='y', color='#e6e5e0', lw=0.6)
ax.set_axisbelow(True)
fig.tight_layout()
fig.savefig('results/gap_vs_tanb.png', facecolor=SURFACE)
print('wrote results/gap_vs_tanb.png')
