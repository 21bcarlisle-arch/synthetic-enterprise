"""Shared ntfy.sh helpers for background processes.

See docs/instructions/NTFY_TWO_WAY_PROTOCOL.md. `session_watchdog.py` polls
the shared NTFY topic for short steering messages Rich sends from the ntfy
app on his phone (Two-Way NTFY Command Channel). To avoid treating our own
outgoing notifications as incoming commands (a feedback loop), every message
sent via `send_ntfy()` has its ntfy-assigned id recorded in `SENT_IDS_FILE`;
`was_sent_by_us()` checks an incoming message's id against that record.

Topic rotation (2026-07-08, docs/staging/NTFY_CHANNEL_HARDENING.md): the
topic name is a secret, no longer committed to git. It is loaded ONLY from
the environment (SE_NTFY_TOPIC), sourced from the gitignored
background/.env.ntfy file — see background/start_worker.sh's env-loading
block. This module raises loudly at import time if the variable is unset
rather than falling back to any default, so a mis-launched process cannot
silently talk over a stale/exposed topic.

Auth: if the topic is reserved/protected, set NTFY_AUTH_TOKEN=t_... in the
environment. Both publish and subscribe calls will include
`Authorization: Bearer <token>`. Without the env var the scripts fall back to
unauthenticated access (public topics only).

Delegation note: hand-written (orchestration-adjacent, per protocol).
"""

import fcntl
import hashlib
import hmac
import json
import os
import subprocess
import time
from pathlib import Path

NTFY_TOPIC: str | None = os.environ.get("SE_NTFY_TOPIC")
if not NTFY_TOPIC:
    raise RuntimeError(
        "SE_NTFY_TOPIC is not set. Load background/.env.ntfy before "
        "starting this process (see background/start_worker.sh) -- there is "
        "no committed default topic any more (2026-07-08 rotation, "
        "docs/staging/NTFY_CHANNEL_HARDENING.md)."
    )
NTFY_PUBLISH_URL = f"https://ntfy.sh/{NTFY_TOPIC}"
NTFY_AUTH_TOKEN: str | None = os.environ.get("NTFY_AUTH_TOKEN")
WAKE_HMAC_KEY: str | None = os.environ.get("SE_WAKE_HMAC_KEY")

SENT_IDS_FILE = Path("/home/rich/synthetic-enterprise/docs/observability/.sent_ntfy_ids.json")
MAX_SENT_IDS = 500

# Delivery observability (2026-08-12, WORKER_FINDING_THE_ESCALATION_CHANNEL_IS_
# FAILING_SILENTLY_2026-08-10 + WORKER_FINDING_THE_ONLY_ESCALATION_CHANNEL_FAILS_
# SILENTLY_2026-08-10, part 1 "say so"). ESCALATION IS NTFY, NEVER THE WINDOW is a
# P0 wall, so this is the only path from this machine to the director -- and it was
# failing OPEN to silence: an HTTP 429 body parses as valid JSON with no `id`, so
# send_ntfy returned a bare None, wrote nothing anywhere, and both the ops mirror and
# the director-input log appended an "out" entry regardless. The record said sent.
# These two files make a non-delivery observable: the log keeps the response body
# VERBATIM (the diagnostic was sitting in result.stdout the whole time, R5), the
# state file carries the transition so a persistent deafness is testable by any
# daemon that does not depend on the failing channel.
DELIVERY_LOG_FILE = Path("/home/rich/synthetic-enterprise/docs/observability/ntfy-delivery-log.md")
DELIVERY_STATE_FILE = Path("/home/rich/synthetic-enterprise/docs/observability/.ntfy_delivery_state.json")
MAX_DELIVERY_LOG_ENTRIES = 200
_DEFAULT_DELIVERY_LOG_FILE = DELIVERY_LOG_FILE
_DEFAULT_DELIVERY_STATE_FILE = DELIVERY_STATE_FILE


def sign_wake_message(text: str, timestamp: int | None = None) -> str:
    """Build a 'text|timestamp|hexhmac' payload for a tmux-relayed wake
    message, signed with SE_WAKE_HMAC_KEY. Raises if the key isn't loaded --
    an unsigned wake message must never be sent silently."""
    if not WAKE_HMAC_KEY:
        raise RuntimeError(
            "SE_WAKE_HMAC_KEY is not set -- cannot sign a wake message. "
            "Load background/.env.ntfy first."
        )
    ts = timestamp if timestamp is not None else int(time.time())
    payload = f"{text}|{ts}"
    digest = hmac.new(WAKE_HMAC_KEY.encode(), payload.encode(), hashlib.sha256).hexdigest()
    return f"{payload}|{digest}"


