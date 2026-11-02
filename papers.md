ATLAS Slepton excess: https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HMBS-2024-64/

ATLAS soft 2L paper: https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2018-16/index.php

LZ paper: https://arxiv.org/pdf/2609.02823

## LZ event: Higgsino dark matter interpretation

### What LZ reports (arXiv:2609.02823)

- One event in 2.84 tonne-years with a 248 ± 23 (stat) ± 23 (sys) keV nuclear recoil, in a region where very little background is expected. Global significance is 2.6σ; the best local significance across all models tested is 3.4σ.
- Standard elastic spin-independent scattering does not fit at all (0σ at every mass). Only interactions whose recoil spectrum extends to high energy fit: momentum-dependent effective-field-theory couplings, and inelastic scattering.
- The only Higgsino statement in the paper is that the inelastic spin-independent interaction (operator O₁ˢ) "resembles a Higgsino model", citing Graham, Ramani & Wong, arXiv:2409.07768.
- Local significance for that interaction (Table S8):

  | Mass gap δ (keV)   | 0   | 50  | 100 | 150 | 200 | 250 | 300 | 350 |
  |--------------------|-----|-----|-----|-----|-----|-----|-----|-----|
  | m_χ = 1000 GeV     | 0.0 | 0.0 | 0.8 | 2.2 | 2.7 | 2.9 | 3.0 | 3.3 |
  | m_χ = 4000 GeV     | 0.0 | 0.0 | 1.0 | 2.3 | 2.7 | 2.9 | 3.0 | 3.3 |

  All models need m_χ ≳ 100 GeV, and the fit levels off from about 400 GeV.

### What a Higgsino explanation would require

The points below are my own estimates from standard Higgsino phenomenology, not from the LZ paper.

1. **A nearly pure Higgsino.** The two neutral states χ̃⁰₁ and χ̃⁰₂ couple to the Z boson only off-diagonally. Z exchange therefore produces only the inelastic transition χ̃⁰₁ N → χ̃⁰₂ N, which is exactly the inelastic interaction tested above. Elastic scattering comes only from loops and is far smaller, which is consistent with the 0σ for standard elastic scattering.
2. **A neutral mass gap of about 150–350 keV.** This gap comes from mixing with the bino and wino. At leading order it is δ₀ ≈ m_Z² (s_W²/M₁ + c_W²/M₂), which is about m_Z²/M for M₁ ≈ M₂ = M. The coefficient should be checked, e.g. against Nagata & Shirai (arXiv:1410.4549).
   - δ₀ = 300 keV needs M ≈ 3 × 10⁷ GeV; δ₀ = 150 keV needs M ≈ 6 × 10⁷ GeV.
   - Gauginos at the TeV scale give δ₀ of order 1 GeV, which is far too large for any scattering.
   - So this is a split-SUSY spectrum: the Higgsinos are light, and the gauginos (and probably the scalars) are at 10⁷–10⁸ GeV.
3. **Mass of about 1.1 TeV if it makes up all the dark matter.** A pure Higgsino gets the full relic density thermally at m ≈ 1.1 TeV, which sits right in the region where the fit is strongest. A lighter Higgsino would be underabundant, so the expected event rate scales with its share of the relic density (unless it is produced non-thermally).
4. **The interaction strength is fixed, not free.** LZ fits the coupling as a free parameter. For a Higgsino it is set by the Z-boson coupling, so only the mass, δ₀ and the dark-matter velocity distribution can vary. Nobody has checked whether the fitted coupling (Fig. 6, top) matches the Higgsino value; that is the key consistency test.
5. **The rate is very sensitive to the velocity tail.** With δ ≈ 300 keV only the fastest dark-matter particles can scatter, so the expected rate depends strongly on the assumed escape velocity and halo model. Inelastic dark matter also predicts strong annual modulation peaking around 2 June. The event was on 16 June 2023, but one event says nothing about modulation.

### Consequences elsewhere

- **LHC:** the charged–neutral mass gap is set by radiative corrections, about 340 MeV. The charged Higgsino then travels a few mm before decaying, which shows up as disappearing tracks. A 1.1 TeV Higgsino is well beyond the LHC's current reach. The soft-2-lepton search (SUSY-2018-16) targets mixed Higgsinos with GeV-scale mass gaps. It does not directly test this pure-Higgsino scenario; it only matters for mixed-Higgsino alternatives with lighter gauginos.
- **Indirect detection:** TeV Higgsino annihilation into gamma-ray lines and continuum is a target for H.E.S.S. and CTAO. Sensitivity depends strongly on the assumed dark-matter density profile.
- **Higgs mass:** with gauginos (and likely scalars) at 10⁷–10⁸ GeV, getting m_h = 125 GeV restricts tanβ to small values. That needs split-SUSY renormalisation-group running, not the standard MSSM spectrum tools.
- **Other experiments:** XENONnT and PandaX-4T should have comparable sensitivity to an extended recoil window. Their data above about 55 keV would test this directly.
- **ATLAS slepton excess:** a split-SUSY Higgsino needs very heavy scalars, which is incompatible with light sleptons. Both excesses cannot come from the same Higgsino-dark-matter spectrum. (This is my inference; I haven't read the slepton paper.)

### Consequences for Run3ModelGen

- This scenario is outside the scan: M₁, M₂ ∈ [-2000, 2000] GeV in `default_config.yaml` gives δ₀ of order 1 GeV.
- micrOMEGAs reports only elastic cross sections (`proton_SI`/`SD`). For a near-pure Higgsino those come out tiny, and they don't describe the inelastic process at all.
- SPheno and SoftSUSY probably can't resolve keV-level splittings for TeV-scale states with gauginos at 10⁷ GeV. They also don't do split-SUSY running.
- A dedicated study would need:
  - fixed μ ≈ 1.1 TeV with decoupled gauginos;
  - δ₀ computed analytically or with a split-SUSY tool;
  - the inelastic Z-exchange rate in xenon (e.g. WimPyDD, which LZ used), compared to the LZ coupling interval.
