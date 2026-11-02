'''Summary figures for the README.

  results/summary_benchmarks.png : LZ elastic limit vs soft-2L fit, one marker per benchmark
  results/joint_search.png       : class A soft-2L signal size vs m(N1), with/without sleptons
  results/spectra.png            : mass spectra of key benchmarks relative to N1

Usage: python plot_summary.py  (from scan/, after benchmarks.py, soft2l_fit.py and the joint scripts)
'''

import json
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from summarize import ORDER, verdicts

HERE = os.path.dirname(os.path.abspath(__file__))
RES = os.path.join(HERE, 'results')
BENCH = os.path.join(HERE, '..', 'benchmarks')

SURFACE, INK, INK2, MUTED, GRID = '#fcfcfb', '#0b0b0b', '#52514e', '#b9b8b2', '#e6e5e0'
# reference categorical palette, fixed slot order (dataviz skill)
CLASSES = {'A': ('#2a78d6', 'o', 'A: wino–Higgsino crossing'),
           'BCE': ('#eb6834', 's', 'B/C/E: Higgsino crossing, mixed'),
           'F': ('#1baf7a', 'D', 'F: nearly pure Higgsino crossing'),
           'D1': ('#eda100', '^', 'D1: compressed Higgsino'),
           'D2': ('#e87ba4', 'v', 'D2: compressed wino/bino')}


def style(ax, fig):
    fig.patch.set_facecolor(SURFACE)
    ax.set_facecolor(SURFACE)
    for s in ('top', 'right'):
        ax.spines[s].set_visible(False)
    for s in ('left', 'bottom'):
        ax.spines[s].set_color(MUTED)
    ax.tick_params(colors=INK2, labelsize=8.5)
    ax.grid(color=GRID, lw=0.6)
    ax.set_axisbelow(True)


def klass(name):
    if name.startswith('A'):
        return 'A'
    if name[0] in 'BCE':
        return 'BCE'
    return name[:2] if name.startswith('D') else 'F'


def label(name):
    return (name.split('_')[0] + (' + μ̃' if 'smuons' in name else ' + ẽ' if 'selectrons' in name else ''))


def benchmarks_plot():
    fit = json.load(open(os.path.join(RES, 'soft2l_fit.json')))
    fig, ax = plt.subplots(figsize=(10, 4.8), dpi=160)
    style(ax, fig)
    ax.axvspan(1e-3, 1, color=CLASSES['F'][0], alpha=0.07, lw=0)
    ax.axhspan(-6, -2, color=CLASSES['D2'][0], alpha=0.08, lw=0)
    ax.text(1.2e-3, -5.6, 'explains soft-2L (Δχ² ≤ −2)', color=INK2, fontsize=8)
    ax.text(1.2e-3, 1.55, 'allowed by LZ elastic limit', color=INK2, fontsize=8)
    seen = set()
    for name in ORDER:
        d = json.load(open(os.path.join(BENCH, f'{name}.json')))
        v = verdicts(d, fit[name])
        k = klass(name)
        c, mk, lab = CLASSES[k]
        x = max(v['si_ratio'], 1.2e-3)
        y = v['2l_dchi2']
        ax.scatter(x, y, s=46, marker=mk, color=c if v['mh'] else SURFACE, edgecolors=c, linewidths=1.6,
                   label=None if k in seen else lab, zorder=3)
        seen.add(k)
    # best joint point (class A + left-handed sleptons, m_h ignored)
    ax.scatter(25, -0.66, s=90, marker='*', color=SURFACE, edgecolors=CLASSES['A'][0], linewidths=1.6, zorder=3,
               label='A + ẽ_L/μ̃_L (best joint point, m_h ignored)')
    for txt, xy, off in (('F1, F2, F3 (+ μ̃, ẽ)', (0.012, 0.0), (-10, 10)), ('A, A2, A + μ̃', (1.4, -0.1), (-12, 12)),
                         ('B, C, E', (25, 0.0), (-14, 10)), ('D1', (35, 0.1), (8, 8)),
                         ('A + ẽ_L/μ̃_L', (25, -0.66), (8, -12)), ('D2', (1.5, -4.0), (8, -2)),
                         ('D2 + μ̃', (2.5, -0.2), (6, -12))):
        ax.annotate(txt, xy, xytext=off, textcoords='offset points', fontsize=7.5, color=INK2)
    ax.axvline(1, color=INK2, lw=1, ls=(0, (3, 3)))
    ax.axhline(-2, color=INK2, lw=1, ls=(0, (3, 3)))
    ax.set_xscale('log')
    ax.set_xlim(1e-3, 150)
    ax.set_ylim(-6, 2)
    ax.set_xlabel('LZ elastic SI × Ωh²/0.12, relative to LZ 2024 limit', color=INK2)
    ax.set_ylabel('soft-2L fit: Δχ² vs SM at predicted rate', color=INK2)
    ax.set_title('No benchmark reaches the lower-left corner (explains LZ and soft-2L)', color=INK, fontsize=10, loc='left')
    ax.legend(fontsize=7.5, frameon=False, loc='upper left', bbox_to_anchor=(1.01, 1.0), labelcolor=INK2)
    ax.text(0.99, 0.02, 'hollow: m_h fails (≈102 GeV)', transform=ax.transAxes, ha='right', fontsize=7.5, color=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'summary_benchmarks.png'), facecolor=SURFACE)


