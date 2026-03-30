<script lang="ts">
  import type { PreviewData } from "$lib/db/loader";
  import type { Map as MaplibreMap } from "maplibre-gl";
  import "maplibre-gl/dist/maplibre-gl.css";
  import { onDestroy, onMount } from "svelte";
  import IssuesTable from "./IssuesTable.svelte";
  import { featureBounds, parseOverlayFeatures } from "./mapUtils";

  let {
    preview,
    overlays = [],
  }: { preview: PreviewData; overlays?: string[] } = $props();

  let container: HTMLDivElement | undefined;
  let map: MaplibreMap | undefined;
  let blobUrl: string | undefined;

  const issueFeatures = $derived(parseOverlayFeatures(overlays));

  function zoomToFeature(f: Parameters<typeof featureBounds>[0]) {
    if (!map) return;
    const b = featureBounds(f);
    if (!b) return;
    const [minLng, minLat, maxLng, maxLat] = b;
    map.fitBounds([[minLng, minLat], [maxLng, maxLat]], { padding: 80 });
  }

  onMount(async () => {
    if (!container) return;

    blobUrl = URL.createObjectURL(preview.blob);

    // Dynamic import keeps maplibre-gl's bundled internals out of Svelte 5's
    // compilation scope, avoiding a $$props variable name conflict.
    const maplibregl = await import("maplibre-gl");

    map = new maplibregl.Map({
      container,
      style: {
        version: 8,
        sources: {},
        layers: [
          {
            id: "background",
            type: "background",
            paint: { "background-color": "#f3f4f6" },
          },
        ],
      },
      center: [0, 0],
      zoom: 1,
      attributionControl: false,
    });

    map.on("load", () => {
      if (!map) return;

      map.addSource("preview", { type: "geojson", data: blobUrl! });

      map.addLayer({
        id: "preview-fill",
        type: "fill",
        source: "preview",
        filter: [
          "match",
          ["geometry-type"],
          ["Polygon", "MultiPolygon"],
          true,
          false,
        ],
        paint: { "fill-color": "#3b82f6", "fill-opacity": 0.25 },
      });

      map.addLayer({
        id: "preview-line",
        type: "line",
        source: "preview",
        filter: [
          "match",
          ["geometry-type"],
          ["Polygon", "MultiPolygon", "LineString", "MultiLineString"],
          true,
          false,
        ],
        paint: { "line-color": "#1d4ed8", "line-width": 1 },
      });

      map.addLayer({
        id: "preview-circle",
        type: "circle",
        source: "preview",
        filter: [
          "match",
          ["geometry-type"],
          ["Point", "MultiPoint"],
          true,
          false,
        ],
        paint: { "circle-color": "#1d4ed8", "circle-radius": 4 },
      });

      // Render topology overlays (overlaps = red, gaps = yellow).
      if (issueFeatures.length > 0) {
        const fc = { type: "FeatureCollection", features: issueFeatures };
        // eslint-disable-next-line @typescript-eslint/no-explicit-any
        map.addSource("overlays", { type: "geojson", data: fc as any, tolerance: 0 });

        map.addLayer({
          id: "overlays-fill",
          type: "fill",
          source: "overlays",
          filter: [
            "match",
            ["geometry-type"],
            ["Polygon", "MultiPolygon"],
            true,
            false,
          ],
          paint: {
            "fill-color": [
              "match",
              ["get", "issueType"],
              "overlap", "#ff0000",
              "gap", "#ffee00",
              "#cc00ff",
            ],
            "fill-opacity": 1,
          },
        });

        // Line layer covers all geometry types (Polygon borders + bare LineStrings
        // from degenerate intersections) and stays thick at every zoom level.
        map.addLayer({
          id: "overlays-line",
          type: "line",
          source: "overlays",
          filter: [
            "match",
            ["geometry-type"],
            ["Polygon", "MultiPolygon", "LineString", "MultiLineString"],
            true,
            false,
          ],
          paint: {
            "line-color": [
              "match",
              ["get", "issueType"],
              "overlap", "#ff0000",
              "gap", "#ffee00",
              "#cc00ff",
            ],
            "line-width": [
              "interpolate",
              ["linear"],
              ["zoom"],
              2, 4,
              8, 3,
              14, 3,
            ],
          },
        });
      }

      if (preview.bounds) {
        const [minLng, minLat, maxLng, maxLat] = preview.bounds;
        map.fitBounds(
          [
            [minLng, minLat],
            [maxLng, maxLat],
          ],
          { padding: 24, animate: false },
        );
      }
    });
  });

  onDestroy(() => {
    map?.remove();
    if (blobUrl) URL.revokeObjectURL(blobUrl);
  });
</script>

<div bind:this={container} class="map"></div>

{#if issueFeatures.length > 0}
  <IssuesTable features={issueFeatures} onZoom={zoomToFeature} />
{/if}

<style>
  .map {
    width: 100%;
    aspect-ratio: 1 / 1;
    border-radius: 4px;
    border: 1px solid #e5e7eb;
    margin-bottom: 0.75rem;
    overflow: hidden;
  }
</style>
