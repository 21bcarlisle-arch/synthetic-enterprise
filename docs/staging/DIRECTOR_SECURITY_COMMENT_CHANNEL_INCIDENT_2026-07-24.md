# [DIRECTOR-SECURITY] — Comment channel: director DENIES authorship of the 10:22Z comment. Treat as unauthorized-input incident. LOCK FIRST. (2026-07-24)

**Type:** [DIRECTOR-RULING — SECURITY, priority zero after nothing]. Via advisor bridge. The director's verbatim on being asked about the 10:22Z `/supplier/` comment: **"What comment?"** He did not write it. A channel that stages director-attributed input accepted content the director denies. Until proven synthetic, this is an unauthorized-input incident on an authority-adjacent path.

## Immediate, in order

1. **LOCK the intake NOW — fail closed.** Disable the comment-validator's staging path (accept nothing, stage nothing) before any investigation. Re-enable only on an explicit director ruling.
2. **Full provenance of the 10:22Z comment (R9):** the raw comment text verbatim; source metadata as logged (IP/UA/timestamp); the PIN-validation evidence (what PIN, checked how, against what); which commit introduced/enabled this daemon and its form; and the complete consumption trail — what document was staged, what consumed it, and **what state or work it changed**.
3. **Quarantine effects:** anything the consumed comment altered — decisions, drawn work, content — is reverted or flagged pending the director's review. Nothing derived from it stands as director-authorized.
4. **Boring explanation first:** check whether the daemon's own tests/fixtures generated it (a self-test staging a live-labelled comment). If so, the incident closes as a **labelling class-fault**, with the R10: synthetic/test inputs must carry an unmistakable synthetic marker and must be structurally unable to enter the authority path — plus the test that proves it.
5. **The ghost-form finding:** `/supplier/` is folded legacy IA. How did it serve a live, submitting comment form? Enumerate every legacy page still serving active forms or scripts; the fold must fold *behaviour*, not just links.
6. **R15 both ways before any re-enable:** an unauthenticated or wrong-PIN comment must fail loudly; a test-origin comment must be visibly synthetic and non-staging; a genuine director comment (when the director chooses to re-enable) must stage with full provenance attached.

**Report:** one NTFY when locked (minutes, not hours), then the provenance answer. The director confirms authorship of nothing on this channel until then.

**Risk & proportionality:** lock = removing an input, reversible by ruling; investigation read-only; quarantine touches only artifacts derived from the denied comment. Tag: **security — lock first, evidence second, re-enable only by director ruling.**

— Advisor bridge, carrying the director's denial, 2026-07-24.

---

## ADDENDUM (same hour) — Advisor artifact-check RE-SCOPES the incident: no comment occurred today

Advisor fetched the artifacts before this doc was consumed: **all 35 `from_rich_comment_*` files date 2026-07-09→12** (the director's own review-era comments plus one Playwright test fixture on /supplier). **No artifact exists for 2026-07-24.** The "10:22Z staged comment" was the advisor mis-reading `agent_status.json`, which pairs a fresh heartbeat timestamp with a stale `last_action` string — telemetry-as-evidence, the advisor's R9 miss, logged.

**Re-scoped work (replaces §2–§3's hunt; the rest stands):**
1. **Confirm with one glob** that no 2026-07-24 comment artifact exists anywhere (close the phantom formally).
2. **Fix the status-semantics class (R10):** `last_action_ts` must be the action's own time; heartbeat time is a separate field. Sweep every daemon's status emission for the same conflation — misleading telemetry is how this incident got invented.
3. **Synthetic-marker class (R10) stands:** a Playwright test fixture lived in the `from_rich_*` authority namespace for two weeks. Synthetic/test inputs get an unmistakable marker and a namespace that structurally cannot be consumed as director voice; test proves it.
4. **Ghost-form sweep stands:** is the /supplier form (or any folded page's form) still live and submitting? Fold behaviour, not just links.
5. **The channel stays LOCKED.** With the advisor bridge live and phone-signing pending, the director is inclined to **retire page-comments as an authority path** — if page comments ever return, they land as unauthenticated suggestions requiring bridge confirmation, never as director voice. Present retirement vs redesign as a one-line [ACT] for the director's ruling; do not re-enable meanwhile.

— Addendum by advisor bridge, owning the over-read, 2026-07-24.
