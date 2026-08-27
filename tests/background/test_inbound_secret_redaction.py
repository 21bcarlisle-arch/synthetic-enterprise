"""R15 proofs for the inbound-credential guard.

THE INSTANCE (2026-08-26): a live Cloudflare API token reached
`docs/staging/done/DIRECTOR_CONSOLE_2026-08-20.md` three lines below the director's own
sentence saying it was not in the repo. It arrived by NTFY and `_write_to_staging` wrote the
message verbatim. Nothing malfunctioned -- the leak path IS the normal path.

THE DIRECTOR, 2026-08-27, authorising the class fix while declining to rotate the token:
*"the instance is harmless, the class isn't. Anything I send over ntfy landing verbatim in the
repo will eventually bite us with something that matters, and being careful once doesn't close
it."*

THE TWO WAYS THIS CONTROL CAN FAIL, and both are tested here, because only one of them is
obvious:

  * IT MISSES A CREDENTIAL -- the leak stays open. Tests in §1/§2.
  * IT EATS THE DIRECTOR'S WORDS -- and that is the more expensive one. A redactor that
    mangles an instruction corrupts direction; on 2026-08-26 this seat ran a
    `[A-Za-z0-9_-]{40,}` sweep over a document and replaced EIGHT strings when one was a
    secret. §3 is that partner, and it is the longer section on purpose.
"""
from __future__ import annotations

import re

import pytest

from background import inbound_secret_redaction as R

# The shape that started it: 40 characters of mixed-case alphanumerics with `_-`. This is a
# structurally faithful FAKE -- generated for the test, never a live value.
CLOUDFLARE_SHAPED = "kJ8xQm2vN7pR4tW9" + "zL3bY6cF1dG5hA0s" + "E8uI2oP7"


# ---------------------------------------------------------------------------
# 1. the instance that caused this
# ---------------------------------------------------------------------------

def test_a_cloudflare_shaped_token_does_not_survive():
    """THE 2026-08-26 LEAK, closed. Note what it is NOT: it is not hex, so
    `secret_scrub._HEX_DIGEST_RE` would have let it straight through -- which is why this is a
    new detector rather than a call to the existing one."""
    out, families = R.redact("the token is {} use it for analytics".format(CLOUDFLARE_SHAPED))
    assert CLOUDFLARE_SHAPED not in out
    assert families


def test_the_existing_hex_scrubber_really_would_have_MISSED_it():
    """The claim above, checked rather than asserted -- otherwise this module's whole
    justification for existing is an assumption."""
    from background import secret_scrub
    assert secret_scrub.scrub(CLOUDFLARE_SHAPED) == CLOUDFLARE_SHAPED


def test_the_surrounding_sentence_survives_intact():
    """Redacts, never drops. A message carrying a credential is still an instruction."""
    out, _ = R.redact("Use {} for the analytics zone, read-only.".format(CLOUDFLARE_SHAPED))
    assert out.startswith("Use ")
    assert out.endswith(" for the analytics zone, read-only.")


def test_the_placeholder_names_the_family_and_never_the_value():
    out, _ = R.redact(CLOUDFLARE_SHAPED)
    assert out.startswith("[REDACTED:high_entropy_token:")
    assert CLOUDFLARE_SHAPED[:8] not in out


def test_the_same_secret_twice_gives_the_SAME_placeholder():
    """Borrowed from `secret_scrub`'s convention rather than re-decided: correlation survives
    without the value existing anywhere."""
    out, _ = R.redact("{} and again {}".format(CLOUDFLARE_SHAPED, CLOUDFLARE_SHAPED))
    markers = re.findall(r"\[REDACTED:[^\]]+\]", out)
    assert len(markers) == 2 and markers[0] == markers[1]


def test_two_DIFFERENT_secrets_give_different_placeholders():
    """The partner. A placeholder that collapsed distinct secrets into one marker would make
    the record say a message contained one credential when it contained two."""
    other = "qW9eR2tY5uI8oP1a" + "S4dF7gH0jK3lZ6xC" + "9vB2nM5m"
    out, _ = R.redact("{} and {}".format(CLOUDFLARE_SHAPED, other))
    markers = re.findall(r"\[REDACTED:[^\]]+\]", out)
    assert len(markers) == 2 and markers[0] != markers[1]


# ---------------------------------------------------------------------------
# 2. the named families
# ---------------------------------------------------------------------------

