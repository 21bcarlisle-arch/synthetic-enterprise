# Competitor Platforms 2026 — Global Energy Retail Architecture Survey

**Provenance:** Supplied by the director 2026-07-08. Unsourced, AI-assisted
compilation. ALL quantitative claims herein are UNVERIFIED (register in
ASSUMPTIONS.md). Use as a structural reference for what functions real
platforms perform, not as a source of figures. Document was truncated at
section 7 (SAP+Salesforce heading only) as supplied.
**Companion instruction:** docs/staging/COMPETITOR_LANDSCAPE_GAP_CHECK.md

---

# Global Energy Retail Architecture & Platforms (Comprehensive 2026 Assessment)

This document provides an exhaustive, technical, and strategic compilation of the primary software architectures driving the global energy and utility transition. It is structured to serve as an initialization context or baseline reference for AI-driven system assessments, architectural evaluations, and transformation planning.

---

## 1. MaxBill: The Multi-Play Unifier

MaxBill operates as a heavy-duty, meter-to-cash engine engineered for complex, high-volume service providers. It is structurally designed to handle multi-play service bundling across distinct industry verticals (Energy, Telco, Water, EV charging).

### Core Architecture & Technical Stack
*   **Infrastructure:** Cloud-first, multi-tenant SaaS architecture.
*   **Backend & Concurrency:** Java (Spring, Java EE) leveraging the **Akka framework**. By utilizing the Actor model, Akka allows the system to handle asynchronous, distributed event processing. This enables the ingestion of millions of smart meter IoT pings simultaneously without causing transactional deadlocks.
*   **Polyglot Persistence Data Strategy:**
    *   *Relational Foundations:* Oracle DB and PostgreSQL maintain strict ACID compliance for financial ledgers, transactional billing states, and customer contracts.
    *   *NoSQL Foundations:* Cassandra and MongoDB ingest high-velocity, unstructured time-series data (raw meter consumption logs) where write-speed is critical.
*   **Event Messaging:** Decoupled modules integrated via Apache Kafka.

### The 8-Module Framework
1.  **Product Catalog & Rating Engine:** Supports complex contingency billing, dynamic tariffs, multi-period recurring subscriptions, and cross-vertical multi-play bundles without custom hardcoding.
2.  **Ordering & BPMN Engine:** Utilizes **Camunda BPM** encapsulated within a microservices chassis to manage service activation, provider switching, and automated tenancy changes.
3.  **Partner Relationship Management (PRM):** Automates revenue sharing, wholesale billing, and multi-tiered commission calculations algorithmically for multi-party business models (B2B2C, broker networks, EV Charge Point Operators).
4.  **CRM & Customer Management:** Manages complex service packages linking properties, resources, and specific meter endpoints to individual customer accounts.
5.  **Meter Reading & Forecasting:** Ingests and validates raw reads from standard and smart IoT meters, estimates missing intervals, and applies AI models to forecast network demand.
6.  **Billing & Invoicing Engine:** Processes usage data against complex tariffs. Decoupled from data ingestion to handle out-of-sequence, bulk, and deferred invoicing without system degradation. Supports automatic retroactive recalculations.
7.  **Revenue & Debt Management:** Focuses on cash-flow optimization by automating dunning processes, calculating algorithmic payment plans, and applying late-fee penalties.
8.  **Self-Care Portal:** A white-labeled React JS web interface enabling consumers to view usage charts, download invoices, and interact with a conversational AI assistant.

### UI/UX Assessment
*   **Agent/Administrative UI:** Prioritizes data density and operational utility over minimalist aesthetics. It relies on a deeply nested, tabular structure and left-hand tree navigation (Property -> Package -> Resource -> Service) designed for power users. Features a "Screen Builder" application leveraging the Form IO library to allow analysts to map drag-and-drop components directly to backend APIs.
*   **Consumer UI:** Simplified, card-based responsive design. Focuses heavily on support ticket deflection by pairing high-visibility consumption charts with an embedded conversational AI assistant.

### Strategic Positioning & Market Footprint
*   **Strengths:** Native handling of cross-industry multi-play bundles on a unified ledger. Strong automated settlement via the PRM engine.
*   **Weaknesses:** The sheer flexibility of the commercial rules engine requires steep initial configuration. Relational data models demand clean, highly standardized data during migration.
*   **Target Segments:** Dominant in Residential and SME multi-play. Highly functional for EV Charge Point Operator (CPO) billing.
*   **Geographies:** Heavily concentrated in Europe (UK, Netherlands, Czechia, Denmark, Baltics, Balkans).

---

## 2. Gorilla: The B2B Margin Intelligence Engine

Gorilla is not a BSS or a transactional ledger. It is a specialized Data Cloud and Calculation Engine focused strictly on the meter-to-margin lifecycle. It replaces the fragile, siloed Excel spreadsheets traditionally used to price bespoke Commercial & Industrial (C&I) and B2B energy contracts.

