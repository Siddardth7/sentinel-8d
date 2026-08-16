# Day 7 — Render, verify, package & publish

**Goal:** produce the headline `reports/8D_Report.pdf`, prove the whole thing
reproduces from a clean run, write the README result + résumé bullet, and tag
`v1.0`. This is the portfolio-ready finish.

**Time budget:** ~3–4 h (≈1 h render + reproducibility, ≈1.5 h README/bullet,
≈0.5 h publish).

**Covers:** `execution.md` §10–12 · **Milestone:** M4.

**Where you left off:** a complete `8D_Report.md` and a full notebook.

---

## 1. Reproducibility pass (do this FIRST)

This is the acceptance test. From a clean state:

```bash
# Restart the kernel and run the notebook top-to-bottom.
# In VS Code: "Restart" then "Run All". Confirm zero errors and that every
# figure + number regenerates.
```

Then walk the checklist from `execution.md` §11:
- [ ] Fresh run reproduces every figure and number.
- [ ] No hard-coded statistics in the 8D — all pulled from notebook outputs.
- [ ] Univariate screen uses FDR/Bonferroni (documented).
- [ ] Multivariate model reports odds ratios **with CIs**.
- [ ] Logistic and tree models agree on the top driver.
- [ ] Root cause passes the physics sanity check.
- [ ] Dataset name, version, URL recorded in README + notebook header.

Fix anything that fails **before** rendering the PDF.

## 2. Render the 8D to PDF

Any of these works — pick what's installed:

```bash
# Option A — pandoc (needs a LaTeX engine or wkhtmltopdf)
pandoc reports/8D_Report.md -o reports/8D_Report.pdf

# Option B — VS Code "Markdown PDF" extension: right-click the file → export PDF

# Option C — print to PDF from a Markdown preview in the browser
```

The PDF is a build artifact and is git-ignored (`.gitignore`) — that's fine; the
`.md` source is what's tracked. If you want the PDF *in* the repo for portfolio
convenience, remove that line from `.gitignore` and commit it deliberately.

## 3. Clean the notebook

- Remove dead/scratch cells and stray prints.
- Make sure the header cell has the final dataset name/version/URL.
- Clear noisy outputs if you like, but keep the ones that show the key results.

## 4. README result summary + résumé bullet

In the root `README.md`, add a short **result** paragraph (one outcome) and one
**quantified résumé bullet**. Templates are in `idea.md` §14 — adapt with your real
numbers, e.g.:

> *"Traced final-inspection failures across an 847-part multi-station machining
> dataset to a single upstream operation via ANOVA and logistic regression
> (p < 0.05); authored an AIAG-format 8D defining the root cause and a permanent
> SPC-based corrective action."*

Also flip the status badge in `README.md` from `planning` to `complete` and update
the progress table in `roadmap.md`.

## 5. Publish & tag

```bash
git add -A
git commit -m "Complete Sentinel-8D: statistical root-cause traceback + 8D report"
git push
git tag v1.0
git push origin v1.0
```

---

## Tools today
- **Jupyter / VS Code** — the reproducibility run and notebook cleanup.
- **pandoc** or a Markdown-to-PDF extension — the render.
- **git** — commit, push, tag.

## Hints & pitfalls
- **Reproducibility before rendering.** Rendering a PDF from numbers you can't
  regenerate is exactly the failure mode this project is built to avoid.
- **Restart-and-Run-All is the real test.** Cells that only work because of leftover
  kernel state will fail a fresh clone — catch them now.
- **The bullet is the deliverable most people will actually read.** Make it
  quantified and specific: named station/parameter, effect size, p-value, the
  corrective action.
- Tag `v1.0` only after the PDF and README are final — the tag is your "done" marker.

## Done checklist
- [ ] Notebook runs clean top-to-bottom; §11 checklist all ticked.
- [ ] `reports/8D_Report.pdf` rendered.
- [ ] Notebook cleaned; header has dataset provenance.
- [ ] README result paragraph + résumé bullet added; badges/roadmap updated.
- [ ] Pushed to GitHub; `v1.0` tagged and pushed.

## What's next
You're done — the case study is portfolio-ready. The D7 hand-off (Control
Plan / PFMEA) feeds directly into **Project 2**. Optional stretches live in
`roadmap.md` (SPC-at-station chart; scale-check the method on full Bosch).
