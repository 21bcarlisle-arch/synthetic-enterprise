"""Tests for background/secret_scrub.py -- DIRECTOR_INPUT_LOG.md's
correlatable hash-prefix scrubbing spec."""
from background import secret_scrub


def test_planted_secret_is_redacted():
    planted = "sk-live-topsecret-9f8e7d6c5b4a"
    result = secret_scrub.scrub(f"the topic is {planted}, keep it safe", known_secrets=[planted])
    assert planted not in result
    assert "[redacted:" in result


def test_redaction_is_correlatable_across_entries():
    """Same real secret -> same placeholder, so an advisor can tell two
    scrubbed entries reference the same underlying value without ever
    seeing it."""
    planted = "sk-live-topsecret-9f8e7d6c5b4a"
    a = secret_scrub.scrub(f"first mention: {planted}", known_secrets=[planted])
    b = secret_scrub.scrub(f"second mention: {planted}", known_secrets=[planted])
    placeholder_a = a.split("[redacted:")[1].split("]")[0]
    placeholder_b = b.split("[redacted:")[1].split("]")[0]
    assert placeholder_a == placeholder_b


def test_bare_long_hex_digest_scrubbed_without_known_secrets_list():
    result = secret_scrub.scrub("signature: 46cfc346e705240bbb0fd30945073e9ceee4984ed89bc1eb5c8f9c60472fd4bd")
    assert "46cfc346e705240bbb0fd30945073e9ceee4984ed89bc1eb5c8f9c60472fd4bd" not in result
    assert "[redacted:" in result


def test_short_hex_like_words_not_scrubbed():
    result = secret_scrub.scrub("committed as d3a731b4")
    assert "d3a731b4" in result
    assert "[redacted:" not in result


def test_normal_text_untouched():
    text = "Phase 3 done, 25 new tests passing"
    assert secret_scrub.scrub(text) == text


def test_none_and_empty_secrets_ignored():
    result = secret_scrub.scrub("normal text", known_secrets=[None, "", "not-present"])  # type: ignore[list-item]
    assert result == "normal text"
