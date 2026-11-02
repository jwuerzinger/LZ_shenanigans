'''Stage B: loop-level benchmarks with the Run3ModelGen tool chain.

For each benchmark (tree-level seed from treelevel_scan.py):
  1. tune A_t so that SPheno's m_h is as close to 125 GeV as the stop masses allow
  2. optionally place the sleptons at a target splitting above N1
  3. tune the crossing parameter (M1 or M2) so that SPheno's loop-level
     m(N2) - m(N1) equals the LZ target delta (keV)
  4. run micrOMEGAs, gm2calc and SModelS (13 TeV LO xsecs via Pythia8)
Writes benchmarks/<name>.slha and benchmarks/<name>.json.

Run from Run3ModelGen/:
  pixi run bash -c '. build/setup.sh && python ../scan/benchmarks.py [name ...]'
'''

import glob
import json
import os
import runpy
import shutil
import sys

import numpy as np
import pyslha
from scipy.optimize import brentq

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3mg import (spheno, signed_neutralinos, crossing, run_micromegas, run_gm2calc,
                  run_SModelS, SMODELS_INI)

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.path.join(HERE, '..', 'benchmarks')
WORK = os.path.join(HERE, 'work')

M_XE = 131.29 * 0.9315      # GeV
E_R = 248e-6                # GeV, LZ event
V_TARGET = 650.0            # km/s needed to produce the 248 keV recoil
C_KMS = 299792.458


def delta_target(m_dm):
    '''Splitting (GeV) for which a 248 keV Xe recoil needs v_min = V_TARGET.'''
    mu = m_dm * M_XE / (m_dm + M_XE)
    d = min(V_TARGET / C_KMS * np.sqrt(2 * M_XE * E_R) - M_XE * E_R / mu, 350e-6)
    if d <= 10e-6:
        raise RuntimeError(f'm(N1) = {m_dm:.0f} GeV too light: a 248 keV recoil needs v > {V_TARGET} km/s even for delta = 0')
    return d


def vmin_kms(m_dm, delta):
    mu = m_dm * M_XE / (m_dm + M_XE)
    return (M_XE * E_R / mu + delta) / np.sqrt(2 * M_XE * E_R) * C_KMS


# At tanb ~ 1.2, 20 TeV stops break EWSB in SPheno (|mu|^2 < 0) and m_h stays
# below ~105 GeV anyway, so class A uses 3 TeV stops and simply fails m_h.
LOWTB_STOPS = dict(mqL3=3000, mtR=3000, mbR=3000)
STOPS = dict(mqL3=4000, mtR=4000, mbR=4000)
MID_STOPS = dict(mqL3=8000, mtR=8000, mbR=8000)   # tanb ~ 5 needs heavier stops for m_h

# Tree-level seeds (results/treelevel_crossings.csv rows / analytic, see README).
# 'cross' is the parameter tuned to sit at the N1/N2 crossing; None = no crossing.
BENCHMARKS = {
    'A_wino_higgsino_crossing': dict(seed=dict(tanb=1.230, M_1=311.072, M_2=-209.0, mu=236.058, **LOWTB_STOPS), cross='M_2',
                                     gap=dict(param='M_1', k=3, target=17.5)),
    'A2_light_wino_higgsino_crossing': dict(seed=dict(tanb=1.185, M_1=-231.636, M_2=146.636, mu=-157.682, **LOWTB_STOPS), cross='M_1',
                                            gap=dict(param='M_2', k=3, target=16.0)),
    'B_light_higgsino_crossing': dict(seed=dict(tanb=10.214, M_1=205.871, M_2=-315.448, mu=164.797, **STOPS), cross='M_2'),
    'C_heavy_higgsino_crossing': dict(seed=dict(tanb=10.361, M_1=656.713, M_2=-817.471, mu=572.376, **STOPS), cross='M_1'),
    'D1_compressed_higgsino': dict(seed=dict(tanb=10.0, M_1=407.4, M_2=814.7, mu=200.0, **STOPS), cross=None),
    'D2_compressed_wino_bino': dict(seed=dict(tanb=10.0, M_1=200.0, M_2=200.0, mu=1000.0, **STOPS), cross=None,
                                    gap=dict(param='M_2', k=2, target=15.0)),
}
# Slepton variants. In pMSSM-19 the first two generations are degenerate, so
# selectrons always come with smuons. Smuon excess (dm 3-10 GeV): only the
# right-handed sleptons light, at m(N1) + 6 GeV (L+R at once is excluded by
# SUSY-2018-16). Slepton variants use m_A = 1 TeV: with m_A = 3 TeV the
# hypercharge S-term keeps the right-handed slepton pole mass above ~200 GeV. Selectron excess (best fit 375/335 GeV): a heavier Higgsino
# crossing at m(N1) ~ 335-350 GeV with R/L sleptons at m(N1) + 35/45 GeV.
for base in ('A_wino_higgsino_crossing', 'B_light_higgsino_crossing', 'D1_compressed_higgsino',
             'D2_compressed_wino_bino'):
    b = BENCHMARKS[base]
    BENCHMARKS[base + '_smuons'] = dict(b, seed=dict(b['seed'], mA=1000), sleptons=dict(meR=6.0))
