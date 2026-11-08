**Severity:** LATENT · **Lane:** E_finance_treasury · **Epoch:** unassigned · **Atom:** `unminted`

# Explore renders a lifetime net figure that the revenue-reconciliation registry does not hold, and the control that says so has been red since 27 Oct

Found by the seat executor on 8 Nov while running the site-wide tests around the Knowledge tab's method-results
page. Observed, with the evidence below; the cause of how long it has been red is inferred from git.

**What is red.** `tests/tools/test_e2_revenue_reconciliation_surfaces.py`, three legs, on origin/main at
a8af509d0:

> an ADVERTISED door renders a net-margin figure and is not in the registry, so an emptied deploy of it would
> pass this control silently: {'explore/index.html'}

**Why.** `site/explore/index.html:539` sums `d.lifetime_net_gbp` into the supplier figure (`supFig.net`). That key
is one of the four `NET_MARGIN_KEY` names the control discovers on. The key arrived with 5977203780 (27 Oct, "The
customer page reconciles with its ledger"). Explore was not added to the expected registry, and it was not given
a clock disclosure the control recognises.

**Why nobody saw it.** The test is not in any commit's impact selection unless the commit touches its inputs. So
it has been red for 12 days without blocking a landing. That is a separate question for the test-selection owner
(a site-wide control whose subject set is every page is selected only by its own file).

**What would close it.** Decide whether Explore's lifetime net is a headline net-margin figure. If it is, add
Explore to the registry and give the figure its R14 clock. If it is incidental arithmetic, the control's key list
should not treat it as a headline. That decision is a finance-lane decision, not a site edit, so it is left open
here.
