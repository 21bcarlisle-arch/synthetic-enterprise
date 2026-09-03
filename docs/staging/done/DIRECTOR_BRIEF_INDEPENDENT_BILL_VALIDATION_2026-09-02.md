# [DIRECTOR-BRIEF] — Independent bill validation behind a curtain (2026-09-02)

**Severity:** LATENT · **Lane:** D_billing_metering · **Epoch:** 3 · **Atom:** unminted

*Header added by the delivery seat, 2026-09-02. The director DID state the severity — "Severity:
LATENT — a programme, not a live defect", inside the `**Type:** [BRIEF — problem, requirements, and the reasoning behind them. Severity: LATENT — a programme, not a live defect. The design is the delivery seat's, and it is explicitly invited to improve on what is proposed here or replace it with something better, provided the properties in §4 hold.]

---

## 1. Why this exists

The journey walk of 31 August and the bill-shock work of 1 September found the same thing from different ends: **the project's arithmetic has never been validated against anything outside itself.** A rate whose money spanned thirteen periods over one period of volume. A bill with five terms where the code assumed four. A bill-shock baseline that was the true bill rather than the issued one, so 63% of the book was differenced against a bill nobody received. A published average unit rate that was the commodity leg presented as the price. None of these was a broken component. Each was a calculation checked only against other calculations by the same author.

The director's diagnosis, stated plainly: **coding different pieces of a calculation in bounded sessions with no shared model is a poor way to produce accurate, scalable arithmetic.** A calculation has invariants — money in equals money out, volume billed equals volume settled, a rate is money over the volume it was charged on — and a bounded session sees its own function and its own tests, never the invariant. So each piece is locally plausible and the whole quietly stops adding up.

The remedy is not more tests written by the same hand. It is **independent reconstruction**: something that has never seen the billing code rebuilds every bill from raw facts and published rules, and every disagreement is a finding about the biller.

**This is also a fidelity requirement, not only a test.** Bill validation is a real B2B service in the GB market. Suppliers are audited by third parties working from raw data. A supplier that cannot produce an auditable export of an account's life, and a statement that shows its working, is not a credible supplier — so building this makes the company more real, not just more correct.

---

## 2. Two exports, kept strictly apart

**The raw export** — the validator's input. Every fact needed to reconstitute an account over its life: meter reads with their dates and type (actual, estimated, customer, deemed); tariff terms with their effective dates; payments as received; adjustments and their reasons. **Nothing derived.** No computed rate, no total, no running balance — and no bill, because a bill *is* the calculation. If a derived figure leaks into this export, the validator confirms our arithmetic against itself and the exercise is worthless.

