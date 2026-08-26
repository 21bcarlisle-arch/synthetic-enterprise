"""H30 — the diagnostic payload of a failed child process.

WHY THIS EXISTS
---------------
`background/sim_runner.py::run_simulation` launched the whole simulation with
`subprocess.run(...)` and no `capture_output`, so the child inherited fds 1/2.
When the runner is started by a daemon those fds point at a socket, not a
terminal — every traceback the child wrote went somewhere nobody reads. On
2026-08-08 eight consecutive runs failed on a plain `NameError` and each one
logged `rc=1` and nothing else; the fault was only ever identified by
re-running the child by hand. The director had to spend attention flagging a
loop that, by construction, could not be diagnosed from its own alert.

R5 says an alert fires on a transition AND CARRIES ITS DIAGNOSTIC PAYLOAD. A
failure report built from a return code alone cannot satisfy that: `rc=1` is
the same string for a missing import, a full disk and a killed process.

WHAT THIS MODULE IS
-------------------
Two small functions, deliberately not a subprocess wrapper. The launch sites
differ (timeouts, cwd, which stream matters, whether stdout must keep
streaming), and a wrapper that tried to own all of that would be the
adapters-for-future-adapters shape the SIMPLICITY GUARD forbids. What they
genuinely share is: turn whatever came back on stderr into something safe to
put in a log line and an NTFY body.

Both are total — bytes, str, None, or a test double's MagicMock all resolve to
a string, never an exception. A diagnostic helper that can itself raise turns a
child's failure into the parent's failure, which is how a monitoring path takes
down the thing it monitors.
"""
from __future__ import annotations

import re

#: Lines of the child's stderr kept for the log. A Python traceback is
#: typically 5-20 lines; 40 holds one comfortably plus whatever the child
#: printed just before dying, without pasting a whole test-suite run into
#: the observability log.
STDERR_TAIL_LINES = 40

#: NTFY bodies are read on a phone. The last stderr line is nearly always the
#: exception type and message — the part that identifies the fault.
NTFY_STDERR_CHARS = 240

#: Rendered when a stream was never piped at all, as opposed to piped and empty.
#: The two are different defects — "nobody looked" is a bug in the LAUNCH SITE,
#: "the child said nothing" is a fact about the child — and a reader who cannot
#: tell them apart re-diagnoses the wrong one. `None` reaches here for both, so
#: the launch site says which by passing `piped=`.
NOT_PIPED = "not captured by the launch site (stream was not piped)"
SAID_NOTHING = "empty (the child wrote nothing to it)"

#: Labels. The header says which of the two reads produced the lines under it, because
#: "last 40 lines" printed over a selection is a small lie that costs a reader the one thing
#: the header is for: knowing whether the lines above are all there were.
SELECTED_LABEL = "the verdict lines a {}-line tail would lose, then that tail"
TAIL_LABEL = "last {} lines"

VERDICT_TRUNCATED = "  [... earlier verdict lines dropped to fit the excerpt budget ...]"
TAIL_JOIN = ("  [... and the last {} lines, where a fail-fast chain leaves the refusal of "
             "whichever step went red ...]")
NO_OUTPUT = "<the gate produced no output to quote>"

#: NO SINGLE LINE MAY EAT THE BUDGET (2026-08-26). The two reads below are each defended
#: against a stream whose NOISE IS UNBOUNDED; neither was defended against ONE LINE that is,
#: and a harness's own narration is where that happens. `tools/pre_commit_test_gate.py` prints
#: its selected file list as a single comma-joined line: at 54 files it is ~2,000 characters and
#: at 62 it is over 4,000, so it ALONE exceeded the 4,000-char budget `surgical_land` passes.
#: The tail then legitimately claimed the whole budget, the `len(floor) >= max_chars` branch
#: below returned the tail alone, and EVERY `FAILED tests/...` node was dropped -- three
#: consecutive refusals in a row quoted a list of file names under the word REFUSED and named
#: no failing test at all. The reader's next move is decided by WHAT went red; a refusal that
#: cannot say costs a whole diagnostic cycle each time, and this one cost three.
#:
#: The fix is a CLASS fix rather than a shorter file list, because the file list is not special
#: -- any step in a twelve-gate chain may print one long line, and the next one will not be this
#: one. So: no line, in the tail or in the selection, may occupy more than this fraction of the
#: budget. An elided line still names its step, which is all the tail is for, and the space it
#: gives back is exactly what the selection needs. Elision is VISIBLE, per the no-silent-caps
#: rule the truncation markers above already follow.
MAX_LINE_SHARE_OF_BUDGET = 0.25
LINE_ELIDED = "  [... {} more characters on this line, elided so it cannot eat the budget ...]"