BENCHMARKS['E_higgsino_crossing_selectrons'] = dict(
    seed=dict(tanb=10.118, M_1=414.037, M_2=-556.697, mu=346.653, mA=1000, **STOPS), cross='M_1',
    sleptons=dict(meR=35.0, meL=45.0))   # split by 10 GeV so SPheno's L/R labels stay put
# B's light N1 (166 GeV) sits below the right-handed slepton floor (~180 GeV) set by the
# hypercharge S-term from the heavy left-handed sleptons; splitting the staus compensates.
BENCHMARKS['B_light_higgsino_crossing_smuons']['seed'].update(mtauL=2000, mtauR=4500)

# Elastic-safe ("blind spot") versions: nearly pure Higgsino crossings with TeV
# gauginos at tanb ~ 5, where the h-N1-N1 coupling is ~30x smaller than in B/C/E.
BENCHMARKS['F1_pure_higgsino_crossing'] = dict(
    seed=dict(tanb=5.0474, M_1=793.3918, M_2=-2242.597, mu=181.942, **MID_STOPS), cross='M_1')
BENCHMARKS['F1_pure_higgsino_crossing_smuons'] = dict(
    seed=dict(tanb=5.0474, M_1=793.3918, M_2=-2242.597, mu=181.942, mA=1000, mtauL=2000, mtauR=4500, **MID_STOPS),
    cross='M_1', sleptons=dict(meR=6.0))
BENCHMARKS['F2_pure_higgsino_crossing_heavy'] = dict(
    seed=dict(tanb=5.0822, M_1=-1423.8878, M_2=3507.8408, mu=-510.3254, **MID_STOPS), cross='M_1')
BENCHMARKS['F3_pure_higgsino_crossing_selectrons'] = dict(
    seed=dict(tanb=5.0323, M_1=-1138.9986, M_2=2994.8354, mu=-342.3223, mA=1000, **MID_STOPS), cross='M_1',
    sleptons=dict(meR=40.0))   # M_2 ~ 3 TeV lifts the left-handed sleptons > 500 GeV: right-handed only


def masses(doc, *pids):
    return [abs(doc.blocks['MASS'][p]) for p in pids]


def tune_At(point, wdir):
    '''Scan X_t/M_S and keep the value closest to m_h = 125 GeV.'''
    ms = point['mqL3']
    best = None
    for xt in np.linspace(-2.5, 2.5, 21):
        p = {**point, 'AT': xt * ms + point['mu'] / point['tanb']}
        doc, _ = spheno(p, wdir, 'at')
        if doc is None:
            continue
        mh = doc.blocks['MASS'][25]
        if best is None or abs(mh - 125) < abs(best[1] - 125):
            best = (p['AT'], mh)
    point['AT'] = best[0]
    return best[1]


def place_sleptons(point, wdir, targets):
    '''Iterate soft masses (in m^2) so slepton pole masses sit at m(N1) + target (GeV).'''
    pids = {'meR': 2000013, 'meL': 1000013}
    doc, _ = spheno(point, wdir, 'sl')
    mn1 = abs(signed_neutralinos(doc)[0])
    for k, dm in targets.items():
        if point.get(k, 3000) >= 2999:
            point[k] = mn1 + dm
    for _ in range(10):
        doc, _ = spheno(point, wdir, 'sl')
        if doc is None:
            raise RuntimeError(f'SPheno failed while placing sleptons at {point}')
        mn1 = abs(signed_neutralinos(doc)[0])
        errs = {k: abs(doc.blocks['MASS'][pids[k]]) ** 2 - (mn1 + dm) ** 2 for k, dm in targets.items()}
        if all(abs(e) < 2 * 0.05 * (mn1 + targets[k]) for k, e in errs.items()):
            return
        for k, e in errs.items():
            m2 = point[k] ** 2 - e
            if m2 <= 0:
                raise RuntimeError(f'slepton target m(N1)+{targets[k]} GeV unreachable via {k} (needs m^2 < 0)')
            point[k] = np.sqrt(m2)
    raise RuntimeError('slepton placement did not converge')


