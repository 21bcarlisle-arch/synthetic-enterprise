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
