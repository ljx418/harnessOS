# Workflow Platform WP-M2 Canvas Plan And Audit

用途：定义 WP-M2 画布交互实现前计划、验收标准和审计结论。
边界：本文是子阶段计划和审计，不是实现证据。

## Development Plan

- The platform canvas must support wheel zoom, viewport pan, node drag, right-side/empty-area drag, port-based free connect, cancel connect and invalid connection feedback.
- Edges must have visible arrowheads in first-eye and zoomed states.
- Canvas graph save and validation must continue through `/bff/pv21/workflows/{workflow_id}/graph` and `/graph/validate`.
- The canvas must expose stable test ids for automated action logging.

## Acceptance Criteria

- Browser action log includes `wheel_zoom`, `pan_canvas`, `node_drag`, `right_area_drag`, `free_connect`, `cancel_connect`, `invalid_connect`.
- `canvas-edge-quality-report.json` records arrow visibility and no critical text overlap.
- Screenshots prove first-eye edge layout and zoomed edge layout.
- PRD review confirms canvas is interactive evidence, not product-grade frontend completion.

## Audit Opinion

```text
wp_m2_readiness=GO
fatal_spec_drift=NONE
major_risk=NONE
implementation_may_start=true
```

