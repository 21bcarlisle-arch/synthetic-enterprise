**Severity:** LATENT · **Lane:** H_harness · **Epoch:** unassigned · **Atom:** `unminted`

# [DIRECTOR-STEER] Official plugins earn their place against our own numbers (2026-11-07)

**Type:** STEER, through the advisor channel. It links to `..._MEASURE_WHERE_READING_TOKENS_GO_BEFORE_SPLITTING_ANY_FILE_2026-11-07.md` and `..._CALIBRATE_THE_READERS_ON_OUR_HISTORY_AND_SAY_WHAT_EACH_GATE_HAS_CAUGHT_2026-11-05.md`. The director's words, from chat on Sat 7 Nov:

- 15:52 GMT: "Are their claude code skills, such as approved by anthropic we should consider using or adding? or do our agents have access to these already? eg /agent-estimate:estimate"
- 15:58 GMT, on the advisor's recommendation below: "stage it"

## What the advisor found (check it)

- **The project enables no plugins.** `.claude/settings.json` carries permissions, fallbackModel, env and hooks, and no `enabledPlugins`. Skynet's user-level settings were not visible to the advisor.
- **Anthropic's official marketplace (`claude-plugins-official`) registers automatically** on first launch, but each plugin must be installed. One secondary source says security-guidance is on by default. That is unverified.
- **`agent-estimate` (kiloloop) is third-party, not Anthropic's.** It is alpha, with one maintainer. Its model limits are labelled by its own author as "Local policy (unmeasured)". Its evidence is anecdotal, including a 4–8x over-estimate. That is a picked number presented as an estimate.

## Wanted

1. **Say what is installed:** `/plugin` on Skynet, per seat if they differ. One line in the stretch log.
2. **Trial `pyright-lsp` inside the token measurement.** Go-to-definition and find-references through a language server, instead of grep plus reading large files. Keep it only if the measurement shows it cuts reading tokens, or catches real defects, without new noise. It needs the `pyright` binary on PATH. Say if that is a problem in WSL.
3. **Compare Anthropic's `code-review` plugin with our two readers at the 11 Nov review.** Use the same labelled set: the trial's known-bad and clean commits, plus any confirmed findings since. Report catches, noise and cost side by side. Keep whichever earns its place, or both if they catch different things. Ours stays live while the comparison runs.
4. **Record `agent-estimate` as rejected in the reading log**, with the reason: unmeasured limits, anecdotal accuracy, and "a number you need is a question to research, never a value to pick". Pacing estimates come from our own session records, through the token measurement.

Later, and only if it helps: `skill-creator`'s evaluation, to test our four skills, and `frontend-design` for the Knowledge tab reshape. Not wanted: `commit-commands` and `pr-review-toolkit`, since we use no pull requests and commits already pass the gate chain. Skip `claude-code-setup`'s recommendations unless one names a measured problem.

## Rules for any plugin

- Official marketplace only, unless the director agrees otherwise.
- Read a plugin's hooks, commands and any code before installing it, the same as any file we did not write. A plugin's hooks run with the seat's permissions.
- Trial before keeping. Record what was installed and how to remove it.
- No plugin may widen the sandbox profile or bypass the hooks. Those walls are unchanged.

## Risk

Touches: Skynet's Claude Code plugin set (installable and removable), and the two existing measurements.
Blast radius: per-seat tooling. A plugin hook could slow or block commits.
Probable failure mode: a plugin's hook interacting with our pre-commit chain or stop hooks, such as an extra Stop hook breaking the heartbeat. Read its hooks first and trial it on one seat.
Proportionality: reversible and narrow — just do it.

— Director steer, 7 Nov 2026, his words above; the reading and drafting are the advisor's.

## Done

2026-11-07, worker tick. Moved to done/ because the doorbell found the seat's progress note (fb50d83ae)
unsigned; the ruling above it is the advisor's signed e7b1f86f7 text, unchanged. Items 1 and 4 were done
by the seat (progress note above). Item 2 (pyright) is queued inside the token measurement, second in
`held_behind_the_exit_test` in `docs/direction/priority_order.yaml`. Item 3 (built-in `code-review`
against our two readers) rides the 11 Nov two-reader review row in `docs/direction/DIRECTION.yaml`.