### Core Architecture & Technical Stack
*   **Infrastructure:** Cloud-native SaaS running on Amazon Web Services (AWS), utilizing an elastic microservices architecture to decouple heavy data calculations from front-end interfaces.
*   **Computational Engine:** Python, Pandas, NumPy, and SciPy.
*   **High-Velocity Data Processing:** Polars, DuckDB, Dask, and PySpark to parallel-process millions of half-hourly meter intervals against highly volatile wholesale market datasets.
*   **Integration:** RESTful APIs, Mulesoft, and bulk data deduplication directly into Amazon S3 data lakes.

### Core Functional Modules
1.  **The Energy Data Cloud:** A unified governance layer aggregating internal data (CRM, historical billing) with external data (wholesale market curves, weather forecasts, broker portals) into an auditable environment.
2.  **Algorithmic Pricing Engine:** Replaces black-box Excel tools. Allows commercial teams to configure and version-control bespoke pricing logic for multi-site C&I deals, factoring in wholesale costs, network charges, green levies, and broker commissions simultaneously. Compresses quote-to-market times to sub-minute runs.
3.  **Forecasting Engine:** Translates raw historical meter reads into actionable forward-looking profiles, dictating the volumes trading teams must hedge on the wholesale market.
4.  **Portfolio & Margin Intelligence:** Continuously runs automated "portfolio recosting." If an industrial client changes their operating hours, Gorilla instantly recalculates the contract's margin profitability, exposing margin leakage before the billing cycle completes.

### UI/UX Assessment
*   **Interface Philosophy:** Built for Pricing Analysts and Commercial Directors, not call-center agents. It provides a visual interface to construct and tweak complex pricing formulas, democratizing data science without requiring analysts to write Python code.
*   **Auditability:** Features strict version-control interfaces that display the exact version of the pricing model and market curve used to generate any historic quote, ensuring complete auditing compliance.

### Strategic Positioning & Market Footprint
*   **Strengths:** Eradication of "spreadsheet risk." Massive speed-to-quote acceleration providing a first-mover advantage. Real-time margin visibility.
*   **Weaknesses:** Absolute dependence on the utility's underlying CRM and BSS data quality. It is a "brain without a body" -- dirty contract data in the source system results in fast, inaccurate calculations.
*   **Target Segments:** Dominant in Enterprise and I&C. Highly effective for automated SME matrix pricing.
*   **Geographies:** UK, USA, Australia, and Western Europe (Germany, Belgium).

---

## 3. Gentrack (g2): The Composable Backbone

Gentrack represents the "Headless/Composable" ecosystem paradigm. Its modern g2 platform completely abandoned monolithic legacy tech to operate as a serverless, API-first billing core designed to sit underneath best-of-breed front-ends like Salesforce Energy & Utilities Cloud.

### Core Architecture & Technical Stack
*   **Infrastructure:** 100% AWS-native, serverless, event-driven distributed architecture.
*   **Compute:** AWS Lambda and AWS Fargate allow compute resources to scale horizontally and automatically from zero to millions of concurrent processes during peak batch billing runs.
*   **Messaging & Event Bus:** Amazon EventBridge, SQS, and SNS form the decoupled asynchronous backbone.
*   **Persistence:** Amazon Aurora for ACID-compliant financial ledgers and master data; Amazon S3, DynamoDB, and AWS Glue for high-velocity IoT meter data lakes and ETL processing.
*   **Integration Layer:** AWS API Gateway and MuleSoft expose all billing and meter operations as RESTful APIs.

### Core Functional Engine
1.  **Meter-to-Cash & Billing Engine (CIS):** Built to handle high-frequency data, natively supporting Market-Wide Half-Hourly Settlement (MHHS), time-of-use (ToU) tariffs, and distributed energy export credits.
2.  **Market Interaction Layer:** Automates industry data flows and regulatory messaging required by national grid operators (e.g., DCC in the UK) to govern customer switching and meter orchestration.
3.  **Forecasting & Margin Intelligence (via Factor):** Integrated via the acquisition of the Factor engine. Competes directly with Gorilla by embedding load forecasting, risk modeling, and margin analytics directly into the BSS ledger.
4.  **Agentic AI & Automation Layer:** Deploys 17+ autonomous AI agents in live production environments to handle complex billing exception processing without human agent intervention. [UNVERIFIED]

### UI/UX Assessment
*   **Interface Philosophy:** Employs a strictly "Headless" strategy. Front-line agents rarely log into a Gentrack UI. Instead, Gentrack utilizes APIs to instantly surface billing data, consumption graphs, and next-best-action alerts directly onto a Salesforce Lightning console.
*   **Administrative UI:** Provides an AWS-hosted management console for back-office analysts and sysadmins, prioritizing data observability and workflow orchestration over consumer aesthetics.

