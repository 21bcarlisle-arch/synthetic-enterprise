# NTFY Message Mirror

Outbound NTFYs and inbound from_rich messages, secret-scrubbed (topic/signatures never appear). See docs/staging/done/ADVISOR_VISIBILITY.md.
Rotates at the most recent entries -- older history lives in git log for this file.

- [2026-07-09 14:06:21 UTC] [IN] this is a live test entry to prove the mirror works end to end
- [2026-07-09 14:08:36 UTC] [OUT] ADVISOR_VISIBILITY.md done + pushed (ffaf2287): NTFY message mirror live at docs/observability/ntfy-mirror.md, secret-scrubbed, wired into send_ntfy() and ntfy_responder.py's inbound path so it's automatic going forward -- this very message will appear in the mirror once sent, which is the doc's own required proof. Found and fixed a real test-isolation bug live while wiring it: some existing tests monkeypatch subprocess.run directly (a shared module object), which was letting the real mirror-write run during test suites and pollute the actual file -- fixed with the same structural PYTEST_CURRENT_TEST guard tmux_relay.py already established, not per-test patches. 19 new tests, epistemic PASS. Push-before-notify rule already in CLAUDE.md from earlier today. Next: DIRECTOR_COMMENTS_BOX.md (per-page authenticated feedback channel).
