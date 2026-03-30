"""
Validate the date columns of a COD-AB boundary file.

Spec: attributes.md § Date Columns

Checks:
  - `valid_on` MUST be present
  - `valid_on` MUST be non-null for all rows
  - All rows MUST share the same `valid_on` value
  - All rows MUST share the same `valid_to` value
  - Date values MUST be parseable as ISO 8601 dates

Usage:
    python scripts/check_dates.py <path/to/file>

Output:
    JSON printed to stdout with keys:
        passed     (bool) — true if no MUST violations
        violations (list) — broken MUST rules
        warnings   (list) — broken SHOULD rules
        info       (list) — notes
"""

import json
import sys
from datetime import date


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


def _parse_date(value) -> bool:
    """Return True if value can be parsed as an ISO 8601 date."""
    import pandas as pd
    if value is None or (hasattr(value, "__class__") and value.__class__.__name__ == "NaTType"):
        return False
    if isinstance(value, (date,)):
        return True
    try:
        pd.Timestamp(value)
        return True
    except Exception:
        return False


def check(path: str) -> dict:
    violations = []
    warnings = []
    info = []

    df = load_attributes(path, columns=["valid_on", "valid_to"])
    columns = list(df.columns)

    # --- valid_on ---
    if "valid_on" not in columns:
        violations.append(
            "`valid_on` column is absent. A `valid_on` column MUST be present in all datasets."
        )
    else:
        null_count = df["valid_on"].isna().sum()
        if null_count > 0:
            violations.append(
                f"`valid_on` has {null_count} null value(s). `valid_on` MUST be non-null for all rows."
            )

        non_null = df["valid_on"].dropna()
        unique_vals = non_null.unique().tolist()

        if len(unique_vals) > 1:
            violations.append(
                f"`valid_on` has {len(unique_vals)} distinct values across rows: {unique_vals}. "
                "All rows in a layer MUST share the same `valid_on` value."
            )

        for v in unique_vals:
            if not _parse_date(v):
                violations.append(
                    f"`valid_on` value {v!r} cannot be parsed as a date. "
                    "Date values MUST be valid ISO 8601 dates."
                )

    # --- valid_to ---
    if "valid_to" not in columns:
        violations.append(
            "`valid_to` column is absent. A `valid_to` column MUST be present in all datasets."
        )
    else:
        unique_vals = df["valid_to"].unique().tolist()

        if len(unique_vals) > 1:
            violations.append(
                f"`valid_to` has {len(unique_vals)} distinct values across rows: {unique_vals}. "
                "All rows in a layer MUST share the same `valid_to` value."
            )

        non_null_to = df["valid_to"].dropna()
        for v in non_null_to.unique().tolist():
            if not _parse_date(v):
                violations.append(
                    f"`valid_to` value {v!r} cannot be parsed as a date. "
                    "Date values MUST be valid ISO 8601 dates."
                )

        null_count = df["valid_to"].isna().sum()
        total = len(df)
        if null_count == total:
            info.append("`valid_to` is null for all rows — dataset is the current (active) version.")
        elif null_count == 0:
            info.append("`valid_to` is non-null for all rows — dataset is a retired version.")
        else:
            # Already flagged as multi-value violation above; no additional info needed
            pass

    passed = len(violations) == 0
    return {"passed": passed, "violations": violations, "warnings": warnings, "info": info}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_dates.py <file>", file=sys.stderr)
        sys.exit(1)

    result = check(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
