# Codes

Version: 0.1.0-draft

## P-Code Columns

For each level L (0 ≤ L ≤ N):

| Column         | Type   | Max length | Notes                                             |
| -------------- | ------ | ---------- | ------------------------------------------------- |
| `adm{L}_pcode` | string | 20         | Place code for the administrative unit at level L |

P-codes (place codes) are alphanumeric strings that uniquely identify an administrative unit. P-codes MUST be hierarchically nested: `adm{L}_pcode` MUST start with `adm{L-1}_pcode` for all L > 0. All p-codes in a column MUST be unique within the file (no duplicates at the same level). P-codes MUST be alphanumeric only (letters and digits, no spaces or special characters).

The admin 0 p-code (`adm0_pcode`) SHOULD equal the country's [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code (e.g., `AF` for Afghanistan).

### Relationship to Government Codes

P-codes SHOULD be derived from official government codes where they exist. Government codes are typically zero-padded numeric strings (e.g., `01`, `02`). The ISO 3166-1 alpha-2 country code is prepended to form the p-code (e.g., `AF01`, `AF02`). P-codes MUST be typed as strings to preserve leading zeros that would be lost if treated as integers. The government's existing digit width and padding MUST be reproduced exactly.

### Fallback When No Government Codes Exist

When no official government coding system exists, units SHOULD be sorted alphanumerically by name and assigned sequential numbers. The numeric portion SHOULD use the minimum number of digits required to represent all units at that level, with zero-padding applied consistently. For example, if a level has 4 units, single digits are sufficient (`UG1`–`UG4`); if a level has 10 or more units, two digits are required (`SS01`–`SS10`).

### Continuity Across Versions

P-codes SHOULD maintain continuity with the previous dataset version so that codes remain stable across updates. Continuity MAY not be achievable when the government introduces a substantially new boundary system, in which case the p-codes SHOULD follow the new government codes.

## Version Column

One of the following MUST be present:

| Column        | Type   | Notes                                  |
| ------------- | ------ | -------------------------------------- |
| `version`     | string | Version string, e.g. `v01` (preferred) |
| `cod_version` | string | Legacy version string, e.g. `V_01`     |

The preferred column name is `version`. The `cod_version` column is a legacy variant present in some older datasets. New datasets MUST use `version`.
