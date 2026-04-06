---
version: 0.1.0-draft
---

# Glossary

**ADM0, ADM1, … ADM5**
Administrative levels 0 through 5. ADM0 is the national boundary; ADM1 is the first subnational subdivision; subsequent levels are increasingly granular. The local concept name for each level (e.g. "Province", "District") varies by country.

**admin_level_full**
The highest administrative level for which the dataset has complete national coverage. May be lower than `admin_level_max` if deeper levels exist but do not cover the entire country.

**admin_level_max**
The deepest administrative level present in the dataset, regardless of national coverage.

**BCP 47**
Internet standard for language identification tags (e.g. `en` for English, `fr` for French, `ar` for Arabic). Defined in [RFC 5646](https://www.rfc-editor.org/rfc/rfc5646). Used to identify which language each name column is written in.

**COD (Common Operational Dataset)**
A dataset curated by UN OCHA and considered essential for humanitarian operations. COD-AB is one type; others include COD-PS (population statistics) and COD-CS (country-specific datasets).

**COD-AB**
Common Operational Dataset – Administrative Boundaries. A collection of administrative boundary polygon datasets, one per country, distributed through HDX.

**EPSG:4326**
The WGS 84 geographic coordinate reference system (latitude/longitude). Required for all COD-AB layers.

**EPSG:6933**
World Equidistant Cylindrical equal-area projection. Used for computing `area_sqkm` values.

**Gazetteer**
A tabular spreadsheet of p-codes and associated feature names, distributed alongside the COD-AB geometry files. Enables non-GIS users to work with the administrative taxonomy.

**Major version**
A version increment (e.g. `v01` → `v02`) assigned when changes may break existing downstream systems — joins, scripts, dashboards, or maps cannot simply auto-refresh.

**Maximum Inscribed Circle (MIC)**
An algorithm that finds the largest circle that fits entirely inside a polygon and uses its centre as a representative point. Guarantees the point falls within the polygon even for concave or non-convex shapes. The RECOMMENDED method for computing `center_lat` / `center_lon`.

**Minor version**
A version increment (e.g. `v02` → `v02.01`) assigned when changes are backward-compatible and downstream systems can auto-refresh without disruption.

**OGC Simple Features**
An international standard (ISO 19125) defining valid geometry types and topological rules. All COD-AB geometries must be valid according to this standard.

**P-code (place code)**
A unique geographic identifier for an administrative unit, beginning with the ISO 3166-1 country code followed by numeric digits. P-codes are the primary key for linking datasets across the humanitarian information system.

**RFC 2119**
An IETF standard defining the interpretation of requirement keywords (MUST, SHOULD, MAY, etc.) used throughout this specification.

**UN M49**
A standard maintained by the UN Statistics Division that defines country and territory names in the six official UN languages. Used for the `adm0_name` requirement.

**valid_on**
The date from which the current version of a dataset is considered valid. Non-null for all datasets.

**valid_to**
The date on which a dataset version was superseded. Null for the current (latest) version; non-null for retired versions.

**WGS 84**
World Geodetic System 1984 — the global standard coordinate reference system used by GPS. Required for all COD-AB layers (EPSG:4326).
