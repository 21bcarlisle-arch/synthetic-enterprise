# Simulation Status -- LATEST

Last updated: 2026-06-30T07:37:29Z

## Current state

- **Phase:** DR complete — this session built Phases DF-DR (SAR/vulnerability/EBSS/EBRS/EMIR/BSC/social obligations/statutory accounts/switching cost/price transparency/PSR/SLC tracker/embedded networks/interconnectors/renewal notices/board meetings)
- **Tests passing:** 5,876 non-sim + simulation suite (all green)
- **Python modules:** 310 company/ + simulation + saas
- **Net position (latest sim run):** £1,243,337 (git 5190a86)

## Latest run figures (git 5190a86, 2026-06-30T07:25)

| Metric | Value |
|--------|-------|
| Total Revenue | £14,135,305 |
| Gross Margin | £6,462,146 |
| Net Margin | £1,243,337 |
| Enterprise Value | £6,037,509 |
| Final Treasury | £3,709,973 |
| Administration Event | None |

## Build summary (2026-06-30)

- Phases completed today: DF, DG, DH, DI, DJ, DK, DL, DM, DN, DO, DP, DQ, DR
- New modules: sar_register, consumer_vulnerability_register, bsc_settlement_run_register,
  social_obligation_register, statutory_accounts_register, switching_cost_model,
  price_transparency_register, embedded_network_register, interconnector_monitor_register,
  renewal_notice_register, board_meeting_register
- Website: all subpage 404s fixed (relative path fix), Capabilities tab (72 capabilities),
  expanded Regulatory tab (23 SLCs)
- Snapshot tool: tools/generate_snapshot.py for 06:00/18:00 checkpoints

## Links

- [Annual Report](../reports/ANNUAL_REPORT.md)
- [Phase History](../claude/phase-history.md)
- [Project Overview](../PROJECT_OVERVIEW.md)