def tune_crossing(point, key, delta, wdir):
    '''Root-find point[key] so that the loop-level crossing function equals +delta.'''
    cache = {}

    def f(x):
        if x not in cache:
            doc, _ = spheno({**point, key: x}, wdir, 'cr')
            cache[x] = np.nan if doc is None else crossing(doc) - delta
        return cache[x]

    x0 = point[key]
    f0 = f(x0)
    step = 0.02 * abs(x0)
    lo = hi = None
    for i in range(1, 40):
        for x in (x0 + i * step, x0 - i * step):
            fx = f(x)
            if np.isfinite(fx) and np.isfinite(f0) and np.sign(fx) != np.sign(f0):
                lo, hi = sorted((x0, x)) if x > x0 else sorted((x, x0))
                break
            if np.isfinite(fx) and not np.isfinite(f0):
                x0, f0 = x, fx
        if lo is not None:
            break
    if lo is None:
        raise RuntimeError(f'no loop-level crossing found for {key} near {point[key]}')
    # bisect; SPheno occasionally fails at isolated points, so step around NaNs
    flo = f(lo)
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        fm = f(mid)
        j = 1
        while not np.isfinite(fm) and j < 6:
            mid = lo + (hi - lo) * (0.5 + 0.07 * j * (-1) ** j)
            fm = f(mid)
            j += 1
        if not np.isfinite(fm):
            raise RuntimeError(f'SPheno fails throughout [{lo}, {hi}]')
        if np.sign(fm) == np.sign(flo):
            lo, flo = mid, fm
        else:
            hi = mid
        if hi - lo < 1e-7:
            break
    point[key] = 0.5 * (lo + hi)


def tune_gap(point, spec, delta, wdir):
    '''Tune spec['gap']['param'] so that m(N_k) - m(N1) = target, re-tuning the crossing inside.'''
    g = spec['gap']
    k, key, target = g['k'], g['param'], g['target']

    def h(x):
        p = {**point, key: x}
        if spec['cross']:
            tune_crossing(p, spec['cross'], delta, wdir)
        doc, _ = spheno(p, wdir, 'gap')
        m = sorted(abs(v) for v in signed_neutralinos(doc))
        h.last = p
        return m[k - 1] - m[0] - target

    x0 = point[key]
    tried = {x0: h(x0)}
    h0 = tried[x0]
    x1 = None
    for i in range(1, 30):
        x = x0 * (1 + 0.01 * i * (1 if i % 2 else -1))
        try:
            tried[x] = h(x)
        except RuntimeError:
            continue
        if np.sign(tried[x]) != np.sign(h0):
            x1 = x
            break
    if x1 is not None:
        brentq(h, *sorted((x0, x1)), xtol=1e-4)
        point.update(h.last)
        return
    # no exact root: take the closest approach if it stays inside the 10-20 GeV window
    xb = min(tried, key=lambda x: abs(tried[x]))
    if abs(tried[xb]) > g.get('tolerance', 2.5):
        raise RuntimeError(f'cannot reach gap target with {key}: closest {tried[xb] + target:.2f} GeV')
    h(xb)
    point.update(h.last)


def smodels_summary(pyfile):
    out = runpy.run_path(pyfile)['smodelsOutput']
    res = []
    for r in out.get('ExptRes', []):
        d = dict(id=r['AnalysisID'], sr=r.get('DataSetID'), txnames=r.get('TxNames'),
                 r=r.get('r'), r_exp=r.get('r_expected'))
        if r.get('nll') is not None and r.get('nll_SM') is not None:
            # -2 ln(L_BSM / L_SM) in SModelS' most sensitive signal region:
            # negative = the benchmark fits the data better than the SM alone
            d['dchi2_vs_SM'] = 2 * (r['nll'] - r['nll_SM'])
        res.append(d)
    res.sort(key=lambda d: -(d['r'] or 0))
    return res


