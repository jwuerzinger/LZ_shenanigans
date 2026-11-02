'''Loop-level pass over joint LZ + soft-2L candidates (class A, m_h ignored).

Picks a stratified subset of results/joint_candidates.csv, tunes the N1/N2 crossing
in SPheno (parallel workers), adds 13 TeV LO cross sections, then runs the
combined SUSY-2018-16 fit on all of them in one process.

Run from Run3ModelGen/:
  pixi run bash -c '. build/setup.sh && python ../scan/joint_loop.py [n_workers] [candidates.csv] [tag]'
Writes scan/work/<tag>/<id>.slha and scan/results/<tag>.csv (tag defaults to joint_loop)
'''

import json
import os
import sys
from multiprocessing import Pool

import numpy as np
import pandas as pd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3mg import spheno, signed_neutralinos
from benchmarks import tune_crossing, delta_target, LOWTB_STOPS

HERE = os.path.dirname(os.path.abspath(__file__))
TAG = sys.argv[3] if len(sys.argv) > 3 else 'joint_loop'
WORK = os.path.join(HERE, 'work', TAG)


def pick(df, per_cell=2):
    df = df.assign(score=df.Z_2L * df.O12,
                   mbin=pd.qcut(df.mN1, 3),
                   gbin=pd.cut(df.dm_2L, [8, 14, 20, 25]),
                   cbin=pd.cut(df.dC, [0, 5, 100]))
    return (df.sort_values('score', ascending=False)
              .groupby(['mbin', 'gbin', 'cbin'], observed=True).head(per_cell)
              .reset_index(drop=True))


def worker(args):
    i, row = args
    wdir = os.path.join(WORK, f'c{i:03d}')
    point = dict(tanb=row['tanb'], M_1=row['M1'], M_2=row['M2'], mu=row['mu'], AT=0, **LOWTB_STOPS)
    try:
        doc, _ = spheno(point, wdir, 'pre')
        delta = delta_target(abs(signed_neutralinos(doc)[0]))
        tune_crossing(point, 'M_1', delta, wdir)
        doc, slha = spheno(point, wdir, 'final')
        from smodels.tools import xsecComputer
        from smodels.base.physicsUnits import TeV
        comp = xsecComputer.XSecComputer(maxOrder=xsecComputer.LO, nevents=10000, pythiaVersion=8)
        xs = comp.compute(sqrts=13 * TeV, slhafile=slha)
        comp.addXSecToFile(xs, slha)
        out = os.path.join(WORK, f'c{i:03d}.slha')
        os.replace(slha, out)
        m = sorted(abs(x) for x in signed_neutralinos(doc))
        return dict(id=f'c{i:03d}', **point, mN1=m[0], dN21_keV=(m[1] - m[0]) * 1e6, dN31=m[2] - m[0],
                    dC1=abs(doc.blocks['MASS'][1000024]) - m[0], slha=out)
    except Exception as exc:
        return dict(id=f'c{i:03d}', error=str(exc))


if __name__ == '__main__':
    nproc = int(sys.argv[1]) if len(sys.argv) > 1 else 6
    cfile = sys.argv[2] if len(sys.argv) > 2 else 'joint_candidates.csv'
    cands = pick(pd.read_csv(os.path.join(HERE, 'results', cfile)))
    os.makedirs(WORK, exist_ok=True)
    with Pool(nproc) as pool:
        res = pool.map(worker, list(cands.iterrows()))
    ok = [r for r in res if 'error' not in r]
    print(f'{len(ok)}/{len(res)} candidates converged', flush=True)
    for r in res:
        if 'error' in r:
            print('  failed', r['id'], r['error'][:100])

    from soft2l_fit import main as fit
    fits, _ = fit([r['slha'] for r in ok])
    for r in ok:
        f = fits[r['id']]
        r.update({f'{k}_dchi2': f[k]['dchi2_mu1'] for k in ('ewk', 'hino', 'slep')})
        r.update({f'{k}_N': f[k]['signal_events'] for k in ('ewk', 'hino')})
        r.update({f'{k}_muhat': f[k]['mu_hat'] for k in ('ewk', 'hino')})
        r['best_dchi2'] = min(r['ewk_dchi2'], r['hino_dchi2'])
    df = pd.DataFrame(ok).sort_values('best_dchi2')
    df.to_csv(os.path.join(HERE, 'results', f'{TAG}.csv'), index=False)
    print(df[['id', 'tanb', 'mN1', 'dN21_keV', 'dN31', 'dC1', 'ewk_N', 'ewk_dchi2', 'hino_N', 'hino_dchi2',
              'hino_muhat', 'best_dchi2']].round(3).to_string())
