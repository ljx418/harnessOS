# V12-0P Prototype Quality Gap Analysis

## Decision

Status: `REMEDIATED_IN_CURRENT_HTML_PROTOTYPE`

The first V12-0P HTML prototype looked noticeably weaker than the imag2 target
experience. This was a real quality issue, not only subjective taste.

## Root Causes

| Gap | Cause | Remediation |
| --- | --- | --- |
| Report-first page hierarchy | The page opened with large audit/documentation cards, pushing the product screen below the fold. | Reduced hero/audit height and moved emphasis to the integrated product screen. |
| Mixed icon language | Emoji, geometric glyphs and text symbols were mixed, making the UI feel like a draft. | Replaced emoji icons with unified letter/line placeholders pending lucide implementation. |
| Weak node craft | Node cards had plain white rectangles, weak separators and limited elevation. | Added layered backgrounds, stronger selected state, header separator, refined line rows, port glow and softer elevation. |
| Canvas lacked depth | Grid, edges and toolbar looked flat. | Added subtle canvas lighting, stronger curved edge treatment, frosted toolbar and stronger minimap surface. |
| State explanation felt detached | State enum existed as a later section, not part of the product story. | Added an inline quality note and kept concrete status chips inside the target screen. |
| Too much "design report", not enough "product" | The HTML tried to be both audit pack and prototype, but the visual priority was wrong. | Rebalanced toward product prototype first, audit evidence second. |

## Remaining Limits

- This is still HTML design evidence, not a browser implementation.
- Real icon quality should be delivered with `lucide-react` during V12 browser
  implementation.
- Real interaction feel still requires pointer, keyboard, focus, canvas and
  network-boundary tests.
- Real parity with the imag2 visual target requires implementation in the
  actual V12 browser workbench, not only this report page.

## Acceptance Impact

The prototype now better supports V12-0P review, but it still should not be used
as V12 browser implementation evidence or Xpert parity evidence.