### Strategic Positioning & Market Footprint
*   **Strengths:** Infinite cloud-native scaling without database deadlocks. Eliminates vendor lock-in, allowing utilities to swap or modify front-end layers without altering the billing core.
*   **Weaknesses:** The "API Glue" burden. The utility assumes the risk and cost of maintaining complex middleware orchestration between Salesforce, Gentrack, and external portals. Slower initial time-to-market compared to "opinionated" systems.
*   **Target Segments:** Dominant in Tier-1/Tier-2 Residential and I&C portfolios.
*   **Geographies:** United Kingdom (dominant), Australia, New Zealand, Singapore, and India.

---

## 4. Kraken: The Universal Monolith

Kraken (Kraken Technologies) explicitly rejects the composable, best-of-breed ecosystem. It operates as a highly unified, fiercely opinionated macro-service monolith. It houses CRM, billing, and DERMS within a single codebase to structurally eliminate API middleware latency and data-synchronization failures.

### Core Architecture & Technical Stack
*   **Infrastructure:** Large-scale macro-service monolith deployed on AWS utilizing Kubernetes for container orchestration.
*   **Backend & Logic:** Python (Django) forms the entire application layer, allowing rapid feature deployment and direct data access across workflows.
*   **Persistence & Querying:** PostgreSQL handles the relational transactional ledger, while GraphQL serves as the data delivery layer to the front end.
*   **Flex Orchestration:** KrakenFlex operates as an integrated micro-stack, utilizing deep reinforcement learning to optimize battery and EV dispatch against live wholesale prices.

### Core Functional Engine
1.  **The Universal Agent CRM:** Merges CRM and billing natively. Front-line customer service agents use a single screen that combines messaging histories (WhatsApp/Email), smart meter consumption, and active debt ledgers. This powers the "Universal Agent" operating model, where one employee owns a customer journey end-to-end.
2.  **KrakenFlex (DERMS & VPP):** Connects domestic assets (EVs, heat pumps) and grid-scale battery storage to the wholesale market. Automates real-time dispatch and instantly passes the financial credits back to the core billing ledger.
3.  **Field Service & Asset Management:** An integrated routing and logistics engine (utilizing Mapbox APIs) that automates and optimizes schedules for smart meter and asset installation engineers.
4.  **The Migration Factory Engine:** An institutionalized, code-driven ETL module that treats legacy data migration as a standardized product feature, achieving unprecedented migration speeds (e.g., millions of accounts migrated from legacy SAP stacks cleanly). [UNVERIFIED]

### UI/UX Assessment
*   **Agent Interface:** Rejects consumerized, simplified dashboards in favor of extreme operational data density. Built in React, the workspace is optimized for speed, loading complete multi-year histories in milliseconds by eliminating third-party API hops.
*   **Customer UI:** Polished, heavily gamified mobile applications and portals designed for total consumer self-service (e.g., self-managed direct debit shifts, meter-read reward games), driving call-volume deflection.

### Strategic Positioning & Market Footprint
*   **Strengths:** Zero middleware friction. Drastic reductions in a utility's cost-to-serve (routinely 30-40% operational cost reduction claimed). [UNVERIFIED] Proven, low-risk migration record at massive scale.
*   **Weaknesses:** Total architectural lock-in. It cannot be bought as a standalone billing engine to connect to an existing Salesforce CRM; the utility must adopt the entire platform and restructure its workforce into cross-functional pods.
*   **Target Segments:** Dominant in high-volume Residential portfolios and Flex/VPP orchestration. Expanding into municipal Water and Broadband.
*   **Geographies:** Global footprint (UK, USA, Australia, Western Europe, Japan).

---

## 5. Kaluza: The Hardware-Integrated Decarbonization Cloud

Kaluza's architectural philosophy is defined by Hardware-Integrated Energy Intelligence. It operates as a modular, cloud-native Platform-as-a-Service (PaaS) built on the premise that billing engines must be natively linked to real-time domestic hardware orchestration (EVs, vehicle-to-grid V2G, heat pumps, and batteries) to monetize the net-zero transition.

### Core Architecture & Technical Stack
*   **Infrastructure:** Modular, event-driven PaaS deployed on AWS (EKS/Elastic Kubernetes Service), managed via Terraform and GitHub Actions.
*   **Backend & Concurrency:** Node.js and TypeScript handle asynchronous operations.
*   **Event Messaging & Ingestion:** Apache Kafka serves as the enterprise data bus, streaming millions of high-frequency IoT telemetry points daily and decoupling the core billing engine from real-time asset control.
*   **Data Engine:** Databricks handles massive unstructured data processing and ETL pipelines, while GraphQL serves as the responsive API integration layer.

