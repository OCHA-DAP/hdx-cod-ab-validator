/**
 * check_versions.js — Browser / DuckDB-WASM version check
 *
 * Validates the version column of a COD-AB boundary file.
 * Returns the same shape as the Python version:
 *   { passed: bool, violations: string[], warnings: string[], info: string[] }
 *
 * Usage:
 *   import { check } from './check_versions.js';
 *
 *   // Set up DuckDB-WASM once in your app, then pass db and conn:
 *   const result = await check(file, db, conn);
 *
 * @param {File} file - A Parquet file selected by the user (File API)
 * @param {import('@duckdb/duckdb-wasm').AsyncDuckDB} db - DuckDB-WASM instance (for file registration)
 * @param {import('@duckdb/duckdb-wasm').AsyncDuckDBConnection} conn - Open connection (for queries)
 */

const VERSION_RE = String.raw`^v\d{2}(\.\d{2})?$`;

// Mirrors check_versions.sql — col is substituted before execution, $1 binds VERSION_RE
function buildSql(col) {
  return `
SELECT
    COUNT(DISTINCT "${col}")                                          AS distinct_count,
    list(DISTINCT "${col}"::VARCHAR ORDER BY 1)                       AS distinct_values,
    list(DISTINCT "${col}"::VARCHAR)
        FILTER (WHERE "${col}" IS NOT NULL
                  AND NOT regexp_full_match("${col}"::VARCHAR, $1))   AS bad_format
FROM data
  `.trim();
}

export async function check(file, db, conn) {
  const violations = [];
  const warnings = [];
  const info = [];

  // Register and load the file into a "data" table
  await conn.query("DROP TABLE IF EXISTS data");
  await db.registerFileHandle(
    "_upload.parquet",
    file,
    2 /* BROWSER_FILEREADER */,
    true,
  );
  await conn.query(
    "CREATE TABLE data AS SELECT * FROM read_parquet('_upload.parquet')",
  );

  // Detect column presence
  const descResult = await conn.query("DESCRIBE data");
  const cols = descResult.toArray().map((r) => r.column_name);

  const hasVersion = cols.includes("version");
  const hasCodVersion = cols.includes("cod_version");

  if (!hasVersion && !hasCodVersion) {
    violations.push(
      "`version` column is absent. A `version` column MUST be present in all datasets.",
    );
    return { passed: false, violations, warnings, info };
  }

  let col;
  if (hasCodVersion && !hasVersion) {
    info.push(
      "Dataset uses `cod_version` instead of `version` — this is a known deviation " +
        "in older datasets and SHOULD be updated to `version` when the dataset is revised.",
    );
    col = "cod_version";
  } else {
    col = "version";
  }

  // Run the SQL from check_versions.sql (inlined via buildSql)
  const stmt = await conn.prepare(buildSql(col));
  const result = await stmt.query(VERSION_RE);
  await stmt.close();

  const row = result.toArray()[0];
  const distinctCount = Number(row.distinct_count);
  const distinctValues = row.distinct_values ?? [];
  const badFormat = row.bad_format ?? [];

  if (distinctCount === 0) {
    violations.push(`\`${col}\` column is entirely null.`);
    return { passed: false, violations, warnings, info };
  }

  if (distinctCount > 1) {
    violations.push(
      `\`${col}\` has multiple distinct values: ${JSON.stringify(distinctValues)}. ` +
        "All rows in a layer MUST share the same version.",
    );
  }

  for (const v of badFormat) {
    if (col === "cod_version") {
      info.push(
        `\`cod_version\` value ${JSON.stringify(v)} does not match the current format ` +
          "(e.g. `v01` or `v02.01`). This is expected for legacy datasets.",
      );
    } else {
      violations.push(
        `\`version\` value ${JSON.stringify(v)} does not match the required format. ` +
          "Must be `v{NN}` (e.g. `v01`) or `v{NN}.{NN}` (e.g. `v02.01`), " +
          "with zero-padded two-digit components.",
      );
    }
  }

  return { passed: violations.length === 0, violations, warnings, info };
}
