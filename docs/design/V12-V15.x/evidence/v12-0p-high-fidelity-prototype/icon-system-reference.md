# V12-0P Icon System Reference

Status: design reference only
Stage: V12-0P
Evidence scope: visual target / maintainable SVG implementation reference

## Purpose

This file records the imag2 icon sprite reference used to improve the V12-0P
prototype visual quality. The generated raster image is not treated as runtime,
browser implementation, BFF, DTO or Workflow Studio evidence.

## Generated Reference

- Reference image: `assets/imag2-icon-sprite-reference.png`
- Applied implementation: inline SVG icon symbols inside
  `xpert-aligned-workbench-v3.html`

## Prompt

```text
A polished UI icon sprite sheet for a modern AI workflow canvas product called
HarnessOS Light Studio. Create 16 small vector-style icons on a transparent or
very light background, consistent blue slate green amber palette, rounded 2px
strokes, no text labels, no emojis. Icons: home dashboard, agents, workflow
graph, skills/tools, MCP plug, evidence document, runtime monitor, favorites
star, templates grid, settings gear, help, chat bubble, timeline, quality
shield, node inspector panel, publish/approval. Style should match premium SaaS
low-code workflow builder, similar to shadcn/lucide icons but slightly more
dimensional with subtle soft shadows and blue active accents. Crisp, high
quality, 4x4 grid, each icon centered with enough padding, suitable for slicing
into UI assets.
```

## Design Decision

- The prototype does not use the raster sprite directly as UI chrome.
- The visual direction is translated into inline SVG symbols so the design is
  inspectable, maintainable and compatible with future lucide/shadcn migration.
- The rail, secondary navigation and canvas toolbar now use SVG icons instead
  of letter placeholders.

## Boundaries

- Not proof of HarnessOS browser implementation.
- Not proof of BFF route enforcement.
- Not proof of DTO correctness.
- Not proof of runtime execution.
- Not proof of Xpert parity or product-grade frontend completion.
