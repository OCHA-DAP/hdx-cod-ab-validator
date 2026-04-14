<script lang="ts">
  let copyState = $state<"idle" | "copying" | "copied">("idle");

  async function copyPrompt() {
    copyState = "copying";
    try {
      const res = await fetch(`${import.meta.env.BASE_URL}prompt`);
      const text = await res.text();
      await navigator.clipboard.writeText(text);
      copyState = "copied";
      setTimeout(() => (copyState = "idle"), 2000);
    } catch {
      copyState = "idle";
    }
  }
</script>

<button class="copy-prompt-button" onclick={copyPrompt} disabled={copyState !== "idle"}>
  {copyState === "copied" ? "Copied!" : copyState === "copying" ? "Copying…" : "Copy prompt"}
</button>

<style>
  .copy-prompt-button {
    display: inline;
    padding: 0;
    background: none;
    border: none;
    font-size: inherit;
    color: #374151;
    cursor: pointer;
    font-family: inherit;
    text-decoration: underline;
    text-underline-offset: 2px;
    text-decoration-color: #9ca3af;
  }
  .copy-prompt-button:hover:not(:disabled) {
    color: #111;
    text-decoration-color: #374151;
  }
  .copy-prompt-button:disabled {
    cursor: default;
    text-decoration: none;
  }
</style>