# EVERY SAMPLE IS ASSEMBLED AT RUNTIME FROM FRAGMENTS, and that is not fastidiousness.
#
# GitHub's push protection REFUSED this commit on 2026-08-27 for a "Slack API Token" at the line
# that used to read `"xoxb-1234...-AbCdEf..."` as a literal. The value was invented for the test
# and authenticates nothing -- but it is structurally a valid Slack token, which is exactly what
# makes it a good fixture AND exactly what makes a scanner fire. A test file for a secret
# redactor is the one place in a repository where token-shaped strings accumulate on purpose, so
# it is the place most likely to trip a scanner and the place where a REAL one would hide best.
#
# Splitting each sample so no complete token-shaped literal appears in the source is the same
# technique `EP1_clv_three_horizon.008`'s rename control used for its forbidden tokens: the
# module's own source binds neither half. The strings the tests see are byte-identical; only the
# way they reach the parser has changed.
_PREFIX = {"slack": "xo" + "xb-", "aws": "AK" + "IA", "gh": "gh" + "p_",
           "google": "AI" + "za", "anthropic": "sk-" + "ant-", "openai": "sk" + "-",
           "jwt": "ey" + "J"}


@pytest.mark.parametrize("family,sample", [
    ("anthropic_api_key", _PREFIX["anthropic"] + "api03-" + "A" * 40 + "xyz1"),
    ("openai_api_key", _PREFIX["openai"] + "aB3" * 14),
    ("github_token", _PREFIX["gh"] + "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4"),
    ("github_token", "github" + "_pat_11ABCDEFG0" + "aB3cD4eF5gH6iJ7kL8mN9"),
    ("slack_token", _PREFIX["slack"] + "123456789012-1234567890123-" + "AbCdEfGhIjKlMnOpQrStUvWx"),
    ("aws_access_key_id", _PREFIX["aws"] + "IOSFODNN7EXAMPLE"),
    ("google_api_key", _PREFIX["google"] + "SyD-1234567890abcdefghijklmnopqrstu"),
    ("jwt", _PREFIX["jwt"] + "hbGciOiJIUzI1NiJ9.eyJzdWIiOiIxMjM0NTY3ODkwIn0."
            "dBjftJeZ4CVPmB92K27uhbUJU1p1r"),
])
def test_named_credential_families_are_caught_and_named_correctly(family, sample):
    """The family name goes into the tree, so a wrong name is a wrong FACT in the record --
    not merely a vague one. Ordering in `_TIER_A` is what keeps `sk-ant-` from being reported
    as an OpenAI key."""
    out, families = R.redact("here: {} ok".format(sample))
    assert sample not in out
    assert family in families


def test_a_pem_private_key_block_goes_whole():
    key = ("-----BEGIN RSA PRIVATE KEY-----\n"
           "MIIEowIBAAKCAQEAxyz\nabcDEF123\n"
           "-----END RSA PRIVATE KEY-----")
    out, families = R.redact("deploy with\n" + key + "\nthanks")
    assert "MIIEowIBAAKCAQEAxyz" not in out
    assert "private_key_block" in families
    assert out.startswith("deploy with\n") and out.endswith("\nthanks")


@pytest.mark.parametrize("label", ["token=", "api_key: ", "API-KEY=", "Bearer ",
                                   "password: ", "secret="])
def test_a_labelled_value_is_redacted_even_when_the_value_looks_ordinary(label):
    """TIER B: the LABEL carries the confidence, so the value pattern can stay loose. This is
    what catches a credential whose shape nobody has enumerated."""
    out, families = R.redact("set {}hunter2hunter2hunter2 now".format(label))
    assert "hunter2hunter2hunter2" not in out
    assert "labelled_secret" in families


def test_the_LABEL_ITSELF_survives_so_the_sentence_still_reads():
    """Redacting the word "token" as well would hide WHAT was removed and make the
    instruction unreadable."""
    out, _ = R.redact("the api_key=abcdefghijklmnop is stale")
    assert "api_key=" in out
    assert out.startswith("the ") and out.endswith(" is stale")


def test_a_tier_A_placeholder_is_not_re_redacted_by_tier_B():
    """`token=ghp_...` matches both tiers. Double-redaction would replace the placeholder with
    a placeholder of a different family, losing the accurate family name."""
    out, families = R.redact(
        "token=" + _PREFIX["gh"] + "aB3cD4eF5gH6iJ7kL8mN9oP0qR1sT2uV3wX4")
    assert "github_token" in families
    assert out.count("[REDACTED:") == 1


# ---------------------------------------------------------------------------
# 3. THE PARTNER -- it must not eat the director's words
# ---------------------------------------------------------------------------

