"""
Validate the format of adm{L}_pcode columns in a COD-AB boundary file.

Spec: boundaries/codes.md § P-Code Format

Checks (per adm{L}_pcode column found in the file):
  - Values MUST be non-null
  - Values MUST match: 2–3 uppercase letters (country code) followed by digits only
  - Values MUST NOT contain delimiters (. or -)
  - Values MUST be at most 20 characters
  - Values MUST be unique within the column
  - Country code prefix MUST be a recognised ISO 3166-1 alpha-2 or alpha-3 code (not just any letters)
  - Alpha-3 country code prefix SHOULD be replaced with alpha-2

Usage:
    python scripts/check_pcode_format.py <path/to/file>

Output:
    JSON printed to stdout with keys:
        passed     (bool) — true if no MUST violations
        violations (list) — broken MUST rules
        warnings   (list) — broken SHOULD rules
        info       (list) — notes
"""

import json
import re
import sys

import pycountry

# Admin0 codes are just the country letters (e.g. "ML"); sub-national levels add digits
PCODE_RE = re.compile(r"^([A-Z]{2,3})\d*$")
ALPHA3_RE = re.compile(r"^[A-Z]{3}")

VALID_ALPHA2 = {c.alpha_2 for c in pycountry.countries}
VALID_ALPHA3 = {c.alpha_3 for c in pycountry.countries}

ALL_PCODE_COLS = [f"adm{L}_pcode" for L in range(6)]


def load_attributes(path: str, columns: list[str] | None = None):
    """Return a DataFrame with only the requested attribute columns (no geometry)."""
    import pandas as pd

    ext = path.rsplit(".", 1)[-1].lower()

    if ext == "csv":
        col_filter = (lambda c: c in columns) if columns else None
        return pd.read_csv(path, dtype=str, usecols=col_filter)

    if ext in ("xlsx", "xls"):
        col_filter = (lambda c: c in columns) if columns else None
        return pd.read_excel(path, usecols=col_filter)

    if ext == "parquet":
        import pyarrow.parquet as pq
        available = set(pq.read_schema(path).names)
        sel = [c for c in columns if c in available] if columns else None
        return pd.read_parquet(path, columns=sel)

    # Spatial formats (GeoPackage, GeoJSON, Shapefile, etc.)
    import geopandas as gpd
    df = gpd.read_file(path, ignore_geometry=True)
    if columns:
        df = df[[c for c in columns if c in df.columns]]
    return df


def _examples(values, n=5):
    """Return a short string showing up to n example values with a count if truncated."""
    sample = list(values)[:n]
    if len(values) <= n:
        return str(sample)
    return f"{sample} … ({len(values)} total)"


def check(path: str) -> dict:
    violations = []
    warnings = []
    info = []

    df = load_attributes(path, columns=ALL_PCODE_COLS)
    pcode_cols = [c for c in ALL_PCODE_COLS if c in df.columns]

    if not pcode_cols:
        info.append("No adm{L}_pcode columns found in this file.")
        return {"passed": True, "violations": violations, "warnings": warnings, "info": info}

    # Uniqueness only applies to the leaf level — parent pcode columns naturally repeat
    # in lower-level files (e.g. adm1_pcode repeats across all adm2 rows in that region)
    leaf_col = pcode_cols[-1]

    for col in pcode_cols:
        # Null check
        null_count = df[col].isna().sum()
        if null_count > 0:
            violations.append(
                f"`{col}` has {null_count} null value(s). P-codes MUST be non-null."
            )

        non_null = df[col].dropna()

        # Format check: 2–3 uppercase letters + digits only
        bad_format = [v for v in non_null.unique() if not PCODE_RE.fullmatch(str(v))]
        if bad_format:
            violations.append(
                f"`{col}` has values that do not match the required format "
                f"(2–3 uppercase letters followed by digits only): {_examples(bad_format)}. "
                "P-codes MUST start with a country code followed by digits only, with no other characters."
            )

        # ISO 3166-1 check: prefix must be a real alpha-2 or alpha-3 code
        well_formed = [v for v in non_null.unique() if PCODE_RE.fullmatch(str(v))]
        bad_iso = []
        for v in well_formed:
            prefix = PCODE_RE.fullmatch(str(v)).group(1)  # type: ignore[union-attr]
            if prefix not in VALID_ALPHA2 and prefix not in VALID_ALPHA3:
                bad_iso.append(v)
        if bad_iso:
            violations.append(
                f"`{col}` has values with a country code prefix that is not a valid ISO 3166-1 "
                f"alpha-2 or alpha-3 code: {_examples(bad_iso)}. "
                "P-codes MUST start with the ISO 3166-1 country code."
            )

        # Delimiter check (catches . and - explicitly for a clearer message)
        has_delimiter = [v for v in non_null.unique() if "." in str(v) or "-" in str(v)]
        if has_delimiter:
            violations.append(
                f"`{col}` has values containing delimiters (. or -): {_examples(has_delimiter)}. "
                "Delimiters MUST NOT appear in p-code values."
            )

        # Length check
        too_long = [v for v in non_null.unique() if len(str(v)) > 20]
        if too_long:
            violations.append(
                f"`{col}` has values exceeding 20 characters: {_examples(too_long)}. "
                "P-codes MUST be at most 20 characters."
            )

        # Uniqueness check — only for the leaf level of this file
        if col == leaf_col:
            dupes = non_null[non_null.duplicated()].unique().tolist()
            if dupes:
                violations.append(
                    f"`{col}` has {len(dupes)} duplicate value(s): {_examples(dupes)}. "
                    "P-codes MUST be unique within their administrative level."
                )

        # Alpha-3 warning (SHOULD use alpha-2)
        alpha3_vals = [v for v in non_null.unique() if ALPHA3_RE.match(str(v))]
        if alpha3_vals:
            warnings.append(
                f"`{col}` uses a 3-letter country code prefix (e.g. {_examples(alpha3_vals[:3])}). "
                "Alpha-2 (2-letter) country code prefix SHOULD be preferred."
            )

    passed = len(violations) == 0
    return {"passed": passed, "violations": violations, "warnings": warnings, "info": info}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_pcode_format.py <file>", file=sys.stderr)
        sys.exit(1)

    result = check(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
