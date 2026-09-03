#!/usr/bin/env python3
"""The comparison: what the curtained validator rebuilt against what the company issued.

REUSE: tools/bill_validation_comparison.py
CLASS: CUSTOM
INDEX: searched "bill", "valid", "compar", "diff", "reconcil", "discrepan", "audit", "statement".
       The three nearest rows are the pieces this JOINS and none of them answers its question:
       `company/billing/raw_account_export` produces the validator's input and must stay ignorant
       of the statement; `tools/independent_bill_validator` rebuilds and is behind a curtain that
       forbids it reading anything of ours; `company/billing/statement_export` says what we claim.
       Work item 4 of the brief is the join, and it cannot live in either of the two modules it
       compares: putting it in the validator breaches the curtain, and putting it in the biller
       makes the biller the judge of its own arithmetic.
       `background/finding_severity` owns the finding header and is imported, not re-implemented.

Brief: `docs/staging/DIRECTOR_BRIEF_INDEPENDENT_BILL_VALIDATION_2026-09-02.md`, work items 4 and 5.
What it cannot catch: `docs/design/WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md`.

WHY THIS MODULE IS NOT BEHIND THE CURTAIN, AND WHY THAT IS NOT A HOLE. §4.2 requires that the
VALIDATOR cannot import the billing code; it says nothing about the comparison, which by definition
has to hold both sides. What §4.3 requires instead is an ORDER -- the validator must not see the
statement before it has rebuilt -- and an order is a property of a process, not of an import graph.
So it is enforced the only way a process property can be: `compare_account` produces the
reconstruction and takes its digest BEFORE the statement is fetched, and the statement is reached
through a callable that is not invoked until that has happened. A test drives it with a statement
source that raises if it is called too early, so the ordering is a thing that can fail rather than
a sentence in a docstring.

WHAT "THE VALIDATOR WINS BY DEFAULT" MEANS MECHANICALLY (§4.4). Every claim carries
`authority: "validator"`. A DISAGREED claim is recorded as a defect in the biller and is never
netted, averaged, tolerance-ed away or dropped for being small: the 295 one-penny VAT differences
this finds are all filed individually and counted, because "295 bills disagree by a penny each" and
"the arithmetic agrees" are different statements and only the first is true. Where the validator is
shown to be wrong, that is a finding too -- about the published rules, the export's completeness, or
a concept nobody had defined -- and it is filed in the same list with its cause named.

THE ONE TOLERANCE, AND WHY IT IS NOT SMOOTHING. Money on both sides is carried to the penny, so
`PENNY = 0.005` is the resolution of the QUANTITY and not a band inside which disagreement is
forgiven. There is no tolerance on volumes, on rates or on counts.

AND THE COMPARISON IS ON AMOUNTS, NEVER ON AN IMPLIED RATE. The obvious VAT check -- divide the
charged VAT by the base and compare the ratio to the statutory rate -- is a ratio of two figures
that have each already been rounded to the penny, so on a small bill it reports rounding noise as a
rate error. `expected = round(base x statutory_rate, 2)` compares two quantities of the same kind at
the precision both actually carry. CLAUDE.md: before dividing two numbers, say what each one counts.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path

PROJECT_DIR = Path(__file__).resolve().parent.parent
REPORT_PATH = PROJECT_DIR / "docs" / "reports" / "bill_validation_comparison.json"

#: The three verdicts a claim can carry, and the third is not a soft version of the first.
#: UNCHECKABLE means the validator could not rebuild the quantity from raw facts and published
#: rules, so NOTHING is known about it -- reporting it as agreement would be the fail-open this
#: whole exercise exists to remove, and it is what a comparison that only counted mismatches would
#: silently do.
AGREED = "AGREED"
DISAGREED = "DISAGREED"
UNCHECKABLE = "UNCHECKABLE"

#: Money is carried to the penny on both sides. See the module docstring: this is the resolution
#: of the quantity, not a band inside which a disagreement is forgiven.
PENNY = 0.005

#: Every claim is the validator's until the validator is shown wrong, and being shown wrong is
#: itself a finding rather than a reason to drop the row (§4.4).
AUTHORITY = "validator"


def _claim(name: str, verdict: str, *, expected=None, observed=None, unit: str = "GBP",
           how: str = "", why: str = "") -> dict:
    # A DIFFERENCE ONLY EXISTS BETWEEN TWO NUMBERS, and the first draft subtracted unconditionally.
    # Every claim carried numbers except `period_alignment`, whose two sides are DATE RANGES -- so
    # the only path that would ever have hit it was the one whose own comment says it is
    # structurally impossible, and it would have raised TypeError instead of reporting the
    # misalignment. Caught by the test written for that path, which is the argument for writing a
    # test for a branch you believe cannot be taken.
    numeric = isinstance(expected, (int, float)) and isinstance(observed, (int, float)) \
        and not isinstance(expected, bool) and not isinstance(observed, bool)
    return {"claim": name, "verdict": verdict, "unit": unit,
            "validator_says": expected, "biller_says": observed,
            "difference": round(observed - expected, 6) if numeric else None,
            "authority": AUTHORITY, "how": how, "why": why}


def _amount(lines: list[dict], label: str):
    for line in lines:
        if line.get("label") == label:
            return line.get("amount_gbp")
    return None


def _line_by_label(lines: list[dict], label: str) -> dict | None:
    for line in lines:
        if line.get("label") == label:
            return line
    return None


def compare_bill(reconstructed: dict, issued: dict, *, statutory_vat: dict,
                 read_volume_kwh: float | None) -> list[dict]:
    """Every claim about ONE bill that can be settled, each with its own verdict.

    THE UNCHECKABLE CLAIMS ARE EMITTED, NOT SKIPPED. A comparison that returns only what it could
    check reports "no differences" over a bill it barely read, and the reader has no way to tell a
    verified bill from an unverified one. Half of every bill here is genuinely unverifiable -- the
    network and policy line bundles DUoS, TNUoS, BSUoS, RO, FiT, CfD, CM and smart metering behind
    one figure and no published artefact reconstructs it -- and that is a fact about the export,
    which belongs in the output.
    """
    claims: list[dict] = []
    v_lines = reconstructed.get("lines") or []
    b_lines = issued.get("lines") or []

    # -- the period the two sides think they are talking about ----------------------------------
    if (reconstructed.get("period_start"), reconstructed.get("period_end")) != \
            (issued.get("period_start"), issued.get("period_end")):
        # PAIRED BY POSITION, SO THE PAIRING IS A CLAIM. Both sides are built from the same
        # invoice list in the same order, which makes a mismatch here structurally impossible --
        # and "structurally impossible" is exactly the sort of thing that turns out to be wrong
        # once a re-issue or a void lands. It is checked rather than assumed, and every other
        # claim on this bill is meaningless if it fails.
        claims.append(_claim(
            "period_alignment", DISAGREED, unit="date range",
            expected="{}..{}".format(reconstructed.get("period_start"),
                                     reconstructed.get("period_end")),
            observed="{}..{}".format(issued.get("period_start"), issued.get("period_end")),
            why="the reconstruction and the issued bill at this position cover different "
                "periods, so every other claim on this bill is comparing two different things"))
        return claims

    # -- volume ---------------------------------------------------------------------------------
    energy_b = _line_by_label(b_lines, "Energy") or {}
    billed_volume = (energy_b.get("inputs") or {}).get("consumption_kwh")
    if read_volume_kwh is None or billed_volume is None:
        claims.append(_claim(
            "volume_kwh", UNCHECKABLE, unit="kWh",
            why="the raw export carries no usable pair of readings for this period, so the volume "
                "the bill was charged on cannot be independently derived. Our own consumption "
                "figure is not evidence for itself."))
    else:
        same = abs(float(read_volume_kwh) - float(billed_volume)) < 1e-9
        claims.append(_claim(
            "volume_kwh", AGREED if same else DISAGREED, unit="kWh",
            expected=float(read_volume_kwh), observed=float(billed_volume),
            how="closing read minus opening read, from the raw export"))

    # -- the two reconstructible money lines ----------------------------------------------------
    for label, name in (("Energy", "energy_gbp"), ("Standing charge", "standing_charge_gbp")):
        v_line = _line_by_label(v_lines, label) or {}
        expected = v_line.get("amount_gbp")
        observed = _amount(b_lines, label)
        if expected is None or observed is None:
            claims.append(_claim(name, UNCHECKABLE,
                                 why=v_line.get("why") or "the bill carries no such line"))
            continue
        claims.append(_claim(name, AGREED if abs(observed - expected) < PENNY else DISAGREED,
                             expected=expected, observed=observed, how=v_line.get("how", "")))

    # -- the line nobody can rebuild ------------------------------------------------------------
    net_v = _line_by_label(v_lines, "Network and policy costs") or {}
    claims.append(_claim(
        "network_and_policy_gbp", UNCHECKABLE,
        observed=_amount(b_lines, "Network and policy costs"),
        why=net_v.get("why") or "no published artefact reconstructs this bundled figure"))

    # -- VAT, against the published law ---------------------------------------------------------
    vat_line = _line_by_label(b_lines, "VAT")
    charged = vat_line.get("amount_gbp") if vat_line else None
    rate = statutory_vat.get("rate")
    if vat_line is None or charged is None or rate is None:
        claims.append(_claim("vat_gbp", UNCHECKABLE,
                             why=statutory_vat.get("why") or "the bill carries no VAT line"))
    else:
        # THE BASE IS THE LINES BEFORE VAT, AND THAT IS A CLAIM THIS MAKES RATHER THAN KNOWS. The
        # issued bill does not record its own VAT base. Reading it as "everything printed above
        # the VAT line" reproduces the total exactly on all 10,583 four-line bills, and on the 966
        # five-line ones the catch-up correction sits BELOW the VAT line and is VAT-INCLUSIVE --
        # which is what makes the identity hold there too. If a future bill shape breaks that, the
        # `bill_total_gbp` claim below goes red rather than this one going quietly wrong.
        index = b_lines.index(vat_line)
        base = round(sum(ln.get("amount_gbp") or 0.0 for ln in b_lines[:index]), 2)
        expected = round(base * rate, 2)
        claims.append(_claim(
            "vat_gbp", AGREED if abs(charged - expected) < PENNY else DISAGREED,
            expected=expected, observed=charged,
            how="statutory {:.0%} on GBP {:.2f} of pre-VAT lines".format(rate, base),
            why=statutory_vat.get("why", "")))

    # -- the biller's own internal identity -----------------------------------------------------
    total = issued.get("total_amount_gbp")
    parts = issued.get("parts_sum_gbp")
    if total is None or parts is None:
        claims.append(_claim("bill_total_gbp", UNCHECKABLE,
                             why="the bill does not carry both a total and a parts sum"))
    else:
        claims.append(_claim(
            "bill_total_gbp", AGREED if abs(total - parts) < PENNY else DISAGREED,
            expected=parts, observed=total,
            how="every printed line summed, against the total the customer was asked for",
            why="this one is the BILLER against ITSELF -- the validator supplies no term. It is "
                "here because a bill whose printed parts do not reach its own total is wrong "
                "whatever any reconstruction says."))
    return claims


def compare_account(customer_id: str, record: dict, *, raw_of=None, reconstruct=None,
                    statement_of=None) -> dict:
    """One account, compared. THE ORDER IS THE POINT and it is enforced here (§4.3).

    `statement_of` is a CALLABLE and not a value, so this function decides WHEN the statement comes
    into existence. It is not called until the reconstruction has been produced and digested. That
    is what makes "the validator did not see the statement first" a property something can fail
    rather than an assurance -- see the test that drives it with a statement source which raises if
    reached early.
    """
    from company.billing import raw_account_export as raw_export_mod
    from company.billing import statement_export as statement_mod
    from tools import independent_bill_validator as validator

    raw_of = raw_of or raw_export_mod.raw_account
    reconstruct = reconstruct or validator.rebuild
    statement_of = statement_of or statement_mod.statement

    raw = raw_of(customer_id, record)
    reconstruction = reconstruct(raw)
    reconstruction_digest = hashlib.sha256(
        json.dumps(reconstruction, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()

    # ---- and only now does the statement exist ------------------------------------------------
    statement = statement_of(customer_id, record)
    statement_digest = statement_mod.statement_digest(statement)

    segment = raw.get("segment") or "resi"
    periods = raw.get("periods") or []
    rebuilt = reconstruction.get("periods") or []
    issued = statement.get("issued_bills") or []
    bills: list[dict] = []
    for i, bill in enumerate(issued):
        if i >= len(rebuilt):
            bills.append({"invoice_number": bill.get("invoice_number"),
                          "claims": [_claim(
                              "reconstruction_exists", DISAGREED, unit="count",
                              expected=len(rebuilt), observed=len(issued),
                              why="the statement carries a bill for which the raw export produced "
                                  "no period, so this bill rests on facts the export does not "
                                  "carry -- a gap in the export, which is a finding about us")]})
            continue
        period = periods[i] if i < len(periods) else {}
        volume, _why = validator._volume_from_reads(period)
        vat = validator.statutory_vat_rate(
            segment=segment, commodity=period.get("commodity") or "electricity",
            kwh=volume or 0.0, days=period.get("days_in_period") or 0.0)
        bills.append({
            "invoice_number": bill.get("invoice_number"),
            "period_start": bill.get("period_start"), "period_end": bill.get("period_end"),
            "claims": compare_bill(rebuilt[i], bill, statutory_vat=vat, read_volume_kwh=volume),
        })
    # A PERIOD WITH NO BILL IS THE OTHER DIRECTION AND IS ALSO FILED. The export knows about a
    # period we never billed for; that is either a missing bill or an export that invents periods,
    # and both are ours.
    if len(rebuilt) > len(issued):
        bills.append({"invoice_number": None, "claims": [_claim(
            "bill_exists", DISAGREED, unit="count",
            expected=len(rebuilt), observed=len(issued),
            why="the raw export carries {} period(s) the statement issues no bill for".format(
                len(rebuilt) - len(issued)))]})

    counts = {AGREED: 0, DISAGREED: 0, UNCHECKABLE: 0}
    for bill in bills:
        for claim in bill["claims"]:
            counts[claim["verdict"]] = counts.get(claim["verdict"], 0) + 1
    return {
        "customer_id": customer_id,
        "segment": segment,
        "bills_compared": len(bills),
        "counts": counts,
        "differences": [dict(claim, invoice_number=bill["invoice_number"])
                        for bill in bills for claim in bill["claims"]
                        if claim["verdict"] == DISAGREED],
        "bills": bills,
        # §4.3, made checkable after the fact: the reconstruction's digest is taken before the
        # statement is fetched, so a reconstruction produced afterwards cannot be presented as one
        # produced before.
        "reconstruction_digest": reconstruction_digest,
        "statement_digest": statement_digest,
        "curtain": reconstruction.get("curtain"),
    }


def _provenance() -> dict:
    """Run id, commit and time -- §4.6, which requires AGREEMENT to carry the same provenance as
    any published figure. An agreement with no clock is a claim about a tree nobody can name."""
    try:
        commit = subprocess.run(["git", "rev-parse", "HEAD"], cwd=str(PROJECT_DIR),
                                capture_output=True, text=True, timeout=30).stdout.strip()
    except (OSError, subprocess.SubprocessError):
        commit = ""
    now = datetime.now(timezone.utc)
    return {
        "generated_at": now.isoformat(),
        "commit": commit or "UNKNOWN -- git could not be asked, so this run cannot name its tree",
        "run_id": "billval-{}-{}".format(now.strftime("%Y%m%dT%H%M%SZ"), (commit or "nocommit")[:9]),
    }


def compare_all(ledger_path: Path | None = None, *, limit: int | None = None) -> dict:
    """Every account in the ledger, every run (§4.5). No sampling and no `--one-account` mode.

    ONE ACCOUNT FIRST WAS THE BRIEF'S SEQUENCING, NOT A SETTING. Work item 5 reads "one account
    first, then every account on every run" -- an order of construction, not a runtime flag. A
    validator with a sample size dial is one whose coverage is a decision somebody makes under
    time pressure, and the first thing dialled down is always the slow part. `limit` exists for
    tests and is reported in the output when set, so a truncated run cannot be read as a full one.
    """
    from company.billing import raw_account_export as raw_export_mod

    ledger = json.loads((ledger_path or raw_export_mod.LEDGER_PATH).read_text())
    customers = ledger.get("customers") or {}
    ids = sorted(customers)
    if limit is not None:
        ids = ids[:limit]
    accounts = [compare_account(cid, customers[cid]) for cid in ids]

    counts = {AGREED: 0, DISAGREED: 0, UNCHECKABLE: 0}
    for account in accounts:
        for verdict, n in account["counts"].items():
            counts[verdict] = counts.get(verdict, 0) + n
    differences = [dict(d, customer_id=a["customer_id"])
                   for a in accounts for d in a["differences"]]
    by_claim: dict[str, int] = {}
    for d in differences:
        by_claim[d["claim"]] = by_claim.get(d["claim"], 0) + 1
    return {
        **_provenance(),
        "accounts_in_ledger": len(customers),
        "accounts_compared": len(accounts),
        "truncated": None if limit is None else
                     "LIMITED TO {} ACCOUNTS -- this is not a full run and must not be read as "
                     "one".format(limit),
        "bills_compared": sum(a["bills_compared"] for a in accounts),
        "counts": counts,
        "differences_by_claim": dict(sorted(by_claim.items())),
        "differences": differences,
        "accounts": accounts,
    }


def render(report: dict) -> str:
    """The one-screen read. Differences first, because that is what the run is for."""
    counts = report["counts"]
    lines = [
        "INDEPENDENT BILL VALIDATION -- comparison",
        "=" * 64,
        "run          {}".format(report.get("run_id")),
        "commit       {}".format(report.get("commit")),
        "generated    {}".format(report.get("generated_at")),
        "accounts     {} of {} in the ledger".format(
            report["accounts_compared"], report["accounts_in_ledger"]),
        "bills        {}".format(report["bills_compared"]),
        "",
        "claims       {} agreed | {} DISAGREED | {} uncheckable".format(
            counts.get(AGREED, 0), counts.get(DISAGREED, 0), counts.get(UNCHECKABLE, 0)),
    ]
    if report.get("truncated"):
        lines.append("!! {}".format(report["truncated"]))
    lines.append("")
    if report["differences_by_claim"]:
        lines.append("DIFFERENCES, by claim -- every one is a finding about the biller:")
        for claim, n in report["differences_by_claim"].items():
            lines.append("  {:<26} {}".format(claim, n))
        lines.append("")
        lines.append("The largest ten, by absolute difference:")
        worst = sorted(
            (d for d in report["differences"] if isinstance(d.get("difference"), (int, float))),
            key=lambda d: abs(d["difference"]), reverse=True)[:10]
        for d in worst:
            lines.append("  {:>10.2f} {:<20} {} inv {}  (validator {}, biller {})".format(
                d["difference"], d["claim"], d.get("customer_id"), d.get("invoice_number"),
                d.get("validator_says"), d.get("biller_says")))
    else:
        lines.append("No differences. Every checkable claim on every bill agrees.")
    lines.append("")
    lines.append("UNCHECKABLE IS NOT AGREEMENT. {} claim(s) could not be rebuilt from raw facts "
                 "and published rules at all.".format(counts.get(UNCHECKABLE, 0)))
    return "\n".join(lines)


def delta_against(previous: dict | None, report: dict) -> list[str]:
    """What CHANGED since the last run. Empty means nothing worth waking anyone for.

    A RUNNER THAT PAGES EVERY CYCLE IS A HEARTBEAT, and a heartbeat is what gets muted. This
    reports three things and nothing else:

      * a difference bigger than a penny -- every difference on record so far is exactly 1p, so
        the first one that is not is the defect this whole programme was built to find, and it
        pages on its FIRST occurrence rather than on a count moving;
      * the number of disagreements changing in either direction, because a drop is as
        interesting as a rise and a silent drop is how a control gets quietly disarmed;
      * a claim type appearing or disappearing, because "vat_gbp: 295" becoming
        "energy_gbp: 1, vat_gbp: 294" is a completely different report at the same total.

    Coverage falling is included in the second: `accounts_compared` is in the comparison, and a
    run over fewer accounts than the ledger holds is reported by `compare_all` itself.
    """
    notes: list[str] = []
    big = [d for d in report["differences"]
           if isinstance(d.get("difference"), (int, float)) and abs(d["difference"]) > 0.011]
    if big:
        worst = max(big, key=lambda d: abs(d["difference"]))
        notes.append(
            "A DIFFERENCE LARGER THAN A PENNY: {} on {} invoice {}, GBP {:+.2f} (validator {}, "
            "biller {}). Every difference on record until now was exactly 1p.".format(
                worst["claim"], worst.get("customer_id"), worst.get("invoice_number"),
                worst["difference"], worst.get("validator_says"), worst.get("biller_says")))
    if previous is None:
        return notes
    was, now = previous.get("counts", {}), report.get("counts", {})
    if was.get(DISAGREED) != now.get(DISAGREED):
        notes.append("disagreements {} -> {}".format(was.get(DISAGREED), now.get(DISAGREED)))
    if previous.get("differences_by_claim") != report.get("differences_by_claim"):
        notes.append("claim mix {} -> {}".format(
            previous.get("differences_by_claim"), report.get("differences_by_claim")))
    if previous.get("accounts_compared") != report.get("accounts_compared"):
        notes.append("accounts compared {} -> {}".format(
            previous.get("accounts_compared"), report.get("accounts_compared")))
    return notes


def main(argv=None) -> int:
    import argparse

    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--out", type=Path, default=REPORT_PATH)
    ap.add_argument("--notify", action="store_true",
                    help="page ONLY on a delta against the previous report (never a heartbeat)")
    ap.add_argument("--limit", type=int, default=None,
                    help="compare only the first N accounts -- FOR TESTS. A limited run says so "
                         "in its own output.")
    ap.add_argument("--quiet", action="store_true")
    ap.add_argument("--fail-on-difference", action="store_true",
                    help="exit non-zero when any claim DISAGREES")
    args = ap.parse_args(argv)

    # READ THE PREVIOUS REPORT BEFORE OVERWRITING IT. The delta is the whole value of running this
    # on a cadence, and it lives in a file this run is about to replace.
    previous = None
    if args.out.is_file():
        try:
            previous = json.loads(args.out.read_text(encoding="utf-8"))
        except (OSError, ValueError):
            previous = None

    report = compare_all(limit=args.limit)
    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(report, indent=1, sort_keys=True) + "\n", encoding="utf-8")
    if not args.quiet:
        print(render(report))
        print("\nwrote {}".format(args.out))

    notes = delta_against(previous, report)
    if args.notify and notes:
        try:
            from background.notify import notify

            notify("bill validation: " + "; ".join(notes))
        except Exception as exc:  # a page that cannot be sent must not lose the report
            print("NOTIFY FAILED ({!r}); the delta was: {}".format(exc, "; ".join(notes)))
    elif args.notify and not args.quiet:
        print("\nno delta against the previous report -- nothing paged, which is the point")

    if args.fail_on_difference and report["counts"].get(DISAGREED, 0):
        return 1
    return 0


if __name__ == "__main__":
    import sys

    sys.exit(main())
