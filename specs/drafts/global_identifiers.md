---
version: 0.1.0-draft
status: proposal
---

# Global Identifiers

This document proposes a scheme for assigning globally stable, persistent identifiers to administrative units in COD-AB datasets. P-codes, as defined in [codes.md](codes.md), are not designed for this purpose: they encode geographic hierarchy and are only guaranteed unique within a given dataset version. Global identifiers are a separate, orthogonal concept.

UIDs are not embedded in boundary files. Instead, they live in an external registry that maps each UID to every P-code and dataset version in which that unit appears. Boundary files are unchanged; the registry is the join layer between stable identifiers and versioned data.

## Identifier Format

Each administrative unit is assigned a UUID v4 (e.g. `7f3a9b2c-4d5e-4f6a-8b9c-0d1e2f3a4b5c`) by UN OCHA, which acts as the central issuing authority. UUIDs are opaque — they encode no geographic or hierarchical information — and are assigned once and never reused or reassigned, regardless of boundary changes, P-code resets, or dataset restructuring.

UUIDs are requested from and registered in the UN OCHA COD-AB registry before a dataset is published. The registry is the authoritative record of which UID corresponds to which administrative unit.

## Registry Table

The registry is a single global table maintained by UN OCHA. It contains one row per `(uid, version)` combination — that is, one row each time a unit appears in a published dataset version.

| Column      | Type    | Notes                                                              |
| ----------- | ------- | ------------------------------------------------------------------ |
| `uid`       | string  | UN OCHA-issued UUID v4                                             |
| `iso2`      | string  | ISO 3166-1 alpha-2 country code                                    |
| `adm_level` | integer | Administrative level (0, 1, 2, …)                                  |
| `pcode`     | string  | P-code for this unit in this version                               |
| `version`   | string  | Dataset version in which this P-code appears (e.g. `v01`, `v02`)  |

The combination of `(iso2, adm_level, pcode, version)` MUST be unique within the registry. A single `uid` will appear in multiple rows if the unit exists across multiple dataset versions, and MAY appear with different `pcode` values if the P-code changed between versions.

### Joining to Boundary Data

To retrieve the boundary geometry or attributes for a given UID in a given version:

1. Look up `(iso2, adm_level, pcode, version)` in the registry for the target `uid` and version.
2. Open the corresponding boundary file for that country, level, and version.
3. Filter rows where `adm{L}_pcode = pcode`.

To find all versions in which a unit has appeared, query the registry for all rows with a given `uid`.

### Example

The unit "Acholi" (Uganda admin 1) is published in versions `v01` and `v02` with the same P-code, then assigned a new P-code in `v03` after redistricting.

| uid          | iso2 | adm_level | pcode  | version |
| ------------ | ---- | --------- | ------ | ------- |
| e5f6a7b8-…   | UG   | 1         | UG101  | v01     |
| e5f6a7b8-…   | UG   | 1         | UG101  | v02     |
| e5f6a7b8-…   | UG   | 1         | UG201  | v03     |

## Change Taxonomy

Administrative restructuring falls into the following event types. Each type has different implications for identifier continuity and registry entries.

### Name Change

The unit's official name changes but its geographic extent and administrative status are unchanged.

- The unit retains its existing UID.
- A new registry row is added for the new version with the same UID and P-code.
- No linkage record is required.

### Boundary Adjustment

The unit's boundary is modified but the unit's identity is continuous — it covers substantially the same territory and retains its role in the hierarchy.

A boundary change SHOULD be treated as an adjustment (same UID) when:

- The area change is less than approximately 10% of the unit's total area, AND
- No change is made to the unit's administrative level or parent unit, AND
- The P-code is unchanged.

A boundary change MUST be treated as a replacement (new UID) when it results from a formal administrative act that dissolves the old unit and constitutes a new one — even if the geographic difference appears small.

### Split

One unit is divided into two or more successor units.

- The original unit receives no further registry entries after the split version.
- Each successor unit is assigned a new UID and added to the registry from the new version onward.
- Each successor unit MUST record the original unit's UID as its predecessor in the linkage table (see below).

### Merge

Two or more units are combined into a single successor unit.

- All predecessor units receive no further registry entries after the merge version.
- The successor unit is assigned a new UID, even if it shares a name with one of the predecessors.
- The successor unit MUST record all predecessor UIDs in the linkage table.

### Absorption

