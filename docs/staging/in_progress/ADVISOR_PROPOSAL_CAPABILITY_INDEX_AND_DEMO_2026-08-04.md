<!-- SUPERVISOR_DRAW: available -->
> **[IN-PROGRESS — 2026-08-08 worker tick] §1 BUILT; §2, §3, §4 STILL OPEN.**
>
> **§1 the capability index — DELIVERED** as atom `AO1_capability_index`, L0→L2
> (`7e5a727d4`, `tools/capability_index.py`, `docs/design/CAPABILITY_INDEX.md`, 24 tests).
> Derived, never hand-authored: 837 rows over the code that exists, ~3s, no committed artefact to
> drift. The proposal's four questions are the row's four fields, and **the empty rows are visible
> by construction** as it asked — 97 unnamed capabilities, 268 orphans, 67 with no test evidence.
>
> **One departure from the proposal, stated rather than absorbed silently.** §1 suggests deriving
> capability identity "from the atom or module under test", i.e. **from the tests**. The delivery
> derives from **source modules**, using tests only as the `evidence` column. Reason: an index keyed
> on the test suite can only ever show capability that is *already tested*, so the most valuable row
> the proposal names — the capability with nothing proving it — is exactly the row that shape cannot
> produce. Deriving from source makes absence visible; deriving from tests makes absence invisible.
>
> **OPEN SUB-ITEMS (this file stays here until they close):**
> 1. **§2 the demo** — a test run with visible output, five suggested loops. Not started. Closest
>    map atom is `AO3_join_test_tier` (the five system tests), now drawable; the demo is the
>    *visible-output* half of those same five and should be built with them, not beside them.
> 2. **§3 the blind check** — batteries executable (`AO8`, drawable, untouched) and blind-by-restricted-
>    context (`AO9`, which must reconcile with `COLD_EYES_PROTOCOL.md`, one mechanism not two).
> 3. **§4 separate the exhaust from the record** — `docs/staging/done/` holds ~4,900 files of which
>    ~4,300 are run-completion markers. **No atom exists for this yet**; it is the one item of the
>    four with no home in the map, which is precisely how work goes invisible (the R17 defect this
>    programme's own absorption hit). Mint it or rule it out — do not leave it here unowned.

# [ADVISOR-PROPOSAL] — How an outsider would assess this, and what that implies we should build (2026-08-04)

**Type:** [PROPOSAL]. Findings and a suggested shape; the mechanism is yours. Refute freely.

## 0. The director's question, which answers the others

*"If a human had to read this codebase and assess this sim and software, how would they do it?"*

They would do three things: **try to run it, read the tests, and look for the gaps.** And they would go to the tests first — because **tests are the only artifact that cannot lie.** Documents describe intentions; tests are executed. A passing test means something real happened. 5,614 documents mean 5,614 things were written.

Everything below follows from that.

## 1. The capability index — derived, never written

**One row per thing the company can do.** Not a document store — a map.

Per row: what it is **in plain words**; whether it works; **what proves it**; and **how you would see it.**

**Derived from the tests, not hand-authored.** A hand-written index drifts the moment code changes; a derived one cannot, and it inherits the coherence rule already ratified — model, diagram, site and map derived from one source, publish failing on disagreement. This is the same principle applied to capability.

**The most valuable rows are the empty ones.** A capability with no test says so; a claim in a document with no capability behind it says so. **The gaps become visible by construction rather than by audit.**

Suggested derivation: capability identity from the atom or module under test, plain-words description authored once and carried alongside, status and evidence from the test run. Where a description is missing, that is a row too — *unnamed capability*.

## 2. The demo — a test run with visible output

**Not a separate artefact.** A demo built by hand is a thing to maintain and a thing that drifts from the code. **The same execution that proves the bill is correct should show you the bill.** One artefact, two jobs.

Different capabilities demo differently, and the index should say which:

- **Document** — here is the bill it produced, the statement, the arrears notice.
- **Chart** — here is the price it formed, the demand it generated, the hedge cover through the year.
- **Trace** — here is one customer's year: reads, bills, payments, an arrear, a recovery.
- **Comparison** — here is what the company believed against what was true.

**Why this matters more than it sounds:** the director has never watched this run. He has seen a website that reports on itself, which is the machine's own account, formatted. A demo is the only verification that checks *every link at once* — vision, interpretation, build and report — because he sees the consequence rather than a claim about it.

**Suggested first five**, matching the five system-test loops already proposed: a run completing and publishing; weather moving through demand to settlement to the book; a meter read becoming a bill, a payment and an arrear; a price becoming a hedge and a P&L; a customer joining, being served, and leaving.

## 3. The blind check — keep the property, drop the manual process

The director is right that it does not scale. But **what made it work was uncontaminated input, not human labour.** Two moves:

**a. Make the existing batteries executable.** Six blind specifications produced disqualification batteries — practitioner statements of what would make this not credible. They are currently **prose in documents**, consulted when someone remembers. Converted to checks, they run forever with nobody pasting anything. That is a large amount of already-purchased external judgement currently sitting inert.

**b. New specifications by restricted context, not by hand.** A reviewer given **only** the plain-words description and the domain — never the code, never the design documents — produces what a practitioner would demand. The property that matters is *what the reviewer cannot see*, and that is enforceable by construction.

## 4. Separate the exhaust from the record

`docs/staging/done/` holds **4,909 files: 4,299 are run-completion markers**, 78 are director or advisor instructions. Machine heartbeat filed in the same drawer as governance.

**Suggested:** operational artefacts to their own location with a retention policy; instructions and rulings kept. The volume was never the problem — the filing is. **78 instructions is a manageable record; 4,909 is an impenetrable one, and they are the same thing badly sorted.**

## 5. Why this is one proposal and not four

Each piece feeds the next. **Tests prove capability → the index is derived from them → the demo is those same tests made visible → the batteries become more tests.** Nothing here is a new class of artefact to maintain; it is the existing test suite made legible, plus one cleanup.

And it puts an honest answer under the director's real worry — *"I only have your word"*. The index is derived, so it cannot flatter. The demo is executed, so it cannot describe something that does not happen. The batteries are external, so they cannot be quietly relaxed.

**What it does not solve:** whether the vision itself is right. Only the blind external check touches that, and only if it keeps being run.

— Advisor proposal, 2026-08-04.
