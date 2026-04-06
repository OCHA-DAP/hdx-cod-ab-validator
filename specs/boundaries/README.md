---
version: 0.1.0-draft
sources:
  - names.md
  - codes.md
  - versions.md
  - attributes.md
  - geometry.md
  - legacy.md
---

# COD-AB Specification

The Common Operational Dataset – Administrative Boundaries (COD-AB) is a collection of administrative boundary datasets published by the United Nations Office for the Coordination of Humanitarian Affairs (UN OCHA). This specification defines the format and schema for the distribution of these datasets.

COD-ABs are maintained on a country-by-country basis, versioned over time, and cover up to six administrative levels (Admin 0–5). A valid COD-AB MUST include at least one subnational layer (Admin 1 or below); a dataset containing only an Admin 0 layer is not valid.

The key words "MUST", "MUST NOT", "REQUIRED", "SHALL", "SHALL NOT", "SHOULD", "SHOULD NOT", "RECOMMENDED", "MAY", and "OPTIONAL" in this document are to be interpreted as described in [RFC 2119](https://datatracker.ietf.org/doc/html/rfc2119).

## Administrative Levels

| Level          | Typical concept         | Required     |
| -------------- | ----------------------- | ------------ |
| Admin 0 (ADM0) | Country / Territory     | Yes          |
| Admin 1 (ADM1) | Province, Region, State | Yes          |
| Admin 2 (ADM2) | District, Department    | If available |
| Admin 3 (ADM3) | Sub-district, County    | If available |
| Admin 4 (ADM4) | Ward, Sub-county        | If available |
| Admin 5 (ADM5) | Village, Locality       | If available |

Admin levels MUST be contiguous: if level N is present, levels 0 through N−1 MUST also be present. The local concept name for each level (e.g. "Province", "District") varies by country and is recorded in the dataset metadata.

## Admin Boundary Layers (`{iso3}_admin{N}`)

Each admin boundary file represents one administrative level for one country version. Every row in the file is a single administrative unit (polygon) at that level. The lowest-level file is the authoritative source for names and p-codes; all higher-level files MUST be derived from it by selecting the distinct combinations of name and p-code columns for the relevant level. Higher-level geometries MUST be derived by dissolving the lowest-level polygons on the parent p-code — this is the only method that guarantees coincident boundaries across layers.

### Column Order

Columns SHOULD appear in the following order within each file:

1. Current-level columns: `adm{N}_name`, `adm{N}_name1`, `adm{N}_name2`, `adm{N}_name3`, `adm{N}_pcode`
2. Ancestor columns: name and p-code columns for each level from N−1 down to 0
3. `valid_on`, `valid_to`
4. `area_sqkm`, `version` (or `cod_version`)
5. `lang`, `lang1`, `lang2`, `lang3`
6. `adm{N}_ref_name` (if present)
7. `iso2`, `iso3` (admin 0 only)
8. `center_lat`, `center_lon`

## Example Column Set

For an admin level 2 file with English primary, Sinhala secondary, and Tamil tertiary language (Sri Lanka, `lka_admin2`):

```text
adm2_name         (string, primary name in English)
adm2_name1        (string, name in Sinhala, nullable)
adm2_name2        (string, name in Tamil, nullable)
adm2_name3        (string, nullable)
adm2_pcode        (string, e.g. "LK11")
adm1_name         (string, parent admin 1 name)
adm1_name1        (string, nullable)
adm1_name2        (string, nullable)
adm1_name3        (string, nullable)
adm1_pcode        (string, e.g. "LK1")
adm0_name         (string, country name)
adm0_name1        (string, nullable)
adm0_name2        (string, nullable)
adm0_name3        (string, nullable)
adm0_pcode        (string, e.g. "LK")
valid_on          (date)
valid_to          (date, nullable)
area_sqkm         (double)
version           (string, e.g. "v03")
lang              (string, e.g. "en")
lang1             (string, e.g. "si", nullable)
lang2             (string, e.g. "ta", nullable)
lang3             (string, nullable)
center_lat        (double)
center_lon        (double)
```