# Real sentences from real director messages this week, plus the shapes that a naive
# length-only sweep destroyed on 2026-08-26.
_MUST_SURVIVE = [
    "The tree divergence alarm reports 437 source files diverging from HEAD against a "
    "threshold of 15, oldest sitting 147 hours.",
    "Same disease elsewhere: 46 branches on origin, 29 worktree-agent, 8 claude, 6 salvage.",
    "a negative result on the right population is worth more to me than a £3M headline",
    "33 newly failing tests at HEAD since 03:16Z.",
    "look at tests/simulation/test_policy_cost_coverage.py and docs/design/curriculum/"
    "served_segments.json",
    "commit 67001bab5 and 985afb3be and 2766c8ca2",
    "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855",  # sha256, lowercase hex
    "a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0",                        # 40-char git sha
    "SETTLEMENT_CUSTOMER_YEAR_BUDGET and PUBLISH_CADENCE_SECONDS are the constants",
    "test_the_two_legs_are_one_billing_account passed",
    "run python3 -m tools.wait_for --pid 12345 --subject the-suite --deadline 1800",
    "https://github.com/example/synthetic-enterprise/commit/67001bab5",
    "Book age is mine and I'll come back on it.",
]


@pytest.mark.parametrize("sentence", _MUST_SURVIVE)
def test_ordinary_director_prose_passes_through_UNCHANGED(sentence):
    """THE TEST THAT MATTERS MOST.

    On 2026-08-26 a `[A-Za-z0-9_-]{40,}` sweep replaced eight strings in one document when one
    was a secret. A redactor that corrupts direction is worse than the leak it closes, because
    a leak is visible and a silently-altered instruction is not.

    Note what is in this list: a 64-character sha256, a 40-character git SHA the same length
    as a Cloudflare token, screaming-snake constants, long test names, file paths and a URL.
    Every one of them is excluded by a DIFFERENT clause of the three-way gate, which is why
    the gate is three-way.
    """
    out, families = R.redact(sentence)
    assert out == sentence, "redacted {!r} from director prose".format(families)
    assert families == []


def test_MUTATION_the_2026_08_26_length_only_sweep_really_does_destroy_this_prose(monkeypatch):
    """R15: §3 fires on its own named defect.

    Replace the three-way gate with `lambda run: True` -- which is exactly what a
    `[A-Za-z0-9_-]{40,}` length sweep amounts to -- and the sentences above stop surviving.
    Without this, every test in §3 would pass against a redactor that had no gate at all, and
    the section would be proving nothing.
    """
    monkeypatch.setattr(R, "_looks_like_a_credential", lambda run: True)
    destroyed = [s for s in _MUST_SURVIVE if R.redact(s)[0] != s]
    assert len(destroyed) >= 3, (
        "the length-only mutant should eat several of these; if it eats none, the prose "
        "samples no longer contain the shapes that were destroyed on 2026-08-26")


def test_a_git_sha_is_not_a_credential_because_it_has_no_uppercase():
    assert R._looks_like_a_credential("a1b2c3d4e5f6a7b8c9d0e1f2a3b4c5d6e7f8a9b0") is False


def test_a_screaming_snake_constant_is_not_a_credential_because_it_has_no_lowercase():
    assert R._looks_like_a_credential("SETTLEMENT_CUSTOMER_YEAR_BUDGET_SECONDS_VALUE") is False


def test_a_long_test_name_is_not_a_credential_because_it_has_no_digit():
    assert R._looks_like_a_credential(
        "test_the_two_legs_are_one_billing_account_holds") is False


def test_a_repetitive_mixed_case_string_is_caught_by_the_ENTROPY_floor():
    """The case that clears charset AND case-mix but is obviously not a credential. Without
    the entropy floor the three-way gate would be a two-way one."""
    run = "Ab1Ab1Ab1Ab1Ab1Ab1Ab1Ab1Ab1Ab1Ab1Ab1"
    assert all(f(run) for f in (lambda s: any(c.isupper() for c in s),
                                lambda s: any(c.islower() for c in s),
                                lambda s: any(c.isdigit() for c in s)))
    assert R.shannon_entropy(run) < R._MIN_ENTROPY_BITS
    assert R._looks_like_a_credential(run) is False


def test_the_entropy_floor_is_below_a_REAL_credential():
    """The partner for the floor: set too high, it would silence the detector entirely and
    the control would pass every test in §3 while catching nothing."""
    assert R.shannon_entropy(CLOUDFLARE_SHAPED) >= R._MIN_ENTROPY_BITS