#: How much of a stream the tail is, when a caller does not say. Sized like STDERR_TAIL_LINES
#: for the same reason: one Python traceback, or one gate's refusal block, fits comfortably.
DEFAULT_TAIL_LINES = STDERR_TAIL_LINES

#: pytest's own count line ("5 failed, 2600 passed in 118.4s"), the line that says whether a
#: list of red nodes is whole. Shared with `tools/surgical_land.py::_test_summary`.
PYTEST_SUMMARY = re.compile(r"^.*\b(\d+ (?:passed|failed|error)[^\n]*)$", re.M)

#: SHOUTED markers, matched CASE-SENSITIVELY. This project shouts its refusals — every gate in
#: tools/git-hooks/pre-commit does — while its ordinary prose is full of lowercase "failed",
#: "error" and "blocked". A case-insensitive match here would select the narrative and drown
#: the verdict, which is the defect this selector exists to remove, one level along.
#:   "FAILED"/"REFUS"   `[site-lane] SITE TESTS FAILED -- COMMIT REFUSED.`,
#:                      `[status-honesty] ... COMMIT REFUSED.`,
#:                      `[process_run] Scoped publish-path gate FAILED`
#:   "ABORT"            the pre-commit test gate, when a changed file's tests go red
#:   "KILLED BY SIGNAL" background_worker's own rendering of an OOM kill (rc < 0)
#:   "[test-gate]" etc. the harness's own SELECTION lines: WHAT was run, which is half of what
#:                      a reader needs in order to act. `[process_run]` is deliberately absent —
#:                      it prefixes every one of the ~100 progress lines a publish emits, so
#:                      selecting on it would rebuild the positional tail with extra steps.
VERDICT_MARKERS = (
    "FAILED", "REFUS", "ABORT", "KILLED BY SIGNAL",
    "[test-gate]", "[site-lane]", "[status-honesty]",
)

#: REFUSAL CLAUSES, matched case-INSENSITIVELY, because these are whole clauses rather than
#: single shouted words: a line that says "not committing" is a refusal in any casing, and the
#: publisher writes it both ways in the same file. Each is quoted verbatim from
#: `background/process_run_complete.py`, which is where a publish's refusals are actually
#: worded — the marker list above catches four of its five and would MISS this one:
#:
#:     "Scoped publish-path gate DID NOT FINISH (>{}s) - not committing content"   (:2418)
#:
#: which carries no shouted word at all. That line is why this second tuple exists; a
#: vocabulary derived from the two refusals that happened to be in the log would have shipped
#: with a hole in it exactly where the timeout path lives.
VERDICT_PHRASES = (
    "not committing",   # :2186 :2369 :2395 :2418 :2426 — every refusal the publisher issues
    "did not finish",   # :2418 — the gate that produced no verdict (R15: unavailable = failed)
    "timed out",        # :2395 — the CAUSE line, which sits above its own consequence
)


def is_verdict_line(line: str) -> bool:
    """Does this line participate in DECIDING a child's verdict?

    Deliberately narrow: the per-node failures, the harness's own selection and refusal lines,
    and pytest's count. Warnings, tracebacks, progress dots and the ~100 `Generated
    site/data/*.json` lines a publish prints are all noise for the purpose of a refusal header
    — the reader's next move is decided by WHAT went red, not by what the runtime warned about
    on the way there.

    A traceback is not matched here ON PURPOSE. Its diagnostic is the LAST line (the exception),
    which is exactly what a positional tail is good at; a stream of that shape matches nothing,
    falls back to the tail, and is rendered in full. Selecting a `Traceback (most recent call
    last):` header while dropping the `NameError` under it would be strictly worse than the
    slice this replaces.
    """
    stripped = line.strip()
    if stripped.startswith(("FAILED ", "ERROR ")):
        return True
    if any(marker in line for marker in VERDICT_MARKERS):
        return True
    lowered = line.lower()
    if any(phrase in lowered for phrase in VERDICT_PHRASES):
        return True
    return bool(PYTEST_SUMMARY.match(line))