### Core Functional Engine
1.  **Kaluza Retail:** A modern meter-to-cash engine that automates utility billing workflows, utilizes advanced predictive analytics (via AWS SageMaker) to forecast churn, and optimizes customer lifetime value through automated exception handling.
2.  **Kaluza Flex (DERMS):** The real-time optimization layer. Maintains out-of-the-box cloud-to-cloud API integrations with over 400+ device OEMs (e.g., Volkswagen Group, Volvo, Wallbox). [UNVERIFIED] It orchestrates smart charging schedules based on wholesale price and grid carbon intensity, injecting financial rewards directly back onto the Kaluza Retail bill.
3.  **Customer Care & Invoicing:** Provides agents with a 360-degree interactive account timeline, automates intelligent estimation profiles when grid meter reads fail, and manages multi-channel payment streams.

### UI/UX Assessment
*   **Agent Experience:** Designed to minimize Average Handling Time (AHT) by overlaying traditional billing grids with hardware-telemetry states. Agents can diagnose both financial status and connected EV charging status on a unified UI.
*   **Consumer Experience:** Provides highly extensible backend APIs that power responsive mobile apps, allowing consumers to interact with their automated energy savings in real-time (e.g., OVO's "Charge Anytime" application).

### Strategic Positioning & Market Footprint
*   **Strengths:** Native, seamless connection between grid-edge hardware orchestration and the retail invoice. Battle-tested at Tier-1 scale (e.g., OVO Energy migration and AGL Australia's 4-million customer Retail Transformation Programme). [UNVERIFIED]
*   **Weaknesses:** Implementation requires mature enterprise architecture capabilities and massive organizational operating model transformation to extract full cost-to-serve efficiencies.
*   **Target Segments:** Dominant in Residential and advanced Flex/VPP portfolios. Evolving commercial/SME capabilities.
*   **Geographies:** UK, Europe, Japan (via Mitsubishi), and Australia.

---

## 6. Flexibility & VPP Orchestrators (Axle Energy & Amber)

These platforms operate exclusively in the "meter-to-market" optimization space. They bypass standard billing engines entirely, focusing on aggregating decentralized residential and SME hardware into automated Virtual Power Plants.

### Core Architecture & Technical Stack
*   **Infrastructure:** API-first microservices built on Go, Node.js, and Python.
*   **Hardware Connectivity:** Purely "asset-light" cloud-to-cloud architecture. They do not install physical gateway hardware inside the home; they integrate directly with manufacturer clouds (e.g., Tesla, SolarEdge, GivEnergy) via REST and Webhook APIs.
*   **Data Bus & Telemetry:** AWS IoT Core, MQTT, and Kafka ingest continuous state-of-charge (SoC) and voltage telemetry.
*   **Data Science & Solvers:** Python-based linear programming solvers and probabilistic machine learning models. Unlike deterministic billing code, these engines continuously run 24-hour predictive simulations balancing home consumption forecasts, solar generation forecasts, wholesale pricing, and battery degradation limits.

### Core Functional Archetypes
*   **Axle Energy (The B2B API Layer):** Operates as the "Stripe for Energy." It provides a universal software abstraction layer that energy suppliers, billing engines, or hardware installers can embed via API, normalizing the communication protocols of dozens of hardware brands into a single control pane for grid flexibility markets.
*   **Amber Electric (The Pass-Through Retail Engine):** A technology company operating as a B2C utility. It eliminates flat-rate tariffs to pass raw, half-hourly wholesale spot market prices directly to the consumer app. Its proprietary "SmartShift" module automatically halts EV charging during price surges and forces home batteries to export power during peak grid stress, capturing institutional-grade Feed-in Tariffs (FiTs) for the household.

### UI/UX Assessment
*   **Interface Philosophy:** Built for transparency and trust. Amber's consumer app features live, color-coded price dials paired with a rolling 24-hour timeline that explicitly narrates the algorithm's intent (e.g., "Holding battery charge until 6:30 PM to export during peak price spike"). This transparency is architecturally necessary to prevent consumer override fatigue.

### Strategic Positioning & Market Footprint
*   **Strengths:** Extreme asset-light scalability. Native monetization of renewable intermittency and negative pricing events. High consumer ROI.
*   **Weaknesses:** Complete vulnerability to third-party hardware API fragmentation; an unannounced OEM firmware change can drop thousands of assets from the VPP instantly. Pass-through models carry severe bill-shock risks if consumer hardware fails during a market spike. Cannot issue traditional multi-play bills; must feed data back to a BSS core.
*   **Geographies:** Confined to highly deregulated, volatile flex markets (primarily Australia and the United Kingdom).

---

## 7. The Enterprise Two-Tier Paradigm: SAP + Salesforce

[Truncated as supplied -- section heading only, no content received.]
