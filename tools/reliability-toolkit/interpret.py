"""
Convert reliability statistics into plain-language interpretations.

The labels used here are commonly cited heuristics rather than universal
psychometric standards. Interpretation should also consider scale length,
purpose, population, dimensionality, and the consequences of measurement
error.
"""

from __future__ import annotations

import math


def interpret_alpha(alpha: float) -> str:
    """
    Return a conventional descriptive label for Cronbach's alpha.

    Thresholds:
        >= 0.90  Excellent
        >= 0.80  Good
        >= 0.70  Acceptable
        >= 0.60  Questionable
        >= 0.50  Poor
        <  0.50  Unacceptable

    These labels are heuristics, not universal standards.
    """
    if not math.isfinite(alpha):
        return "Cronbach's alpha could not be interpreted"

    if alpha >= 0.90:
        return "Excellent internal consistency"

    if alpha >= 0.80:
        return "Good internal consistency"

    if alpha >= 0.70:
        return "Acceptable internal consistency"

    if alpha >= 0.60:
        return "Questionable internal consistency"

    if alpha >= 0.50:
        return "Poor internal consistency"

    return "Unacceptable internal consistency"


def alpha_warnings(alpha: float) -> list[str]:
    """
    Return important qualifications associated with an alpha estimate.

    Warnings are returned for:
    - Undefined or nonfinite alpha values
    - Very high alpha values that may reflect item redundancy
    - Negative alpha values that may indicate coding or scale problems
    """
    if not math.isfinite(alpha):
        return [
            "Alpha is undefined or nonfinite and should not be interpreted."
        ]

    warnings: list[str] = []

    if alpha > 0.95:
        warnings.append(
            "Very high alpha may indicate redundant items. Review whether "
            "some items are measuring nearly identical content."
        )

    if alpha < 0:
        warnings.append(
            "Negative alpha may indicate reverse-coded items, inconsistent "
            "item direction, or substantial multidimensionality."
        )

    return warnings


def item_warning(
    item_total_corr: float,
    threshold: float = 0.30,
) -> str | None:
    """
    Return a review message for a weak or undefined item diagnostic.

    Parameters
    ----------
    item_total_corr:
        Corrected item-total correlation for one item.

    threshold:
        Correlations below this value are flagged for review. The default
        value of 0.30 is a commonly used heuristic rather than a strict rule.

    Returns
    -------
    str | None
        A warning message when the item should be reviewed, otherwise None.
    """
    if not math.isfinite(item_total_corr):
        return (
            "The item-total correlation is undefined, possibly because the "
            "item or remaining scale score has zero variance."
        )

    if item_total_corr < threshold:
        return (
            f"Low corrected item-total correlation "
            f"({item_total_corr:.2f}). Review the item's coding, wording, "
            "variance, and conceptual fit before considering removal."
        )

    return None