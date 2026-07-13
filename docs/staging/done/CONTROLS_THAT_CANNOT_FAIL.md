# CONTROLS THAT CANNOT FAIL — mutation-test the entire quality apparatus (P0 class fix, R10)

**Staged:** 2026-07-13 by advisor. **Disposition: QUEUE, rank HIGHEST.** Not an
interrupt — but nothing on the map matters more than this, because everything on
the map is currently graded by controls we cannot prove work.

## The finding that forces this (your red-team's, and it is superb)
- **`vat_by_segment`, a flagship TIER-1 control, is a TAUTOLOGY**: it derives VAT
  from the segment and checks it against the same segment. It passes every bill
  ever written and **structurally cannot catch the SME-as-Household mislabel
  class it was named to catch.**
- **The Qwen sanity backstop FAILS SILENT**: returns "clean" whenever Ollama is
  down — i.e. on every autonomous run where it wasn't up. The check has been
  passing by NOT RUNNING.
- Fail-open on subtotal <= 0. Plus four more.

**The instances are being fixed (F5 done, F6/F7 registered). The CLASS is not:
we do not know which of our controls are real.** Every level promotion, every
Expert Hour, every green suite this project has ever recorded rests on controls
that may be theatre. **A control that cannot fail is worse than no control — it
manufactures confidence.**

## The requirement — prove every control can FAIL
For EVERY invariant, Tier-1 gate, validator, evaluator, daemon and health check:
1. **Mutation test it.** Inject the exact defect it exists to catch. **It must
   fire.** A control that does not fire on its own named defect is not a
   control — it is decoration, and it must be deleted or rebuilt. No exceptions,
   no "it's obviously fine".
2. **Audit for the three killer patterns** (name them; they are now doctrine):
   - **TAUTOLOGY** — derives the checked value from the same source it checks
     against (the VAT case). Look for any control whose inputs are not
     INDEPENDENT of the thing under test. This is the independence rule, applied
     to controls.
   - **FAIL-OPEN** — passes when data is missing, zero, empty or malformed.
   - **FAIL-SILENT** — passes when the CHECKER ITSELF is unavailable (the Qwen/
     Ollama case). Any control that can be absent must ALARM on absence, never
     return clean. **An unavailable check is a FAILED check.**
3. **Report the kill list**: which controls fired, which did not, which were
   theatre. Publish the number. That number is the single most important
   integrity metric this project has, and it belongs on The Proof door.
4. **Standing rule (CLAUDE.md):** no control may be counted as evidence for a
   level promotion, an Expert Hour pass, or a green suite unless it has a
   passing MUTATION test proving it fires on its own named defect. Retro-apply:
   any atom whose promotion rested on a theatre control is re-opened.

## Why this outranks everything else on the map
The whole apparatus — levels, exit tests, Expert Hours, the trust ledger, the
epistemic verifier — is a machine for producing justified confidence. If the
controls underneath it cannot fail, that machine is producing UNjustified
confidence at scale, and every number it has ever emitted is suspect. Fixing
this is not quality work. It is the precondition for believing anything else we
have built.

## And the pitch consequence (do not bury this — feature it)
"We audited our own controls and found our flagship Tier-1 check could not fail"
is one of the strongest artefacts this project will ever produce. Every real
supplier has controls exactly like this — tautological, fail-open, fail-silent —
and NOBODY audits them, which is precisely why regulators keep finding the same
harms after the same "controls" passed. Publish the kill list, the fixes, and
the method. The Proof door.

## DoD
Every control mutation-tested with results published; the three killer patterns
audited across the whole library; kill list published with counts; the standing
rule in CLAUDE.md; any promotion resting on a theatre control re-opened; F6/F7
closed as part of the class, not as instances. Report the number of controls
that turned out to be theatre — honestly, however embarrassing.