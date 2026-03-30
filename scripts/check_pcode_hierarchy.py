"""
Validate that adm{L}_pcode values are hierarchically nested within adm{L-1}_pcode.

Spec: boundaries/codes.md § Uniqueness and Hierarchy

For each consecutive pair of pcode columns present in the file (e.g. adm1_pcode and
adm2_pcode), every adm{L}_pcode value MUST start with the corresponding adm{L-1}_pcode
value on the same row.

Example: if adm1_pcode is "ML03", then adm2_pcode MUST start with "ML03".

Usage:
    python scripts/check_pcode_hierarchy.py <path/to/file>

Output:
    JSON printed to stdout with keys:
        passed     (bool) — true if no MUST violations
        violations (list) — broken MUST rules
        warnings   (list) — broken SHOULD rules
        info       (list) — notes
"""

import json
import sys

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

    # Build consecutive pairs where both columns are present
    pairs = [
        (pcode_cols[i], pcode_cols[i + 1])
        for i in range(len(pcode_cols) - 1)
        if pcode_cols[i + 1] == f"adm{int(pcode_cols[i][3]) + 1}_pcode"
    ]

    if not pairs:
        info.append(
            "No consecutive adm{L}_pcode / adm{L+1}_pcode pairs found — no hierarchy to check."
        )
        return {"passed": True, "violations": violations, "warnings": warnings, "info": info}

    for parent_col, child_col in pairs:
        # Only check rows where both values are present (nulls caught by check_pcode_format)
        sub = df[df[parent_col].notna() & df[child_col].notna()]

        bad = sub[~sub.apply(lambda r: r[child_col].startswith(r[parent_col]), axis=1)]

        if len(bad) > 0:
            examples = list(zip(bad[parent_col], bad[child_col]))
            violations.append(
                f"`{child_col}` does not start with `{parent_col}` for {len(bad)} row(s). "
                f"Examples (parent, child): {_examples(examples)}. "
                "P-codes MUST be hierarchically nested."
            )

    passed = len(violations) == 0
    return {"passed": passed, "violations": violations, "warnings": warnings, "info": info}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_pcode_hierarchy.py <file>", file=sys.stderr)
        sys.exit(1)

    result = check(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