def verdict_excerpt(text: str, *, max_chars: int | None = None,
                    max_lines: int | None = None,
                    empty_marker: str = NO_OUTPUT) -> tuple[str, bool]:
    """The stream's TAIL, plus the earlier verdict lines that tail would lose.

    Returns `(excerpt, selected)` — `selected` says whether anything was added ahead of the
    tail, so a caller can label its excerpt honestly.

    TWO READS, BOTH NECESSARY, AND THE HISTORY IS WHY EITHER ALONE IS FAIL-OPEN.

    *The tail alone was wrong* (2026-08-20 and 2026-08-21, two incidents, one shape). A publish
    prints ~100 `Generated site/data/*.json` lines AFTER the sentence naming its refusal, so
    `lines[-40:]` was a list of things that went RIGHT; and a gate's stdout+stderr concatenated
    put import-time SyntaxWarnings after pytest's verdict, so one `\\_` in an f-string filled
    all 4000 characters. In both the noise is UNBOUNDED and the signal BOUNDED, so no budget
    rescues a positional read on its own.

    *The selection alone was ALSO wrong, and worse* (2026-08-24,
    WORKER_FINDING_THE_GATES_REFUSAL_QUOTES_SIX_GREEN_LINES_WHEN_A_NON_PYTEST_GATE_REDS). The
    first version of this function returned the selection and fell back to the tail only when
    the selection was EMPTY — keyed on the selection being empty, never on its being WRONG.
    `tools/git-hooks/pre-commit` runs TWELVE gates and the vocabulary below knows three of
    them; when the pytest gate PASSES and the tenth gate reds, the pass's own green
    `[test-gate] ✓` lines are recognised vocabulary, the fallback cannot fire, and the refusal
    hands its reader six green ticks under the word REFUSED. That is worse than an empty
    excerpt: an empty one says it knows nothing, and this one invites the inference that the
    refusal is spurious — which ends in a bypass, and bypass is a WALL.

    SO THE TAIL IS NOT THE FALLBACK, IT IS THE FLOOR. It is always present, and the selection
    is only ever ADDED to it. That closes the vocabulary hole STRUCTURALLY rather than by
    naming nine more gates (R10: an instance fix for a class defect, which decays the moment a
    thirteenth gate is added): a `cmd || exit 1` chain stops at its first failure, so whichever
    step reds wrote the END of the stream — which is exactly what a tail is good at, and needs
    no vocabulary at all. The selection's remaining job is the one the tail genuinely cannot
    do: carry the individual FAILED nodes out of a pytest run that printed 200 lines after
    them.

    Requires the caller to hand it ONE stream. Concatenating stdout and stderr defeats the
    floor, because then the tail belongs to whichever stream was appended last rather than to
    the step that failed — see `surgical_land.run_gate`, which stopped doing that on the same
    day for this reason.

    This never returns an empty excerpt: a refusal that cannot say why it fired is one an
    operator learns to bypass.
    """
    lines = [ln.rstrip() for ln in text.splitlines() if ln.strip()] if isinstance(text, str) \
        else []
    if not lines:
        return empty_marker, False

    tail_n = max_lines if max_lines is not None else DEFAULT_TAIL_LINES
    cut = max(0, len(lines) - tail_n)
    tail = [_elide_long(ln, max_chars) for ln in lines[cut:]]
    # ONLY the verdict lines the tail would lose. A verdict line already inside the tail is
    # printed by the tail; repeating it would spend the budget saying the same thing twice.
    # Elided BEFORE the membership test, never after: `is_verdict_line` reads the start of a
    # line, and an elided line keeps its start, so selection is unaffected either way -- but a
    # 4,000-character FAILED node would otherwise reproduce the eviction one level in.
    earlier = [_elide_long(ln, max_chars) for ln in lines[:cut] if is_verdict_line(ln)]

    if not earlier:
        return _cap_chars("\n".join(tail), max_chars), False

    joiner = TAIL_JOIN.format(len(tail))
    # THE TAIL HAS PRIORITY IN THE BUDGET. It is the part that explains the refusal; the
    # earlier verdict lines are context for it. A budget that squeezed the tail out to fit
    # more FAILED nodes would reintroduce the defect above at a smaller scale.
    floor = "\n".join([joiner] + tail)
    if max_chars is not None and len(floor) >= max_chars:
        return _cap_chars("\n".join(tail), max_chars), False

    keep: list[str] = []
    used = 0 if max_chars is None else len(floor) + 1
    dropped = False
    for line in earlier:
        if len(keep) >= tail_n or (max_chars is not None
                                   and used + len(line) + 1 + len(VERDICT_TRUNCATED) > max_chars):
            dropped = True
            break
        keep.append(line)
        used += len(line) + 1
    if dropped:
        # NO SILENT CAPS. A truncated list that does not say so reads as a complete one.
        keep = keep[:-1] + [VERDICT_TRUNCATED] if keep else [VERDICT_TRUNCATED]
    return "\n".join(keep + [joiner] + tail), True


