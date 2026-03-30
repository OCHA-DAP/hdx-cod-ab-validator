import type { AsyncDuckDBConnection } from "@duckdb/duckdb-wasm";
import type { Check, CheckResult } from "./types.ts";

const OVERLAP_FEATURE_LIMIT = 2000;

async function findGeomColumn(
  conn: AsyncDuckDBConnection,
): Promise<string | null> {
  const desc = await conn.query("DESCRIBE data");
  const cols = desc.toArray() as Array<{
    column_name: string;
    column_type: string;
  }>;
  return cols.find((r) => r.column_type === "GEOMETRY")?.column_name ?? null;
}

async function run(
  conn: AsyncDuckDBConnection,
  _columns: string[],
): Promise<CheckResult> {
  const violations: string[] = [];
  const warnings: string[] = [];
  const info: string[] = [];

  const geomCol = await findGeomColumn(conn);
  if (!geomCol) {
    info.push("No GEOMETRY column found — topology checks skipped.");
    return { passed: true, violations, warnings, info };
  }

  const q = JSON.stringify(geomCol);

  // ── 1. Overlaps ────────────────────────────────────────────────────────────
  // Use a row-numbered self-join to find pairs sharing interior area.
  // ST_Intersects AND NOT ST_Touches catches both partial overlaps and
  // containment (one polygon fully inside another).
  const countResult = await conn.query(
    `SELECT COUNT(*) AS n FROM data WHERE ${q} IS NOT NULL`,
  );
  const featureCount = Number(
    (countResult.toArray()[0] as Record<string, unknown>).n,
  );

  if (featureCount > OVERLAP_FEATURE_LIMIT) {
    warnings.push(
      `Layer has ${featureCount} features — overlap check skipped (limit: ${OVERLAP_FEATURE_LIMIT}). ` +
        "Polygons within a layer MUST NOT overlap each other.",
    );
  } else {
    const overlapResult = await conn.query(`
      WITH indexed AS (
        SELECT row_number() OVER () AS rn, ${q} AS geom
        FROM data
        WHERE ${q} IS NOT NULL
      )
      SELECT COUNT(*) AS overlap_count
      FROM indexed a
      JOIN indexed b ON a.rn < b.rn
      WHERE ST_Intersects(a.geom, b.geom)
        AND NOT ST_Touches(a.geom, b.geom)
    `);
    const overlapCount = Number(
      (overlapResult.toArray()[0] as Record<string, unknown>).overlap_count,
    );
    if (overlapCount > 0) {
      violations.push(
        `${overlapCount} pair(s) of polygons overlap. ` +
          "Polygons within a layer MUST NOT overlap each other.",
      );
    } else {
      info.push("No overlapping polygons detected.");
    }
  }

  // ── 2. Gaps ────────────────────────────────────────────────────────────────
  // Union all polygons, convert to GeoJSON, then count interior rings (holes).
  // GeoJSON coordinates layout:
  //   Polygon:      [ exterior_ring, hole1, hole2, … ]          → holes = length − 1
  //   MultiPolygon: [ [ext, hole…], [ext, hole…], … ]           → holes = Σ(length − 1)
  // Using ST_AsGeoJSON avoids ST_GeometryN / ST_Dump which are unavailable here.
  const gapResult = await conn.query(`
    WITH unioned AS (
      SELECT
        ST_GeometryType(ST_Union_Agg(${q}))::VARCHAR AS geom_type,
        ST_AsGeoJSON(ST_Union_Agg(${q}))             AS gj
      FROM data
      WHERE ${q} IS NOT NULL
    )
    SELECT
      geom_type,
      CASE geom_type
        WHEN 'POLYGON' THEN
          json_array_length(json_extract(gj, '$.coordinates')) - 1
        WHEN 'MULTIPOLYGON' THEN (
          SELECT COALESCE(
            SUM(json_array_length(json_extract(gj, '$.coordinates[' || i::VARCHAR || ']')) - 1),
            0
          )
          FROM generate_series(0::BIGINT, json_array_length(json_extract(gj, '$.coordinates'))::BIGINT - 1) t(i)
        )
        ELSE 0
      END AS gap_ring_count
    FROM unioned
  `);
  const gapRow = gapResult.toArray()[0] as Record<string, unknown>;
  const gapRingCount = Number(gapRow.gap_ring_count ?? 0);

  if (gapRingCount > 0) {
    violations.push(
      `${gapRingCount} gap(s) detected between adjacent polygons. ` +
        "There MUST be no gaps (slivers) between adjacent polygons within a layer.",
    );
  } else {
    info.push("No gaps detected between polygons.");
  }

  return { passed: violations.length === 0, violations, warnings, info };
}

export const checkTopology: Check = {
  name: "check_topology",
  label: "Topology",
  specSection: "Topology",
  appliesTo: ["all"],
  run,
};
