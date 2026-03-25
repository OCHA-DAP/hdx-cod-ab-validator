# hdx-cod-ab-specification

Normative specification for the **COD-AB (Common Operational Dataset – Administrative Boundaries)** format published by UN OCHA. It defines the required file structure, column schemas, naming conventions, coordinate reference systems, and metadata registry layout for admin boundary datasets on HDX.

## Specification files

- [specs/boundaries.md](specs/boundaries.md) — Admin boundary file overview, column order, and known deviations
- [specs/boundaries/names.md](specs/boundaries/names.md) — Name and language column schema
- [specs/boundaries/codes.md](specs/boundaries/codes.md) — P-code and version column schema
- [specs/boundaries/attributes.md](specs/boundaries/attributes.md) — Date, computed, and identifier column schema
- [specs/file-structure.md](specs/file-structure.md) — Directory and file naming conventions, CRS requirements
- [specs/metadata.md](specs/metadata.md) — Metadata registry table schema

## Validating a dataset with an LLM

This repository includes an [`llms.txt`](llms.txt) file — a machine-readable index following the [llms.txt convention](https://llmstxt.org/) that points LLMs to the relevant spec content. It also includes a self-contained validator prompt.

To interactively validate a COD-AB dataset:

1. Open a conversation with an LLM that can fetch URLs or read files (e.g. Claude, ChatGPT with browsing, or any tool that supports `llms.txt`).
2. Point the LLM at `llms.txt` in this repo, or directly fetch [`validator.md`](validator.md).
3. Follow the guided prompts to check your dataset against the spec.

[`validator.md`](validator.md) is a self-contained prompt — you can paste it directly into a chat session without needing the LLM to fetch anything.
