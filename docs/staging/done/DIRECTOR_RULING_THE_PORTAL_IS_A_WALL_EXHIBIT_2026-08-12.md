# DIRECTOR RULING — the household page is a wall exhibit, and its bill drops the line that explains itself

Staged 2026-08-12 by the advisor. Director ruling given in session on both parts.
Both parts land in the same file (`site/customers/index.html`), which is why they are one
document: Part 2's redesign must not undo Part 1's fix.

**Place in the epoch arc.** Part 1 is Epoch 1 (core fidelity — UK-compliant billing), at the
rendered value rather than the ledger. Part 2 serves Epoch 3 (walled interfaces): it does not
build wall, it makes an existing separation legible on a public surface. Neither part is Epoch 2
work and neither should be sequenced ahead of the no-caller class fix.

---

## Part 1 — The printed bill does not foot on its face

**Proportionality: reversible / narrow.** One file, presentation only, no ledger change.

### The problem

Bill `C1g-INV141` (gas, Sep 2021) renders as four charge lines totalling about £26, and a total
of minus £2. Nothing on the page explains the sign. The account holder cannot reconcile it, and
neither could the director looking at it.

The record is correct. It carries `catchup_adjustment_gbp = -28.40` — an August overcharge
corrected on the September bill — and `total_amount_gbp = -2.43` foots to the penny across five
components. `BILL_FOOTS` in `company/compliance/domain_invariants.py` already defines that
five-component set, already includes the catch-up term, and already passes on this record.

The gap is that the invariant guards the ledger record and nothing guards the rendered page.
Two defects, both on the print path only:

1. **The fifth component is never printed.** Both `billEquationHtml()` (on-screen) and
   `downloadBillPdf()` (the PDF) enumerate four line items and stop. The adjustment that decides
   the sign of the total is invisible in both.
2. **Every money figure on that path is rounded to whole pounds.** The file defines two different
   functions both named `gbp`; the bill path resolves to the zero-decimal one built for portfolio
   totals. £11.86 prints as £12, £1.24 as £1, minus £2.43 as minus £2. A domestic energy bill
   showing whole pounds would not survive scrutiny, independent of defect 1.

Population size: the `BILL_FOOTS` rebuild note records 147 catch-up bills in the run population.
That is a figure quoted from a docstring, not one I measured — worth confirming against the
current run before sizing the fix.

### Requirements

- A catch-up adjustment appears as its own labelled line wherever a bill's arithmetic is shown —
  on-screen and in the PDF — with the correcting period named, since the record already carries
  `catchup_period_start` / `catchup_period_end`.
- The lines shown sum to the total shown, to the penny, on the face of the bill.
- Money on the bill path renders in pounds and pence.
- The customer-facing wording explains a back-billing correction in plain terms. What is written
  is a domain question; if the phrasing is uncertain, ask rather than guess.

### Non-negotiables

- **Carry the value through; do not derive it.** `generate_invoice_data.py` already records that
  re-deriving a printed figure in the render layer was the defect that made 86.1% of invoices fail
  their own multiplication. Do not repeat it here.
- **Reuse the footing component set, do not restate it.** `BILL_FOOTS` owns what must sum to the
  total. A second list of components in the renderer is a divergence waiting to happen.
- No ledger, generator or invariant change. The data is right.
- The rendered page, not the record, is what must be shown to have changed.

### Risk

Touches one live public file on the display path. Blast radius is the household bill view and the
downloadable PDF. Probable failure mode: the fix lands as a fifth `if` in each of two renderers,
and the next component added to a bill is missed in both again — the same class, one instance
later. Mitigation worth considering inline: the two renderers agreeing by construction rather than
by inspection, and a check that fails when a rendered bill's shown lines do not sum to its shown
total.

---

## Part 2 — Rename the page and make the wall the exhibit

**Proportionality: contract-touching.** Public URL, site door mapping, the wall's public account
of itself.

### The problem

`site/customers/index.html` is titled "Customer Portal" and invites a visitor to "log in with your
Poesys account number to view your household". What it then shows is three layers at once:

