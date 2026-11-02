'''Class A + light left-handed sleptons: does a slepton cascade fit soft-2L?

In class A, N3 is ~50% wino, so it couples to left-handed sleptons. With
l~_L (and nu~) a few GeV above N1, N3 -> l~ l -> l l N1 gives same-flavour soft
dileptons with m_ll < m(N3) - m(N1), far more often than N3 -> Z* N1 (~3%).

SModelS has no efficiency maps for these cascades, so before computing cross
sections every electroweakino -> slepton -> N1/N2 chain is folded into an
equivalent direct decay (e.g. N3 -> N1 mu+ mu-) with the product branching ratio.
The rates and mass gaps are kept, the m_ll shape is not (approximation).

Run from Run3ModelGen/:
  pixi run bash -c '. build/setup.sh && python ../scan/joint_sleptons.py <candidates.csv> <ids...>'
'''

import os
import sys
from collections import defaultdict
from multiprocessing import Pool

import pandas as pd
import pyslha

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from r3mg import spheno, signed_neutralinos
from benchmarks import tune_crossing, delta_target, place_sleptons, LOWTB_STOPS

HERE = os.path.dirname(os.path.abspath(__file__))
WORK = os.path.join(HERE, 'work', 'joint_sleptons')
SLEPTONS = {1000011, 1000013, 2000011, 2000013, 1000012, 1000014, 1000015, 2000015, 1000016}
EWKINOS = (1000023, 1000025, 1000035, 1000024, 1000037)
DM_L = (5.0, 8.0)          # m(l~_L) - m(N1) [GeV]


def flatten(slha_in, slha_out):
    '''Fold electroweakino -> slepton -> (N1/N2 + lepton) chains into direct decays.'''
    doc = pyslha.read(slha_in, ignorenomass=True)
    for parent in EWKINOS:
        if parent not in doc.decays:
            continue
        dec = doc.decays[parent]
        merged = defaultdict(float)
        for d in dec.decays:
            slep = [p for p in d.ids if abs(p) in SLEPTONS]
            if not slep:
                merged[tuple(d.ids)] += d.br
                continue
            s = slep[0]
            rest = list(d.ids)
            rest.remove(s)
            for sd in doc.decays[abs(s)].decays:
                ids = [(-p if s < 0 and p not in (1000022, 1000023) else p) for p in sd.ids]
                merged[tuple(sorted(rest + ids, key=abs))] += d.br * sd.br
        dec.decays = [pyslha.Decay(br, len(ids), list(ids), parent) for ids, br in merged.items()]
    pyslha.write(slha_out, doc)


def worker(args):
    cid, row, dm = args
    tag = f'{cid}_L{dm:.0f}'
    wdir = os.path.join(WORK, tag)
    point = dict(tanb=row['tanb'], M_1=row['M_1'], M_2=row['M_2'], mu=row['mu'], AT=0, **LOWTB_STOPS)
    try:
        doc, _ = spheno(point, wdir, 'pre')
        delta = delta_target(abs(signed_neutralinos(doc)[0]))
        tune_crossing(point, 'M_1', delta, wdir)
        for _ in range(2):
            place_sleptons(point, wdir, {'meL': dm})
            tune_crossing(point, 'M_1', delta, wdir)
        doc, slha = spheno(point, wdir, 'final')
        m = sorted(abs(x) for x in signed_neutralinos(doc))
        msnu = abs(doc.blocks['MASS'][1000014])
        if msnu <= m[0]:
            return dict(id=tag, error=f'sneutrino LSP ({msnu:.1f} < {m[0]:.1f})')
        flat = os.path.join(WORK, f'{tag}.slha')
        flatten(slha, flat)
        from smodels.tools import xsecComputer
        from smodels.base.physicsUnits import TeV
        comp = xsecComputer.XSecComputer(maxOrder=xsecComputer.LO, nevents=10000, pythiaVersion=8)
        comp.addXSecToFile(comp.compute(sqrts=13 * TeV, slhafile=flat), flat)
        n3 = doc.decays[1000025]
        br_ll = sum(d.br for d in n3.decays if any(abs(p) in (1000011, 1000013) for p in d.ids))
        return dict(id=tag, **point, mN1=m[0], dN21_keV=(m[1] - m[0]) * 1e6, dN31=m[2] - m[0],
                    dC1=abs(doc.blocks['MASS'][1000024]) - m[0],
                    m_smuL=abs(doc.blocks['MASS'][1000013]), m_snu=msnu, BR_N3_to_slepL=br_ll,
                    slha=flat, spheno_slha=slha)
    except Exception as exc:
        return dict(id=tag, error=str(exc))


if __name__ == '__main__':
    cfile, ids = sys.argv[1], sys.argv[2:]
    src = pd.read_csv(os.path.join(HERE, 'results', cfile)).set_index('id')
    jobs = [(i, src.loc[i], dm) for i in ids for dm in DM_L]
    os.makedirs(WORK, exist_ok=True)
    with Pool(6) as pool:
        res = pool.map(worker, jobs)
    ok = [r for r in res if 'error' not in r]
    for r in res:
        if 'error' in r:
            print('  failed', r['id'], r['error'][:120])
    from soft2l_fit import main as fit
    fits, _ = fit([r['slha'] for r in ok])
    for r in ok:
        f = fits[r['id']]
        for k in ('ewk', 'hino', 'slep'):
            r[f'{k}_N'], r[f'{k}_dchi2'], r[f'{k}_muhat'] = (f[k]['signal_events'], f[k]['dchi2_mu1'], f[k]['mu_hat'])
    df = pd.DataFrame(ok).sort_values('ewk_dchi2')
    out = os.path.join(HERE, 'results', 'joint_sleptons.csv')
    df.to_csv(out, index=False, mode='a', header=not os.path.exists(out))
    print(df[['id', 'tanb', 'mN1', 'dN21_keV', 'dN31', 'dC1', 'm_smuL', 'm_snu', 'BR_N3_to_slepL',
              'ewk_N', 'ewk_dchi2', 'ewk_muhat', 'hino_N', 'hino_dchi2', 'slep_N', 'slep_dchi2']].round(3).to_string())
