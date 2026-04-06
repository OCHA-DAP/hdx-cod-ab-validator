---
version: 0.1.0-draft
status: open
---

# Open Questions & Discrepancies

This file tracks known conflicts between the machine-readable specification and the operational guidance documents. Each item needs a team decision before the relevant spec file can be considered final.

---

## OQ-1: Reference Name Field — Deprecated or Current Practice?

**Spec says:** `adm{N}_ref_name` is deprecated and SHOULD NOT be included in new datasets (`boundaries/attributes.md`).

**Guidance docs say:** A reference name field should be included whenever admin names contain accented characters, apostrophes, or non-Western scripts, and should contain the romanized Latin-script form.

**Question:** Is the ref_name field being retired? If so, how should a romanized fallback for non-Latin primary scripts be stored going forward? If not, the spec should be updated.

---

## OQ-2: P-Code Delimiters — Are Dashes Permitted?

**Spec says:** The sub-national portion of a p-code MUST consist of numeric digits only, and p-codes MUST be stored without delimiters (`boundaries/codes.md`).

**Guidance docs say:** Dashes in p-codes are "unusual but permitted" (Haiti example: `HT0114-01`).

**Question:** Are delimiter-based p-codes in existing datasets a legacy issue to be corrected, or still acceptable for new datasets? Should the guidance be updated to align with the spec?

---

## OQ-3: iso2 / iso3 in Higher Admin Levels

**Spec says:** `iso2` and `iso3` currently appear only in admin 0 files but SHOULD be included in higher admin levels for schema consistency (`boundaries/attributes.md`).

**Guidance docs:** Do not mention including `iso2` / `iso3` in levels above admin 0.

**Question:** Should new and revised datasets begin including these columns in ADM1 and above?

---

## OQ-4: Language Tag Columns

**Spec says:** `lang`, `lang1`, `lang2`, `lang3` are REQUIRED in all datasets and MUST be valid BCP 47 tags (`boundaries/names.md`).

**Guidance docs:** Do not mention language tag columns. Guidance focuses on naming language-specific name fields but provides no language tag requirements.

**Question:** Are `lang` columns currently being populated in all COD-AB datasets? When will this be enforced? How should legacy datasets without language tags be treated?

---

## OQ-5: center_lat / center_lon Algorithm

**Spec says:** `center_lat` / `center_lon` SHOULD be generated using a Maximum Inscribed Circle (MIC) algorithm, which guarantees the point falls within the polygon (`boundaries/attributes.md`).

**Guidance docs:** Recommend ArcGIS Pro "Feature To Point" with the "Inside" option, which places the point inside the polygon but is not equivalent to MIC.

**Question:** Should the guidance be updated to prefer MIC where tooling allows? Are there plans to recompute existing datasets using MIC?

---

## OQ-6: Column Order Enforcement

**Spec says:** Columns SHOULD appear in a defined order (`boundaries.md`).

**Guidance docs:** Do not address column order.

**Question:** Does the validator currently check column order? If so, existing processed datasets should be audited for compliance.
