# WORKER FINDING — the door-vs-ledger tripwire compared 10 of 19 shared fields, and the 2 that diverged at HEAD were both outside its subject

**Severity:** BLOCKING (H27_payment_belief_gap 2→3) · **Lane:** H_harness · **Disposition:** REPAIRED IN THIS TICK (the atom's own `file_scope`)

**Found:** 2026-08-18, Expert Hour #37 (worker tick, self-refill 2→3 HARDEN draw on `H27_payment_belief_gap`).
**Measured at:** HEAD `f72135409`. §1–§2 are `observed-with-evidence` (R9); §5 is labelled where inferred.
**Class:** a control whose subject is a hand-kept list, so a field can be published unchecked by being absent from a tuple — the same class as the no-caller family (R10), one level down: not *is the control called*, but *what is it called ON*.

## 1. The measurement

`check_published_door_reproduces_the_ledger` — built by Hour #33 precisely to close the door-vs-ledger relation, and recorded DISCHARGED in this atom's `level_hold_note` — returns **ZERO violations** on the committed pair at HEAD while the two artefacts **disagree on two published fields**:

| field | committed door (`site/data/proof.json`) | committed ledger (`docs/observability/coupled_gap_ledger.json`) |
|---|---|---|
| `recon_saturation_band_days` | `[-6, 483]` | `[-6, 82]` |
| `recon_saturation_caveat` | 2,625 chars | 821 chars |

Both read from **one ref** (`git show HEAD:` on each side, into `/tmp/h37_head`) — not a working-tree artefact.

The caveat divergence is not cosmetic. The door carries D28's correction and the ledger does not:

> "AND THE UPPER EDGE IS A PROPERTY OF THE DRAW, NOT OF THE BOOK'S SHAPE (atom D28). The +82d above was measured on ONE draw size (n=300 …); THE BAND STAMPED BESIDE THIS NUMBER IS THIS BOOK'S OWN, derived from its 1482 scored cases: -6d to +483d."

That is 1,804 characters of correction — two Hours' work — present on the surface a reader meets and **absent from the record that surface is nominally derived from**.

## 2. Why the control could not see it

The comparison walked `_DOOR_LEDGER_COMPONENTS`, a hand-kept tuple of ten:

```python
for name in _DOOR_LEDGER_COMPONENTS:
    if name not in door_components or name not in ledger_components:
        continue
```

The two artefacts share **19** components. Ten were compared; nine were never looked at, including both divergent ones. The vacuity guard fires only when `compared` is **empty**, so nine unchecked fields sit comfortably inside a "clean" verdict.

**Neither prior guard could have caught this, which is why the repair is a shape change and not a wider tuple:**

* the SITE-lane ratchet asserts `declared ⊆ compared` — it wedges when a field **leaves**;
* `test_the_component_population_is_not_a_hand_picked_subset` measures coverage against the fields that moved in the 2026-08-17 incident — **every one numeric**.

Both prove the subject has not *shrunk*. Neither can ask whether it was ever the whole published surface. And the family that went unchecked is the `*_caveat` family — the fields carrying the instrument's own **disclosed limits**, which already published a measurably false claim at Hour #31 and a correction that reached no surface at Hour #32.

## 3. The repair (landed, this atom's `file_scope`)

**The subject is now DERIVED from the two artefacts** — every component both sides carry — rather than declared. `_DOOR_LEDGER_COMPONENTS` survives as a **required floor**: a field in it missing from either side is now a violation, because with an intersection-derived subject, erosion would otherwise make the control agree *more easily*.

**R15 both ways against real history, not a fixture:**

* **RED** on the committed pair at HEAD — 2 violations, naming exactly the two divergent fields; subject 10 → 19.
* **GREEN** on the live regenerated pair — 0 violations, subject 23.

**Four mutations proven to fire** (`tests/tools/test_couple_w2_11_d5.py`):

1. a shared field outside the declared tuple diverges → fires (pins #37's defect);
2. **null control** — restore the pre-#37 declared-only subject on the *same* pair → comes back clean, proving the widening is load-bearing and not decorative;
3. a required floor field dropped from the ledger → fires as `REQUIRED` (fail-open on its own subject);
4. a door-only field → **recorded, not judged** (see §4).

Also corrected: `_PRODUCTION_BOOK` / `_FIXTURE_BOOK` omitted `missed_failure_rate`, one of the ten required — the pinned incident fixtures modelled a door that could not exist. Both now carry it at its real value (`0.0`; `missed` is 0 in both books). The pinning is unchanged.

## 4. Queued, not fixed (`SELF_INTERRUPT_DISCIPLINE`)

At HEAD the door publishes **4 fields the ledger has no record of at all** — `dimension_caveats`, `recon_collapsed_runs`, `recon_collapsed_runs_measured_on`, `recon_saturation_band_measured_on`. These are **unfalsifiable by construction**: there is nothing to reproduce them from. They are now `measure`d into `door_only` and deliberately **not** judged — firing on them needs a ledger schema change outside this atom's `file_scope`. A test pins that they stay recorded-not-judged, so the lead can be neither quietly dropped nor quietly promoted.

(The live working-tree ledger regeneration has since added all four, so `door_only` is empty there — which is exactly why the finding had to be measured at HEAD. An uncommitted regeneration masked it locally: *a published artefact can be committed while its source record is not.*)

## 5. What this does to the promotion (inferred from the pre-committed condition)

Hour #31 pre-committed the bar **before** #32 ran: *one Hour against the corrected instrument that ends with NO BLOCKING finding takes the 2→3.*

Hour #37 ends with a blocking finding. **The level stays at 2.** The per-Hour defect rate on this instrument is now **1.0 across nine consecutive Hours** (#28–#33, #35–#37). An Hour cannot be its own confirmation: #37 corrected the instrument, so #37 is not the Hour that clears it.

What #37 does change is the *kind* of surface left: the door-vs-ledger relation is no longer checked on a subset chosen by hand. The next Hour draws against an instrument whose comparison population is derived from the artefacts themselves.

## 6. Owed work, carried forward

* **(A) The `door_only` four** — §4. Needs a ledger schema decision, not a control.
* **(B) The note-field roll** — unchanged from #36: the roll chunks LIST entries and cannot split one string field, so every Hour must compact as it writes (this one did). A store change outside this atom.
* **(C) #28's surviving leads** — the 14 undeclared live entries nothing re-measures on a schedule; #27's clamp and six-unwalked-rows; D35's scoped build; #21's vacuous-in-isolation sibling control.
* **(D) NEW, from §1 — DISCHARGED IN THE COMMIT THAT LANDS THIS DOCUMENT.** The committed ledger was stale against the committed door on this pair; the working tree carried a regeneration that agrees. Landing the widened control WITHOUT it would have put a red control at HEAD for every lane, so both go in one commit — and the regeneration is committed as produced, never hand-edited toward agreement, per the SITE-lane tripwire's own guidance (the ledger is older, so a real run measured the door's figure and the record was simply never committed).

  Verified on real state before landing, not asserted: the widened control returns **2 violations** on the pair read from `git show HEAD:` on both sides (subject 19, naming `recon_saturation_band_days` and `recon_saturation_caveat`), and **0 violations** on the pair this commit creates — HEAD's door against the regenerated ledger, subject 23, `door_only` empty. That second measurement is deliberately taken against **HEAD's** door and not the working tree's, because `site/data/proof.json` carries another lane's staged publishing-run update that this commit does not take: the pair this commit leaves behind is green whether or not that update lands.
