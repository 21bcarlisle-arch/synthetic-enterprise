# saas/

The business layer. The simulated energy supplier itself: billing, tariffs,
CLV/CAC, churn, hedge effectiveness, and the customer reaction function that
models non-rational responses to (arithmetically correct) bills.

## The seam rule

`saas/` never imports from `sim/`, and never reaches into `sim/` internals.
Everything it knows about the market — prices, forecasts, forward curves —
arrives exclusively through [`interface/`](../interface/). This is the
architectural enforcement of the Point-in-Time Blindfold: the business layer
can only ever see what the interface chooses to expose, never the future and
never the simulation's internal state.
