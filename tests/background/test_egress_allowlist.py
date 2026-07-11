"""Tests for background/egress_allowlist.py -- Option 2 floor, part (b)."""
import pytest

from background.egress_allowlist import check_allowed, guarded_request, EgressBlocked


class TestCheckAllowed:
    @pytest.mark.parametrize("url", [
        "https://data.elexon.co.uk/bmrs/api/v1/x",
        "https://api.neso.energy/x",
        "https://api.open-meteo.com/v1/forecast",
        "https://skynet-1.taila062fa.ts.net:8765/health",
        "https://github.com/21bcarlisle-arch/synthetic-enterprise",
        "https://raw.githubusercontent.com/x/y/main/z",
        "https://pypi.org/simple/requests/",
        "https://registry.npmjs.org/playwright",
        "https://ntfy.sh/some-topic",
        "http://localhost:8801/status",
        "http://127.0.0.1:8765/health",
    ])
    def test_allows_named_endpoints(self, url):
        assert check_allowed(url) is True

    @pytest.mark.parametrize("url", [
        "https://evil.example.com/exfiltrate",
        "https://not-github.com/",
        "https://githubusercontent.com.evil.net/",  # suffix-spoofing attempt
        "https://elexon.co.uk.attacker.com/",  # suffix-spoofing attempt
        "http://169.254.169.254/latest/meta-data/",  # cloud metadata SSRF target
    ])
    def test_blocks_unlisted_endpoints(self, url):
        assert check_allowed(url) is False

    def test_case_insensitive(self):
        assert check_allowed("https://GITHUB.COM/x") is True

    def test_bare_hostname_without_scheme(self):
        assert check_allowed("github.com/x") is True

    def test_empty_string_blocked(self):
        assert check_allowed("") is False

    def test_subdomain_of_allowed_host_permitted(self):
        assert check_allowed("https://api.github.com/repos/x") is True

    def test_similar_but_different_domain_blocked(self):
        """github.com.evil.com is NOT a subdomain of github.com -- must not
        match via a naive substring check."""
        assert check_allowed("https://github.com.evil.com/") is False


class TestGuardedRequest:
    def test_calls_through_for_allowed_url(self):
        calls = []
        def fake_get(url, **kwargs):
            calls.append(url)
            return "response"
        result = guarded_request(fake_get, "https://github.com/x")
        assert result == "response"
        assert calls == ["https://github.com/x"]

    def test_raises_and_never_calls_for_blocked_url(self):
        calls = []
        def fake_get(url, **kwargs):
            calls.append(url)
            return "response"
        with pytest.raises(EgressBlocked):
            guarded_request(fake_get, "https://evil.example.com/")
        assert calls == []  # the underlying function must never be invoked

    def test_passes_through_extra_args_and_kwargs(self):
        received = {}
        def fake_get(url, timeout=None, headers=None):
            received["url"] = url
            received["timeout"] = timeout
            received["headers"] = headers
            return "ok"
        guarded_request(fake_get, "https://github.com/x", timeout=5, headers={"A": "B"})
        assert received == {"url": "https://github.com/x", "timeout": 5, "headers": {"A": "B"}}
