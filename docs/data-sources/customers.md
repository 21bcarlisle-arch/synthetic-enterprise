# Customer Cohort in `saas/customers.py`

This document outlines the four customer profiles defined in `saas/customers.py`, which were introduced in Phase 0b/0c. These profiles provide full identities for each customer, including their geographical location and home characteristics, serving as a single source of truth for subsequent phases such as pricing, hedging, and weather correlation.

## Customer Profiles

| Customer ID | Acquisition Date | Location (City, Lat/Lon)         | Home Type       | Bed Count | EPC Rating | EAC (kWh) |
|-------------|------------------|---------------------------------|-----------------|-----------|------------|-----------|
| C1          | 2016-01-01       | London (51.5074, -0.1278)     | Urban Flat      | 2         | D          | 2,800     |
| C2          | 2016-04-01       | Manchester (53.4808, -2.2426) | Suburban Semi    | 3         | D          | 3,500     |
| C3          | 2016-07-01       | Glasgow (55.8642, -4.2518)   | Tenement Flat   | 2         | E          | 3,200     |
| C4          | 2016-10-01       | Cotswolds (51.8330, -1.8433)  | Rural Detached  | 4         | E          | 5,500     |

## Why This Spread Was Chosen

The deliberate diversity across the UK geography (south/north-west/Scotland/rural-south-west), home archetypes (flat/semi/tenement/detached), and EAC range (2,800-5,500 kWh) ensures that later analyses, such as weather correlation in Phase 1b, have genuine variation to work with. The EPC ratings (D, D, E, E) and bedroom counts loosely track home size/type, making these profiles plausible synthetic identities for testing purposes.

## Schema Fields and Their Purpose

- **`commodity`**: Currently always "electricity". This field exists to leave the door open for gas dual-fuel support in the future (Master Backlog Phase 2b) without requiring a schema migration.
  
- **`segment`**: Currently always "resi". This field is included to accommodate SME (Master Backlog Phase 2a) and later I&C segments in the future.

- **`contract_type`**: Currently always "fixed_1yr". This field is designed to accommodate other contract shapes, such as variable contracts or renewal terms, in future phases.

- **`eac_kwh`**: Nullable for potential future smart-meter cohorts where consumption would be measured rather than estimated. No null-handling code exists yet because this scenario cannot occur with the current synthetic cohort; this is a forward-compatibility note.

- **`location`**: Stored as both latitude/longitude (for weather-API lookups in Phase 1b) and a human-readable region (for reporting). This redundancy ensures that neither later use case has to derive the other.

## Implementation

The customer profiles are implemented in `saas/customers.py`. The key functions and classes include:

- **`CUSTOMERS`**: A list of the four customer-profile dicts, in cohort order.
- **`get_customer(customer_id)`**: Retrieves a specific customer profile by ID.
- **`get_customers_for_segment(segment)`**: Returns a list of customers belonging to a specified segment.
- **`customer_to_settlement_input(customer)`**: Converts a customer profile into the format required for settlement inputs.