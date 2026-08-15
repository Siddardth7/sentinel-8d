# Resources — Multi-Station Defect Traceback → 8D

Everything needed to execute this project. **Datasets and research papers are given as verified original links (✅).** Videos/tutorials are given as search strings (🔎) — pick whatever fits.

---

## 1. Datasets (original sources — verified Aug 14, 2026)

### Preferred — CiP-DMD (discrete manufacturing, named parameters)
- **Paper / record (Zenodo):** DOI **10.5281/zenodo.8420132** — https://zenodo.org/records/8420132
  ⚠️ This Zenodo record hosts the **conference paper PDF only** (`PROCIR_ICME 2023_CiP_DMD_Final.pdf`), *not* the data files.
- **Published paper (ScienceDirect, Procedia CIRP):** https://www.sciencedirect.com/science/article/pii/S2212827124009624
- **Data access:** the dataset is released under CC-BY-4.0 through the authors / **InterQ** EU project. Confirm the live data-file location from the paper's "Data availability" section on Day 1 (this is the project's one access risk — see `execution.md` §2).

### Committed fallback — Bosch Production Line Performance (guaranteed downloadable)
- **Kaggle competition data:** https://www.kaggle.com/c/bosch-production-line-performance/data
  ~1M real parts, hundreds of station-level measurements, per-part pass/fail (`Response`). Anonymized feature names (Line→Station→Feature). Structurally ideal for traceback; the method runs unchanged here.

### Alternative — Bosch CNC Machining Dataset (UCI)
- https://archive.ics.uci.edu/dataset/752/bosch+cnc+machining+dataset — real CNC machining time-series (vibration), useful if you want a different machining angle.

## 2. Research papers (original links — verified)

- **Jourdan, N., Biegel, T., Bretones Cassoli, B., & Metternich, J.** *A new benchmark dataset for machine learning applications in discrete manufacturing: CiP-DMD.* Procedia CIRP (CIRP ICME 2023). — https://www.sciencedirect.com/science/article/pii/S2212827124009624 · Zenodo mirror: https://zenodo.org/records/8420132
  *Read first — it documents the schema, stations, parameters, and the process↔quality traceability model you'll rely on.*
- Curated dataset indexes (to find further RCA-suitable manufacturing data):
  - `nicolasj92/industrial-ml-datasets` (maintained by CiP-DMD's first author) — https://github.com/nicolasj92/industrial-ml-datasets
  - `jonathanwvd/awesome-industrial-datasets` — https://github.com/jonathanwvd/awesome-industrial-datasets

## 3. Standards & methodology (8D / RCA)

*(Standards bodies gate PDFs behind purchase; use these as reference names / search terms rather than links.)*
- **Ford Global 8D (G8D)** — the canonical D1–D8 structure. 🔎 "Ford Global 8D methodology disciplines"
- **AIAG CQI-20 — Effective Problem Solving** — industry RCA/8D reference. 🔎 "AIAG CQI-20 effective problem solving"
- **AS9100 / IATF 16949 clause 10.2** — corrective-action requirements. 🔎 "IATF 16949 clause 10.2 corrective action"
- **AS13100 (aerospace engine)** — mandates 8D-style problem solving (relevant to the aerospace résumé framing). 🔎 "AS13100 problem solving 8D"

## 4. Python libraries

| Library | Use | Docs |
|---------|-----|------|
| pandas / numpy | wrangling, join process↔quality | https://pandas.pydata.org/docs/ |
| scipy.stats | t-test / ANOVA / χ² | https://docs.scipy.org/doc/scipy/reference/stats.html |
| statsmodels | logistic regression, odds ratios, VIF | https://www.statsmodels.org/stable/ |
| scikit-learn | tree cross-check + importances | https://scikit-learn.org/stable/ |
| matplotlib / seaborn | Pareto, effect plots | https://matplotlib.org/ · https://seaborn.pydata.org/ |

Install: `pip install pandas numpy scipy statsmodels scikit-learn matplotlib seaborn jupyter`

## 5. Tutorials & video (search strings — 🔎)

- 8D report walkthrough → 🔎 "8D problem solving report example walkthrough" (channels: *Quality HUB India*, *CQE Academy*)
- ANOVA in Python → 🔎 "ANOVA Python statsmodels tutorial"
- Logistic regression interpretation → 🔎 "logistic regression statsmodels odds ratio interpret Python"
- Multiple-comparison correction → 🔎 "Benjamini Hochberg FDR Python statsmodels multipletests"
- VIF / multicollinearity → 🔎 "variance inflation factor VIF statsmodels Python"
- Pareto chart → 🔎 "Pareto chart pandas matplotlib"

## 6. Books (reference)

- Montgomery, D.C. — *Introduction to Statistical Quality Control* (RCA, capability, SPC controls).
- Andersen & Fagerhaug — *Root Cause Analysis: Simplified Tools and Techniques*.
- AIAG — *SPC* and *MSA* reference manuals (context for the corrective-action controls).

---

*Dataset existence and paper links verified Aug 14, 2026. The single moving part is CiP-DMD's data-file location — confirmed at download; the Bosch PLP fallback removes that as a blocker.*
