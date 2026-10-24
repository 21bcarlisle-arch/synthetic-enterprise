# saas/

The first business layer (July 2026): part of the SUPPLIER, beside `company/`,
which came later and holds most of it. Customer value, CLV/CAC, churn belief,
cost to serve, reporting. Whatever is here is the supplier's belief and may be
wrong; how households actually behave is the world's (`simulation/`).

*Corrected 2026-10-24: this used to list "the customer reaction function that
models non-rational responses to bills" as the business layer's. A household's
reaction is a fact about the world, and the world still reading `churn_model`
and `home_move_win_rate` from here is the B2 debt in
`docs/design/WALL_CROSSING_DISPOSITION_REGISTER.md`. The seam is now
`company/interfaces/`, not only `interface/`.*

## The seam rule

`saas/` never imports from `sim/`, and never reaches into `sim/` internals.
Everything it knows about the market — prices, forecasts, forward curves —
arrives exclusively through [`interface/`](../interface/). This is the
architectural enforcement of the Point-in-Time Blindfold: the business layer
can only ever see what the interface chooses to expose, never the future and
never the simulation's internal state.
