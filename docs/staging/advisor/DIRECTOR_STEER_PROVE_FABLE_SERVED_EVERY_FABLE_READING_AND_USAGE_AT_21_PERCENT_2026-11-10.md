**Severity:** BLOCKING · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Prove Fable served every Fable reading, and his usage reading is 21% (2026-11-10)

**Type:** STEER, through the advisor channel. It adds to `DIRECTOR_STEER_TEST_FABLE_5_2_AGAINST_OPUS_5_5_ON_OUR_OWN_WORK_2026-11-10.md` and to your pre-registration (`docs/staging/records/SEAT_PREREG_FABLE_5_2_AGAINST_OPUS_5_5_ON_THE_17_OCT_LABELLED_COMMITS_2026-11-10.md`). The director's words, from chat on Tue 10 Nov:

- 07:40 GMT: "How is the test valid? Can we run fable 5.2?"
- 07:42 GMT, on the advisor's recommendation to confirm which model served each reading: "Check it. NB 21% used."

## 1. Prove which model served each reading

CLI 2.1.319 reports `claude-fable-5-2` as `unrecognized_model`. Your smoke call ran and was priced at Opus rates. Nothing yet shows that Fable **answered** it rather than something else serving the call. If any Fable reading was silently served by another model, the comparison is Opus against itself, and a null result would be meaningless.

Wanted:
- **Before trusting any result,** record for every reading the model that actually served it, from the response itself (the API's `model` field, or the CLI's per-model usage breakdown). Do not take it from the requested flag.
- **A Fable reading not served by `claude-fable-5-2` is void,** reported as such, and never counted.
- **Add this as a fifth reported fact in the pre-registration,** marked as added after filing, not before. It is a validity condition, not a changed prediction, and it is stated before any reading result is known.
- If it shows the current CLI cannot actually reach Fable 5.2, say so. Then update Claude Code first (one seat, hooks and gates checked, rollback recorded) and rerun.

## 2. His usage reading

**21% of the weekly allowance used**, at 07:42 GMT Tue 10 Nov. Pace against it under P12. The test's spend is small against what is left, so run it in full.

## Risk

Touches: the Fable test's records only.
Blast radius: none beyond the test.
Probable failure mode: reading the model from the request or the CLI's echo of `--model` rather than from what served the call. Prove the check would catch a substitution, for example by asking for Fable and asserting on what came back.
Proportionality: reversible and narrow — just do it.

— Director steer, 10 Nov 2026, his words above; the drafting is the advisor's.