def verify_wake_message(signed: str, max_age_seconds: int = 300) -> str | None:
    """Verify a 'text|timestamp|hexhmac' payload produced by
    `sign_wake_message`. Returns the original text if the signature is valid
    and not stale, otherwise None -- callers must treat None as untrusted
    input (log it, do not act on it as a real wake)."""
    if not WAKE_HMAC_KEY:
        return None
    try:
        text, ts_str, digest = signed.rsplit("|", 2)
        ts = int(ts_str)
    except ValueError:
        return None
    expected = hmac.new(
        WAKE_HMAC_KEY.encode(), f"{text}|{ts}".encode(), hashlib.sha256
    ).hexdigest()
    if not hmac.compare_digest(expected, digest):
        return None
    if abs(time.time() - ts) > max_age_seconds:
        return None
    return text


def record_sent_id(msg_id: str) -> None:
    """Append `msg_id` to SENT_IDS_FILE (keeping at most MAX_SENT_IDS), under
    an exclusive file lock so concurrent daemon sends cannot LOSE an id via a
    read-modify-write race.

    A lost id is exactly the echo-loop defect this file exists to prevent
    (2026-07-15, inbound_tagging_and_rate_guard): multiple daemons
    (health_check, action_needed, session_watchdog, the responder's own
    replies) can call send_ntfy concurrently on this one shared tree; the
    previous unlocked read-append-write meant two overlapping senders each read
    the same list, appended their own id, and the last writer clobbered the
    other's id. An unrecorded id makes was_sent_by_us() return False for our
    OWN outbound, so ntfy_responder captures it as INBOUND and stages a bogus
    from_rich -- which was observed live for our own [ACTION NEEDED] and
    [HEALTH CHECK] sends. The flock serialises the whole read-modify-write; the
    write is atomic (tmp + os.replace) so a concurrent was_sent_by_us() reader
    never sees a truncated/partial file."""
    SENT_IDS_FILE.parent.mkdir(parents=True, exist_ok=True)
    lock_path = SENT_IDS_FILE.with_name(SENT_IDS_FILE.name + ".lock")
    with open(lock_path, "w") as lock_f:
        fcntl.flock(lock_f, fcntl.LOCK_EX)
        try:
            # ABSENT AND UNREADABLE ARE OPPOSITE FACTS HERE, AND THIS TREATED THEM AS ONE
            # (2026-09-04). No file means nothing was ever sent, so starting a fresh list is
            # right. An unreadable file means ids WERE recorded and cannot be read -- and
            # `ids = []` then wrote a ONE-ENTRY list over them, destroying the only record that
            # our own outbound was ours. Measured, against a prior of three sent ids: truncated,
            # empty and a mapping all left `['id_new']` and turned `was_sent_by_us('id1')` False.
            # That is the echo-loop this file exists to prevent, and the flock above only ever
            # protected against a race losing ONE id. `null` and `{"a": 1}` were worse: they
            # PARSE, so `ids.append` raised AttributeError inside the lock, on the send path.
            ids: list[str] = []
            if SENT_IDS_FILE.is_file():
                try:
                    loaded = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
                except (json.JSONDecodeError, ValueError):
                    loaded = None
                if isinstance(loaded, list) and all(isinstance(i, str) for i in loaded):
                    ids = loaded
                else:
                    _preserve_unreadable_sent_ids()
            ids.append(msg_id)
            ids = ids[-MAX_SENT_IDS:]
            tmp_path = SENT_IDS_FILE.with_name(SENT_IDS_FILE.name + ".tmp")
            tmp_path.write_text(json.dumps(ids), encoding="utf-8")
            os.replace(tmp_path, SENT_IDS_FILE)
        finally:
            fcntl.flock(lock_f, fcntl.LOCK_UN)


def _preserve_unreadable_sent_ids() -> str | None:
    """Move an unreadable sent-ids file aside so the rebuild cannot destroy it. Where it went.

    Called with the flock already held. The retention rule (never overwrite an earlier copy;
    best-effort) now lives once in `episode_prior.preserve_unreadable` -- this and its two
    siblings were byte-identical copies until 2026-09-04.
    """
    from background.episode_prior import preserve_unreadable
    return preserve_unreadable(SENT_IDS_FILE)