def run(name, spec):
    wdir = os.path.join(WORK, name)
    shutil.rmtree(wdir, ignore_errors=True)
    os.makedirs(wdir)
    point = dict(spec['seed'])
    summary = dict(name=name)

    summary['mh_best'] = tune_At(point, wdir)
    delta = None

    def tune_electroweakinos():
        nonlocal delta
        if spec['cross']:
            doc, _ = spheno(point, wdir, 'pre')
            delta = delta_target(abs(signed_neutralinos(doc)[0]))
        if 'gap' in spec:
            tune_gap(point, spec, delta, wdir)
        elif spec['cross']:
            tune_crossing(point, spec['cross'], delta, wdir)

    tune_electroweakinos()
    if 'sleptons' in spec:
        for _ in range(2):          # sleptons and electroweakinos feed back on each other
            place_sleptons(point, wdir, spec['sleptons'])
            tune_electroweakinos()
    if spec['cross']:
        tune_crossing(point, spec['cross'], delta, wdir)   # crossing always last
        summary['delta_target_keV'] = delta * 1e6

    doc, slha = spheno(point, wdir, 'final')
    if doc is None:
        raise RuntimeError('final SPheno run failed')
    n = signed_neutralinos(doc)
    mN = [abs(x) for x in n]
    mC1, mC2 = masses(doc, 1000024, 1000037)
    summary.update(
        inputs=point,
        mh=doc.blocks['MASS'][25],
        mN=mN, mC=[mC1, mC2],
        dm_N2N1_keV=(mN[1] - mN[0]) * 1e6,
        dm_N3N1=mN[2] - mN[0], dm_C1N1=mC1 - mN[0],
        m_smuR=abs(doc.blocks['MASS'][2000013]), m_smuL=abs(doc.blocks['MASS'][1000013]),
        m_selR=abs(doc.blocks['MASS'][2000011]), m_selL=abs(doc.blocks['MASS'][1000011]),
    )
    if spec['cross']:
        summary['vmin_248keV_kms'] = vmin_kms(mN[0], mN[1] - mN[0])
    nmix = doc.blocks['NMIX']
    summary['N1_composition'] = dict(bino=nmix[1, 1] ** 2, wino=nmix[1, 2] ** 2,
                                     higgsino=nmix[1, 3] ** 2 + nmix[1, 4] ** 2)
    o12 = nmix[1, 3] * nmix[2, 3] - nmix[1, 4] * nmix[2, 4]
    summary['Z_N1N2_rel_pure_higgsino'] = abs(o12)
    summary['decays'] = {str(pid): sorted(([round(d.br, 4), list(d.ids)] for d in doc.decays[pid].decays),
                                          reverse=True)[:4]
                         for pid in (1000023, 1000025, 1000024, 2000013, 1000013) if pid in doc.decays}

    # micrOMEGAs: relic density + elastic cross sections
    mo_raw, mo_csv = os.path.join(wdir, 'mo.txt'), os.path.join(wdir, 'mo.csv')
    if run_micromegas(slha, mo_raw, mo_csv):
        mo = dict(l.strip().split(',') for l in open(mo_csv) if ',' in l)
        mo.pop('Variable', None)
        summary['micromegas'] = {k: float(v) for k, v in mo.items()}
    gm2 = os.path.join(wdir, 'gm2.slha')
    if run_gm2calc(slha, gm2):
        try:
            summary['delta_amu'] = pyslha.read(gm2, ignorenomass=True).blocks['GM2CalcOutput'][0]
        except Exception:
            pass

    # SModelS on a copy (the xsecs get appended to the copy only)
    smo_dir = os.path.join(wdir, 'smodels')
    os.makedirs(smo_dir, exist_ok=True)
    xs = os.path.join(wdir, 'final_xsec.slha')
    if run_SModelS(slha, smo_dir, SMODELS_INI, xsec_dest=xs, nevents=20000, include_nll=False):
        pyf = glob.glob(os.path.join(smo_dir, '*.py'))
        if pyf:
            summary['smodels'] = smodels_summary(pyf[0])

    os.makedirs(OUTDIR, exist_ok=True)
    shutil.copy2(xs if os.path.exists(xs) else slha, os.path.join(OUTDIR, f'{name}.slha'))
    with open(os.path.join(OUTDIR, f'{name}.json'), 'w') as fh:
        json.dump(summary, fh, indent=1, default=float)
    print(f"[{name}] mN={np.round(mN, 4)} dN2N1={summary['dm_N2N1_keV']:.1f} keV "
          f"dN3N1={summary['dm_N3N1']:.2f} dC1N1={summary['dm_C1N1']:.3f} mh={summary['mh']:.2f} "
          f"Oh2={summary.get('micromegas', {}).get('Omega')}", flush=True)


if __name__ == '__main__':
    names = sys.argv[1:] or list(BENCHMARKS)
    for nm in names:
        try:
            run(nm, BENCHMARKS[nm])
        except Exception as exc:
            print(f'[{nm}] FAILED: {exc}', flush=True)
