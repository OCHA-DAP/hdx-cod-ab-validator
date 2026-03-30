# AGENTS.md

This file provides guidance to AI Agents when working with code in this repository.

## Repository Purpose

This is a **specification repository** for the COD-AB (Common Operational Dataset – Administrative Boundaries) format published by UN OCHA. It contains Markdown specifications and example data (in `examples/`). There is no build system, test suite, or application code.

## Structure

- `specs/boundaries.md` — Main specification for admin boundary file layout, column schemas, naming conventions, CRS, and known deviations
- `specs/metadata.md` — Specification for the metadata registry table schema
- `examples/` — Example datasets
- `scripts/` — Validation scripts callable by AI agents (see `scripts/index.json` for the manifest)

## Validation Scripts

Each script in `scripts/index.json` declares an `applies_to` field specifying its intended layer type(s). The controlled vocabulary is:

- `"admin"` — admin boundary polygons (admin0–5). Semantic tag; geometry type alone cannot distinguish these from other polygon layers, so the user must identify which files are admin layers.
- `"lines"` — line geometry layers (LineString/MultiLineString). Auto-detectable from geometry type.
- `"points"` — point geometry layers. Auto-detectable from geometry type.
- `"all"` — applies to every layer regardless of type.

When a user asks you to validate a COD-AB file, check `scripts/index.json` for available scripts and only run a script against files that match its `applies_to` target. Each script exports a `check(path: str) -> dict` function and can also be run as a CLI.

**For a single file**, use the CLI:

```bash
uv run scripts/check_versions.py path/to/file.gpkg
```

**For multiple files**, import the `check()` functions directly in a Python script rather than shelling out per file — subprocess startup cost is ~300ms per call and becomes the dominant bottleneck at scale:

```python
import sys
sys.path.insert(0, "scripts")
import check_versions, check_dates

result = check_versions.check(str(path))
```

Scripts return `{"passed": bool, "violations": [...], "warnings": [...], "info": [...]}`. The CLI exits 0 on pass, 1 on violations. After running one or more validation scripts, present results as a formatted summary report:

**If all checks pass for a group:** show a single `###` heading with "All checks passed" — no table, no messages.

**If any check fails in a group:** use a `###` heading (country name and folder) and render a table where:
- Rows are files
- Columns are validation checks, using clean human-readable names (e.g. `check_versions` → "Version")
- Cells show Pass/Fail

Follow the table with only the failing details: violations (MUST rules broken), warnings (SHOULD rules broken), and info messages — per layer, clearly labeled.

**Always end with an issue-grouped summary table** with columns: Issue | Severity | Folders affected | Files affected. Include both violations (MUST rules) and warnings (SHOULD rules). Group by issue type (e.g. "Missing `valid_on`/`valid_to` columns", "Mixed values within a layer") and count how many folders and files are affected by each. Add a brief sentence interpreting the dominant pattern.

## Editing Guidelines

- Preserve RFC 2119 keyword semantics when editing specs — changes to MUST/SHOULD/MAY have normative impact
- The "Known Deviations" sections document gaps between the spec and current real-world data; keep these accurate as the spec evolves
- New column additions should include: column name, type, max length (if string), nullable status, and notes — matching the table format in the existing specs
