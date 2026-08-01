"""
OpenMeasure: Reliability Toolkit

Streamlit user interface. All statistical calculations live in core/.
This file handles data upload, column selection, validation, and presentation.

Run with:
    streamlit run app.py
"""

from pathlib import Path

import pandas as pd
import streamlit as st

from core import interpret as interp
from core import reliability as rel


SAMPLE_DATA_PATH = Path("sample_data/survey_example.csv")


st.set_page_config(
    page_title="OpenMeasure",
    page_icon="📊",
    layout="centered",
)

st.title("📊 OpenMeasure")
st.caption("Reliability Toolkit: Cronbach's alpha and item diagnostics")

st.divider()
st.subheader("1. Upload your data")

uploaded_file = st.file_uploader(
    "CSV file in wide format, with one row per participant",
    type=["csv"],
)

if uploaded_file is None:
    st.info(
        "Upload a CSV to get started, or download the sample dataset below."
    )

    if SAMPLE_DATA_PATH.exists():
        with SAMPLE_DATA_PATH.open("rb") as sample_file:
            st.download_button(
                label="Download sample dataset",
                data=sample_file,
                file_name="survey_example.csv",
                mime="text/csv",
            )
    else:
        st.warning(
            "The sample dataset could not be found at "
            "`sample_data/survey_example.csv`."
        )

    st.stop()


try:
    dataframe = pd.read_csv(uploaded_file)
except (pd.errors.ParserError, UnicodeDecodeError, ValueError) as error:
    st.error(
        "The uploaded file could not be read as a CSV. "
        "Check the file format, delimiter, and text encoding."
    )
    st.caption(str(error))
    st.stop()


if dataframe.empty:
    st.error("The uploaded CSV contains no data rows.")
    st.stop()

if dataframe.shape[1] < 2:
    st.error("The uploaded CSV must contain at least two columns.")
    st.stop()


st.write(
    f"Loaded **{dataframe.shape[0]} rows** and "
    f"**{dataframe.shape[1]} columns**."
)
st.dataframe(
    dataframe.head(),
    use_container_width=True,
    hide_index=True,
)


st.divider()
st.subheader("2. Select columns")

id_column = st.selectbox(
    "Participant ID column",
    options=["(none)", *dataframe.columns.tolist()],
    help=(
        "This column is excluded from the reliability analysis. "
        "Choose '(none)' if the dataset has no participant identifier."
    ),
)

excluded_id = None if id_column == "(none)" else id_column

candidate_columns = [
    column
    for column in dataframe.columns
    if column != excluded_id
]

numeric_columns = [
    column
    for column in candidate_columns
    if pd.api.types.is_numeric_dtype(dataframe[column])
]

item_columns = st.multiselect(
    "Items to include in the reliability analysis",
    options=candidate_columns,
    default=numeric_columns,
    help=(
        "Select numeric columns representing scale items. "
        "At least two items are required."
    ),
)

if len(item_columns) < 2:
    st.warning("Select at least two item columns to compute reliability.")

analyze_clicked = st.button(
    "Analyze",
    type="primary",
    disabled=len(item_columns) < 2,
)


