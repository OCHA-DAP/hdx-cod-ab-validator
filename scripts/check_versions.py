"""
Validate the version column of a COD-AB boundary file.

Spec: validator.md § Versions

Usage:
    python scripts/check_versions.py <path/to/file>

Output:
    JSON printed to stdout with keys:
        passed   (bool)   — true if no MUST violations
        violations (list) — broken MUST rules
        warnings   (list) — broken SHOULD rules
        info       (list) — notes (e.g. known deviations)
"""

import json
import sys
import re

MAJOR_RE = re.compile(r"^v\d{2}$")
MINOR_RE = re.compile(r"^v\d{2}\.\d{2}$")


def load_attributes(path: str, columns: list[str] | None = None):
    """Return a DataFrame with only the requested attribute columns (no geometry).

    Accepts any tabular or geodata format readable by pandas or geopandas:
    CSV, Parquet (including GeoParquet), Excel, GeoJSON, GeoPackage, Shapefile, FlatGeobuf, etc.
    """
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


def check(path: str) -> dict:
    violations = []
    warnings = []
    info = []

    df = load_attributes(path, columns=["version", "cod_version"])
    columns = list(df.columns)

    has_version = "version" in columns
    has_cod_version = "cod_version" in columns

    if not has_version and not has_cod_version:
        violations.append(
            "version column is absent. A `version` column MUST be present in all datasets."
        )
        return {"passed": False, "violations": violations, "warnings": warnings, "info": info}

    if has_cod_version and not has_version:
        info.append(
            "Dataset uses `cod_version` instead of `version` — this is a known deviation "
            "in older datasets and SHOULD be updated to `version` when the dataset is revised."
        )
        col = "cod_version"
    else:
        col = "version"

    values = df[col].dropna().unique().tolist()

    if len(values) == 0:
        violations.append(f"`{col}` column is entirely null.")
        return {"passed": False, "violations": violations, "warnings": warnings, "info": info}

    if len(values) > 1:
        violations.append(
            f"`{col}` has multiple distinct values across rows: {values}. "
            "All rows in a layer must share the same version."
        )

    for v in values:
        v_str = str(v)
        if col == "cod_version":
            # Known deviation: V_01 format — flag as info, not violation
            if not (MAJOR_RE.match(v_str) or MINOR_RE.match(v_str)):
                info.append(
                    f"`cod_version` value {v_str!r} does not match the current format "
                    f"(e.g. `v01` or `v02.01`). This is expected for legacy datasets."
                )
        else:
            if not (MAJOR_RE.match(v_str) or MINOR_RE.match(v_str)):
                violations.append(
                    f"`version` value {v_str!r} does not match the required format. "
                    "Must be `v{{NN}}` (e.g. `v01`) or `v{{NN}}.{{NN}}` (e.g. `v02.01`), "
                    "with zero-padded two-digit components."
                )

    passed = len(violations) == 0
    return {"passed": passed, "violations": violations, "warnings": warnings, "info": info}


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("Usage: python scripts/check_versions.py <file>", file=sys.stderr)
        sys.exit(1)

    result = check(sys.argv[1])
    print(json.dumps(result, indent=2))
    sys.exit(0 if result["passed"] else 1)
