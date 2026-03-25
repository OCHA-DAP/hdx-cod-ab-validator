# File Structure

Version: 0.1.0-draft

## File Layout

The file layout is:

```text
cod_ab_{iso3}_{version}/    # one directory per country version
  {iso3}_admin0             # admin level 0 (country)
  {iso3}_admin1             # admin level 1
  {iso3}_admin2             # admin level 2 (if present)
  {iso3}_admin3             # admin level 3 (if present)
  {iso3}_admin4             # admin level 4 (if present)
  {iso3}_admin5             # admin level 5 (if present)
  {iso3}_adminlines         # boundary lines (if present)
  {iso3}_adminpoints        # administrative points (if present)
  {iso3}_admincapitals      # administrative capitals (if present)
```

### Directory Naming

Each versioned country dataset has its own directory named `cod_ab_{iso3}_{version}` where:

- `{iso3}` is the [ISO 3166-1 alpha-3](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-3) country code in lowercase (e.g., `afg`, `eth`)
- `{version}` is the dataset version, formatted as `v{NN}` (e.g., `v01`, `v02`)

> **Note:** Some existing directories use the format `v_{NN}` (e.g., `cod_ab_blr_v_01`). This is a legacy naming convention. New datasets SHOULD use the `v{NN}` format.

### File Naming

Each admin boundary file is named `{iso3}_admin{N}` where `{N}` is the integer admin level (0–5). The ISO3 code MUST be lowercase. Admin level 0 (country boundary) and Admin level 1 MUST be present; higher levels are present only if the country has data at that level. Admin levels MUST be contiguous: if level N is present, levels 0 through N-1 MUST also be present.

### Coordinate Reference System

All geometries MUST use [EPSG:4326](https://epsg.io/4326) (WGS 84, geographic latitude/longitude).