def sent_ids_unreadable() -> bool:
    """True when the sent-ids file EXISTS and cannot be trusted -- i.e. we cannot tell whose a
    message is. Named rather than inlined so a caller that wants to fail closed can ask, and so
    the question is greppable. See `was_sent_by_us` for the judgement that is still open."""
    if not SENT_IDS_FILE.is_file():
        return False
    try:
        loaded = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return True
    return not (isinstance(loaded, list) and all(isinstance(i, str) for i in loaded))


def was_sent_by_us(msg_id: str | None) -> bool:
    """True if `msg_id` was recorded by a prior `send_ntfy()` call.

    THE ANSWER FOR AN UNREADABLE FILE IS STILL False, AND THE JUDGEMENT IS NOW SETTLED ELSEWHERE
    (2026-09-04). Absent and unreadable are NOT the same fact. Absent means nothing was ever sent,
    so False is simply true. Unreadable means we cannot tell whose a message is, and neither
    boolean is honest there: False says "not ours", which is how `ntfy_responder` came to capture
    our own outbound as INBOUND and stage a bogus `from_rich` carrying the director's authority he
    never gave; True would suppress a real message from him. The resolution is that the question is
    not this loader's to answer -- it stays a plain "is this id in the record", and the RESPONDER
    asks `sent_ids_unreadable()` FIRST and refuses to classify at all, quarantining the message
    unstaged and unanswered. See `ntfy_responder.check_once`'s provenance branch and
    tests/background/test_the_responder_refuses_to_guess_whose_a_message_is.py. Do not "fix" this
    to return True: that would move the decision back inside a loader and silently re-arm the
    other failure for every future caller.

    What IS fixed: a non-list prior no longer decides this by accident. `json.loads` accepts
    `"abc"`, and `msg_id in "abc"` is a SUBSTRING test, so a corrupt file could answer True for an
    id nobody sent; `null` raised TypeError on the `in`; a mapping tested its keys.
    """
    if not msg_id or not SENT_IDS_FILE.is_file():
        return False
    try:
        ids = json.loads(SENT_IDS_FILE.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, ValueError):
        return False
    if not isinstance(ids, list):
        return False
    return msg_id in ids


def _split_trailing_status(stdout: str) -> tuple[str, str | None]:
    """Split curl's `-w '\\n%{http_code}'` suffix off the response body.

    The status of the POST TO THE TOPIC is the only honest health signal here.
    `curl -I https://ntfy.sh/` returns 200 while the topic is rate-limited, and a
    HEAD on the topic URL returns 404 whether it is healthy or limited (ntfy
    publishes by POST) -- so the obvious reachability probe EXONERATES the failing
    channel. Recorded in the finding; do not replace this with a host probe.

    Tolerates a body with no status suffix (a fake `subprocess.run` in an older
    test, or a curl that never ran) rather than mangling it."""
    body, sep, tail = stdout.rpartition("\n")
    candidate = tail.strip()
    if sep and len(candidate) == 3 and candidate.isdigit():
        return body, candidate
    return stdout, None


def delivery_state() -> dict:
    """The last recorded delivery outcome: {'delivered', 'reason', 'since',
    'consecutive_failures'}. Empty dict if nothing has been recorded yet.

    Exists so 'am I deaf?' is answerable WITHOUT sending on the channel under
    test -- the finding established that the channel cannot be probed cheaply,
    so the only honest design is to make every real send observable."""
    return delivery_state_classified()[0]


def delivery_state_classified() -> tuple[dict, str]:
    """`(state, verdict)` -- ABSENT and PRESENT-BUT-UNREADABLE are opposite facts.

    See background/episode_prior.py. This returned `{}` for both, so a truncated file made
    `delivered` read as None -- the cold-start branch -- and a multi-hour deafness episode
    restamped `since_epoch` at now. And `null`/`[1, 2, 3]` parse, so they escaped the
    except-clause and raised AttributeError at `previous.get("delivered")` on EVERY ntfy send,
    including the send carrying the failure this channel exists to report."""
    from background.episode_prior import load_episode_prior

    return load_episode_prior(DELIVERY_STATE_FILE)


