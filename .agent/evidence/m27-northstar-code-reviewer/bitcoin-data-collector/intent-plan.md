# Implementation Plan — Kalshi BTC Hourly Event Scan

## Acceptance Criteria

- Scan Kalshi hourly BTC events and map strikes/contracts
- Compute fair value / probability estimates with orderbook features
- Persist scan outputs and support live runner integration
- Include unit tests for fair value, strike probability, orderbook guardrails, event target parsing

## Non-Goals

- Auto-posting trades without human approval
- Committing live API secrets or private keys
- Pull request webhook automation
- Full production brokerage connectivity