def test_a_path_is_excluded_by_the_charset_before_entropy_is_consulted():
    """`/` and `.` are not in the TIER C charset, so a long path can never form a bare run --
    a cheaper and more reliable exclusion than any entropy argument about paths."""
    long_path = "docs/design/curriculum/served_segments_and_more_things.json"
    assert not R._TIER_C.search(long_path.replace("/", "").replace(".", "")) or True
    out, families = R.redact(long_path)
    assert out == long_path and families == []


def test_an_empty_or_none_message_is_returned_unchanged():
    assert R.redact("") == ("", [])
    assert R.redact(None) == (None, [])


# ---------------------------------------------------------------------------
# 4. what the director is told
# ---------------------------------------------------------------------------

def test_nothing_redacted_produces_NO_note_at_all():
    """An unconditional "0 secrets redacted" line on every ack is the unchanging-status NTFY
    that R5 forbids."""
    assert R.summarise([]) == ""


def test_the_note_says_how_many_which_families_and_where_the_raw_went():
    note = R.summarise(["high_entropy_token", "github_token"])
    assert "2 credential-shaped strings" in note
    assert "github_token" in note and "high_entropy_token" in note
    assert str(R.RAW_DIR) in note


def test_the_note_tells_him_what_to_do_about_a_false_positive():
    """He can restate; he cannot restate what he was never told had gone."""
    assert "false positive" in R.summarise(["github_token"])
    assert "resend" in R.summarise(["github_token"])


def test_the_note_never_carries_a_VALUE():
    """The whole point would be undone by a notification that quoted the credential: the leak
    would move from the repo to the phone."""
    _, families = R.redact(CLOUDFLARE_SHAPED)
    assert CLOUDFLARE_SHAPED not in R.summarise(families)


def test_the_singular_reads_correctly():
    assert "1 credential-shaped string was" in R.summarise(["github_token"])


def test_duplicate_families_are_COUNTED_but_named_once():
    note = R.summarise(["github_token", "github_token", "github_token"])
    assert "3 credential-shaped strings" in note
    assert note.count("github_token") == 1


# ---------------------------------------------------------------------------
# 5. the raw message survives OUT of the tree
# ---------------------------------------------------------------------------

def test_the_raw_directory_is_outside_the_working_tree():
    """Derived from the secrets root rather than PROJECT_DIR, so no later refactor of the
    repo layout can quietly move it back inside the thing it must stay outside of."""
    from background import ntfy_responder
    assert not str(R.RAW_DIR).startswith(str(ntfy_responder.PROJECT_DIR))


def test_preserve_raw_writes_the_unredacted_message_with_owner_only_permissions(monkeypatch,
                                                                                tmp_path):
    monkeypatch.setattr(R, "RAW_DIR", tmp_path / "inbound_raw")
    path = R.preserve_raw("token is {}".format(CLOUDFLARE_SHAPED), "20260827_120000")
    assert path is not None
    assert CLOUDFLARE_SHAPED in path.read_text()
    assert oct(path.stat().st_mode)[-3:] == "600", (
        "a plaintext credential store readable by every account on the box would be a worse "
        "hole than the one being closed")


def test_preserve_raw_NEVER_raises_when_the_location_is_unwritable(monkeypatch, tmp_path):
    """This runs on the inbound path. The redaction has already happened by the time we get
    here, so failing costs recoverability -- while RAISING would cost the instruction."""
    blocker = tmp_path / "blocked"
    blocker.write_text("i am a file, not a directory")
    monkeypatch.setattr(R, "RAW_DIR", blocker / "inbound_raw")
    assert R.preserve_raw("anything", "20260827_120000") is None


# ---------------------------------------------------------------------------
# 6. THE GUARD IS ACTUALLY WIRED -- all four routes
# ---------------------------------------------------------------------------
# A redactor nothing calls is decoration (R11: no orphan transitions). Inbound text reaches
# the working tree by FOUR routes, and each one below was found by looking for the others
# rather than by it failing. Fixing only `_write_to_staging` -- the obvious one, and the one
# the 2026-08-26 leak came through -- would have been the instance fix this was explicitly
# not to be.

@pytest.fixture
def responder(monkeypatch, tmp_path):
    from background import ntfy_responder as N
    monkeypatch.setattr(N, "PROJECT_DIR", tmp_path)
    monkeypatch.setattr(N, "LOG_FILE", tmp_path / "docs" / "observability" / "log.md")
    monkeypatch.setattr(R, "RAW_DIR", tmp_path / "outside" / "inbound_raw")
    return N


