**Severity:** RECORDED · **Lane:** A_strategy_governance · **Epoch:** unassigned · **Atom:** `unminted`

# The 25 Nov K8/forward-bands/retention ruling is refused, can't be archived, and isn't waiting, so every tick redraws it

**Found:** 25 Nov, seat executor, drawn as an advisor-channel refusal.

The ruling `docs/staging/advisor/DIRECTOR_RULING_K8_FOR_WORLD_MODELS_FORWARD_BANDS_YES_AND_STEP_BACK_ON_THE_RETENTION_RESULT_2026-11-25.md`
was read in its signed bytes (2c72aaaf6). The only difference from origin is the unsigned "In hand,
not done" note that 11a4387c6 appended, and that note changes no instruction. All three parts are
carried. Part 1 is in canon K8. Part 2 is handed off as `the-forward-world-has-bands-for-gas` and
`k8-covers-world-models-one-leg-test`. Part 3 is handed off as
`the-retention-result-decomposed-and-checked-against-reality`, due 27 Nov. All three are LIVE.

The draw asked for the file to be moved to `done/`. That cannot be done yet. Three checks each hold
it in place:

1. **Refused.** `advisor_channel.provenance` reads the last origin commit to the path. That commit
   is 11a4387c6, and it is unsigned. Only the advisor can re-sign it.
2. **Unarchivable.** The move was attempted, and `ruling_archive_question_gate` refuses it. The
   ruling's three quoted questions are `open` in the register: "What should we really expect to
   happen?", "What is the thesis?" and "What is the knowledge here we are seeking replicate?". They
   are the part-3 work itself.
3. **Not waiting.** `advisor_channel.waiting_on` exempts a file only while an open
   `for_the_director` row names it. All three of this ruling's rows are closed.

So until 27 Nov, each tick draws it at rung zero and finds nothing to do. That is the 20 Nov
site-login shape again, reached by a different route.

**Done instead:** the part-3 continuation was re-handed with its ruling path corrected; it had named
`done/`. Its last step is now to close the three questions in the register and then archive the
ruling, so the redraw stops when the answer lands.

**Two lessons, both cheap:**
- Never append status to a signed advisor file. Put it in DIRECTION or a continuation. The one-line
  note in 11a4387c6 is what made this file refused.
- A possible one-leg fix, not built: `waiting_on` could also treat a file as waiting while a LIVE
  continuation names its path. Weigh it at orientation against the cost of another exemption path.
