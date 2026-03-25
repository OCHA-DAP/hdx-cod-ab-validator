# Codes

Version: 0.1.0-draft

## P-Code Columns

For each level L (0 ≤ L ≤ N):

| Column         | Type   | Max length | Notes                                             |
| -------------- | ------ | ---------- | ------------------------------------------------- |
| `adm{L}_pcode` | string | 20         | Place code for the administrative unit at level L |

P-codes (place codes) are alphanumeric strings that uniquely identify an administrative unit. P-codes MUST be hierarchically nested: `adm{L}_pcode` MUST start with `adm{L-1}_pcode` for all L > 0. All p-codes in a column MUST be unique within the file (no duplicates at the same level). P-codes MUST be alphanumeric only (letters and digits, no spaces or special characters).

The admin 0 p-code (`adm0_pcode`) SHOULD equal the country's [ISO 3166-1 alpha-2](https://en.wikipedia.org/wiki/ISO_3166-1_alpha-2) code (e.g., `AF` for Afghanistan).

## Version Column

One of the following MUST be present:

| Column        | Type   | Notes                                  |
| ------------- | ------ | -------------------------------------- |
| `version`     | string | Version string, e.g. `v01` (preferred) |
| `cod_version` | string | Legacy version string, e.g. `V_01`     |

The preferred column name is `version`. The `cod_version` column is a legacy variant present in some older datasets. New datasets MUST use `version`.
