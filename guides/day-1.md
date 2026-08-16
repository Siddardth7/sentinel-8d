# Day 1 — Environment, scaffold & the data access gate

**Goal:** a working Python environment, the repo open in VS Code, and a usable
dataset sitting in `data/raw/`. By end of day you can `import` your libraries and
you know which dataset you're building on.

**Time budget:** ~3–4 h (≈1 h env, ≈2 h data gate, ≈0.5 h notebook header).

**Covers:** `execution.md` §1–2 · **Milestone:** M1 start.

> This is the one day with real *external risk* — the preferred dataset may not be
> downloadable. There's a committed fallback, and a hard time-box so you don't lose
> the day to it. Read "The data access gate" before you start downloading.

---

## 1. Open the repo in VS Code

You already have this folder. Open it:

```bash
cd /Users/sid/Documents/Upskill/Projects/quality-engineering/case-studies/sentinel-8d
code .
```

Install the VS Code **Python** and **Jupyter** extensions (Microsoft) if you don't
have them — you'll run the notebook inside VS Code.

## 2. Create the virtual environment & install

```bash
python3.11 -m venv .venv
source .venv/bin/activate          # Windows: .venv\Scripts\activate
pip install --upgrade pip
pip install -r requirements.txt
```

In VS Code, pick the interpreter: **Cmd+Shift+P → Python: Select Interpreter →**
the `.venv` one. The notebook must run on this kernel.

**Freeze exact versions** now that everything resolved (reproducibility):

```bash
pip freeze > requirements.txt
```

Sanity check:

```bash
python -c "import pandas, numpy, scipy, statsmodels, sklearn, matplotlib, seaborn; print('ok')"
```

## 3. Confirm the scaffold

The folder structure is already created (see it with `ls -R src data reports`). You
don't need to build folders today — just confirm they're there and that `.gitignore`
is keeping `.venv/` and `data/raw/` out of git:

```bash
git status --short      # should NOT list .venv or files under data/raw/
```

## 4. The data access gate  ⏱️ hard time-box: ~1 hour

Follow `resources.md` §1 for links. Work the **preferred** option first, but set a
timer — if you don't have usable data files in hand within ~1 hour, switch to the
fallback and don't look back. The method is identical either way.

### Option A — preferred: CiP-DMD (named parameters)
- The Zenodo record (DOI `10.5281/zenodo.8420132`) hosts the **paper PDF only** —
  not the data. Read the paper's **"Data availability"** section and follow it to
  the actual files (routed through the authors / the InterQ EU project).
- Why prefer it: parameters have **real names**, so your root cause can be
  *"Operation 30, feed rate"* instead of an anonymized index. Much stronger story.
- Put the downloaded files in `data/raw/`.

### Option B — committed fallback: Bosch Production Line Performance (Kaggle)
- https://www.kaggle.com/c/bosch-production-line-performance/data — download
  `train_numeric.csv` (and `train_categorical.csv`, `train_date.csv` if you want
  them). You'll need a (free) Kaggle account and to accept the competition rules.
- It's ~2 GB numeric. **Work on a stratified sample**: keep *all* failures + a
  matched random sample of passes. That keeps every later step fast.
- Trade-off: feature names are anonymized (`L0_S0_F0`…). Station order is encoded
  in the naming (Line → Station → Feature), so traceback still works; you just
  state the cause at the station/feature level.

### Record what you used
In the notebook header cell (`notebooks/01_traceback.ipynb`, top markdown cell),
fill in **dataset name, version/date, and the download URL**. Also note it in the
README later. This matters for the reproducibility checklist (`execution.md` §11).

## 5. First notebook run

Open `notebooks/01_traceback.ipynb`, select the `.venv` kernel, and run the
**Setup** cell. It should import `src.load / clean / stats` without error (the
functions are stubs that raise `NotImplementedError` — that's expected; you're only
checking the imports resolve). Set `DATASET = "cip_dmd"` or `"bosch"`.

---

## Tools today
- **VS Code** + Python/Jupyter extensions — your editor and notebook host.
- **venv + pip** — isolated environment.
- **Kaggle** (browser or `kaggle` CLI) if you take Option B.

## Hints & pitfalls
- **Don't fight the CiP-DMD download past the hour.** The fallback is there so a
  data-access snag never costs you the project. Switching is a *documented plan*,
  not a failure.
- **Bosch is big.** Never load `train_numeric.csv` whole into memory to "look
  around" — read with `nrows=` / `usecols=` first, then down-sample. You'll build
  the real sampling in `src/load.load_raw` on Day 1/2.
- **Commit the freeze.** Unpinned installs drift; the frozen `requirements.txt` is
  what makes a fresh clone reproduce your numbers.
- Keep raw data **out of git** — it's already git-ignored; don't force-add it.

## Done checklist
- [ ] `.venv` active; `pip install -r requirements.txt` succeeded; versions frozen.
- [ ] `python -c "import ..."` prints `ok`.
- [ ] A usable dataset is in `data/raw/` (CiP-DMD **or** Bosch sample).
- [ ] Notebook Setup cell runs; `DATASET` is set; header records name/version/URL.
- [ ] `git status` does not show `.venv` or raw data.

## What's next
→ [day-2.md](day-2.md): turn the raw files into a data dictionary, a process-flow
sketch, and one tidy row per part.
