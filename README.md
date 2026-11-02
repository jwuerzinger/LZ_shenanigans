# LZ shenanigans

Can a pMSSM spectrum explain three mild excesses at once?

| Excess | Size | Paper |
|---|---|---|
| LZ: one nuclear recoil at 248 keV | 2.6σ global, 3.4σ local | [arXiv:2609.02823](https://arxiv.org/pdf/2609.02823) |
| ATLAS soft-2-lepton electroweakino search: m_ℓℓ < 20 GeV | 2.7σ local | [SUSY-2018-16](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/SUSY-2018-16/index.php), arXiv:1911.12606 |
| ATLAS compressed sleptons: smuons at Δm ≈ 3–10 GeV, selectrons at Δm ≈ 30–50 GeV | 2.4σ / 2.0σ local | [HMBS-2024-64](https://atlas.web.cern.ch/Atlas/GROUPS/PHYSICS/PAPERS/HMBS-2024-64/), arXiv:2503.17186 |

The spectra are computed with [Run3ModelGen](Run3ModelGen) (submodule, branch `osx-arm64`): SPheno, micrOMEGAs 7.1.10, gm2calc and SModelS 3.2.1.

## Results

**Bottom line: no pMSSM configuration explains LZ and the soft-2L excess together with m_h = 125 GeV.**

1. **LZ needs a nearly degenerate N1/N2 pair.** The LZ event fits only interactions that favour high-energy recoils. In the MSSM that means Z-mediated inelastic scattering, N1 N → N2 N, with m(N2) − m(N1) ≈ 100–250 keV. With TeV-scale gauginos this happens only at an accidental *crossing* of the two Higgsino-like states (they have opposite CP, so they don't mix). Hitting the crossing needs one gaugino mass tuned to about 10⁻⁶.
2. **LZ alone works**, for an almost pure Higgsino with gauginos at 1–3.5 TeV and tanβ ≈ 5 (benchmarks F1, F2). These have m_h = 125 GeV, C1 about 1 GeV above N1, and elastic scattering well below the LZ 2024 limit. Crossings with more gaugino mixing (B, C, E) give the right inelastic splitting but are excluded by LZ's own elastic spin-independent limit, by factors of 17–40.
3. **LZ + soft-2L needs tanβ ≲ 1.3.** Soft-2L needs a third neutralino 10–20 GeV above the pair. That only happens with the wino within about 20 GeV of μ, opposite in sign, at tanβ ≲ 1.3 (class A, [figure](#tree-level-result)). There m_h ≈ 102 GeV, which LEP excludes. Even ignoring m_h, N3 decays mostly to C1 + W* and N2 + γ, so the soft-2L fit barely moves (Δχ² ≈ −0.3).
4. **Soft-2L alone** is fit by an ordinary compressed wino/bino at about 200 GeV with Δm = 15 GeV (D2): Δχ² = −4.0 at the predicted cross section, with a best-fit signal strength of 2.5. But CMS-SUS-21-008 already gives r = 0.98 for this point, so the extra signal the excess wants is in tension with CMS. A compressed Higgsino (D1) adds almost nothing.
5. **Sleptons can be added to the LZ-only spectra.** A right-handed smuon 6 GeV above N1 (F1 + smuons) or right-handed sleptons 40 GeV above N1 (F3) keep LZ, m_h and all SModelS limits intact. In pMSSM-19, though, selectrons and smuons are degenerate, so each such spectrum predicts the same excess in ee and μμ. ATLAS saw the smuon excess only in μμ and the selectron excess only in ee. The slepton search is not in the SModelS database, so this match is kinematic only.

### Which configuration explains which excess

Benchmark spectra (SLHA files with decay tables and 13 TeV cross sections) are in [`benchmarks/`](benchmarks). Each has a JSON summary next to it with masses, mixing, micrOMEGAs output and the SModelS results.

| Configuration | Benchmarks | LZ | soft-2L | smuon | selectron | m_h = 125 |
|---|---|---|---|---|---|---|
| **A** wino–Higgsino crossing, tanβ ≈ 1.2, wino within 20 GeV of μ (M2·μ < 0) | A, A + smuons, A2 | ✓ / (✓) | ≈0 | ✓ with smuons | – | ✗ (~102 GeV) |
| **B/C/E** Higgsino crossing with sizeable gaugino mixing, tanβ ≈ 10 | B, B + smuons, C, E | ✗ elastic SI | – | ✓ with smuons | ✓ (E) | ✓ |
| **F** nearly pure Higgsino crossing, TeV gauginos, tanβ ≈ 5 | F1, F1 + smuons, F2, F3 | ✓ | – | ✓ with smuons | ✓ (F3, R only) | ✓ |
| **D1** compressed Higgsino, Δm = 15 GeV | D1, D1 + smuons | – | – | ✗ (excluded) | – | ✓ |
| **D2** compressed wino/bino, Δm = 15 GeV | D2, D2 + smuons | – | ✓ (Δχ² −4.0), CMS tension | ✓ with smuons | – | ✓ |

Legend: ✓ fits or allowed; (✓) borderline (within the uncertainty of the limit); ≈0 a signal is predicted but doesn't improve the fit; – no relevant signal; ✗ excluded or disfavoured.

Per benchmark:

| Benchmark | tanβ | M₁ | M₂ | μ | m(N1) | N2−N1 | N3−N1 | C1−N1 | light sleptons | m_h | Ωh² | SI / LZ limit |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| [A_wino_higgsino_crossing](benchmarks/A_wino_higgsino_crossing.slha) | 1.23 | 345.3 | -221.3 | 236.1 | 252.5 | 163 keV | 17.5 | 4.53 | – | 102.8 | 0.00475 | 0.77 |
| [A_wino_higgsino_crossing_smuons](benchmarks/A_wino_higgsino_crossing_smuons.slha) | 1.23 | 342.5 | -221.5 | 236.1 | 250.5 | 161 keV | 17.5 | 4.18 | μ̃_R 256 | 102.9 | 0.00606 | 2.2 |
| [A2_light_wino_higgsino_crossing](benchmarks/A2_light_wino_higgsino_crossing.slha) | 1.19 | -273.9 | 151.8 | -157.7 | 180.8 | 109 keV | 16.0 | 7.48 | – | 101.5 | 0.00379 | 2 |
| [B_light_higgsino_crossing](benchmarks/B_light_higgsino_crossing.slha) | 10.21 | 205.9 | -244.6 | 164.8 | 165.7 | 103 keV | 69.2 | 5.04 | – | 125.1 | 0.00427 | 37 |
| [B_light_higgsino_crossing_smuons](benchmarks/B_light_higgsino_crossing_smuons.slha) | 10.21 | 205.9 | -241.0 | 164.8 | 164.5 | 100 keV | 68.7 | 5.03 | μ̃_R 170 | 125.0 | 0.00527 | 40 |
| [C_heavy_higgsino_crossing](benchmarks/C_heavy_higgsino_crossing.slha) | 10.36 | 676.7 | -817.5 | 572.4 | 562.7 | 232 keV | 119.6 | 1.97 | – | 125.0 | 0.0325 | 20 |
| [E_higgsino_crossing_selectrons](benchmarks/E_higgsino_crossing_selectrons.slha) | 10.12 | 445.5 | -556.7 | 346.7 | 352.4 | 200 keV | 97.9 | 3.09 | μ̃_R 387, ẽ_L 397 | 124.9 | 0.0142 | 17 |
| [F1_pure_higgsino_crossing](benchmarks/F1_pure_higgsino_crossing.slha) | 5.05 | 931.4 | -2242.6 | 181.9 | 229.2 | 154 keV | 686.5 | 1.19 | – | 124.9 | 0.00562 | 0.024 |
| [F1_pure_higgsino_crossing_smuons](benchmarks/F1_pure_higgsino_crossing_smuons.slha) | 5.05 | 887.7 | -2242.6 | 181.9 | 227.5 | 153 keV | 639.6 | 1.25 | μ̃_R 233 | 125.1 | 0.00692 | 0.024 |
| [F2_pure_higgsino_crossing_heavy](benchmarks/F2_pure_higgsino_crossing_heavy.slha) | 5.08 | -1641.0 | 3507.8 | -510.3 | 546.7 | 231 keV | 1063.7 | 0.79 | – | 125.0 | 0.0302 | 0.012 |
| [F3_pure_higgsino_crossing_selectrons](benchmarks/F3_pure_higgsino_crossing_selectrons.slha) | 5.03 | -1327.6 | 2994.8 | -342.3 | 382.7 | 207 keV | 911.7 | 0.92 | μ̃_R 423 | 125.0 | 0.0154 | 0.009 |
| [D1_compressed_higgsino](benchmarks/D1_compressed_higgsino.slha) | 10.00 | 407.4 | 814.7 | 200.0 | 207.7 | 14.9 GeV | 203.2 | 8.13 | – | 124.7 | 0.00762 | 26 |
| [D1_compressed_higgsino_smuons](benchmarks/D1_compressed_higgsino_smuons.slha) | 10.00 | 407.4 | 814.7 | 200.0 | 207.5 | 15.0 GeV | 199.2 | 8.24 | μ̃_R 213 | 124.6 | 0.0127 | 51 |
| [D2_compressed_wino_bino](benchmarks/D2_compressed_wino_bino.slha) | 10.00 | 200.0 | 197.0 | 1000.0 | 197.2 | 15.0 GeV | 819.3 | 15.06 | – | 125.1 | 0.0422 | 1.5 |
| [D2_compressed_wino_bino_smuons](benchmarks/D2_compressed_wino_bino_smuons.slha) | 10.00 | 200.0 | 194.5 | 1000.0 | 194.8 | 15.0 GeV | 818.5 | 15.07 | μ̃_R 201 | 125.0 | 0.0529 | 2.5 |

Masses are in GeV. Inputs are SPheno `EXTPAR` values at the SUSY scale. "Light sleptons" lists the smuon pole masses; in pMSSM-19 the selectrons are degenerate with them. "SI / LZ limit" is micrOMEGAs' spin-independent proton cross section × Ωh²/0.12, divided by the approximate LZ 2024 limit.

| Benchmark | LZ | soft-2L (Δχ² at μ = 1) | smuon | selectron | m_h | SModelS r_max |
|---|---|---|---|---|---|---|
| A_wino_higgsino_crossing | ✓ | – (−0.0) | – | – | ✗ 103 | 0.36 |
| A_wino_higgsino_crossing_smuons | (✓) | – (−0.0) | ✓ | – | ✗ 103 | 0.37 |
| A2_light_wino_higgsino_crossing | (✓) | ≈0 (−0.3) | – | – | ✗ 102 | 0.66 |
| B_light_higgsino_crossing | ✗ SI | ≈0 (−0.3) | – | – | ✓ | 0.59 |
| B_light_higgsino_crossing_smuons | ✗ SI | ≈0 (−0.3) | ✓ | – | ✓ | 0.61 |
| C_heavy_higgsino_crossing | ✗ SI | – (+0.0) | – | – | ✓ | 0.05 |
| E_higgsino_crossing_selectrons | ✗ SI | – (+0.0) | – | ✓ | ✓ | 0.10 |
| F1_pure_higgsino_crossing | ✓ | – (−0.0) | – | – | ✓ | 0.52 |
| F1_pure_higgsino_crossing_smuons | ✓ | – (−0.0) | ✓ | – | ✓ | 0.54 |
| F2_pure_higgsino_crossing_heavy | ✓ | – (+0.0) | – | – | ✓ | 0.02 |
| F3_pure_higgsino_crossing_selectrons | ✓ | – (+0.0) | – | ✓ | ✓ | 0.08 |
| D1_compressed_higgsino | – | – (+0.1) | – | – | ✓ | 0.38 |
| D1_compressed_higgsino_smuons | – | – (−0.0) | ✗ | – | ✓ | 1.09 |
| D2_compressed_wino_bino | – | ✓ (−4.0) | – | – | ✓ | 0.98 |
| D2_compressed_wino_bino_smuons | – | ≈0 (−0.2) | ✓ | – | ✓ | 0.27 |

The criteria behind each column are in [How the verdicts are made](#how-the-verdicts-are-made).

## The excesses

### LZ: one high-energy nuclear recoil (arXiv:2609.02823)

- One event in 2.84 tonne-years with a 248 ± 23 (stat) ± 23 (sys) keV nuclear recoil, in a region where very little background is expected. Global significance is 2.6σ; the best local significance across all models tested is 3.4σ.
- Standard elastic spin-independent scattering does not fit at all (0σ at every mass). Only interactions whose recoil spectrum extends to high energy fit: momentum-dependent effective-field-theory couplings, and inelastic scattering.
- The only Higgsino statement in the paper is that the inelastic spin-independent interaction (operator O₁ˢ) "resembles a Higgsino model", citing Graham, Ramani & Wong, arXiv:2409.07768.
- Local significance for that interaction (Table S8). LZ tested it only at 400, 1000 and 4000 GeV:

  | Mass gap δ (keV)   | 0   | 50  | 100 | 150 | 200 | 250 | 300 | 350 |
  |--------------------|-----|-----|-----|-----|-----|-----|-----|-----|
  | m_χ = 400 GeV      | 0.0 | 0.0 | 0.8 | 2.2 | 2.6 | 2.9 | 2.9 | –   |
  | m_χ = 1000 GeV     | 0.0 | 0.0 | 0.8 | 2.2 | 2.7 | 2.9 | 3.0 | 3.3 |
  | m_χ = 4000 GeV     | 0.0 | 0.0 | 1.0 | 2.3 | 2.7 | 2.9 | 3.0 | 3.3 |

  All models need m_χ ≳ 100 GeV, and the fit levels off from about 400 GeV.

#### What a Higgsino explanation requires

The points below are my own estimates from standard Higgsino phenomenology, not from the LZ paper.

1. **A Higgsino-like N1/N2 pair.** The two neutral Higgsino states couple to the Z boson only off-diagonally, so Z exchange gives exactly the inelastic transition N1 N → N2 N that LZ tested. Elastic scattering must stay small, which is consistent with the 0σ for standard elastic scattering.
2. **A neutral mass gap of about 100–350 keV.** Away from any tuning the gap is set by gaugino mixing, δ ≈ m_Z² (s_W²/M₁ + c_W²/M₂), which needs gauginos at 10⁷–10⁸ GeV (split SUSY).
   - **Update from the scan below:** the bino and wino contributions can cancel. The two states have opposite CP, so their masses cross, and at the crossing δ = 0 even with TeV gauginos. The price is tuning one gaugino mass to about 10⁻⁶ (e.g. ±0.2 MeV in M₁ for δ = 300 ± 100 keV). Split SUSY is not required.
3. **Mass of about 1.1 TeV if it makes up all the dark matter.** A pure Higgsino gets the full relic density thermally at m ≈ 1.1 TeV. A lighter one is underabundant (Ωh² ≈ 0.004–0.03 for the benchmarks), so the expected LZ rate scales with Ωh²/0.12.
4. **The interaction strength is fixed, not free.** LZ fits the coupling as a free parameter. For a Higgsino it is set by the Z coupling, so only the mass, δ and the dark-matter velocity distribution can vary. Nobody has checked whether the fitted coupling (LZ Fig. 6, top) matches the Higgsino value; that is the key consistency test, and it is not done here.
5. **The rate is very sensitive to the velocity tail.** With δ of a few hundred keV only the fastest dark matter can scatter, so the expected rate depends strongly on the escape velocity and halo model. Inelastic dark matter also predicts strong annual modulation peaking around 2 June. The event was on 16 June 2023, but one event says nothing about modulation.
6. **The kinematics favour heavier dark matter.** In xenon the largest reachable gap is about μ_N v²_max/2, roughly 270 keV at 200 GeV and 390 keV at 1 TeV. Lighter Higgsinos need a smaller gap, which also allows lower-energy recoils that LZ didn't see. Below about 150 GeV even δ = 0 needs v > 650 km/s for a 248 keV recoil.

#### Consequences elsewhere

- **LHC:** for a nearly pure Higgsino, the chargino is only about 0.3–1 GeV above N1 (benchmarks F: 0.8–1.3 GeV), giving soft or disappearing-track signatures rather than soft dileptons. A 1.1 TeV Higgsino is beyond the LHC's current reach.
- **N2 is long-lived:** with a ~100 keV gap, N2 decays almost entirely as N2 → N1 γ with a lifetime of order seconds (benchmark B: Γ = 3 × 10⁻²⁵ GeV). That's invisible at colliders.
- **Indirect detection:** TeV Higgsino annihilation into gamma-ray lines and continuum is a target for H.E.S.S. and CTAO, with a strong dependence on the assumed density profile.
- **Other experiments:** XENONnT and PandaX-4T should have comparable sensitivity in an extended recoil window. Their data above about 55 keV would test this directly.

### ATLAS slepton search in the compressed corridor (HMBS-2024-64)

arXiv:2503.17186, JHEP 08 (2025) 053. √s = 13 TeV, 140 fb⁻¹.

- **Searches for:** selectron and smuon pairs, each decaying to ℓ χ̃⁰₁, in the corridor Δm(ℓ̃, χ̃⁰₁) ≲ m_W. Events need an initial-state-radiation jet, missing energy, and two same-flavour opposite-sign leptons. The analysis uses cut-and-count regions plus BDT regions, each optimised for a given Δm. The χ̃⁰₁ composition is not specified (simplified models).
- **Overall:** ATLAS calls the results "generally consistent with the SM".
- **Smuon excess, at Δm ≈ 3–10 GeV:**
  - Two independent regions (μμ BDT optimised for Δm = 5+10 GeV) see 23 events vs 13.7 ± 2.6 expected (1.9σ local) and 26 vs 13.7 ± 2.5 (2.4σ local).
  - Best-fitting model: (m_μ̃, m_χ̃⁰₁) = (150, 140) GeV, discovery significance 2.1σ.
- **Selectron excess, at Δm ≈ 30–50 GeV:**
  - One region (ee BDT optimised for Δm = 40+50 GeV) sees 7 events vs 2.8 ± 0.8 expected (2.0σ local).
  - Best-fitting model: (m_ẽ, m_χ̃⁰₁) = (375, 335) GeV, discovery significance 1.9σ.
  - This excess leaves the selectron exclusion with no coverage at Δm = 30–50 GeV.
- **The two excesses don't match:** they sit at different Δm and in different flavours. The smuon best-fit masses give only 0.18σ in the selectron channel, and the selectron best fit gives only 0.74σ in the smuon channel.
- **Limits:** selectrons excluded up to about 300 GeV, smuons up to about 350 GeV, for Δm between 2 and 100 GeV (assuming degenerate L/R states).

### ATLAS soft-2-lepton electroweakino search (SUSY-2018-16)

arXiv:1911.12606, PRD 101 (2020) 052005. √s = 13 TeV, 139 fb⁻¹.

- **Searches for:** compressed Higgsino (χ̃⁰₂, χ̃±₁, χ̃⁰₁) and wino/bino models, plus sleptons, in events with two soft same-flavour opposite-sign leptons, missing energy, and an initial-state-radiation or vector-boson-fusion topology.
- **Overall:** ATLAS calls the data consistent with the SM; no excess is mentioned in the abstract.
- **Mild excess in Table 10:** in the inclusive electroweakino regions, the dilepton mass cut m_ℓℓ < 20 GeV gives 383 events vs 301 ± 23 expected (p₀ = 0.0034, 2.7σ local).
  - Neighbouring mass cuts are also high (p₀ = 0.0065 for m_ℓℓ < 30 GeV, 0.034 for m_ℓℓ < 10 GeV, 0.027 for m_ℓℓ < 40 GeV), but these regions overlap and largely reflect the same events.
  - ATLAS traces it to too many μμ events at 10 < m_μμ < 20 GeV in the high-missing-energy region. In the exclusive bins in SModelS: 23 events vs 14.6 ± 3.0 in μμ, high E_T^miss, m_ℓℓ = 10–20 GeV, and 16 vs 4.8 ± 1.6 in ee, high E_T^miss, m_ℓℓ = 5–10 GeV.
  - The separate Higgsino interpretation (SModelS entry `ATLAS-SUSY-2018-16-hino`) has 170 vs 112.4 ± 12.6 in its inclusive SR-E-med region.
  - Since m_ℓℓ ends at Δm(χ̃⁰₂, χ̃⁰₁), this suggests Δm ≈ 10–20 GeV. That reading is mine; the paper doesn't state a gap.
- **Limits:**
  - Higgsino χ̃⁰₂ below 193 GeV is excluded at Δm = 9.3 GeV. At the LEP mass bound, Δm from 2.4 to 55 GeV is excluded.
  - Wino/bino is excluded up to 240 GeV at Δm = 7 GeV.
  - Degenerate light-flavour sleptons are excluded up to 251 GeV, down to Δm = 550 MeV.
  - All observed limits are within 2σ of the expected ones.

## pMSSM scan

### Method

**Stage A: tree-level scan** ([`scan/treelevel_scan.py`](scan/treelevel_scan.py), [`scan/neutralino.py`](scan/neutralino.py)).
- Samples tanβ ∈ [1, 60] (log), μ ∈ ±[100, 800] GeV and one gaugino mass ∈ ±[100, 5000] GeV, 200,000 points per mode.
- For each sample it root-finds every value of the other gaugino mass at which N1 and N2 are exactly degenerate (N2 − N1 = 0).
- Result: 261,877 crossings. The 189,500 that are LZ-capable with a neutral LSP are in [`scan/results/treelevel_lz_candidates.csv.gz`](scan/results/treelevel_lz_candidates.csv.gz).
- Criteria:
  - **LZ:** m(N1) ≥ 100 GeV and Z–N1–N2 coupling ≥ 0.1 × the pure-Higgsino value.
  - **Soft-2L:** a neutralino N3 or N4 10–20 GeV above N1 that couples to N1/N2 via the Z, with m(N1) ≤ 300 GeV.
  - **Neutral LSP:** m(C1) > m(N1) − 0.25 GeV at tree level. The loop correction then lifts C1 by about 0.3 GeV.

**Stage B: loop-level benchmarks** ([`scan/benchmarks.py`](scan/benchmarks.py)), using Run3ModelGen's pipeline steps.
1. A_t is scanned to bring m_h as close to 125 GeV as possible.
2. Sleptons, if any, are placed at m(N1) + Δm.
3. The crossing parameter (M₁ or M₂) is root-found so that SPheno's *loop-level* N2 − N1 equals the target δ. SPheno prints masses to 1 keV. δ is chosen so that a 248 keV xenon recoil needs v_min = 650 km/s, capped at 350 keV.
4. For class A and D2, a second parameter is tuned to set the N3 − N1 or N2 − N1 gap.
5. micrOMEGAs, gm2calc and SModelS run on the final spectrum (LO 13 TeV cross sections from Pythia8, 20k events).

**Soft-2L fit** ([`scan/soft2l_fit.py`](scan/soft2l_fit.py)). SModelS ships SUSY-2018-16 without a covariance matrix or full likelihood, so by default it reports only the single most sensitive signal region, which is not where the excess sits. The fit instead combines all exclusive bins in a simple likelihood: Poisson per bin, Gaussian background uncertainty profiled per bin, bins treated as uncorrelated. It does this three times:
- `ewk`: the 2ℓ electroweakino bins (wino/bino mass relations, `TChiWZoff`);
- `hino`: the four inclusive Higgsino regions (`TChiWZoff`, `TChiZoff`, `TChiWWoff`);
- `slep`: the slepton m_T2 bins.

The table quotes the better of `ewk` and `hino`: Δχ² = −2 ln(L_model / L_SM) at the predicted cross section. Results: [`scan/results/soft2l_fit.json`](scan/results/soft2l_fit.json).

### How the verdicts are made

Implemented in [`scan/summarize.py`](scan/summarize.py):

| Column | Criterion |
|---|---|
| LZ | keV crossing present; elastic SI × Ωh²/0.12 below the LZ 2024 limit, approximated as 2.2 × 10⁻⁴⁸ cm² × m/40 GeV. Ratio < 1 ✓, 1–3 (✓), larger ✗ SI |
| soft-2L | best Δχ² ≤ −2 ✓; −2…0 ≈0; > +4 ✗ |
| smuon | m(μ̃) − m(N1) in 3–10 GeV and slepton-bin Δχ² < 4 |
| selectron | m(ẽ) − m(N1) in 30–50 GeV |
| m_h | |m_h − 125| < 3 GeV (SPheno) |
| SModelS r_max | largest observed r over all analyses in the database; > 1 is excluded |

### Tree-level result

![Smallest N3−N1 gap vs tanβ](scan/results/gap_vs_tanb.png)

Among LZ-capable crossings with a neutral LSP, the smallest gap to the next neutralino grows quickly with tanβ:

| tanβ | 1–1.3 | 1.3–1.6 | 1.6–2 | 2–3 | 3–4 | > 4 |
|---|---|---|---|---|---|---|
| smallest N3 − N1 [GeV] | 1.0 | 23 | 37 | 52 | 72 | 48–59 |

- **Soft-2L window:** the 10–20 GeV window is only reached for tanβ ≲ 1.3, always with the wino within about 20 GeV of μ and M₂·μ < 0, M₁·μ > 0.
- **The other sign pattern (M₁·μ < 0, M₂·μ > 0)** reaches the window only with a charged LSP. At tree level, m(C1) − m(N1,2) ≈ −sin2β [m_W²/2|M₂| + m_Z² s_W²/2|M₁|] < 0 at the crossing.
- **m_h:** SPheno reaches 125 GeV only for tanβ ≳ 3, with stops up to 20 TeV at maximal mixing (tanβ = 3: 125.2 GeV; tanβ = 2: 118.3 GeV; tanβ = 1.5: 112.9 GeV).

### Caveats

- **Tuning:** every LZ benchmark is tuned to about 10⁻⁶ in one gaugino mass. The loop-level crossing is found numerically. Its location moves by GeV with loop corrections, but the crossing itself always exists, because the CP-even and CP-odd states never mix.
- **LZ rate not computed:** no benchmark's expected LZ rate or recoil spectrum is calculated. That needs the Higgsino Z coupling, the relic fraction and a halo model, e.g. with WimPyDD as LZ used. The LZ significances are only known for m ≥ 400 GeV, so of the viable spectra only F2 (547 GeV, δ = 231 keV, about 2.6–2.9σ per Table S8) has one.
- **Elastic SI limit:** the LZ 2024 limit is a rough linear scaling, good to a factor of about 1.5. Class A also has a large spin-dependent cross section (about 10⁻³⁹ cm² before relic scaling), which should be checked against spin-dependent neutron limits.
- **Soft-2L fit:** it ignores correlated systematics. It also depends on SModelS topology coverage:
  - cascades through light sleptons (D2 + smuons) have no efficiency map, so their soft-2L signal is missing;
  - charginos within 5 GeV of N1 are treated as invisible.
- **Slepton search not in SModelS:** the slepton excess is judged kinematically against the paper's Δm windows only. In pMSSM-19 the first two generations are degenerate, so every slepton benchmark predicts equal ee and μμ signals.
- **Slepton benchmark setup:**
  - Getting right-handed sleptons within 6 GeV of a 165–230 GeV N1 needs m_A = 1 TeV and split staus (mτ̃L = 2 TeV, mτ̃R = 4.5 TeV) to compensate the hypercharge S-term.
  - With M₂ ≈ 3 TeV, left-handed sleptons can't be brought close to N1 at all (F3 is right-handed only).
- **Class A spectra:** at tanβ ≈ 1.2 these use 3 TeV stops, because heavier stops break electroweak symmetry breaking in SPheno.

## Reproducing

```bash
git clone --recurse-submodules git@github.com:jwuerzinger/LZ_shenanigans.git
cd LZ_shenanigans/Run3ModelGen
pixi install && pixi run build          # SPheno, micrOMEGAs 7.1.10, SModelS, ...

# Stage A (about 10 min, writes scan/results/treelevel_crossings.csv)
cd ../scan && ../Run3ModelGen/.pixi/envs/default/bin/python treelevel_scan.py 200000
../Run3ModelGen/.pixi/envs/default/bin/python plot_treelevel.py

# Stage B + fits (about 30 min)
cd ../Run3ModelGen
pixi run bash -c '. build/setup.sh && python ../scan/benchmarks.py'               # all, or pass names
pixi run bash -c '. build/setup.sh && python ../scan/soft2l_fit.py ../benchmarks/*.slha'
cd ../scan && ../Run3ModelGen/.pixi/envs/default/bin/python summarize.py
```

## Layout

```
README.md            this file
benchmarks/          SLHA spectra (+ decays, 13 TeV xsecs) and JSON summaries
scan/
  neutralino.py      tree-level neutralino/chargino sector
  treelevel_scan.py  stage A
  plot_treelevel.py  figure above
  r3mg.py            thin wrapper around Run3ModelGen's SPheno step
  benchmarks.py      stage B (loop-level tuning, micrOMEGAs, gm2calc, SModelS)
  soft2l_fit.py      combined SUSY-2018-16 likelihood
  summarize.py       tables above
  results/           scan output, fit results, figure
Run3ModelGen/        submodule (pMSSM tool chain)
```
