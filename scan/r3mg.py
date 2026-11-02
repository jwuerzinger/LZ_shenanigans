'''Thin wrapper around Run3ModelGen's pipeline steps for single benchmark points.

Must run inside the Run3ModelGen pixi env with build/setup.sh sourced, e.g.
  cd Run3ModelGen && pixi run bash -c '. build/setup.sh && python ../scan/<script>.py'
'''

import os
import pyslha
from Run3ModelGen.steps import (run_prep_input, run_SPheno, run_micromegas, run_superiso,
                                run_gm2calc, run_SModelS)

R3MG = os.environ['RUN3MODELGENDIR'].rstrip('/')
RAW = os.path.join(R3MG, 'source/Run3ModelGen/data/raw.slha')
SMODELS_INI = os.path.join(R3MG, 'source/Run3ModelGen/data/SModelS_parameters.ini')

# pMSSM-19 defaults for everything the excesses don't care about: decoupled
# coloured sector, heavy stops for m_h at low tanb, heavy staus/sleptons.
DEFAULTS = dict(M_3=4000, AT=0, Ab=0, Atau=0, mA=3000, meL=3000, mtauL=3000, meR=3000,
                mtauR=3000, mqL1=5000, mqL3=5000, muR=5000, mtR=5000, mdR=5000, mbR=5000)

NEUTRALINOS = (1000022, 1000023, 1000025, 1000035)


def spheno(point, workdir, tag='sp'):
    '''Run prep_input + SPheno; return (pyslha doc or None, path).'''
    os.makedirs(workdir, exist_ok=True)
    p = {**DEFAULTS, **point}
    inp, out, log = (os.path.join(workdir, f'{tag}.{x}') for x in ('in.slha', 'slha', 'log'))
    run_prep_input(p, RAW, inp)
    if not run_SPheno(inp, out, log, RAW):
        return None, out
    return pyslha.read(out, ignorenomass=True), out


def signed_neutralinos(doc):
    '''Signed neutralino pole masses ordered by |mass|.'''
    return sorted((doc.blocks['MASS'][pid] for pid in NEUTRALINOS), key=abs)


def crossing(doc):
    '''|lightest positive| - |lightest negative| neutralino mass (GeV); 0 at the N1/N2 crossing.'''
    m = signed_neutralinos(doc)
    pos = min(x for x in m if x > 0) if any(x > 0 for x in m) else 1e9
    neg = min(-x for x in m if x < 0) if any(x < 0 for x in m) else 1e9
    return pos - neg