def joint_plot():
    a = pd.concat([pd.read_csv(os.path.join(RES, f)) for f in ('joint_loop.csv', 'joint_loop_light.csv')])
    s = pd.read_csv(os.path.join(RES, 'joint_sleptons.csv'))
    fig, ax = plt.subplots(figsize=(8.5, 4.2), dpi=160)
    style(ax, fig)
    # mu_hat = best-fit signal strength in the Higgsino regions; 0 means no signal there
    a = a[a.hino_N > 0]
    ax.scatter(a.mN1, a.hino_muhat, s=26, marker='o', color=CLASSES['A'][0], label='class A, no light sleptons', zorder=3)
    ax.scatter(s.mN1, s.hino_muhat, s=34, marker='D', color=CLASSES['BCE'][0],
               label='class A + ẽ_L/μ̃_L 5–8 GeV above N1', zorder=3)
    ax.axhline(1, color=INK2, lw=1, ls=(0, (3, 3)))
    ax.text(415, 1.08, 'predicted rate = what the data prefer', color=INK2, fontsize=8, ha='right')
    ax.text(415, 0.23, 'signal too large', color=INK2, fontsize=8, ha='right')
    ax.text(415, 9.0, 'signal too small', color=INK2, fontsize=8, ha='right', va='top')
    ax.set_yscale('log')
    ax.set_ylim(0.15, 20)
    ax.set_yticks([0.2, 0.5, 1, 2, 5, 10, 20])
    ax.set_yticklabels(['0.2', '0.5', '1', '2', '5', '10', '20'])
    ax.set_xlabel('m(N1) [GeV] (loop level)', color=INK2)
    ax.set_ylabel('best-fit signal strength μ̂ (SUSY-2018-16-hino)', color=INK2)
    ax.set_title('Class A, m_h ignored: light sleptons bring the soft-2L rate to μ̂ ≈ 1 at m(N1) ≈ 220 GeV',
                 color=INK, fontsize=10, loc='left')
    ax.legend(fontsize=8, frameon=False, loc='upper center', bbox_to_anchor=(0.6, 0.99), labelcolor=INK2)
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'joint_search.png'), facecolor=SURFACE)


def spectra_plot():
    picks = [('A_wino_higgsino_crossing', 'A'), ('F1_pure_higgsino_crossing_smuons', 'F1 + μ̃'),
             ('D2_compressed_wino_bino', 'D2')]
    js = pd.read_csv(os.path.join(RES, 'joint_sleptons.csv')).set_index('id').loc['c027_L5']
    fig, ax = plt.subplots(figsize=(8.5, 4.4), dpi=160)
    style(ax, fig)
    ax.grid(False)
    ax.grid(axis='y', color=GRID, lw=0.6)
    cols = []
    for name, lab in picks:
        d = json.load(open(os.path.join(BENCH, f'{name}.json')))
        m0 = d['mN'][0]
        crossing = d['dm_N2N1_keV'] < 1000
        lv = ([('N1/N2', 0.0)] if crossing else [('N1', 0.0), ('N2', d['mN'][1] - m0)])
        lv += [('N3', d['mN'][2] - m0), ('C1', d['mC'][0] - m0)]
        sl = min(d['m_smuR'], d['m_smuL']) - m0
        if sl < 100:
            lv.append(('μ̃', sl))
        cols.append((f'{lab}\nm(N1) = {m0:.0f}', lv, d['dm_N2N1_keV']))
    cols.append((f"A + ẽ_L/μ̃_L\nm(N1) = {js.mN1:.0f}",
                 [('N1/N2', 0.0), ('N3', js.dN31), ('C1', js.dC1), ('ẽ_L/μ̃_L', js.m_smuL - js.mN1),
                  ('ν̃', js.m_snu - js.mN1)], js.dN21_keV))
    kc = {'N1/N2': CLASSES['A'][0], 'N1': CLASSES['A'][0], 'N2': CLASSES['A'][0], 'N3': CLASSES['BCE'][0],
          'C1': CLASSES['F'][0], 'μ̃': CLASSES['D2'][0], 'ẽ_L/μ̃_L': CLASSES['D2'][0], 'ν̃': CLASSES['D1'][0]}
    for i, (title, levels, dn21) in enumerate(cols):
        placed = []
        for nm, y in sorted(levels, key=lambda t: t[1]):
            ax.hlines(y, i - 0.28, i + 0.28, color=kc[nm], lw=2.5)
            ty = y
            while any(abs(ty - p) < 1.1 for p in placed):
                ty += 1.1
            placed.append(ty)
            ax.text(i + 0.32, ty, nm, va='center', fontsize=7.5, color=INK2)
        if dn21 < 1000:
            ax.text(i, -2.2, f'N2−N1 = {dn21:.0f} keV', ha='center', fontsize=7, color=INK2)
    ax.axhspan(10, 20, color=CLASSES['BCE'][0], alpha=0.08, lw=0)
    ax.text(len(cols) - 0.45, 15, 'soft-2L\nwindow', fontsize=7.5, color=INK2, va='center')
    ax.set_xticks(range(len(cols)))
    ax.set_xticklabels([c[0] for c in cols], fontsize=8, color=INK2)
    ax.set_xlim(-0.6, len(cols) - 0.1)
    ax.set_ylim(-3.5, 25)
    ax.set_ylabel('m − m(N1) [GeV]', color=INK2)
    ax.set_title('Light states of key benchmarks (> 25 GeV above N1 not shown)', color=INK, fontsize=10, loc='left')
    fig.tight_layout()
    fig.savefig(os.path.join(RES, 'spectra.png'), facecolor=SURFACE)


if __name__ == '__main__':
    benchmarks_plot()
    joint_plot()
    spectra_plot()
    print('wrote summary_benchmarks.png, joint_search.png, spectra.png')
