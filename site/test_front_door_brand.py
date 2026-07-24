"""RC-row regression guards for the Front door (SITE_V5 surface 1, iteration 2).

The director's axis-1 verdict scored the front-door MVP FAIL ("It still looks awful").
Iteration 2 rebuilds it to the BRAND_CONSTITUTION architectural exemplar. These tests
guard the specific rubric-row fixes so a later edit can't silently regress them --
each asserts a named RC row from DIRECTOR_AXIS1_SITE_VERDICT_ROWSCORED_2026-07-23.md.

Brand-token/hex compliance for the <style> block is enforced separately by
tests/tools/test_brand_compliance.py (this surface is in the adoption frontier).
"""
import re
from pathlib import Path

INDEX = Path(__file__).resolve().parent / "index.html"


def _text() -> str:
    return INDEX.read_text()


def _style_block(text: str) -> str:
    m = re.search(r"<style>(.*?)</style>", text, re.S)
    assert m, "no <style> block"
    return m.group(1)


def _script_block(text: str) -> str:
    # The page's own inline script (the CDN + any src= tags are skipped by the bare
    # <script> match, same convention as the render harness). Since
    # DIRECTOR_RULING_FRONT_MISSION_BLOCK (2026-07-24) the front door renders no live
    # figure and carries no inline script -- the "no bad string in the script" guards
    # below then hold vacuously (there is no script to smuggle a regression into),
    # which is the correct post-condition, so an absent block returns "".
    m = re.search(r"<script>(.*?)</script>", text, re.S)
    return m.group(1) if m else ""


# ---- RC4: type-only BLACK wordmark (not the legacy teal logo) -----------------------------
def test_wordmark_is_the_black_poesys_type_only_mark():
    text = _text()
    assert 'class="nav-logo wordmark">poesys.</a>' in text, "type-only poesys. wordmark missing"
    style = _style_block(text)
    # The wordmark must resolve to structural ink, never a decorative accent colour.
    m = re.search(r"\.nav-logo\s*\{[^}]*\}", style)
    assert m, ".nav-logo rule not found"
    assert "var(--text)" in m.group(0), ".nav-logo must be structural ink"
    assert "var(--teal)" not in m.group(0), "wordmark still uses the legacy teal accent (RC4)"


# ---- RC4: colour is information, never decoration -- no decorative colour top-borders ------
def test_no_decorative_coloured_card_top_borders():
    style = _style_block(_text())
    # The prior build lifted rounded cards with a decorative `border-top: 3px solid var(--blue)`
    # -- colour with no status meaning. It must be gone.
    assert "border-top: 3px solid var(--blue)" not in style
    assert "border-top-color: var(--amber)" not in style


# ---- RC4: the chat/comments widget is removed from the marketing front door ---------------
def test_no_chat_widget_on_the_front_door():
    text = _text()
    assert "director-comments.js" not in text, "chat widget must be removed from the front door (RC4)"


# ---- RC4: no leading tilde on any board numeral (the number and its clock, chip carries status)
def test_no_leading_tilde_on_board_figures():
    script = _script_block(_text())
    # The numerals are produced by gbp(); a leading tilde would appear as '"~"+' concatenation
    # or a literal '~£' / '~"+gbp'. None of those may exist -- provisional status rides the chip.
    assert '"~£' not in script and "'~£" not in script, "tilde prefixed to a currency numeral (RC4)"
    assert '"~"+gbp' not in script and "'~'+gbp" not in script, "tilde prefixed to gbp() output (RC4)"


# ---- RC4: the front door carries no raw hex anywhere (BRAG via token source only) ---------
def test_front_door_has_no_offbrand_hex():
    # The cost-to-serve chart (which the prior thesis-chart guard covered) moved to
    # /proof under DIRECTOR_RULING_FRONT_MISSION_BLOCK; its no-hex guard lives there now
    # (site/proof/test_proof_door.py). This asserts the front door as a whole -- style +
    # any residual script -- smuggles no off-brand raw hex.
    text = _text()
    for bad in ("#1baf7a", "#4a3aa7", "#52514e", "#e1e0d9", "#0b0b0b"):
        assert bad not in _script_block(text), f"off-brand raw hex {bad} on the front door (RC4)"


# ---- RC5/RC7: no effort metric AND no cohort-derived financial leads the surface ----------
def test_no_effort_metrics_on_the_surface():
    text = _text().lower()
    for effort in ("tests passing", "tests collected", "test executions", "commits/day", "phases complete"):
        assert effort not in text, f"effort metric {effort!r} on the front door (RC5)"
    # RC7 (DIRECTOR_RULING_IDEA_FIRST_EXTERNAL_REGISTER 2026-07-24) SUPERSEDES the RC5
    # "outcome figures lead" rule for CURRICULUM-COHORT financials: £-figures earned across
    # the small teaching cohort (net margin / treasury / enterprise value / bills) fail the
    # veteran sniff test and may not lead a public surface. The front now leads with the idea
    # (hero + thesis) and the honest build state (the diagram); these cohort financials are
    # rendered only inside /proof, framed as teaching-cohort output.
    script = _script_block(_text())
    for cohort_fin in ("net_margin_gbp", "treasury_end_gbp", "enterprise_value_gbp", "bills_total"):
        assert cohort_fin not in script, f"cohort financial {cohort_fin} leads the front door (RC7)"
