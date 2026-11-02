'''Build the README tables from benchmarks/*.json and results/soft2l_fit.json.

Verdict criteria (see README for the reasoning):
  m_h      : |m_h - 125| < 3 GeV (SPheno)
  LZ       : keV-split N1/N2 pair with N2 - N1 tuned so a 248 keV recoil needs v = 650 km/s,
             AND elastic SI (scaled by Omega h^2 / 0.12) below the LZ 2024 limit,
             approximated as 2.2e-48 cm^2 x m/40 GeV (ratio < 1 ok, 1-3 borderline)
  soft-2L  : best of the SUSY-2018-16 combined fits (exclusive ewk bins / -hino regions):
             dchi2(mu=1) <= -2 explains, -2..0 negligible, > +4 disfavoured
  smuon    : m(mu~) - m(N1) in 3-10 GeV and slepton fit dchi2(mu=1) < 4
  selectron: m(e~) - m(N1) in 30-50 GeV
  LHC      : SModelS r_max < 1

Usage: python summarize.py  (writes results/summary.md)
'''

import glob
import json
import os

HERE = os.path.dirname(os.path.abspath(__file__))
BENCH = os.path.join(HERE, '..', 'benchmarks')
FIT = json.load(open(os.path.join(HERE, 'results', 'soft2l_fit.json')))

ORDER = ['A_wino_higgsino_crossing', 'A_wino_higgsino_crossing_smuons', 'A2_light_wino_higgsino_crossing',
         'B_light_higgsino_crossing', 'B_light_higgsino_crossing_smuons', 'C_heavy_higgsino_crossing',
         'E_higgsino_crossing_selectrons', 'F1_pure_higgsino_crossing', 'F1_pure_higgsino_crossing_smuons',
         'F2_pure_higgsino_crossing_heavy', 'F3_pure_higgsino_crossing_selectrons',
         'D1_compressed_higgsino', 'D1_compressed_higgsino_smuons', 'D2_compressed_wino_bino',
         'D2_compressed_wino_bino_smuons']


def lz_limit(m):
    return 2.2e-48 * m / 40.0


def verdicts(d, fit):
    v = {}
    m1 = d['mN'][0]
    mo = d.get('micromegas', {})
    v['mh'] = abs(d['mh'] - 125) < 3
    si_ratio = mo.get('proton_SI', 0) * 1e-36 * mo.get('Omega', 0.12) / 0.12 / lz_limit(m1)
    v['si_ratio'] = si_ratio
    crossing = d['dm_N2N1_keV'] < 1000
    v['lz'] = 'no' if not crossing else ('yes' if si_ratio < 1 else 'borderline' if si_ratio < 3 else 'elastic')
    best = min(fit['ewk']['dchi2_mu1'], fit['hino']['dchi2_mu1'])
    v['2l_dchi2'] = best
    v['2l'] = 'yes' if best <= -2 else ('disfavoured' if best > 4 else 'negligible' if best < -0.05 else 'no')
    dmu = min(d['m_smuR'], d['m_smuL']) - m1
    dse = min(d['m_selR'], d['m_selL']) - m1
    v['smuon'] = ('disfavoured' if fit['slep']['dchi2_mu1'] > 4 else 'yes') if 3 <= dmu <= 10 else 'no'
    v['selectron'] = 'yes' if 30 <= dse <= 50 else 'no'
    r = max((x['r'] or 0) for x in d.get('smodels', [{'r': 0}]))
    v['r_max'] = r
    return v


SYM = {'yes': '✓', 'no': '–', 'negligible': '≈0', 'borderline': '(✓)', 'elastic': '✗ SI', 'disfavoured': '✗'}


def main():
    rows_bench, rows_verdict = [], []
    for name in ORDER:
        d = json.load(open(os.path.join(BENCH, f'{name}.json')))
        fit = FIT[name]
        v = verdicts(d, fit)
        m = d['mN']
        dn21 = f"{d['dm_N2N1_keV']:.0f} keV" if d['dm_N2N1_keV'] < 1000 else f"{d['dm_N2N1_keV'] / 1e6:.1f} GeV"
        inp = d['inputs']
        sl = []
        if min(d['m_smuR'], d['m_smuL']) < 1000:
            sl.append(f"μ̃_R {d['m_smuR']:.0f}")
        if d['m_selL'] < 1000:
            sl.append(f"ẽ_L {d['m_selL']:.0f}")
        mo = d.get('micromegas', {})
        rows_bench.append(
            f"| [{name}](benchmarks/{name}.slha) | {inp['tanb']:.2f} | {inp['M_1']:.1f} | {inp['M_2']:.1f} | {inp['mu']:.1f} "
            f"| {m[0]:.1f} | {dn21} | {m[2] - m[0]:.1f} | {d['dm_C1N1']:.2f} | {', '.join(sl) or '–'} "
            f"| {d['mh']:.1f} | {mo.get('Omega', float('nan')):.3g} | {v['si_ratio']:.2g} |")
        rows_verdict.append(
            f"| {name} | {SYM[v['lz']]} | {SYM[v['2l']]} ({v['2l_dchi2']:+.1f}) | {SYM[v['smuon']]} | {SYM[v['selectron']]} "
            f"| {'✓' if v['mh'] else '✗ ' + format(d['mh'], '.0f')} | {v['r_max']:.2f} |")
    out = ['| Benchmark | tanβ | M₁ | M₂ | μ | m(N1) | N2−N1 | N3−N1 | C1−N1 | light sleptons | m_h | Ωh² | SI / LZ limit |',
           '|---|---|---|---|---|---|---|---|---|---|---|---|---|', *rows_bench, '',
           '| Benchmark | LZ | soft-2L (Δχ²) | smuon | selectron | m_h | SModelS r_max |',
           '|---|---|---|---|---|---|---|', *rows_verdict]
    with open(os.path.join(HERE, 'results', 'summary.md'), 'w') as fh:
        fh.write('\n'.join(out) + '\n')
    print('\n'.join(out))


if __name__ == '__main__':
    main()