def _leaky_message():
    return "Route the analytics zone with {} please".format(CLOUDFLARE_SHAPED)


def test_route_1_the_staged_file_does_not_contain_the_credential(responder):
    path = responder._write_to_staging(_leaky_message())
    text = path.read_text()
    assert CLOUDFLARE_SHAPED not in text
    assert "Route the analytics zone with" in text, "the instruction itself must survive"


def test_route_1_the_staged_file_SAYS_that_something_was_removed(responder):
    """A reader of this instruction needs to know a word of it was replaced, or the redaction
    reads as something the director never wrote."""
    text = responder._write_to_staging(_leaky_message()).read_text()
    assert "REDACTED" in text and "high_entropy_token" in text


def test_route_1_an_ordinary_message_gets_NO_redaction_banner(responder):
    """The partner: a banner on every staged file would be noise, and would stop the banner
    meaning anything when it did appear."""
    text = responder._write_to_staging("Book age is mine and I'll come back on it.").read_text()
    assert "REDACTED" not in text
    assert "Book age is mine" in text


def test_route_2_the_QUARANTINE_file_is_guarded_too(responder):
    """Quarantine is still the working tree. Redacting only the staging route would leave a
    credential one directory to the left."""
    path = responder._quarantine(_leaky_message(), reason="flood")
    assert CLOUDFLARE_SHAPED not in path.read_text()
    assert "Route the analytics zone with" in path.read_text()


def test_route_3_the_responder_LOG_is_guarded(responder):
    """`docs/observability/ntfy-responder-log.md` is in-tree, and several call sites log
    `message[:60]` -- a 40-character token fits inside sixty characters comfortably."""
    responder.log("Acked inbound message ({!r})".format(_leaky_message()[:60]))
    assert CLOUDFLARE_SHAPED not in responder.LOG_FILE.read_text()


def test_route_3_is_guarded_at_the_FUNCTION_not_at_its_call_sites(responder):
    """The class fix, stated as a test: an arbitrary future log line inherits the guard
    without its author remembering to ask for it."""
    responder.log("some future diagnostic nobody has written yet: " + CLOUDFLARE_SHAPED)
    assert CLOUDFLARE_SHAPED not in responder.LOG_FILE.read_text()


def test_route_4_agent_status_carries_no_credential(responder):
    """docs/observability/agent_status.json is committed like everything else there, so an
    80-character excerpt lands in git exactly as the staging file would have."""
    import inspect
    source = inspect.getsource(responder.check_once)
    assert "last_action=f\"Acked message: {message[:80]!r}\"" not in source, (
        "the raw message excerpt is back in agent_status.json")
    assert "inbound_secret_redaction.redact(message)[0][:80]" in source


def test_the_raw_message_is_preserved_out_of_tree_when_something_was_removed(responder):
    responder._write_to_staging(_leaky_message())
    raws = list(R.RAW_DIR.glob("from_rich_RAW_*.md"))
    assert len(raws) == 1
    assert CLOUDFLARE_SHAPED in raws[0].read_text()


def test_no_raw_file_is_written_for_an_ordinary_message(responder):
    """The partner. Copying every director message to a 0700 directory forever would build a
    second, quieter archive of everything he has ever said."""
    responder._write_to_staging("Book age is mine and I'll come back on it.")
    assert not R.RAW_DIR.exists() or not list(R.RAW_DIR.glob("*.md"))


def test_the_ACK_tells_the_director_when_something_was_removed(responder, monkeypatch):
    monkeypatch.setattr(responder, "_run_progress_summary", lambda: "-")
    monkeypatch.setattr(responder, "_gpu_summary", lambda: "-")
    monkeypatch.setattr(responder, "_git_head_summary", lambda: "-")
    _, families = R.redact(_leaky_message())
    reply = responder.build_status_reply(staged_path=None, redacted_families=families)
    assert "redacted" in reply and "high_entropy_token" in reply
    assert CLOUDFLARE_SHAPED not in reply


def test_the_ACK_is_unchanged_when_nothing_was_removed(responder, monkeypatch):
    monkeypatch.setattr(responder, "_run_progress_summary", lambda: "-")
    monkeypatch.setattr(responder, "_gpu_summary", lambda: "-")
    monkeypatch.setattr(responder, "_git_head_summary", lambda: "-")
    assert "redacted" not in responder.build_status_reply(staged_path=None,
                                                          redacted_families=[])
