# F4_company_internal_authz — FRAME (canonical per-atom, doc-only)

**Atom:** `F4_company_internal_authz` · lane `F_risk_compliance` · epoch **5**
· `level_current: 0` → `level_target: 2` · `loop_stage: idle` · `dial_inherited: 1`
· `depends_on: []`.
**Epoch-5-gated:** DISCOVER/FRAME thought is available now
(EPOCH_GATING_AND_ATOM_AUTHORSHIP); BUILD is not.

**Turn:** H17 Lane-3 FRAME, doc-only / no BUILD code (EPOCH_GATING Rule 1) / no map edit
(F1, level reported via `docs/design/atom_status/F4_company_internal_authz.yaml`).

---

## Why this doc exists (and why it is NOT churn)

F4 carried only **inline DISCOVER-stage prose** in `docs/design/maturity_map.yaml`'s own
`simplifications` list — three real, dated entries (the 2026-07-11 in-console registration,
the 2026-07-12 greenfield confirmation, the 2026-07-13 real-hook finding) — and **no
`*_FRAME.md` on disk**. The intrinsic frame-saturation guard
(`background/supervisor.py::_is_frame_saturated` / `_atom_has_frame_doc`) does not recognise
scattered registration prose in the map as this atom's terminus, so the idle-FRAME draw
correctly kept re-offering F4 as genuinely un-FRAMEd. This doc is that missing terminus. It
**consolidates** (does not re-derive or re-research) the three DISCOVER findings into F4's
own design plus a single stated BUILD-unblock gate. Per MAKE_IT_STICK, saturation is
recomputed from disk on the next cycle — no marker to remember, no re-emission once this
lands. That is the honest end state: F4's FRAME work IS complete once consolidated; the only
remaining path to `level_target: 2` is BUILT, epoch-gated code.

**Honest scope note, stated plainly not buried:** the 2026-07-12 DISCOVER pass grepped
`company/` and `saas/` directly and found **zero** existing maker-checker / RBAC /
segregation-of-duties concept — the blank registration is accurate, genuinely greenfield,
not a mis-registration hiding real code (contrast the W2_3/B4 cases where a blank-looking
registration turned out to hide existing code). The 2026-07-13 pass then found the **one**
real, concrete hook (§4) in code built the same session. That hook is a *future integration
point*, not existing F4 functionality: F4 itself is still L0, correctly.

---

## 1. WHAT F4 is — and the sharp distinction it must hold

F4 is the **simulated company's own internal operational-controls layer** governing WHO (which
internal role/function) may APPROVE WHICH class of financially-effecting decision. It is a
real UK-supplier concern — segregation of duties, maker-checker on payment/refund approvals,
role-based access on customer-account actions (`real_world_twin`, map, verbatim: *"a real
supplier's internal controls — segregation of duties, maker-checker on payment approvals,
RBAC on customer-account actions"*).

**The distinction that is the crux of this atom — get it right or the whole thing is
mis-scoped:** F4 is **NOT** the agent's own harness security profile (Developer / Restricted /
Hardened, `background/secrets_location.py` / `egress_allowlist.py`, the director-console-only
profile-change wall). Those govern what THE BUILDER MACHINE is allowed to do — a Category-8
one-way-door, safety-control concern. F4 governs what a fictional INTERNAL ROLE inside the
SIMULATED COMPANY is allowed to approve during a run. Two entirely different actors:

| | Agent harness security profile | `F4_company_internal_authz` |
|---|---|---|
| **Whose access it controls** | The real builder machine (tool grants, secrets, egress) | A simulated company's internal roles (pricing analyst, credit manager, director) |
| **Change authority** | Director-console-only, Category-8 one-way door (CLAUDE.md, no exceptions) | Ordinary reversible sim design — a DIAL, built when Epoch 5 opens |
| **What it feeds** | The build's own safety posture | The go-live NFR register's **authn/authz** category, at the *company operational-controls* level (see §4a) |
| **Epistemic status** | Real-world security control on the harness | A simulated business capability, measured against a harness gap like any other atom |

F4 belongs entirely to the second column. Conflating the two would either (a) treat a routine
reversible sim-design atom as a Tier-1 safety change (a stall-inducing category error), or
(b) worse, imply the agent's own profile is in scope of an idle-drawable atom (it never is).

---

## 2. The three controls in F4's name, made precise

F4's name enumerates three distinct controls. They are related but not the same; a build that
collapses them loses the point of naming all three.

