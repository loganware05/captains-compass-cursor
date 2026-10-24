# Accessibility review — openui-control-plane

- Widgets use semantic regions (`role="region"`, `role="status"`).
- Plan approval exposes expandable risk details via native `<details>`/`<summary>`.
- Approve/reject are CLI-attested actions with visible instructions in the card
  (keyboard path remains terminal/`northstar ui`); no unlabeled icon-only buttons.
- Closeout ledger presents SHA comparison in a two-column layout with text codes.
- Contrast: dark slate text on light gradient backgrounds (not purple/glow theme).
