# OpenMeasure: Reliability Toolkit

OpenMeasure is a small researcher-facing web application for evaluating the internal consistency of survey scales. Users can upload a wide-format CSV, select item columns, and receive Cronbach's alpha, item diagnostics, split-half reliability, and plain-language interpretation.

This first release is intentionally narrow: one measurement problem implemented transparently, tested carefully, and documented with its assumptions and limitations.

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL Streamlit prints (usually `http://localhost:8501`).

A sample dataset is in `sample_data/survey_example.csv` if you want to try
it without your own data.

## Input format

CSV, wide format: one row per participant, one column per item.

```
participant_id,Q1,Q2,Q3,Q4,Q5
1,4,5,4,5,4
2,3,2,3,2,3
```

Missing values are handled via listwise deletion (rows with any missing
item are excluded from the reliability calculation, but counted and
reported).

## What it computes

**Cronbach's alpha**

```
α = (k / (k - 1)) * (1 - Σ(item variances) / variance(total score))
```

where *k* is the number of items. Measures internal consistency, i.e.
whether items appear to measure the same underlying construct.

Interpretation thresholds (George & Mallery, 2003):

| Alpha | Interpretation |
|-------|---------------|
| ≥ 0.90 | Excellent |
| ≥ 0.80 | Good |
| ≥ 0.70 | Acceptable |
| ≥ 0.60 | Questionable |
| ≥ 0.50 | Poor |
| < 0.50 | Unacceptable |

These are conventions, not statistical laws. Context matters (a 6-item
screening tool and a 40-item validated scale don't need the same bar).

**Corrected item-total correlation**

For each item, the correlation between that item and the sum of all
*other* items (the item itself is excluded to avoid inflating its own
correlation). Items below 0.30 are flagged as candidates for review or
removal.

**Alpha if item dropped**

Alpha recomputed with each item removed one at a time, so you can see
whether removing a weak item would improve the scale.

**Split-half reliability + Spearman-Brown correction**

Items are randomly split into two halves, and the correlation between the
two half-scores is computed. Because splitting a test in half typically
underestimates reliability of the full test, the Spearman-Brown formula
corrects for this:

```
r_sb = 2r / (1 + r)
```

where *r* is the raw split-half correlation. Requires at least 4 items.

## What it does NOT do (yet)

- No test-retest or intraclass correlation (ICC) for repeated-measures /
  time-series reliability. Cronbach's alpha assumes items measured once,
  not the same item measured across time.
- No factor analysis or dimensionality checks. Alpha does not verify a
  scale is unidimensional, high alpha with multiple underlying factors is
  possible and is a known limitation of the statistic.
- No validity analysis (alpha measures consistency, not whether the scale
  measures what it claims to measure).

## Project structure

```
reliability-toolkit/
  core/
    reliability.py   # pure statistical functions, no UI code
    interpret.py      # thresholds -> plain language
  app.py              # Streamlit UI
  tests/
    test_reliability.py
  sample_data/
    survey_example.csv
```

`core/` has no dependency on Streamlit and can be imported and used
directly from a script, notebook, or future API.

## Running tests

```bash
pip install pytest
pytest tests/
```

## References

- Cronbach, L. J. (1951). Coefficient alpha and the internal structure of
  tests. *Psychometrika, 16*(3), 297–334.
- George, D., & Mallery, P. (2003). *SPSS for Windows step by step: A
  simple guide and reference, 11.0 update* (4th ed.). Allyn & Bacon.
- Brown, W. (1910). Some experimental results in the correlation of
  mental abilities. *British Journal of Psychology, 3*(3), 296–322.
  (Spearman-Brown correction)
- Nunnally, J. C. (1978). *Psychometric theory* (2nd ed.). McGraw-Hill.

## Roadmap

- [ ] Downloadable PDF/HTML report
- [ ] ICC module for repeated-measures reliability
- [ ] Validity module (convergent/discriminant via correlation matrices)
- [ ] FastAPI wrapper so `core/` can be used as a hosted API, not just a UI
