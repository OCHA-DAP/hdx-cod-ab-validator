<script lang="ts">
  import { onMount } from "svelte";

  interface SpecTab {
    id: string;
    label: string;
    html: string;
  }

  let { specTabs }: { specTabs: SpecTab[] } = $props();

  let showSpec = $state(true);
  let activeTab = $state("overview");

  const validTabIds = new Set(specTabs.map((t) => t.id));

  function parseHash(hash: string): { show: boolean; tab: string } {
    const h = hash.replace(/^#/, "");
    if (h.startsWith("spec-")) {
      const tab = h.slice(5);
      return { show: true, tab: validTabIds.has(tab) ? tab : "overview" };
    }
    return { show: true, tab: "overview" };
  }

  function buildHash(show: boolean, tab: string): string {
    if (!show || tab === "overview") return "";
    return `#spec-${tab}`;
  }

  onMount(() => {
    const { show, tab } = parseHash(window.location.hash);
    showSpec = show;
    activeTab = tab;

    function onHashChange() {
      const { show: s, tab: t } = parseHash(window.location.hash);
      showSpec = s;
      activeTab = t;
    }
    window.addEventListener("hashchange", onHashChange);
    return () => window.removeEventListener("hashchange", onHashChange);
  });

  $effect(() => {
    const hash = buildHash(showSpec, activeTab);
    if (typeof window !== "undefined" && window.location.hash !== hash) {
      history.replaceState(null, "", hash || window.location.pathname);
    }
  });

  let activeTabHtml = $derived(specTabs.find((t) => t.id === activeTab)?.html ?? "");
</script>

<button
  class="spec-button"
  class:active={showSpec}
  onclick={() => {
    showSpec = !showSpec;
    history.pushState(null, "", buildHash(showSpec, activeTab) || window.location.pathname);
  }}
>
  {showSpec ? "Hide specification" : "View specification"}
</button>

{#if showSpec}
  <section class="spec">
    <nav class="spec-tabs">
      {#each specTabs as tab (tab.id)}
        <button
          class="spec-tab"
          class:active={activeTab === tab.id}
          onclick={(e) => {
            activeTab = tab.id;
            history.pushState(null, "", buildHash(showSpec, tab.id));
            (e.currentTarget as HTMLButtonElement).blur();
          }}
        >
          {tab.label}
        </button>
      {/each}
    </nav>
    <div class="spec-content">
      <!-- eslint-disable-next-line svelte/no-at-html-tags -->
      {@html activeTabHtml}
    </div>
  </section>
{/if}

<style>
  .spec-button {
    margin-top: 0.5rem;
    padding: 0.25rem 0.75rem;
    background: #f3f4f6;
    border: 1px solid #e5e7eb;
    border-radius: 999px;
    font-size: 0.85rem;
    color: #374151;
    cursor: pointer;
    font-family: inherit;
    transition:
      background 0.1s,
      color 0.1s,
      border-color 0.1s;
  }
  .spec-button:hover {
    background: #e5e7eb;
  }
  .spec-button.active {
    background: #1d4ed8;
    border-color: #1d4ed8;
    color: white;
    font-weight: 600;
  }
  .spec-button.active:hover {
    background: #1e40af;
    border-color: #1e40af;
  }
  .spec {
    margin: 1.25rem 0;
    background: #f9fafb;
    border: 1px solid #e5e7eb;
    border-radius: 6px;
    font-size: 0.9rem;
    line-height: 1.65;
  }
  .spec-tabs {
    display: flex;
    gap: 0;
    border-bottom: 1px solid #e5e7eb;
    padding: 0 1rem;
    overflow-x: auto;
    scrollbar-width: none;
  }
  .spec-tabs::-webkit-scrollbar {
    display: none;
  }
  .spec-tab {
    padding: 0.5rem 0.875rem;
    background: none;
    border: none;
    border-bottom: 2px solid transparent;
    font-size: 0.85rem;
    color: #6b7280;
    cursor: pointer;
    white-space: nowrap;
    margin-bottom: -1px;
  }
  .spec-tab:hover {
    color: #111;
  }
  .spec-tab.active {
    color: #1d4ed8;
    border-bottom-color: #1d4ed8;
    font-weight: 600;
  }
  .spec-content {
    padding: 1.25rem 1.5rem;
  }
  .spec-content :global(h1) {
    font-size: 1.3rem;
    margin: 0 0 0.75rem;
  }
  .spec-content :global(h2) {
    font-size: 1.05rem;
    margin: 1.25rem 0 0.4rem;
  }
  .spec-content :global(h3) {
    font-size: 0.95rem;
    margin: 1rem 0 0.3rem;
  }
  .spec-content :global(p) {
    margin: 0.4rem 0;
  }
  .spec-content :global(ul),
  .spec-content :global(ol) {
    margin: 0.4rem 0;
    padding-left: 1.5rem;
  }
  .spec-content :global(table) {
    border-collapse: collapse;
    width: 100%;
    font-size: 0.85rem;
    margin: 0.5rem 0;
  }
  .spec-content :global(th),
  .spec-content :global(td) {
    border: 1px solid #d1d5db;
    padding: 0.35rem 0.6rem;
    text-align: left;
  }
  .spec-content :global(th) {
    background: #e5e7eb;
  }
  .spec-content :global(pre) {
    background: #e5e7eb;
    padding: 0.75rem 1rem;
    border-radius: 4px;
    overflow-x: auto;
    font-size: 0.82rem;
  }
  .spec-content :global(code) {
    font-size: 0.85em;
    background: #e5e7eb;
    padding: 0.1em 0.3em;
    border-radius: 3px;
  }
  .spec-content :global(pre code) {
    background: none;
    padding: 0;
  }
</style>
