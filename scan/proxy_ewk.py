'''Rough exclusive-bin (SR_ewk_2l) recast for class A spectra.

In class A the chargino sits only a few GeV above N1, so SModelS compresses it into
the missing energy and C1 N3 production never matches the TChiWZoff efficiency
maps that carry the exclusive m_ll bins of SUSY-2018-16. As a proxy, move C1 up to
m(N3) (keeping its decays and all branching ratios), recompute the 13 TeV cross
sections and fit. The dilepton efficiency is set by m(N3) - m(N1), which is kept;
C1 production is somewhat underestimated and N3 N1/N2 production stays uncovered.

Run from Run3ModelGen/:
  pixi run bash -c '. build/setup.sh && python ../scan/proxy_ewk.py <flattened.slha ...>'
'''

import os
import re
import sys

import pyslha

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def make_proxy(src, dst):
    text = open(src).read()
    text = text.split('XSECTION')[0]                 # drop old cross sections
    doc = pyslha.readSLHA(text, ignorenomass=True)
    m3 = abs(doc.blocks['MASS'][1000025])
    pattern = re.compile(r'^(\s+1000024\s+)(\S+)(.*)$', re.M)
    text = pattern.sub(lambda m: f'{m.group(1)}{m3:.8E}{m.group(3)}', text, count=1)
    open(dst, 'w').write(text)


if __name__ == '__main__':
    from smodels.tools import xsecComputer
    from smodels.base.physicsUnits import TeV
    from soft2l_fit import main as fit
    proxies = []
    for f in sys.argv[1:]:
        dst = f.replace('.slha', '_proxy.slha')
        make_proxy(f, dst)
        comp = xsecComputer.XSecComputer(maxOrder=xsecComputer.LO, nevents=10000, pythiaVersion=8)
        comp.addXSecToFile(comp.compute(sqrts=13 * TeV, slhafile=dst), dst)
        proxies.append(dst)
    fits, _ = fit(proxies)
    for name, r in fits.items():
        e = r['ewk']
        print(f"{name:28s} ewk proxy: N={e['signal_events']:6.1f} dchi2(mu=1)={e['dchi2_mu1']:6.2f} "
              f"mu_hat={e['mu_hat']:5.2f} dchi2(mu_hat)={e['dchi2_muhat']:6.2f}  excess bins {r['excess_bins_signal']}")
