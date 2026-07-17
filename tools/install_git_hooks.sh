#!/bin/sh
# Install the repo's git hooks so a FRESH CLONE gets them (director P0, 2026-07-17: the pre-commit
# test gate must be reconstruct-from-repo, not a local-only .git/config setting -- structural
# impossibility of a red commit only holds if the gate is actually installed). Idempotent: points
# core.hooksPath at the committed tools/git-hooks/ dir. Run once per clone (or from a bootstrap).
set -e
cd "$(git rev-parse --show-toplevel)"
git config core.hooksPath tools/git-hooks
echo "core.hooksPath = $(git config --get core.hooksPath)  -> pre-commit test-gate ACTIVE"