def record_delivery_outcome(delivered: bool, detail: str) -> None:
    """Record whether a POST actually landed, and log the failure text verbatim.

    Test isolation without making the writes untestable: a pytest run that has NOT
    redirected both paths is a silent no-op (the same class of structural guard as
    ntfy_mirror.append_mirror_entry), but a test that monkeypatches them exercises
    the real body. Blanket-guarding on PYTEST_CURRENT_TEST alone would make this
    mechanism unfalsifiable, which is the very defect it was written to fix (R15)."""
    if os.environ.get("PYTEST_CURRENT_TEST") is not None and (
        DELIVERY_LOG_FILE == _DEFAULT_DELIVERY_LOG_FILE
        or DELIVERY_STATE_FILE == _DEFAULT_DELIVERY_STATE_FILE
    ):
        return

    previous, _prior = delivery_state_classified()
    was_delivered = previous.get("delivered")
    failures = 0 if delivered else int(previous.get("consecutive_failures") or 0) + 1
    transition = was_delivered is not None and bool(was_delivered) != delivered
    now = time.time()
    ts = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(now))

    try:
        from background.ntfy_mirror import scrub_secrets
        safe_detail = scrub_secrets(detail, topic=NTFY_TOPIC).replace("\n", " ")
    except Exception:
        safe_detail = detail.replace(NTFY_TOPIC or "\0", "[topic-scrubbed]").replace("\n", " ")

    # EPISODE-SCOPED FIELDS, guarded (self-clearing-alarm census, PW2/PW4). A deafness
    # episode's start and length are exactly the fields an alarm would read for
    # SEVERITY, so a write that has not DEMONSTRATED the episode ended must not be able
    # to shorten them -- that is the 25-hour outage that paged as "paused 30 seconds ago".
    # `since_epoch` is the GUARDED CARRIER and `since` is DERIVED from it below, so the two
    # cannot disagree. Until 2026-08-12 that split existed for a different reason -- the guard
    # was numeric-only and skipped a string field silently, so an ISO `since` could not be
    # wired at all (WORKER_FINDING_THE_MONOTONIC_GUARD_IS_NUMERIC_ONLY, now closed: the guard
    # orders ISO and REFUSES a field it cannot order). The split survives that fix on its own
    # merits, and declaring BOTH would not: `since`'s proposed value is echoed out of the
    # persisted file, so a corrupt string on disk would become a raise inside `send_ntfy` --
    # a data-dependent refusal on the director's only channel. One carrier, one rendering.
    # CLOSE CONDITION: `delivered`, i.e. ntfy returned a server-assigned message id for
    # this POST. It is the strongest evidence this channel can produce and it comes from
    # the SERVER's response body, never from this state file (R15 anti-tautology).
    # AND THE PROPOSAL IS SCREENED BEFORE IT IS OFFERED (2026-09-04). `previous.get("since_epoch",
    # now)` echoed the persisted value straight back, so a `0` on disk was re-proposed every write
    # and -- because `since_fields` is LOW-water and `0` is the earliest instant orderable -- would
    # have beaten a real start too. Adopting only a RECORDED instant, and stamping `now` when there
    # is none, is exactly what the sibling carrier does
    # (`process_run_complete.record_publish_gate_failure`), and calling the same function is what
    # keeps the two answers one answer. `now` rather than `None` because a start we cannot recover
    # still has to be a start: the episode is demonstrably open (the failure streak is rising), and
    # a lower bound that grows correctly from here beats "unknown" forever.
    from background.episode_monotonic import guard_episode, recorded_instant_seconds
    from background.episode_prior import prior_unreadable as _prior_unreadable
    _persisted_epoch = previous.get("since_epoch")
    _carry_epoch = (
        _persisted_epoch if recorded_instant_seconds(_persisted_epoch) is not None else now
    )
    state = guard_episode(
        previous,
        {
            "delivered": delivered,
            "reason": None if delivered else safe_detail[:500],
            "since": ts if transition or was_delivered is None else previous.get("since", ts),
            "since_epoch": now if transition or was_delivered is None else _carry_epoch,
            "last_checked": ts,
            "consecutive_failures": failures,
            # ABSENT vs PRESENT-BUT-UNREADABLE (2026-09-04). `was_delivered is None` above means
            # "cold start, stamp now" -- and an unreadable file produced exactly that reading, so a
            # deafness episode of unknown length restarted at zero on a file nobody could parse.
            # There is no earlier value to recover, so `now` stands; what changes is that the
            # record no longer CLAIMS a cold start it never observed.
            "prior_unreadable": _prior_unreadable(_prior),
        },
        since_fields=("since_epoch",),
        streak_fields=("consecutive_failures",),
        episode_closed=delivered,
    )
    # ONE NAME, ONE NUMBER. The guard repairs `since_epoch`; if `since` were written
    # independently a flap could low-water the epoch back while the string restamped to now,
    # and the two surfaces would describe one episode with two starts -- the defect
    # `episode_age_seconds` exists to prevent, one field over.
    # ...and the SAME screen the carrier's own module states (2026-09-04). `NaN` is worse than
    # wrong -- `time.gmtime` RAISES on it, inside `send_ntfy`, on the path that exists to report
    # that the channel is broken.
    #
    # THE DERIVATION IS NOW UNCONDITIONAL, and the first draft of this block was wrong about why
    # (corrected here, beside the claim). It said "leaving `since` as the guard returned it is the
    # honest branch: an unrecordable epoch is no episode start, and the derived string must not
    # assert one". But `since`'s own proposal is ALSO echoed off disk -- `previous.get("since",
    # ts)` -- so leaving it alone did not decline to assert a start, it re-published whatever
    # string was beside the bad epoch. Measured: a persisted `{since_epoch: 0, since:
    # "1970-01-01T00:00:00Z"}` survived a failure write with both fields intact. ONE NAME, ONE
    # NUMBER means the rendered string is derived from the carrier or is `None`; it may never be
    # inherited.
    #
    # The `None` leg is a BACKSTOP and today's data cannot reach it -- the proposal above is
    # screened, so the guard can only return a recorded instant. Established rather than assumed: a
    # mutation flipping that `else` back to `state.get("since")` SURVIVED the whole suite, which
    # said equivalence, not missing test. So the condition is INJECTED instead
    # (`test_the_ntfy_rendered_string_refuses_to_assert_a_start_the_carrier_does_not_have`): if an
    # upstream regression ever hands this line an unrecordable carrier, the rendered field goes
    # absent rather than inheriting a start from disk.
    _guarded_epoch = recorded_instant_seconds(state.get("since_epoch"))
    state["since"] = (
        time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime(_guarded_epoch))
        if _guarded_epoch is not None else None
    )
    try:
        DELIVERY_STATE_FILE.parent.mkdir(parents=True, exist_ok=True)
        DELIVERY_STATE_FILE.write_text(json.dumps(state, indent=2) + "\n", encoding="utf-8")
    except OSError:
        pass

    # R5: a healthy send stays quiet unless it is the RECOVERY transition. A drop is
    # logged every time -- each one is a director message that did not arrive, not a
    # repeated unchanged status.
    if delivered and not transition:
        return
    label = "DELIVERED" if delivered else "NOT DELIVERED"
    line = f"- [{ts}] [{label}] {safe_detail[:500]}"
    if not delivered:
        line += f" (consecutive failures: {failures})"
    try:
        DELIVERY_LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        existing = (
            DELIVERY_LOG_FILE.read_text(encoding="utf-8").splitlines()
            if DELIVERY_LOG_FILE.is_file() else []
        )
        header = "# NTFY Delivery Log"
        entries = [ln for ln in existing if ln.startswith("- [")]
        entries.append(line)
        entries = entries[-MAX_DELIVERY_LOG_ENTRIES:]
        DELIVERY_LOG_FILE.write_text(
            header + "\n\nEvery POST to the director topic that did not land, verbatim.\n"
            "Written by background/ntfy_utils.send_ntfy.\n\n" + "\n".join(entries) + "\n",
            encoding="utf-8",
        )
    except OSError:
        pass


