"""The publisher's own published bytes: the results block it writes into docs/status/LATEST.md.

Everything else the publish cycle puts on a surface is written by a producer the publisher
imports (`publish_scope.PUBLISH_PATH_SOURCES`). This block was the one exception, computed
inline in `process_run_complete.py`. Living there, it was the only reason a defect in the
publisher could make a published figure wrong, and so the only argument for counting the
publisher's alarm, census and git tests in the blocking publish scope. 141 of 348 blocking
files reached the scope through the publisher, not through a figure (OPS6, 2026-11-09).

The path is a parameter, not a module constant: `process_run_complete.LATEST_MD` stays the
one name every test patches, and the publisher's `update_latest_md` passes it in.

REUSE: background/publish_content.py
CLASS: CUSTOM
INDEX: searched "publish content", "latest md" -- the matches are the publisher itself (the
       function's former home) and `background/status_honesty.py`, which only describes the
       block. Nothing else writes it, so this is a move, not a second implementation.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from pathlib import Path

RESULTS_BLOCK_START = "**Latest simulation results"


def render_results_block(data: dict, elapsed_s: float, git_hash: str, date_str: str) -> str:
    """The block's text. It carries its own clock (run and date): this is the only live £ on
    the status page, and undated it cannot be told from the dated records of earlier runs in
    the same file (2026-09-19)."""
    ledger = data.get("_ledger_headline", {})
    net = data.get("total_net_gbp", ledger.get("net_margin_gbp", 0))  # includes bad debt + hedging
    gross = ledger.get("gross_margin_gbp", data.get("total_gross_gbp", 0))
    ret_log = data.get("retention_log", [])
    offers = len(ret_log)
    retained = sum(1 for r in ret_log if r.get("outcome") == "retained")
    return "\n".join([
        "**Latest simulation results (2016–2025)** — auto-processed ({:.0f}s / {:.0f} min)"
        " // run {}, {}:".format(elapsed_s, elapsed_s / 60, git_hash, date_str),
        "- Net margin: \xa3{:,.2f} | Gross: \xa3{:,.2f} | Capital: \xa3{:,.0f}".format(
            net, gross, data.get("total_capital_gbp", 0)),
        "- Treasury: \xa3{:,.0f} → \xa3{:,.0f} | {} committee interventions | {} bills issued"
        .format(
            data.get("starting_treasury_gbp", 0), data.get("final_treasury_gbp", 0),
            data.get("committee_wake_ups_total", 0), data.get("bills_total", 0)),
        "- Enterprise value: \xa3{:,.2f} | Net after CTS: \xa3{:,.0f}".format(
            data.get("enterprise_value_gbp", 0), data.get("net_margin_after_cost_to_serve_gbp", 0)),
        "- Retention: {} offers, {}/{} retained | {} no-offer churns | {} total churned accounts"
        .format(
            offers, retained, offers, len(data.get("no_offer_churn_log", [])),
            len(data.get("churned_billing_accounts", []))),
    ])


def write_latest_results(path: Path, data: dict, elapsed_s: float, git_hash: str = "unknown",
                         *, now: datetime | None = None) -> bool:
    """Replace the results block in `path` in place, or append it. Returns True iff the block
    was absent and has been created (the caller logs that)."""
    now = now or datetime.now(timezone.utc)
    text = path.read_text()
    stamp = "Last updated: {}".format(now.strftime("%Y-%m-%dT%H:%M:%SZ"))
    text = re.sub(r"Last updated: \S+", stamp, text)
    block = render_results_block(data, elapsed_s, git_hash, now.strftime("%Y-%m-%d"))
    start = text.find(RESULTS_BLOCK_START)
    created = start == -1
    if created:
        text = text.rstrip() + "\n\n" + block + "\n"
    else:
        end = text.find("\n\n", start)
        text = text[:start] + block + text[len(text) if end == -1 else end:]
    path.write_text(text)
    return created

