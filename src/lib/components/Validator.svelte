<script lang="ts">
  import FileUpload from "$lib/components/FileUpload.svelte";
  import ResultsReport from "$lib/components/ResultsReport.svelte";
  import { duckdbState, initDuckDB } from "$lib/db/duckdb.svelte";
  import type { DatasetResult } from "$lib/runner";
  import { runValidation } from "$lib/runner";
  import { onMount, untrack } from "svelte";

  let files = $state<File[]>([]);
  let running = $state(false);
  let result = $state<DatasetResult | null>(null);
  let runError = $state<string | null>(null);

  onMount(() => {
    initDuckDB();
  });

  $effect(() => {
    const f = files;
    if (f.length > 0 && duckdbState.ready) {
      untrack(() => {
        if (!running) handleRun();
      });
    }
  });

  async function handleRun() {
    const { db, conn } = duckdbState;
    if (!db || !conn) return;
    running = true;
    result = null;
    runError = null;
    try {
      result = await runValidation(files, db, conn);
    } catch (e) {
      runError = e instanceof Error ? e.message : String(e);
    } finally {
      running = false;
    }
  }
</script>

{#if duckdbState.initError}
  <p class="error">Failed to initialise DuckDB: {duckdbState.initError}</p>
{:else if !duckdbState.ready}
  <p class="status">Initialising DuckDB…</p>
{/if}

<FileUpload bind:files disabled={!duckdbState.ready} />

{#if running}
  <p class="status">
    Running checks<span class="dots"><span>.</span><span>.</span><span>.</span></span>
  </p>
{/if}

{#if runError}
  <p class="error">{runError}</p>
{/if}

{#if result}
  <div class="results-wide">
    <ResultsReport {result} />
  </div>
{/if}

<style>
  .results-wide {
    width: 960px;
    margin-left: calc((960px - 720px) / -2);
  }
  .status {
    color: #6b7280;
    font-size: 0.9rem;
    margin: 0.5rem 0;
  }
  .dots span {
    animation: blink 1.2s infinite;
    opacity: 0;
  }
  .dots span:nth-child(2) {
    animation-delay: 0.2s;
  }
  .dots span:nth-child(3) {
    animation-delay: 0.4s;
  }
  @keyframes blink {
    0%,
    80%,
    100% {
      opacity: 0;
    }
    40% {
      opacity: 1;
    }
  }
  .error {
    color: #b91c1c;
    font-size: 0.9rem;
    margin: 0.5rem 0;
  }
</style>
