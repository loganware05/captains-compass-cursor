# N4 stack verification (WS0)

Recorded 2026-10-26. Hermetic fixtures do not require clones; live mode must use these pins.

| Stack ID | GitHub | Role in pilot | Pin ref | SHA | NorthStar `.cursor/` | Substitution |
|---|---|---|---|---|---|---|
| `traphouse` | `loganware05/TrapHouseKitchen` | Order-status tasks | `main` | `f7c4719ba016feae17308c5d39a929187671aa72` | Yes | — |
| `verdant` | `loganware05/Verdant.sys` | Plant/data validation (PDF “Verdant AI”) | `main` | `351166908a8551d534f7cfea09e7414d617bce79` | **No** | Hermetic + default live path uses `sandbox` substitute |
| `bitcoin` | `loganware05/bitcoin-data-collector` | Idempotent recovery | `cursor/m35-c2-northstar-install-5182` | `468c9483a1731afc80bec0e1bcfc45bfe09e5b2e` | Yes (M35 install branch) | Default branch `cursor/kalshi-live-decision-system` @ `2100a0f…` is **not** the N4 pin |
| `sandbox` | `loganware05/captain-compass-sandbox` | Fallback / Verdant substitute | `main` | `5a1d32e0a8d49ffebcd62c598c12201e3f19985e` | Yes (N2) | Used when `verdant` lacks install |

## Notes

- Live mode requires Captain-local checkouts; harness never silently clones.
- Evaluate-only default (`COMPASS_N4_LIVE_IMPLEMENT` unset/off).
