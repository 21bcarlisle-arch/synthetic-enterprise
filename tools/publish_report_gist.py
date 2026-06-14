#!/usr/bin/env python3
"""Publish docs/reports/ANNUAL_REPORT.md so Rich's strategy advisor
(claude.ai) can fetch it directly, with no copy-paste from Rich.

claude.ai's sandbox cannot fetch raw.githubusercontent.com or Tailscale
URLs, and Gists aren't indexed by search engines. GitHub Pages URLs are
normal public web pages and already work for this repo (the status page at
docs/status/ is served the same way) -- Pages is configured to serve from
the `main` branch's `/docs` directory and rebuilds automatically on every
push.

So the fix is: commit and push docs/reports/ANNUAL_REPORT.md (and the JSON
cache) to `main` whenever they change, which makes the regenerated report
available within a couple of minutes at:

    https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md

A Gist is also kept up to date as a secondary access path.

Prints the Pages URL (primary) and Gist URL (secondary) on stdout.

Delegation note: hand-written (orchestration-adjacent -- shells out to `git`
and `gh`, per protocol).
"""

import subprocess

from saas.reporting.annual_report import DEFAULT_REPORT_DATA_PATH, DEFAULT_REPORT_PATH

GIST_DESCRIPTION = "Synthetic Enterprise Annual Report — latest"
PAGES_REPORT_URL = "https://21bcarlisle-arch.github.io/synthetic-enterprise/reports/ANNUAL_REPORT.md"

REPORT_PATHS = [str(DEFAULT_REPORT_PATH), str(DEFAULT_REPORT_DATA_PATH)]


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


def publish_gist() -> str:
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


def publish_pages() -> str:
    """Commit and push the report files to `main` so GitHub Pages picks up
    the regenerated report, then return its Pages URL.

    No-op (no commit) if the report files are unchanged.
    """
    status = subprocess.run(
        ["git", "status", "--porcelain", *REPORT_PATHS],
        capture_output=True, text=True, check=True,
    ).stdout.strip()

    if status:
        subprocess.run(["git", "add", *REPORT_PATHS], check=True)
        subprocess.run(
            ["git", "commit", "-m", "Update published annual report (make publish-report)"],
            check=True,
        )
        subprocess.run(["git", "push"], check=True)

    return PAGES_REPORT_URL


def main() -> None:
    pages_url = publish_pages()
    gist_url = publish_gist()
    print(f"Pages (primary): {pages_url}")
    print(f"Gist (secondary): {gist_url}")


if __name__ == "__main__":
    main()