if analyze_clicked:
    selected_data = dataframe.loc[:, item_columns].copy()

    conversion_failures: dict[str, int] = {}

    for column in selected_data.columns:
        original_missing = selected_data[column].isna()
        converted = pd.to_numeric(
            selected_data[column],
            errors="coerce",
        )

        newly_missing = converted.isna() & ~original_missing

        if newly_missing.any():
            conversion_failures[str(column)] = int(newly_missing.sum())

        selected_data[column] = converted

    if conversion_failures:
        details = ", ".join(
            f"{column}: {count}"
            for column, count in conversion_failures.items()
        )

        st.error(
            "Some selected item columns contain nonnumeric values. "
            "Please correct the data or select different columns."
        )
        st.caption(f"Values that could not be converted: {details}")
        st.stop()

    try:
        result = rel.analyze(selected_data)
    except (TypeError, ValueError) as error:
        st.error(str(error))
        st.stop()

    st.divider()
    st.subheader("Dataset")

    dataset_col_1, dataset_col_2, dataset_col_3 = st.columns(3)

    dataset_col_1.metric(
        "Participants",
        result.n_participants,
    )
    dataset_col_2.metric(
        "Items",
        result.n_items,
    )
    dataset_col_3.metric(
        "Excluded cases",
        result.n_excluded_cases,
    )

    st.caption(
        f"Complete cases used: {result.n_complete_cases} | "
        f"Excluded cases: {result.pct_excluded_cases:.1f}% | "
        f"Missing item cells: {result.pct_missing_cells:.1f}%"
    )

    if result.n_excluded_cases > 0:
        st.info(
            "Rows containing a missing value in any selected item were "
            "excluded from all reliability calculations using listwise deletion."
        )

    st.divider()
    st.subheader("Reliability")

    reliability_col_1, reliability_col_2, reliability_col_3 = st.columns(3)

    reliability_col_1.metric(
        "Cronbach's α",
        f"{result.cronbach_alpha:.2f}",
    )

    if result.split_half_correlation is not None:
        reliability_col_2.metric(
            "Split-half r",
            f"{result.split_half_correlation:.2f}",
        )
    else:
        reliability_col_2.metric(
            "Split-half r",
            "Not available",
        )

    if result.spearman_brown is not None:
        reliability_col_3.metric(
            "Spearman-Brown",
            f"{result.spearman_brown:.2f}",
        )
    else:
        reliability_col_3.metric(
            "Spearman-Brown",
            "Not available",
        )

    if result.split_half_correlation is None:
        st.caption(
            "Odd-even split-half reliability requires at least four items, "
            "an even number of items, and nonzero variance in both halves."
        )

    alpha_interpretation = interp.interpret_alpha(
        result.cronbach_alpha
    )
    st.success(f"**{alpha_interpretation}**")

    st.caption(
        "Interpretive labels are conventional guidelines. "
        "Interpretation should also consider scale length, purpose, "
        "population, and the consequences of measurement error."
    )

    for warning in interp.alpha_warnings(
        result.cronbach_alpha
    ):
        st.warning(warning)

    st.divider()
    st.subheader("Item diagnostics")

    diagnostic_rows: list[dict[str, object]] = []

    for diagnostic in result.item_diagnostics:
        diagnostic_rows.append(
            {
                "Item": diagnostic.item,
                "Item-total correlation": (
                    round(diagnostic.item_total_corr, 3)
                    if pd.notna(diagnostic.item_total_corr)
                    else None
                ),
                "α if dropped": (
                    round(diagnostic.alpha_if_dropped, 3)
                    if pd.notna(diagnostic.alpha_if_dropped)
                    else None
                ),
                "Review": "⚠️" if diagnostic.flagged else "✅",
            }
        )

    diagnostic_dataframe = pd.DataFrame(diagnostic_rows)

    st.dataframe(
        diagnostic_dataframe,
        use_container_width=True,
        hide_index=True,
    )

    for diagnostic in result.item_diagnostics:
        message = interp.item_warning(
            diagnostic.item_total_corr
        )

        if message:
            st.caption(
                f"**{diagnostic.item}**: {message}"
            )

    valid_dropped_alphas = [
        diagnostic
        for diagnostic in result.item_diagnostics
        if pd.notna(diagnostic.alpha_if_dropped)
    ]

    if valid_dropped_alphas:
        best_drop = max(
            valid_dropped_alphas,
            key=lambda diagnostic: diagnostic.alpha_if_dropped,
        )

        if best_drop.alpha_if_dropped > result.cronbach_alpha:
            st.info(
                f"Removing **{best_drop.item}** would raise alpha from "
                f"{result.cronbach_alpha:.2f} to "
                f"{best_drop.alpha_if_dropped:.2f}. "
                "This item should be reviewed rather than automatically removed."
            )

    st.divider()
    st.subheader("Item-total correlation chart")

    chart_rows = [
        {
            "Item": diagnostic.item,
            "Item-total correlation": diagnostic.item_total_corr,
        }
        for diagnostic in result.item_diagnostics
        if pd.notna(diagnostic.item_total_corr)
    ]

    if chart_rows:
        chart_dataframe = (
            pd.DataFrame(chart_rows)
            .set_index("Item")
        )

        st.bar_chart(
            chart_dataframe,
            use_container_width=True,
        )
    else:
        st.info(
            "Item-total correlations could not be calculated for the "
            "selected items."
        )