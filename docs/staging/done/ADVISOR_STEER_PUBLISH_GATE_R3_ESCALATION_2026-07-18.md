# ADVISOR STEER — Publish gate: 6th wedge episode AFTER the class fix — verify deployed, else redesign (2026-07-18)

**Type:** [STEER] — absorb; this is the R3 escalation the advisor committed to if the wedge recurred.

**The facts:** publish_gate_wedged has now fired in SIX distinct episodes today (30x overnight-fix era, 3x ~06:57, 3x 08:35, 11x 09:36, 3x 15:24, 11x 16:23). H23 — the class fix (independent green signal decoupling content publish from operational-test velocity) — was BUILT and DIRECTOR-RATIFIED at L3 hours before the latest episode. A ratified fix that does not stop the failure means one of exactly two things:

1. **H23 is not deployed in the RUNNING gate** (R2 committed-vs-running — the same gap that has bitten three times today), or
2. **H23 is deployed and does not work** — in which case the design is wrong and R3 mandates redesign, not another patch.

**The ask:** determine which, with evidence (show the running gate's code path honoring the independent green signal, then show one wedge-free cycle under active velocity). If (1): deploy, and register the meta-class — "ratified fixes must reach the running system as part of DONE" — as a mechanical check, because committed-not-deployed is now itself a recurring class. If (2): redesign per R3. Do not instance-patch a seventh time.

**Why it matters:** the site is the director's window; every wedge blinds him. Six episodes in one day is the alarm system correctly reporting that the class fix has not actually taken effect.

**Risk & proportionality:** verification is read-only; a deploy is a daemon restart (own commit, revert-clean). Tag: narrow — just do it.

— Advisor, via the staging channel, per its stated escalation commitment.
