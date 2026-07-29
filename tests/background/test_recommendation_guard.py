"""NEVER ASK WITHOUT RECOMMENDING — R15 tests for the outbound ask guard.

R15 demands a control be able to FAIL on its own named defect, and equally that it
NOT fire on the legitimate traffic it must let through. Both directions are tested
here; the mutation record lives in the commit message.

The named defect: an NTFY that asks the director for a decision and recommends
nothing (director ruling, 2026-07-29).
"""
import pytest

from background.recommendation_guard import (
    RecommendationRequired,
    check_message,
)


# ---------------------------------------------------------------- fires (blocks)

def test_bare_question_is_blocked():
    """The exact defect: a question, no recommendation."""
    with pytest.raises(RecommendationRequired):
        check_message(
            "Should the 2022 gas inversion be treated as a fact or a dial?"
        )


def test_two_bare_questions_are_blocked():
    """The literal shape that provoked the ruling -- questions, no recommendation."""
    with pytest.raises(RecommendationRequired):
        check_message(
            "Is 2022 a fact or a dial? And should a trajectory be scripted?"
        )


def test_decision_request_without_a_question_mark_is_blocked():
    """An ask does not need punctuation to be an ask."""
    with pytest.raises(RecommendationRequired):
        check_message(
            "Two options for the storage model. Let me know which one you prefer."
        )


def test_which_would_you_like_is_blocked():
    """The director named this phrasing specifically as the thing to stop."""
    with pytest.raises(RecommendationRequired):
        check_message("Option A or option B for the fold -- which would you like")


def test_the_error_names_the_ruling_and_quotes_the_message():
    """A blocked send must tell the caller how to fix it, not merely refuse."""
    with pytest.raises(RecommendationRequired) as exc:
        check_message("Which lane should I draw from next?")
    text = str(exc.value)
    assert "never ask without recommending" in text
    assert "Which lane should I draw from next?" in text


# ------------------------------------------------------------- permits (passes)

def test_a_plain_statement_is_permitted():
    """No ask -> the guard is not involved at all."""
    check_message("Publish gate cleared: the fold's duplicate-key guard now fires.")


def test_an_ask_that_recommends_is_permitted():
    """Asking is fine. Asking without recommending is not."""
    check_message(
        "Storage model: script the trajectory, or generate it from stock-and-flow? "
        "I recommend generating it -- a scripted path cannot surprise the company. "
        "Proceeding that way unless you object."
    )


def test_here_is_what_im_doing_unless_you_object_is_permitted():
    """The director's own prescribed phrasing must pass."""
    check_message(
        "The 2022 inversion is replayed real history, not a dial. "
        "Here's what I'm doing: treating it as baseline fact. Unless you object?"
    )


def test_empty_and_non_string_messages_are_ignored():
    """The guard must never be the reason a send crashes on junk input."""
    check_message("")
    check_message("   ")
    check_message(None)  # type: ignore[arg-type]


# --------------------------------------------- the ruling's own reserved carve-out

@pytest.mark.parametrize(
    "message",
    [
        "Approve £4,000/month of real spend on the Elexon data feed?",
        "Shall I rotate the production GitHub token and change repo settings?",
        "Do you want me to publish this headline margin figure on the public site?",
        "Should I email the real customer about their final bill?",
    ],
)
def test_director_reserved_asks_may_be_bare(message):
    """Real money, real people, safety controls, public claims -- these are exactly
    what he reserved, so a bare ask about them is CORRECT, not a defect.

    This is the half that stops the guard being a tautology that blocks every
    question: if it fired here too, it would be punishing the escalations the
    ruling explicitly preserved.
    """
    check_message(message)


def test_reserved_detection_is_delegated_not_re_enumerated(monkeypatch):
    """DON'T ACCRETE: the reserved list must come from one_way_door, not a second
    copy inside this module. Proven by making the delegate say 'not a door' and
    watching a money ask become blockable."""
    import background.recommendation_guard as rg

    class _NotADoor:
        is_one_way_door = False

    monkeypatch.setattr(rg, "classify_action", lambda *a, **k: _NotADoor())
    with pytest.raises(RecommendationRequired):
        rg.check_message("Approve £4,000/month of real spend on the data feed?")


def test_guard_permits_when_classification_itself_breaks(monkeypatch):
    """The guard must not crash the alert path if the door classifier throws.

    Resolving to 'permit' here is the deliberate choice: one extra question the
    director can ignore beats an exception on the channel that carries alerts.
    """
    import background.recommendation_guard as rg

    def _boom(*a, **k):
        raise RuntimeError("classifier exploded")

    monkeypatch.setattr(rg, "classify_action", _boom)
    rg.check_message("Some ask with no recommendation at all?")


# ------------------------------------------------------------------ wired in live

def _probe_ntfy_utils():
    """Load an INDEPENDENT copy of background/ntfy_utils.py to exercise the REAL
    send_ntfy body.

    Why not just import it: tests/conftest.py:158 monkeypatches
    `background.ntfy_utils.send_ntfy` for the whole suite (so no test can buzz the
    director's phone), which means the imported name is a stub and the live wiring
    is unobservable through it.

    Why not importlib.reload: reloading an already-imported module is a known
    incident source in this repo (H29 -- a single reload-in-a-finally desynchronised
    module state for unrelated tests). This builds a SEPARATE module object from the
    same file and never touches sys.modules, so the live module is untouched.
    """
    import importlib.util
    from pathlib import Path

    path = Path(__file__).resolve().parents[2] / "background" / "ntfy_utils.py"
    spec = importlib.util.spec_from_file_location("_ntfy_utils_probe", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_send_ntfy_actually_enforces_the_guard():
    """The rule must live on the real channel, not merely in a module nobody calls.

    Asserts against the REAL send_ntfy body: the guard is checked ahead of the
    pytest suppression, so a bare ask raises instead of being posted.
    """
    with pytest.raises(RecommendationRequired):
        _probe_ntfy_utils().send_ntfy("Which atom would you like me to draw next?")


def test_send_ntfy_still_sends_a_recommending_message():
    """The wiring must not block ordinary traffic.

    Reaching the pytest-suppression sentinel proves the guard let the message
    through AND that no real POST happened.
    """
    assert _probe_ntfy_utils().send_ntfy(
        "Publish gate cleared. I'm proceeding to the next atom unless you object."
    ) == "pytest-suppressed"