- **Customer-observable:** bills, usage, payments, meter details.
- **Company-only:** lifetime revenue and net, cost to serve, churn probability, customer lifetime
  value, pricing action, forecast profit.
- **SIM-only:** a satisfaction score, the causal reaction chain, and wholesale trading margin —
  the last already carrying an on-page note calling it "SIM-internal".

No supplier shows a customer their own churn probability. Nothing outside the simulation can see a
satisfaction score at all. The page is already honest in places — there is a labelled honesty wall
and the trading-margin note — but honest labelling inside a page that calls itself the customer's
own view still misrepresents the thing the project exists to demonstrate. A separate, genuinely
customer-facing portal already exists at `company/portal/`, which is what makes the name a
collision as well as a claim.

`SITE_CONSTITUTION.md` already places household drill-down under **The Company** door, absorbed
as-is. So the page is arguably already re-homed on paper and only the name and framing lag.

### Director ruling

Keep all three layers. **Rename and re-home the page as a deliberate side-by-side comparison of
the two sides of the epistemic wall.** The layering becomes the exhibit rather than a leak to be
apologised for.

### Requirements

- Every figure on the page is attributed to a side: what the customer can see, what the company
  knows, what only the simulation knows.
- A visitor can see the customer-eye view as its own coherent thing — exactly what a real account
  holder would see and nothing more — not merely a subset they must assemble by reading labels.
- The page states plainly why the two sides differ, and that the difference is the point.
- Name, title, entry copy and URL stop claiming to be a customer's portal. Old URL redirects.
- The relationship to the real portal at `company/portal/` is stated, not left to be inferred.

### Non-negotiables

- **No SIM-only figure may be presented as something the company knows.** That is the wall itself,
  and the page is now its shop window.
- **No company-only figure may be presented as something the customer sees.**
- **The side-declaration must be structural, not prose.** A control that cannot fail is not a
  control. If a new panel can be added to this page without declaring which side of the wall it
  sits on, nothing has been built — only written down. The existing honesty-wall notes are prose
  and this is exactly the gap they leave.
- No new data plumbing. Everything named above is already in the per-customer JSON.
- Do not weaken or remove the honesty notes already on the page; absorb them.
- Part 1 lands intact through this work.

### Risk

Touches a live public page, its URL, inbound links and the sitemap, and takes a position in the
site's own account of the wall. Blast radius is one door plus anything linking to it.

Two probable failure modes. First, a rename without redirects, and the door 404s — the site
constitution's own pixel/redirect rule covers this and should be followed rather than
re-litigated. Second and more likely: the attribution ships as a paragraph at the top of the page
while the panels below stay unmarked, which reads as done and enforces nothing. The second is the
one to design against.

---

## What is decided and what is open

**Decided (director, this session):** keep all three layers; rename and re-home as a two-sided
wall comparison; the bill must show its catch-up line and print in pence.

**Open to the builder:** the page's new name and URL; how the two sides are laid out; the
mechanism that makes a panel declare its side; the customer-facing wording for a back-billing
correction; whether Part 1 ships ahead of Part 2 or inside it.

---

**[PROCESSED 2026-08-12, worker tick]** This ruling carries no formal `WORK THIS CREATES` block
(§4 of `DIRECTOR_RULING_WORK_DEFINITION_AND_COHERENCE_2026-07-27`) — flagged as a defect, not
silently absorbed: `docs/staging/PLANNER_MINTED_portal_wall_exhibit_2026-08-12.md` requests the
block from the author. Both Parts minted as atoms from the ruling's own Requirements/
Non-negotiables sections: Part 1 → `D36_bill_render_footing_and_pence` (lane D_billing_metering,
level 0→2); Part 2 → `SITE2_two_sided_wall_exhibit` (lane H_harness, level 0→3, since a public wall
exhibit's trustworthiness is an Expert-Hour-verdict claim, not a mechanically-real one). Neither
Part is built yet — minting registers the work in `docs/design/maturity_map.yaml` so it can be
drawn and built as its own atom; see the PLANNER_MINTED doc for the full disposition.
