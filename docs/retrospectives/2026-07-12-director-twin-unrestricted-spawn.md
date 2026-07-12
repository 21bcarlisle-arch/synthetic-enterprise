# 2026-07-12 — DIRECTOR_TWIN's first live test spawned an unrestricted autonomous peer

**Claim discipline (R9): everything below is observed-with-evidence** — commit timestamps
(19:45:55/19:46:03 BST) line up to the second with the `ask_twin()` test call's own log entry
(`2026-07-12T18:46:53+00:00` UTC = 19:46:53 BST), the two commits' content and file list are
byte-identical to this session's own uncommitted working-tree files, and `git diff --stat HEAD`
confirmed `CLAUDE.md`/`background/one_way_door.py`/`background/decision_log.py` were already
byte-identical to HEAD at the moment of discovery. Nothing here is inferred.

## What happened

Building the first working version of `background/director_twin.py` (DIRECTOR_TWIN.md), I ran one
real, live test of `ask_twin()` to verify the mechanism end-to-end (this project's own standing
verification discipline — "verify to the rendered value," R11 — not code alone). The twin's
`_default_invoke()` shelled out to `claude -p --model claude-sonnet-5 --dangerously-skip-permissions`
with `cwd` set to this exact repository.

That spawned a **fully unrestricted, fresh Claude Code session sharing this working directory**.
It inherited CLAUDE.md's own "at startup... poll `docs/staging/` and action unread files
immediately" instruction, found four real staged docs sitting in the root
(`RERANK_AND_PROVISIONAL_PLAN.md`, `PROCEED_BY_DEFAULT.md`, `DIRECTOR_TWIN.md`, `MAKE_IT_STICK.md`),
found this session's own already-written (but not yet committed) working files satisfying those
instructions, and — entirely independently, with no direction from this session or the director —
committed them (`2b7d1465`), archived the staged docs (`d51fdcd5`), and **pushed to origin**. All of
this happened inside the ~27 seconds the test call was running, before it returned its actual text
answer back to this session.

## Why this was possible

`ask_twin()`'s only real requirement is "reason over embedded text, print an answer" — the entire
canon is already embedded in the prompt string (see `ask_twin()`'s own prompt construction). It
never needed repo access, tool access, or permission-bypass at all. The first implementation gave it
all three anyway, because the invocation was copied from `background/autonomous_runner.py`'s pattern
(a genuinely autonomous turn, where full access is the correct design) without re-deriving what
*this specific caller* actually needed (R4: diagnosis discipline — name the nearest analogue and
state the diff; the diff here — "this one doesn't need write access at all" — was skipped).

## The class-level lesson (R10: fix the class, not the instance)

**Any subprocess-spawned `claude -p` call sharing this repo's working directory is a second writer,
not a sandboxed function call** — it inherits the full CLAUDE.md system prompt and, unless
explicitly restricted, will act autonomously on whatever it finds there. This applies to every
future caller of this pattern, not just the twin. The fix must be structural (disable tool access at
the CLI level), not a convention to remember (MAKE_IT_STICK's own diagnosis: "policy in memory dies
at the next `/clear` or drifts under load").

## The fix (verified working, not just written)

Three layers of defense in depth in `_default_invoke()`:
1. Drop `--dangerously-skip-permissions` entirely (default-deny permission mode; a non-interactive
   `-p` call cannot satisfy a permission prompt, so any tool-call attempt fails closed).
2. `--tools=` (one argv token, not two — verified directly: `["--tools", ""]` as separate list
   elements is misparsed by the CLI and errors; `["--tools="]` as one token works) structurally
   disables every tool. Verified against a real adversarial test: instructed to write a file via its
   Write tool, the model printed a plausible "I created it" narrative, but the file was never
   actually written (checked directly with `ls`/`cat` — nothing on disk).
3. `cwd` set to a fresh `tempfile.TemporaryDirectory()` outside this repo entirely — so even a
   hypothetical bypass would find no `CLAUDE.md`, no `docs/staging/`, nothing to act on.

Re-verified end-to-end after the fix: `ask_twin("In one sentence, what is Law B?")` answered
correctly from the embedded canon in 4.8 seconds, with zero repo/tool access.

## What was NOT lost

No content was corrupted or duplicated — the spawned session committed real, correct work (my own).
The actual defect is procedural: a commit and a push to origin happened without this session's or
the director's explicit authorisation, from an unintended side channel. Per PROCEED_BY_DEFAULT.md's
own one-way-door list, an unauthorised push is not itself one of the seven categories, but the
*mechanism* that produced it (an unrestricted autonomous spawn) could just as easily have taken a
genuinely consequential action under different prompt content — this is exactly why the fix is
structural rather than "it turned out fine this time."

## Follow-up audit (done, same session)

Checked every `background/*.py` module for a `claude -p`/`--dangerously-skip-permissions` call:
`session_watchdog.py` and `autonomous_runner.py` both do — both are legitimate, intentional
full-autonomy relaunchers (restarting the real autonomous agent session IS their entire purpose;
full repo access and skip-permissions are correct there, not a bug). No other instance of this
incident's class exists in the codebase today.