*(Corrected 2026-09-02 on the delivery seat's objection: the first draft listed "the issued bills as documents" here, two sentences after "nothing derived". A bill is entirely derived and belongs on the statement side. The objection was right.)*

**The statement export** — what we claim. The issued bills as documents, exactly as the customer saw them; every bill's calculation shown line by line; and the balance after each event across the account's life — the transaction history a real supplier gives a customer, and a bill that shows how it reached its number. This is what the validator's reconstruction is compared against.

The separation is the whole value. The validator must never see the statement before it has rebuilt.

---

## 3. The validator, behind a curtain

A validation lane that **structurally cannot import the billing code** — nothing from `company/` or `saas/` — enforced with the same machinery that keeps the company out of the world's internals. It receives the raw export and the published tariff and regulatory rules from the knowledge commons, and rebuilds every bill and the running balance from those alone.

Then the comparison. Every difference between the reconstruction and the statement is filed as a finding about the biller. **The validator wins until proven otherwise.** Where the validator is shown to be wrong, that is itself a finding — about the published rules, the export's completeness, or an ambiguity in a concept — and each of those is worth having.

**What this catches:** implementation errors that belong to us. Wrong signs, wrong denominators, an empty baseline, a rate over the wrong volume, a missing term. A fresh reconstruction from rules does not inherit them.

**What this does not reliably catch, stated honestly:** a domain assumption the validator might share with the biller — the half-month direct debit is the recent example. The same model can make the same domain error twice. That is why the validator reads *published* rules rather than our summaries of them, and why the director still reads the results. The design should say plainly where this residual risk sits rather than claim independence it does not have.

---

## 4. Properties that must hold

These are the requirements. Everything else is the delivery seat's.

1. The raw export contains nothing derived. Provable: a check that refuses a derived field.
2. The validator cannot import the billing code. Provable the way a wall is proved — a mutation that lets it peek must fail a test.
3. The validator does not see the statement until it has produced its reconstruction.
4. Every difference is filed, none is smoothed, and the validator wins by default.
5. It runs on its own schedule, on every account on every run, and needs nobody present.
6. Where the validator's reconstruction and the statement agree, that agreement carries the same provenance as any published figure — run id, commit, time.

---

## 5. Improve it

The delivery seat has improved two director ideas this week by disagreeing with them — walk-first over a registry, and a theme over a class. The same is invited here. If there is a better shape than two exports and a curtained lane, build that instead and record why. If the residual risk in §3 can be reduced — a second reconstruction by a different route, a rules-derived check the validator must also pass, anything that makes shared error less likely — do it. If part of this is wrong in mechanism, say so.

The only things not open are the properties in §4.

## WORK THIS CREATES (canonical, in-document)
1. The raw export, with its no-derived-fields check.
2. The statement export — calculation shown, balance over time.
3. The curtained validator, its curtain proved.
4. The comparison, filing every difference.
5. One account first, then every account on every run, scheduled.
6. A plain statement of what the design cannot catch, and where the director's review still sits.

— Director brief, 2026-09-02, drafted with the advisor. Arithmetic checked only against itself is not checked. This makes the company auditable, which is what a real supplier is.

---

## Disposition — CLOSED 2026-09-03, delivery seat

**All six canonical work items are delivered, and each line below is a path that exists in this
commit rather than a claim.** This brief has been rank 1 in the draw since it was filed; a completed
instruction that nothing dispositions is re-offered every tick forever, which is why the close is an
act and not an inference.

| item | delivered by | its control |
|---|---|---|
| 1. raw export, nothing derived | `company/billing/raw_account_export.py` | `tests/company/billing/test_the_raw_export_carries_nothing_derived.py` |
| 2. statement export, calculation shown, balance over time | `company/billing/statement_export.py` | `tests/company/billing/test_the_statement_shows_how_each_bill_reached_its_number.py` |
| 3. curtained validator, curtain proved | `tools/independent_bill_validator.py` | `tests/tools/…without_us.py::test_a_repository_import_BREACHES_the_curtain` and `::test_the_curtain_is_asserted_at_the_ENTRY_POINT_not_only_in_a_test` |
| 4. the comparison, filing every difference | `tools/bill_validation_comparison.py` (`d886b0114`) | §4.3's order is enforced in code — the reconstruction is digested before the statement is fetched — and driven by a statement source that raises if reached early |
| 5. every account, every run, scheduled | `background/bill-validation.{service,timer}`, hourly, `Persistent` | declared in `schedule_manifest.yaml`; `schedule_reconciler` 0 drift / 19 OK |
| 6. what the design cannot catch | `docs/design/WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md` | prose by nature, and §3 of this brief asked for exactly that |

**Item 5 was verified from the journal, not from the unit file**, per R1: `journalctl --user -u
bill-validation.service` shows nine firings between 09:04:52 and 17:03:11 on 2026-09-03. That is
what makes "it runs every cycle" a fact rather than a configuration.

**And it is what found the one thing that was still broken.** The FIRST unattended firing, 09:04:52,
was the only one with a delta to report — disagreements 295 → 293 — and it died on
`TypeError: notify() missing 1 required keyword-only argument: 'kind'`. The eight firings after it
were silent for the honest reason (no delta), so nothing looked wrong. Item 5 had been landed and
armed and could not tell anybody what it found. Repaired and landed at `f67415d62`, together with a
static control over all 93 `notify` call sites in the tree so the class cannot recur, and with the
second live instance it turned up: `background/delivery_seat.py::_notify`, the seat's own escalation
route to the director, which had swallowed two escalations in a month.

**What this brief BOUGHT, stated because a delivered programme should say what it found.** The first
full run compared 69,294 claims and filed 310 differences, every one of them exactly one penny, and
every one of them the validator's own fault — banker's rounding inherited from the language default,
float subtraction, then float multiplication, each found only by fixing the previous one. Fifteen of
fifteen line differences fell in the biller's favour, about 1 in 33,000 under a fair coin, which is
what made them worth chasing rather than reporting. The biller's arithmetic survived its first
independent audit; the auditor did not, three times.

**Still owed, and NOT held against this brief.** §5 invited improvement on the residual risk in §3 —
a domain assumption the validator might share with the biller. Nothing here reduces it, and
`WHAT_THE_BILL_VALIDATION_CANNOT_CATCH.md` says so plainly rather than claiming an independence the
design does not have. A second reconstruction by a different route remains the obvious next move and
is not started.

Archived to `done/` in the commit that carries this note.