def _elide_long(line: str, max_chars: int | None) -> str:
    """One line, shortened if it would take more than its share of the excerpt budget.

    Keeps the HEAD of the line, because that is where a step names itself
    (`[test-gate] 62 test file(s): ...`, `FAILED tests/x.py::y`) -- and where `is_verdict_line`
    looks. The elision is stated in the output rather than silent, so a reader can tell a
    shortened line from a short one.

    No budget means no share to exceed, so nothing is elided: an unbounded caller wants the
    whole stream and this function must not be the thing that decides otherwise."""
    if max_chars is None:
        return line
    cap = max(1, int(max_chars * MAX_LINE_SHARE_OF_BUDGET))
    if len(line) <= cap:
        return line
    return line[:cap] + LINE_ELIDED.format(len(line) - cap)


def _cap_chars(text: str, max_chars: int | None) -> str:
    """Trim to a character budget from the END, on a line boundary.

    A raw `text[-n:]` opens the excerpt mid-token (`t.py:7952: SyntaxWarning...`), and a reader
    who cannot tell a truncated line from a real one spends the first second of a diagnosis on
    the wrong question. Dropping the partial line costs one line and removes the ambiguity;
    when the budget cannot hold even one whole line, the character slice is still better than
    nothing and is returned as-is."""
    if max_chars is None or len(text) <= max_chars:
        return text
    cut = text[-max_chars:]
    _, sep, rest = cut.partition("\n")
    return rest if sep and rest.strip() else cut


def _positional_tail(text: object, *, max_chars: int | None,
                     max_lines: int | None) -> str:
    """The old behaviour, kept as the fallback and as nothing else."""
    if not isinstance(text, str):
        return ""
    out = stderr_tail(text, limit=max_lines) if max_lines is not None else text
    return out[-max_chars:] if max_chars is not None else out


def stderr_tail(raw: object, limit: int = STDERR_TAIL_LINES) -> str:
    """Last `limit` non-blank lines of a child's stderr, as text.

    Accepts `bytes` (undecodable sequences are replaced, never raised on),
    `str`, `None`, or anything else — anything that is not text resolves to
    "" so a caller can always interpolate the result. Returns "" when there
    is nothing to show, which callers must render as an explicit "no stderr
    captured" rather than an empty gap: a silent blank reads exactly like the
    defect this module exists to remove.
    """
    # None, a MagicMock from a test double, an int from a caller that passed the
    # wrong thing. None of those are a diagnostic payload — `_as_text` resolves
    # each to "" rather than raising.
    text = _as_text(raw)
    lines = [line.rstrip() for line in text.splitlines() if line.strip()]
    if not lines:
        return ""
    return "\n".join(lines[-limit:])