- **(a) RBAC — role-based access control.** A mapping from internal ROLE → the set of
  decision classes that role is permitted to approve. A pricing analyst may approve a routine
  `PRICING_MOVE`; only a credit manager may approve a `CREDIT_COLLECTIONS_POLICY` change;
  only the director may approve a `CUSTOMER_HARM_REMEDIATION` or a
  `LEGAL_CONTRACTUAL_COMMITMENT`. RBAC answers *"is this resolver even allowed to touch this
  class of decision at all?"*
- **(b) Maker-checker (four-eyes).** The proposer of a financially-effecting action is
  **never its sole approver**. Even where a role is RBAC-permitted to approve a class, the
  *specific individual/process* that MADE the request cannot be the one that CHECKS it.
  Maker-checker answers *"is the approver a DIFFERENT actor from the maker?"* — an
  independence constraint orthogonal to RBAC's role-permission constraint.
- **(c) Segregation of duties (SoD).** A structural constraint across internal FUNCTIONS: the
  function that originates spend cannot also be the function that reconciles it; the function
  that sets collections policy cannot also be the function that books the write-off it
  authorises. SoD answers *"are conflicting duties held by distinct functions?"* — a
  standing organisational-shape constraint, broader than a single decision's maker≠checker.

**The load-bearing object is a decision-class → required-role → maker≠checker table.** These
map 1:1 onto the six classes already in `DECISION_RIGHTS_REGISTER` (§4), so F4's design is a
*translation* of an existing register, not a new taxonomy:

| Decision class (existing register) | Required approving role (RBAC) | Maker ≠ checker? | Segregation-of-duties note |
|---|---|---|---|
| `PRICING_MOVE` | pricing-authority role (analyst for routine; senior for above-threshold) | Yes — the renewal engine that proposes the rate is never the sole approver of it | pricing origination ≠ pricing sign-off above threshold |
| `HEDGE_MANDATE_CHANGE` | risk/treasury role; director for mandate (not per-period op) | Yes | trading desk that runs the hedge ≠ the role that revises its mandate |
| `CREDIT_COLLECTIONS_POLICY` | credit-manager role | Yes — the ledger process booking a write-off ≠ the role approving the policy that permits it | collections operation ≠ write-off policy authority |
| `CUSTOMER_HARM_REMEDIATION` | **director only** (register: *"always human, no sim-policy-agent delegation"*) | Yes — remediation proposer ≠ approver | defect origination ≠ remediation sign-off |
| `LEGAL_CONTRACTUAL_COMMITMENT` | **director only** (same) | Yes | commercial origination ≠ binding-commitment authority |
| `SPEND_ABOVE_THRESHOLD` | budget-holder role; director above a director-set amount | Yes | spend request ≠ spend approval |

The register's own `approver` field already names these approvers as **free-text strings**
(e.g. `"director (real mode) -- always human, no sim-policy-agent delegation for this
class"`). F4's job is to make that named claim **enforceable**, not to invent a parallel
scheme (§4).

---

## 3. What L1 / L2 mean for F4 in `F_risk_compliance` terms

- **L0 (current, confirmed 0):** no RBAC/maker-checker/SoD concept exists in `company/` or
  `saas/` (2026-07-12 grep, zero matches). `resolve_decision_request()` accepts a resolution
  from any caller with no identity/role parameter at all (§4). The register's `approver`
  field is descriptive prose only, unenforced.
- **L1:** F4 exists as real, tested code — a role/permission model plus a maker≠checker check
  — exercised end-to-end by tests against the real `DECISION_RIGHTS_REGISTER`, but not yet
  wired as a mandatory gate in the live resolve path (analogous to A3's own L1: built and
  tested, not yet the enforced live caller).
- **L2 (target):** the check is **live and mandatory** on the real decision path —
  `resolve_decision_request()` (or its successor entry point) rejects a resolution whose
  claimed resolver role is not RBAC-permitted for the class, or whose resolver is the same
  actor that made the request. `actual`-side provenance (`resolved_by`) carries a real,
  non-fabricated identity. The coupled harness gap (§6) can then measure a bypass attempt.