One unit is dissolved and its territory is added to an existing neighbor, which retains its identity.

- The absorbed unit receives no further registry entries.
- The absorbing unit retains its UID and continues to receive registry entries in new versions.
- A linkage record MUST be created from the absorbed unit's UID to the absorbing unit's UID with relationship `absorbed_into`.

### Complete Redistricting

An entire administrative level is restructured — for example, a country reorganises 10 regions into 15 new provinces.

- All units at the affected level receive no further registry entries.
- All new units are assigned new UIDs and added to the registry.
- Where a new unit's territory corresponds predominantly (> 50% area overlap) to a single predecessor, a linkage record SHOULD be created. Where territory is divided across multiple predecessors, linkage records SHOULD be created for all predecessors with an `overlap_pct` value.
- Where no reliable geographic correspondence can be established, linkage MAY be omitted rather than guessed.

### Creation

A new administrative level is introduced, or a new unit is created in territory that was previously unclassified.

- A new UID is assigned and added to the registry.
- No predecessor linkage is required.

### Abolishment

A unit is dissolved with no successor — its territory reverts to a parent level or is redistributed without a single identifiable heir.

- The unit receives no further registry entries.
- The linkage table SHOULD record relationship `abolished` with no `target_uid`.

## Linkage Table

Unit succession is recorded in a separate linkage table maintained by UN OCHA alongside the registry. It contains one row per `(source_uid, target_uid)` pair.

| Column           | Type    | Notes                                                                                   |
| ---------------- | ------- | --------------------------------------------------------------------------------------- |
| `source_uid`     | string  | UID of the retired (predecessor) unit                                                   |
| `target_uid`     | string  | UID of the successor unit; null if relationship is `abolished`                          |
| `relationship`   | string  | One of: `split_into`, `merged_into`, `absorbed_into`, `redistricted_into`, `abolished` |
| `effective_date` | date    | Date the administrative change took effect                                              |
| `overlap_pct`    | integer | Estimated percentage of `source_uid` area now covered by `target_uid`; null if unknown |
| `notes`          | string  | Optional. Citation of the legal instrument or source authorising the change             |

A split of one unit into three produces three rows with the same `source_uid`. A merge of three units into one produces three rows with the same `target_uid`.

`overlap_pct` values for a given `source_uid` SHOULD sum to 100 where coverage is complete. Where geometry is unavailable to compute overlap precisely, an approximate value is acceptable; the `notes` field SHOULD indicate this.

### Example

Uganda restructured its administrative level 1. The Northern Region (`a1b2c3d4-…`) was split into three new units: Acholi (`e5f6a7b8-…`), Lango (`c9d0e1f2-…`), and West Nile (`a3b4c5d6-…`).

| source_uid  | target_uid  | relationship | effective_date | overlap_pct | notes                             |
| ----------- | ----------- | ------------ | -------------- | ----------- | --------------------------------- |
| a1b2c3d4-…  | e5f6a7b8-…  | split_into   | 2005-07-01     | 35          | Uganda Local Governments Act 2005 |
| a1b2c3d4-…  | c9d0e1f2-…  | split_into   | 2005-07-01     | 40          | Uganda Local Governments Act 2005 |
| a1b2c3d4-…  | a3b4c5d6-…  | split_into   | 2005-07-01     | 25          | Uganda Local Governments Act 2005 |

## Querying Succession

Because a single unit may have gone through multiple restructurings, the linkage table supports multi-hop traversal. To find all current units that descend from a given UID:

1. Find all rows in the linkage table where `source_uid` equals the target UID → collect `target_uid` values.
2. For each `target_uid`, check whether that unit has been further retired (i.e. appears again as `source_uid`).
3. Repeat until no further successors are found.

This produces the full set of present-day units that correspond, in whole or in part, to the original unit.

## Relationship to P-Codes

UIDs and P-codes serve different purposes and are independent:

- A **UID** identifies a unit permanently. It does not change when the unit is renamed, when boundaries are adjusted, or when a new dataset version is published.
- A **P-code** encodes the unit's current position in the geographic hierarchy. It changes when the hierarchy changes, and it is reset when a dataset undergoes major restructuring.

Boundary files contain only P-codes. The registry is the bridge between UIDs and P-codes. A data consumer that needs to join across versions SHOULD resolve UIDs via the registry, then join to boundary files on `(iso2, adm_level, pcode, version)`.