def child_output_excerpt(stdout: object, stderr: object, *,
                         stdout_piped: bool = True, stderr_piped: bool = True,
                         limit: int = STDERR_TAIL_LINES) -> str:
    """BOTH streams of a failed child, labelled — the excerpt a wedge diagnosis starts from.

    WHY THIS EXISTS, AND WHY `stderr_tail` WAS NOT ENOUGH (2026-08-21, a 32-hour
    publishing outage that logged zero diagnostic characters per cycle).
    `background_worker.process_leftover_run_markers` launches the publisher with
    `stderr=subprocess.PIPE` and NOTHING for stdout, under a comment that says
    "Capture what the publisher actually said." It does not: the publisher's
    `log()` writes its narrative — including *every* refusal it can issue — to
    **stdout**. So the one line the worker log offers a reader is

        Failed to process run_complete_….md (rc=1) — will retry next cycle
          publisher stderr (last 40 lines):
          WARNING (pytensor.configdefaults): g++ not detected! …
          … SyntaxWarning: "\\_" is an invalid escape sequence …

    — four lines of library noise, identical on all 46 refusals across 2026-08-20/21,
    while the sentence that actually names the cause ("Fast test suite timed out
    (>300s)", "Scoped publish-path gate FAILED") went to an fd the daemon's parent
    points at a socket. `sim_runner`'s auto-process branch is the same shape and goes
    further: it tells the reader "the refusing gate is named in the publisher log
    tail" — of a tail that structurally cannot name it.

    THE POSITIONAL TAIL WAS THE SECOND HALF OF THE DEFECT, AND IT IS NOW CLOSED
    (2026-08-24). Rendering both streams fixed WHICH stream is read; it did not fix
    WHERE IN IT the excerpt looks. `lines[-limit:]` selects by position, and a
    publish prints roughly a hundred `Generated site/data/*.json` lines AFTER the
    sentence that names its refusal — so on the 2026-08-21 17:37Z cycle the forty
    lines this rendered were forty things that went RIGHT, while
    `Fast test suite timed out (>3400s) -- NOT committing` sat just above them.
    Each stream now goes through `verdict_excerpt`, which SELECTS the deciding lines
    and falls back to this same tail when it recognises none — never worse than the
    slice, and much better on the stream that actually refuses.

    THE LABEL IS PART OF THE FIX. It says which of the two happened, because
    "last 40 lines" printed over a selection is a small lie that costs a reader the
    one thing the header is for: knowing whether the lines above are all there were.

    BOTH, NEVER ONE. Preferring stdout would fail-open the other way: a child that
    dies on an uncaught traceback says nothing on stdout and everything on stderr.
    A helper that guessed would be right most of the time, which is the property
    that makes a diagnostic untrustworthy exactly when it is needed. Cost of showing
    both is a few log lines; cost of guessing wrong is another 32-hour outage
    diagnosed by hand.

    Total, like the rest of this module: bytes/str/None/MagicMock all render, and
    a stream that was never piped is reported as such rather than as silence (R15 —
    an unavailable check is a FAILED check, and an unavailable *diagnostic* must not
    read as a clean one).
    """
    parts = []
    for name, raw, piped in (("stdout", stdout, stdout_piped),
                             ("stderr", stderr, stderr_piped)):
        if not piped:
            parts.append("  child {}: {}".format(name, NOT_PIPED))
            continue
        text = _as_text(raw)
        if not text.strip():
            parts.append("  child {}: {}".format(name, SAID_NOTHING))
            continue
        excerpt, selected = verdict_excerpt(text, max_lines=limit, empty_marker="")
        if not excerpt.strip():
            parts.append("  child {}: {}".format(name, SAID_NOTHING))
            continue
        label = SELECTED_LABEL.format(limit) if selected else TAIL_LABEL.format(limit)
        parts.append("  child {} ({}):\n{}".format(name, label, excerpt))
    return "\n".join(parts)


def _as_text(raw: object) -> str:
    """bytes/str/anything -> str, total. Shared by the tail and the selector so a caller can
    never get one behaviour from one and a different one from the other."""
    if isinstance(raw, bytes):
        return raw.decode("utf-8", errors="replace")
    return raw if isinstance(raw, str) else ""


def failure_detail(raw: object, chars: int = NTFY_STDERR_CHARS) -> str:
    """One-line summary of a child's stderr, sized for an NTFY body.

    Takes the LAST line (for a traceback, the exception line) and truncates.
    Returns an explicit marker when nothing was captured, so a reader can tell
    "the child said nothing" apart from "nobody looked" — the second is a
    defect in this code and must not be able to masquerade as the first.
    """
    tail = stderr_tail(raw, limit=1)
    if not tail:
        return "no stderr captured"
    if len(tail) > chars:
        return tail[: chars - 1] + "…"
    return tail
