# Security review — openui-control-plane

- UI APPROVE denied without `COMPASS_CAPTAIN_APPROVE=1` (unit + CLI verified).
- Open UI gate fail-closed when `COMPASS_OPENUI_ENABLED` unset (exit 2).
- Unknown OpenUI Lang components rejected by structural validator (including nested calls).
- `plan-approval-check.sh` treats `northstar ui approve` / `run-openui.sh approve`
  as plan forges (requires `COMPASS_CAPTAIN_APPROVE=1` for shell path).
- No secrets introduced; no product-repo installer copy of UI runtime.
- Approval writer does not bypass commit requirement for product edits
  (working-tree APPROVED still requires commit before product-source unlock).
- Streamed props are treated as data (quoted strings); no `eval` of OpenUI Lang.
- Documented equivalent to `--ui` on every surface: `northstar ui emit --surface …`.