def send_ntfy(message: str, headers: dict[str, str] | None = None,
              *, _allow_real_send: bool = False) -> str | None:
    """POST `message` to the shared ntfy topic, record its id (so the
    inbound-command poller can recognise and skip it), mirror it
    (secret-scrubbed) for the advisor (ADVISOR_VISIBILITY.md), and return
    the id (or None if the request or id-parsing failed).

    A None return is no longer silent: the outcome is recorded to
    DELIVERY_STATE_FILE and, on a non-delivery, the curl rc / HTTP status / response
    body are logged VERBATIM to DELIVERY_LOG_FILE, and both audit trails record
    `out-undelivered` rather than `out`. Callers that must know may still test the
    return value, but nothing now depends on their remembering to
    (MAKE_IT_STICK: mechanism, not discipline). What this does NOT do is retry or
    queue -- an undelivered message still evaporates with the process (part 2, the
    durable outbox) and nothing yet alarms on sustained deafness (part 3)."""
    # HARD PYTEST GUARD (2026-07-16, director: "my phone is spamming with test
    # messages"). NEVER POST a real NTFY from inside a test run. A test that
    # exercises any notification path WITHOUT mocking send_ntfy would otherwise
    # buzz the director's PHONE with synthetic content ("fake reason", "atom X") --
    # and EVERY process that runs the suite (the publish gate each cycle, an
    # auto-resumed session's recovery checklist, an interactive `pytest` run) did
    # exactly that. pytest sets PYTEST_CURRENT_TEST for the duration of every test;
    # this makes a real send STRUCTURALLY IMPOSSIBLE there, independent of whether
    # each individual test remembers to mock (MAKE_IT_STICK: mechanism, not
    # discipline). This is the ONE fix for the whole test-spam class; a test that
    # needs to assert on a send mocks send_ntfy (replacing this function) as before.
    # NEVER ASK WITHOUT RECOMMENDING (2026-07-29 director ruling). Checked FIRST,
    # ahead of the pytest guard, so the rule is real on every path and testable on
    # this one. Raises rather than dropping -- a bare ask must fail loudly at its
    # call site, never vanish. See background/recommendation_guard.py for why the
    # blocking form is safe here (blast radius measured, not assumed).
    from background.recommendation_guard import check_message
    check_message(message)

    # INTERNAL WORK-ORDER TEXT NEVER REACHES THE DIRECTOR CHANNEL (2026-08-13 director; see
    # background/doorbell_redaction.py). Placed AFTER the recommendation guard so the ask/
    # recommend rule is judged on what the caller actually wrote, and BEFORE the pytest guard so
    # the redaction is real on every path and testable on this one. REDACTS rather than raising:
    # the alarm is legitimate and only its payload is internal, and deleting an alert to punish
    # its formatting would be the worse defect. Logged, never silent.
    from background.doorbell_redaction import redact, was_redacted
    _original, message = message, redact(message)
    if was_redacted(_original, message):
        # The full text stays recoverable in the ops mirror under its own direction, so the
        # redaction removes it from his PHONE and from nowhere else.
        try:
            from background.ntfy_mirror import append_mirror_entry
            append_mirror_entry("out-redacted", _original, topic=NTFY_TOPIC)
        except Exception:
            pass  # a guard must never block or break a real send

    import os
    if os.environ.get("PYTEST_CURRENT_TEST") and not _allow_real_send:
        # A test that genuinely exercises the POST/parse internals (with curl mocked)
        # passes _allow_real_send=True; everything else is suppressed so no test can
        # buzz the director's phone by forgetting to mock.
        return "pytest-suppressed"  # sentinel: a real POST never happens under pytest
    cmd = ["curl", "-s"]
    if NTFY_AUTH_TOKEN:
        cmd += ["-H", f"Authorization: Bearer {NTFY_AUTH_TOKEN}"]
    for key, value in (headers or {}).items():
        cmd += ["-H", f"{key}: {value}"]
    cmd += ["-w", "\n%{http_code}", "-d", message, NTFY_PUBLISH_URL]

    result = subprocess.run(cmd, capture_output=True, text=True)
    body, status = _split_trailing_status(getattr(result, "stdout", "") or "")
    returncode = getattr(result, "returncode", 0) or 0
    try:
        msg_id = json.loads(body).get("id")
    except json.JSONDecodeError:
        msg_id = None

    if msg_id:
        record_sent_id(msg_id)
        record_delivery_outcome(True, f"id={msg_id} http={status or 'unknown'}")
    else:
        # The whole defect was here: an id-less response used to return a bare None.
        # curl rc, HTTP status and the response body are all diagnostics that existed
        # and were thrown away -- a 429 body says "limit reached: daily message quota
        # reached" in plain English.
        stderr = (getattr(result, "stderr", "") or "").strip()
        record_delivery_outcome(
            False,
            f"curl rc={returncode} http={status or 'unknown'} "
            f"body={body.strip()[:300] or '(empty)'}"
            + (f" stderr={stderr[:200]}" if stderr else ""),
        )

    # The record states the OUTCOME, not the attempt. An "out" entry for a message
    # that never left the box is a record that lies -- both audit trails used to
    # append one unconditionally.
    direction = "out" if msg_id else "out-undelivered"

    try:
        from background.ntfy_mirror import append_mirror_entry
        append_mirror_entry(direction, message, topic=NTFY_TOPIC)
    except Exception:
        pass  # mirroring must never block or break a real send

    try:
        from background.director_input_log import append_entry
        append_entry("ntfy", message, direction=direction, hmac_verified=None)
    except Exception:
        pass  # logging must never block or break a real send

    return msg_id
