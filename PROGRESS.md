# Progress

## Current status

**Implementing / ready: AHF-P02 Jev shadow** — Linear
[OVA-63](https://linear.app/ovaltechnologysolutions/issue/OVA-63/ahf-p02-jev-shadow-decisions-over-ahf-adapter)
· Branch `cursor/ahf-p02-jev-shadow-8613` · Release **v1.51.0**.

| Item | Value |
|---|---|
| On main | **v1.50.0** AHF-P01 (#188) @ `d771e6e` |
| Active plan | `ahf-p02-jev-shadow` — **APPROVED** / implementing |
| Next | AHF-P03 on `bitcoin-data-collector` ([OVA-64](https://linear.app/ovaltechnologysolutions/issue/OVA-64/ahf-p03-btc-exchange-netflow-on-chain-metric-bitcoin-data-collector)) |
| Rollback | `rollback/pre-ahf-p02-jev-shadow` @ `d771e6e` |

## Parallel track — On-Chain / AI Hedge Fund (AHF)

1. ~~**AHF-P01 Intake + read-only adapter**~~ merged (#188) — OVA-62 · v1.50.0
2. **AHF-P02 Jev shadow** ← implementing (OVA-63)
3. AHF-P03 BTC on-chain metric family (`bitcoin-data-collector`) — OVA-64
4. AHF-P04+ On-chain analyst, portfolio experiments, behavioral feed — deferred

## Behavioral Intelligence Loop

1. ~~M46–M49~~ merged through v1.49.0
5. M50 Policy / instruction promotion (deferred)
6. M51 Kimi K3 Project Overseer (deferred)

## Blockers

None. Live Jev optional — set `COMPASS_JEV_API_KEY` / `TYPESAFE_API_KEY` Captain-local
(never commit). Hermetic file fixtures cover CI.
