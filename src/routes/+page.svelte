<script lang="ts">
  import { check } from "$lib/scripts/check_versions.js";
  import * as duckdb from "@duckdb/duckdb-wasm";
  import { onMount } from "svelte";

  let db: duckdb.AsyncDuckDB | null = null;
  let conn: duckdb.AsyncDuckDBConnection | null = null;
  let dbReady = $state(false);
  let result = $state<{
    passed: boolean;
    violations: string[];
    warnings: string[];
    info: string[];
  } | null>(null);
  let running = $state(false);
  let error = $state<string | null>(null);

  onMount(async () => {
    const bundles = duckdb.getJsDelivrBundles();
    const bundle = await duckdb.selectBundle(bundles);
    const workerUrl = URL.createObjectURL(
      new Blob([`importScripts("${bundle.mainWorker}");`], {
        type: "text/javascript",
      }),
    );
    const worker = new Worker(workerUrl);
    const logger = new duckdb.ConsoleLogger(duckdb.LogLevel.WARNING);
    db = new duckdb.AsyncDuckDB(logger, worker);
    await db.instantiate(bundle.mainModule, bundle.pthreadWorker);
    URL.revokeObjectURL(workerUrl);
    conn = await db.connect();
    dbReady = true;
  });

  async function handleFile(event: Event) {
    const file = (event.target as HTMLInputElement).files?.[0];
    if (!file || !db || !conn) return;

    running = true;
    result = null;
    error = null;

    try {
      result = await check(file, db, conn);
    } catch (e) {
      error = e instanceof Error ? e.message : String(e);
    } finally {
      running = false;
    }
  }
</script>

<main>
  <h1>COD-AB Version Check</h1>

  <label>
    Upload a Parquet file
    <input
      type="file"
      accept=".parquet"
      onchange={handleFile}
      disabled={!dbReady}
    />
  </label>

  {#if !dbReady}
    <p class="status">Initialising DuckDB…</p>
  {/if}

  {#if running}
    <p class="status">Running check…</p>
  {/if}

  {#if error}
    <p class="error">{error}</p>
  {/if}

  {#if result}
    <section
      class="result"
      class:passed={result.passed}
      class:failed={!result.passed}
    >
      <h2>{result.passed ? "✓ Passed" : "✗ Failed"}</h2>

      {#if result.violations.length}
        <h3>Violations</h3>
        <ul>
          {#each result.violations as v}<li>{v}</li>{/each}
        </ul>
      {/if}

      {#if result.warnings.length}
        <h3>Warnings</h3>
        <ul>
          {#each result.warnings as w}<li>{w}</li>{/each}
        </ul>
      {/if}

      {#if result.info.length}
        <h3>Info</h3>
        <ul>
          {#each result.info as i}<li>{i}</li>{/each}
        </ul>
      {/if}
    </section>
  {/if}
</main>

<style>
  main {
    max-width: 640px;
    margin: 2rem auto;
    font-family: sans-serif;
    padding: 0 1rem;
  }
  .status {
    color: #666;
  }
  .error {
    color: #c00;
  }
  .result {
    margin-top: 1.5rem;
    padding: 1rem;
    border-radius: 6px;
    border: 1px solid #ccc;
  }
  .result.passed {
    border-color: #2a2;
    background: #f0fff0;
  }
  .result.failed {
    border-color: #c00;
    background: #fff0f0;
  }
  ul {
    padding-left: 1.2rem;
  }
  li {
    margin: 0.3rem 0;
  }
</style>
