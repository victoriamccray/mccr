# OpenMeasure: Reliability Toolkit

A small researcher-facing web application for evaluating the internal consistency of survey scales. Upload a CSV, select your item columns, and receive **Cronbach's alpha**, **corrected item-total correlations**, **alpha if item deleted**, **split-half reliability**, and **plain-language interpretation**.

This is **v1** of a planned larger project, **OpenMeasure**, a collection of tools for improving measurement quality in research. The first release is intentionally narrow: one measurement problem implemented transparently, tested carefully, and documented with its assumptions and limitations.

---

## Features

- Upload wide-format survey data as a CSV
- Compute Cronbach's alpha
- Compute odd-even split-half reliability with Spearman-Brown correction
- Calculate corrected item-total correlations
- Calculate alpha if each item is removed
- Plain-language interpretation of results
- Report missing data and excluded observations
- Unit-tested statistical functions independent of the UI

---

## Quickstart

```bash
pip install -r requirements.txt
streamlit run app.py
```

Then open the local URL printed by Streamlit (typically `http://localhost:8501`).

A sample dataset is included in:

```text
sample_data/survey_example.csv
```

---

## Input Format

CSV in **wide format**, with one row per participant and one column per survey item.

```csv
participant_id,Q1,Q2,Q3,Q4,Q5
1,4,5,4,5,4
2,3,2,3,2,3
```

Rows containing any missing selected item are excluded from all reliability calculations using **listwise deletion**. The number and percentage of excluded rows are reported.

---

# What It Computes

## Cronbach's Alpha

\[
\alpha=\frac{k}{k-1}
\left(1-\frac{\sum \sigma_i^2}{\sigma_T^2}\right)
\]

where *k* is the number of items.

Cronbach's alpha estimates **internal consistency**, or the degree to which a set of items appears to measure the same underlying construct.

### Conventional Interpretation

| Alpha | Interpretation |
|-------:|----------------|
| ≥ 0.90 | Excellent |
| ≥ 0.80 | Good |
| ≥ 0.70 | Acceptable |
| ≥ 0.60 | Questionable |
| ≥ 0.50 | Poor |
| < 0.50 | Unacceptable |

These descriptive labels are commonly cited heuristic guidelines (George & Mallery, 2003), but interpretation should also consider the scale's length, purpose, target population, and the consequences of measurement error.

---

## Corrected Item-Total Correlation

For each item, OpenMeasure calculates the correlation between that item and the sum of all remaining items (excluding the item itself).

Items with corrected item-total correlations below **0.30** are flagged for review. A low correlation may indicate a poorly functioning item, reverse coding, restricted variability, or multidimensionality rather than automatically indicating that the item should be removed.

---

## Alpha if Item Deleted

Cronbach's alpha is recalculated after removing each item individually.

This diagnostic helps identify items whose removal would substantially increase the scale's internal consistency.

---

## Split-Half Reliability

Items are divided into **odd- and even-numbered halves**. Total scores are calculated for each half, and the correlation between the two half scores is computed.

Because a half-length test generally underestimates the reliability of the full scale, OpenMeasure applies the **Spearman-Brown correction**:

\[
r_{SB}=\frac{2r}{1+r}
\]

where *r* is the correlation between the odd and even halves.

A minimum of **four items** is required for split-half reliability.

---

# What It Does Not Do (Yet)

- Test-retest reliability or intraclass correlation (ICC) for repeated-measures data
- Exploratory or confirmatory factor analysis
- Dimensionality assessment
- Validity analyses (e.g., convergent or discriminant validity)
- Measurement invariance testing

Cronbach's alpha measures **internal consistency**, not whether a scale measures the intended construct or is unidimensional.

---

# Project Structure

```text
openmeasure/
├── README.md
├── app.py
├── requirements.txt
├── core/
│   ├── __init__.py
│   ├── reliability.py      # Statistical functions
│   ├── interpret.py        # Plain-language interpretations
│   ├── validation.py       # Input validation
│   └── plots.py            # Visualizations
├── tests/
│   └── test_reliability.py
├── sample_data/
│   └── survey_example.csv
├── assets/
└── docs/
```

The statistical functions in `core/` are independent of the Streamlit interface and can be imported directly into notebooks, scripts, or future API services.

---

## Running Tests

```bash
pip install pytest
pytest tests/
```

---

## References

Brown, W. (1910). *Some experimental results in the correlation of mental abilities.* *British Journal of Psychology, 3*(3), 296–322.

Cronbach, L. J. (1951). *Coefficient alpha and the internal structure of tests.* *Psychometrika, 16*(3), 297–334.

George, D., & Mallery, P. (2003). *SPSS for Windows Step by Step: A Simple Guide and Reference* (4th ed.). Allyn & Bacon.

Nunnally, J. C. (1978). *Psychometric Theory* (2nd ed.). McGraw-Hill.

---

# Roadmap

- Downloadable PDF and HTML reports
- Intraclass correlation (ICC) for repeated-measures reliability
- Validity module (convergent and discriminant validity)
- Exploratory factor analysis
- FastAPI backend so the statistical engine can be used programmatically
- Additional psychometric diagnostics and visualizations

---

## License

MIT License

---

## Author

**Victoria McCray, MSc**

GitHub: https://github.com/victoriamccray

Portfolio: https://victoriamccray.github.io/


## References

Brown, W. (1910). *Some experimental results in the correlation of mental abilities.* British Journal of Psychology, 3(3), 296–322.

Cronbach, L. J. (1951). *Coefficient alpha and the internal structure of tests.* Psychometrika, 16(3), 297–334. https://doi.org/10.1007/BF02310555

DeVellis, R. F. (2017). *Scale Development: Theory and Applications* (4th ed.). Sage.

George, D., & Mallery, P. (2003). *SPSS for Windows Step by Step: A Simple Guide and Reference* (4th ed.). Allyn & Bacon.

Nunnally, J. C. (1978). *Psychometric Theory* (2nd ed.). McGraw-Hill.

Spearman, C. (1910). *Correlation calculated from faulty data.* British Journal of Psychology, 3(3), 271–295.