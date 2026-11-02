'''Does a benchmark explain the ATLAS soft-2L (SUSY-2018-16) excess?

SModelS ships SUSY-2018-16 as 82 efficiency-map signal regions but without a
covariance matrix or pyhf likelihood, so it can only report its single most
sensitive region. Here all exclusive electroweakino bins (SR_ewk_2l_{ee,mm}_
{low,med,high}_{a..h}; a..h = m_ll bins [1,2,3,5,10,20,30,40,60] GeV) are
combined in a simple likelihood: Poisson per bin, Gaussian background
uncertainty profiled per bin, bins treated as uncorrelated. The slepton bins
(SR_slep_*, m_T2 bins) overlap with these and are fitted separately.

Those efficiency maps only contain TChiWZoff (wino/bino-like mass relations) and
TSlepSlep. Higgsino-like spectra (chargino between the neutralinos, or a chargino
compressed into the missing energy) are only covered by the separate
ATLAS-SUSY-2018-16-hino entry: four inclusive regions (2l low/med/high MET and
1l1T, mutually exclusive) with TChiWZoff/TChiZoff/TChiWWoff. That is the 'hino' fit.

Reported per benchmark and bin set:
  dchi2(mu=1)  = -2 ln L(signal as predicted) / L(SM)   (< 0: fits better than SM)
  mu_hat, dchi2(mu_hat): best-fit signal strength and its improvement over the SM

Run from Run3ModelGen/ (needs the SLHA files with XSECTION blocks):
  pixi run bash -c '. build/setup.sh && python ../scan/soft2l_fit.py ../benchmarks/*.slha'
'''

import json
import os
import sys

import numpy as np
from scipy.optimize import minimize_scalar
from scipy.special import gammaln

from smodels.base.model import Model
from smodels.base.physicsUnits import GeV, fb
from smodels.decomposition import decomposer
from smodels.experiment.databaseObj import Database
from smodels.matching.theoryPrediction import theoryPredictionsFor
from smodels.share.models.mssm import BSMList
from smodels.share.models.SMparticles import SMList

LUMI = 139.0


def nll_bin(n, s, b, db):
    '''-ln L for one bin, background nuisance profiled (Gaussian, truncated at 0).'''
    def f(x):
        lam = max(s + x, 1e-9)
        return -(n * np.log(lam) - lam - gammaln(n + 1)) + 0.5 * ((x - b) / db) ** 2
    r = minimize_scalar(f, bounds=(max(1e-6, b - 5 * db), b + 5 * db + 5 * np.sqrt(n + 1)), method='bounded')
    return r.fun


def fit(bins):
    def nll(mu):
        return sum(nll_bin(n, mu * s, b, db) for n, s, b, db in bins)
    n0 = nll(0.0)
    mus = np.concatenate([np.linspace(0, 2, 41), np.linspace(2.5, 20, 36)])
    vals = [nll(m) for m in mus]
    i = int(np.argmin(vals))
    return dict(dchi2_mu1=2 * (nll(1.0) - n0), mu_hat=float(mus[i]), dchi2_muhat=2 * (vals[i] - n0))


def main(files):
    db = Database(os.path.join(os.environ['RUN3MODELGENDIR'], 'official321.pcl'))
    db.selectExpResults(analysisIDs=['ATLAS-SUSY-2018-16', 'ATLAS-SUSY-2018-16-hino'],
                        dataTypes=['efficiencyMap'])
    datasets = {(er.globalInfo.id, ds.getID()): ds.dataInfo for er in db.expResultList for ds in er.datasets}
    out = {}
    for f in files:
        model = Model(BSMparticles=BSMList, SMparticles=SMList)
        model.updateParticles(inputFile=f)
        top = decomposer.decompose(model, 0.005 * fb, massCompress=True, invisibleCompress=True,
                                   minmassgap=5 * GeV, minmassgapISR=1 * GeV)
        sig = {sid: 0.0 for sid in datasets}
        for p in theoryPredictionsFor(db, top, useBestDataset=False, combinedResults=False) or []:
            sig[(p.analysisId(), p.dataset.getID())] += p.xsection.asNumber(fb) * LUMI
        res = {}
        for label, ana, prefix in (('ewk', 'ATLAS-SUSY-2018-16', 'SR_ewk_2l_'),
                                   ('slep', 'ATLAS-SUSY-2018-16', 'SR_slep_2l_'),
                                   ('hino', 'ATLAS-SUSY-2018-16-hino', 'SR_ewk_')):
            bins = [(d.observedN, sig[key], d.expectedBG, d.bgError)
                    for key, d in datasets.items() if key[0] == ana and key[1].startswith(prefix)]
            res[label] = fit(bins)
            res[label]['signal_events'] = sum(b[1] for b in bins)
        # the bins that carry the excess: high-MET, m_ll 10-20 GeV
        res['excess_bins_signal'] = {sid: round(sig[('ATLAS-SUSY-2018-16', sid)], 2)
                                     for sid in ('SR_ewk_2l_mm_high_e', 'SR_ewk_2l_ee_high_e')}
        res['excess_bins_signal']['hino:SR_ewk_2l_med'] = round(sig[('ATLAS-SUSY-2018-16-hino', 'SR_ewk_2l_med')], 2)
        name = os.path.splitext(os.path.basename(f))[0]
        out[name] = res
        print(name, json.dumps(res), flush=True)
    return out, datasets


if __name__ == '__main__':
    out, datasets = main(sys.argv[1:])
    here = os.path.dirname(os.path.abspath(__file__))
    with open(os.path.join(here, 'results', 'soft2l_fit.json'), 'w') as fh:
        json.dump(out, fh, indent=1)