- **L3+ (not this atom's target):** `level_target: 2` is the map's own ceiling for F4; a
  full production RBAC/IAM system (external identity provider, session tokens, audit-grade
  access logging) is explicitly out of scope — the SIMPLICITY GUARD forbids building it now
  (§5).

---

## 4. The real integration point — ONE architecture, not two

The 2026-07-13 DISCOVER pass found the exact, concrete hook, verified again by direct read of
`company/governance/decision_rights.py` this turn:

- `DECISION_RIGHTS_REGISTER` (lines 100–155) already carries a per-class **`approver`**
  free-text field naming who may approve that class.
- `resolve_decision_request(decision_class, entity_id, valid_time, decision, rationale,
  resolved_at, actual_effort_minutes=None, log=None)` (lines 292–348) — the entry point that
  answers a pending request — has **no `resolved_by` / role / identity parameter at all**
  (signature confirmed live). It accepts a resolution from ANY caller and performs zero
  verification that the resolver matches the register's named `approver`. The only guard it
  has is that a *pending* request must already exist (a `ValueError` otherwise) — that is a
  state check, not an authorisation check. The same is true of `log_decision_event()` and
  `record_governance_decision()` (A3's caller): nothing distinguishes "the director resolved
  this" from "any process resolved this" at the schema level. A4's own FRAME (§6, verbatim)
  already flagged this identical carried-forward gap.

**Therefore F4's eventual BUILD is: make the register's existing `approver` field genuinely
ENFORCEABLE at resolve time — a real identity/role check against the register's own claim —
NOT a second, disconnected authz mechanism.** Concretely: `resolve_decision_request()` gains
a `resolved_by` (role/identity) argument; F4's role model checks it against
`DECISION_RIGHTS_REGISTER[decision_class].approver` (which likely evolves from free-text
string to a structured role reference) AND against the maker of the pending request
(maker≠checker, §2b). One architecture: the register already IS the source of truth for "who
may approve what"; F4 turns its descriptive claim into an enforced precondition. This is the
same **"one mechanism, not two"** discipline A3/A4/C-S3 already applied — do not build a
parallel authz store the register would then have to be kept in sync with.

### 4a. Where this feeds the go-live NFR register (honest precision)

`docs/design/H4_GO_LIVE_NFR_REGISTER.md`'s **Security (authn/authz/secrets/pen test)** row is
currently populated with *harness-posture* findings (gitignored secrets, stale dev
file-servers, CORS, `pip-audit`/pen-test gaps) — i.e. the first column of §1's table. F4
populates the **same NFR category** but at the *simulated-company operational-controls* level
(the second column): a real go-live supplier needs BOTH — a secured production surface AND
internal segregation-of-duties/maker-checker on financial approvals. The 2026-07-12 DISCOVER
note read the register's authz gap as "exactly this atom's scope"; the precise truth is that
F4 supplies the *company-internal-controls half* of that authn/authz category, distinct from
(and not duplicative of) the harness-security half already measured there. Named, not
conflated.

---

## 5. Epistemic wall + scale/portability constraints

**Epistemic wall — clean.** F4 operates purely on **company-side decision requests** (the
company's own governed decisions, its own roles, its own register). It reads no SIM-internal
ground truth: no churn parameters, no forward-curve internals, no VaR internals, no per-customer
hidden traits. An authz check on "did the actor with role R submit-then-not-self-approve
decision class C" is entirely inside the company's own governance layer. It must never import
`sim.*` / `simulation.*` internals; the `tools/epistemic_verifier` gate that scans every
`company/governance/**` commit applies to F4's build exactly as to any other. This is honest —
F4 has no motive or path to peek through the wall, because authorisation is a company-internal
fact, not a world fact.

**Scale/portability constraints that DO apply (PRODUCTION_READINESS_SCALE_ADDENDUM.md):**
- **C-S1 event-arrival tolerance / C-S3 async wall contract:** an authz check must be correct
  even though submit and resolve are separate events in time (a request is `submit`ted, then
  `resolve`d later — `decision_rights.py` already splits these). The role/maker check runs at
  resolve time against the maker recorded at submit time; it must not assume both arrive in
  one step.
- **C-S2 idempotency + deterministic replay:** re-processing the same resolution must be
  harmless; the check is a pure function of (register, request's recorded maker, claimed
  resolver) — no hidden state, no RNG, replay-identical. No new RNG substream is needed (authz
  is deterministic, not stochastic).
- **SIMPLICITY GUARD (binding):** satisfy all of the above with the **simplest construct** —
  a role→classes dict and a maker≠checker equality check against the already-recorded request
  maker. **No RBAC-framework cathedral**, no external IAM, no adapters-for-future-adapters.
  The `DecisionEvent` bitemporal log already provides the seam; F4 adds a discipline (a check
  at the resolve boundary), not an architecture.
- **Portability:** the role model should key on FUNCTION, not a hardcoded org chart, so a
  second market/segment fits behind the same seam (PORTABILITY_DESIGN_CONSTRAINTS.md) — a
  design lens for BUILD, not work to do now.

---

## 6. Coupled-triad framing (A6) — the gap is the score

F4 is a **COMPANY-lane control** (`F_risk_compliance`). Per COUPLED_TRIAD_DESIGN.md, a control
is complete only once a world can defeat it and the harness measures the gap:

- **WORLD/SIM add (what can defeat it):** a run in which a decision is resolved by an actor
  that is NOT the register's named approver, or by the very actor that MADE the request
  (a maker self-approving). Today, because `resolve_decision_request()` takes no resolver,
  such a bypass is *structurally invisible* — the SIM can trivially defeat a control that does
  not exist.
- **HARNESS gap (what it is measured against, R15 controls-must-fail):** a **mutation test**
  that injects exactly that bypass — a maker self-approving a `PRICING_MOVE`, or a
  pricing-analyst role resolving a `CUSTOMER_HARM_REMEDIATION` the register reserves to the
  director — and asserts F4's check **FIRES**. A maker-checker/RBAC control that CANNOT be
  shown to reject its own named defect is worse than none (CLAUDE.md R15: TAUTOLOGY /
  FAIL-OPEN / FAIL-SILENT). The specific FAIL-OPEN risk to guard: passing when `resolved_by`
  is missing/`None` — an absent resolver must be a REJECT, never a silent allow. That
  mutation is the concrete named defect F4's harness leg must fire on before any promotion.
- **The gap reported per digest** is: can any resolution reach the log without a
  register-consistent, maker-distinct approver? At L0 the answer is "yes, trivially" — that IS
  the current measured gap, and closing it to "no, and a mutation test proves the check fires"
  is F4's L2.

---

## 7. The single BUILD-unblock gate (epoch-sequencing intelligence — HELD at L0)

| Atom | Epoch | Level (held) | Single BUILD-unblock gate | Gate class |
|------|-------|--------------|---------------------------|------------|
| `F4_company_internal_authz` | 5 | **0 (→2)** | **Epoch-5 BUILD-open** (TWIN, standing approver for BUILD-within-the-open-epoch per EPOCH_GATING_AND_ATOM_AUTHORSHIP §3a) — the SOLE remaining condition. `depends_on: []` — verified live against `maturity_map.yaml`, there is **no unmet prerequisite**: the real integration target (`decision_rights.py`'s register + `resolve_decision_request()`) already exists and is live (built for A2/A3). Once Epoch-5 opens, BUILD (a) adds a `resolved_by` role/identity parameter to the resolve entry point, (b) makes `DECISION_RIGHTS_REGISTER.approver` structured + enforceable, (c) implements the role→classes RBAC map, the maker≠checker independence check, and the SoD constraint (§2 table), and (d) adds the R15 mutation test proving the check fires on a maker self-approving / wrong-role bypass (§6). | DIAL (epoch sequencing only — empty `depends_on`, no unmet dependency) |

**Pre-BUILD action items (named, not done here — out of this Lane-3 doc-only scope):**
- Extend `resolve_decision_request()` / `record_governance_decision()` with a `resolved_by`
  role/identity argument (§4) — the one schema change that unblocks enforcement; A4's FRAME
  already anticipated stamping this same `resolved_by` field.
- Evolve `DECISION_RIGHTS_REGISTER.approver` from free-text to a structured role reference the
  RBAC map can check against, **preserving** the director-owned "curriculum, not agent-tuned"
  discipline on the register's contents (the *values* stay the director's; F4 only makes the
  *shape* enforceable).
- Author the R15 mutation test as part of BUILD, not after — no promotion without it.

**Disposition:** level **HELD at 0** (idle atom; FRAME complete ≠ built; epoch-gated per
EPOCH_GATING Rule 1; `level_target: 2` reachable only via BUILD). This FRAME is F4's canonical
terminus; the next idle draw reads F4 as frame-saturated and yields to genuinely-un-FRAMEd
work instead. No BUILD code, no map edit (F1).

---

*Sources consolidated (not re-derived): `docs/design/maturity_map.yaml` (`F4_company_internal_authz`'s
own three dated `simplifications`: 2026-07-11 registration, 2026-07-12 greenfield grep, 2026-07-13
real-hook finding, and its `real_world_twin`), `company/governance/decision_rights.py`
(`DECISION_RIGHTS_REGISTER`'s `approver` field + `resolve_decision_request()`'s real signature —
confirmed to have no `resolved_by`/role parameter, this turn), `docs/design/H4_GO_LIVE_NFR_REGISTER.md`
(the authn/authz go-live NFR category F4 feeds, §4a), `docs/design/frame/A4_sim_approver_FRAME.md` §6
(the identical carried-forward maker-checker gap A4 already named), COUPLED_TRIAD_DESIGN.md (gap-as-score,
§6) and CLAUDE.md R15 (controls-must-fail mutation-test discipline), PRODUCTION_READINESS_SCALE_ADDENDUM.md
(C-S1/2/3 + SIMPLICITY GUARD). No BUILD code, no external research re-run; the register's contents remain
director-owned throughout.*
