import type { AsyncDuckDBConnection } from "@duckdb/duckdb-wasm";
import type { Check, CheckResult } from "./types.ts";

const VERSION_RE = String.raw`^v\d{2}(\.\d{2})?$`;

function buildSql(col: string): string {
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

async function run(
  conn: AsyncDuckDBConnection,
  columns: string[],
): Promise<CheckResult> {
  const violations: string[] = [];
  const warnings: string[] = [];
  const info: string[] = [];

  const hasVersion = columns.includes("version");
  const hasCodVersion = columns.includes("cod_version");

  if (!hasVersion && !hasCodVersion) {
    violations.push(
      "`version` column is absent. A `version` column MUST be present in all datasets.",
    );
    return { passed: false, violations, warnings, info };
  }

  let col: string;
  if (hasCodVersion && !hasVersion) {
    info.push(
      "Dataset uses `cod_version` instead of `version` — this is a known deviation " +
        "in older datasets and SHOULD be updated to `version` when the dataset is revised.",
    );
    col = "cod_version";
  } else {
    col = "version";
  }

  const stmt = await conn.prepare(buildSql(col));
  const result = await stmt.query(VERSION_RE);
  await stmt.close();

  const row = result.toArray()[0];
  const distinctCount = Number(row.distinct_count);
  // Arrow list columns may contain BigInt values (e.g. when the source column is
  // an integer type). Array.from + .map(String) converts them to plain strings at
  // runtime so JSON.stringify on the resulting arrays is always safe.
  const distinctValues = Array.from(row.distinct_values ?? []).map(String);
  const badFormat = Array.from(row.bad_format ?? []).map(String);

  if (distinctCount === 0) {
    violations.push(`\`${col}\` column is entirely null.`);
    return { passed: false, violations, warnings, info };
  }

  if (distinctCount > 1) {
    const listed = distinctValues.map((v) => `"${v}"`).join(", ");
    violations.push(
      `\`${col}\` has multiple distinct values: [${listed}]. ` +
        "All rows in a layer MUST share the same version.",
    );
  }

  for (const v of badFormat) {
    if (col === "cod_version") {
      info.push(
        `\`cod_version\` value "${v}" does not match the current format ` +
          "(e.g. `v01` or `v02.01`). This is expected for legacy datasets.",
      );
    } else {
      violations.push(
        `\`version\` value "${v}" does not match the required format. ` +
          "Must be `v{NN}` (e.g. `v01`) or `v{NN}.{NN}` (e.g. `v02.01`), " +
          "with zero-padded two-digit components.",
      );
    }
  }

  return { passed: violations.length === 0, violations, warnings, info };
}

export const checkVersions: Check = {
  name: "check_versions",
  label: "Version",
  specSection: "Versions",
  appliesTo: ["all"],
  run,
};
