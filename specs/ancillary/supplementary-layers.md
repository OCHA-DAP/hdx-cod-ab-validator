# Supplementary Layers

Version: 0.1.0-draft

## Admin Lines (`{iso3}_adminlines`)

Boundary line representations of the administrative units. These are derived from the admin boundary polygons and may not be present for all countries.

| Column       | Type                    | Notes                                                     |
| ------------ | ----------------------- | --------------------------------------------------------- |
| `adm_level`  | int16                   | Admin level this boundary segment represents              |
| `name`       | string                  | Name of the boundary segment                              |
| `valid_on`   | timestamp with timezone | See [date columns](boundaries/attributes.md#date-columns) |
| `valid_to`   | timestamp               | See [date columns](boundaries/attributes.md#date-columns) |
| `version`    | string                  | See [version column](boundaries/codes.md#version-column)  |
| `right_pcod` | string                  | P-code of the unit to the right of the line               |
| `left_pcod`  | string                  | P-code of the unit to the left of the line                |

## Admin Points (`{iso3}_adminpoints`)

Point representations of administrative units (e.g. label points). Schema varies by country and is not yet standardized. Where these points serve as representative points for polygons, they SHOULD be generated using a Maximum Inscribed Circle (MIC) algorithm, consistent with the `center_lat`/`center_lon` columns described in [attributes](boundaries/attributes.md#computed-columns).

## Admin Capitals (`{iso3}_admincapitals`)

Point locations of administrative capital cities. These are real-world populated places (government seats), not geometric centroids. Schema varies by country and is not yet standardized.

ADM1 capitals MUST be present. ADM2 capitals SHOULD be present. Lower levels are OPTIONAL.
