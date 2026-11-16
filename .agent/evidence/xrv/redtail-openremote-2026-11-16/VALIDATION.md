# OpenRemote ↔ Demo Controls indicator alignment

**Date:** 2026-11-16  
**Repo:** https://github.com/loganware05/RedTailEnergy  
**Thread:** `<t3-thread://v2/6f2ef0e3-84db-45f4-b721-1941b59842dd/75bf98b5-9289-4201-a21e-6870ffc41140>`  
**Source work:** OpenRemote cloudy-night embed + hub indicator marriage (Packs Ready retained)

## Intent

Marry previously existing Demo Presentation Controls / role-view indicators with the embedded OpenRemote cloudy-night telemetry so shared metrics cannot drift (e.g. Headcount ↔ Occupancy).

## Changes

| Area | Behavior |
| --- | --- |
| `getOpenRemoteAlignedIndicators` | Occupancy, SOC, solar, critical load, packs from OR hour |
| `App.tsx` | Headcount base = OR occupancy; live sim overlay uses OR SOC/solar/load |
| `OpenRemoteTelemetryPanel` | Shared props keep Occupancy / Battery / Solar / Load / Packs Ready in sync |
| Packs Ready | **Kept** (not removed) |

## Verification

- `npm run lint` → pass (see `lint.txt`)
- Hour 4 metrics (see `or-hr4-metrics.json`): occupancy 42, SOC ~36.8%, solar 0, critical load 1.9, packs 7
- Browser: Demo Controls Headcount **42** = Occupancy **42**; Battery **37%** ≈ Battery SOC **37.0%**; Solar/Load **0.0 / 1.9** = Solar AC / Critical load; Packs Ready **7**
- Screenshot: `demo-controls-aligned-hr4.png`

## NorthStar witness

- Product readiness: `northstar-readiness.json` (profile=product)
- Portfolio with control plane: deposited under captains-compass `.agent/evidence/xrv/redtail-openremote-2026-11-16/`
- EER: `eer-redtail-openremote-telemetry.json` (control plane)

## Runtime notes

- App served durably via Docker `redtail-energy-web` on `:3000` (agent-shell Vite dies at turn end)
- Optional OpenRemote Manager stack remains at `https://localhost` (self-signed cert)
