#!/usr/bin/env python3
"""Publish docs/reports/ANNUAL_REPORT.md as a public GitHub Gist.

Phase 5b deliverable 5: Rich's strategy advisor cannot fetch
raw.githubusercontent.com or Tailscale URLs -- only publicly indexed pages.
Publishing the report as a Gist with a fixed, searchable description lets
the advisor find and fetch it directly without copy-paste.

Finds an existing gist with description `GIST_DESCRIPTION` and updates its
file from `docs/reports/ANNUAL_REPORT.md`, or creates a new public gist if
none exists. Prints the gist's HTML URL on stdout.

Delegation note: hand-written (orchestration-adjacent -- shells out to `gh`,
per protocol).
"""

import subprocess

from saas.reporting.annual_report import DEFAULT_REPORT_PATH

GIST_DESCRIPTION = "Synthetic Enterprise Annual Report — latest"


def _find_existing_gist_id() -> str | None:
    result = subprocess.run(
        ["gh", "api", "gists", "--jq",
         f'[.[] | select(.description == "{GIST_DESCRIPTION}")] | .[0].id // ""'],
        capture_output=True, text=True, check=True,
    )
    gist_id = result.stdout.strip()
    return gist_id or None


def _gist_url(gist_id: str) -> str:
    result = subprocess.run(
        ["gh", "api", f"gists/{gist_id}", "--jq", ".html_url"],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip()


def publish() -> str:
    """Create or update the Gist and return its HTML URL."""
    report_path = str(DEFAULT_REPORT_PATH)
    gist_id = _find_existing_gist_id()

    if gist_id:
        subprocess.run(["gh", "gist", "edit", gist_id, report_path], check=True)
        return _gist_url(gist_id)

    result = subprocess.run(
        ["gh", "gist", "create", "--public", "--desc", GIST_DESCRIPTION, report_path],
        capture_output=True, text=True, check=True,
    )
    return result.stdout.strip().splitlines()[-1]


def main() -> None:
    url = publish()
    print(url)


if __name__ == "__main__":
    main()
