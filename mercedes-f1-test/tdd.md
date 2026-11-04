# Technical Design Document: mercedes-f1-test

## 1. Overview & Purpose
Totto is a voice-first conversational fan agent for Mercedes Formula 1. It helps fans get race information, understand Mercedes performance, ask historical and educational Formula 1 questions, find official ticketing destinations, and receive lightweight mocked merch support.

- **Modality:** audio
- **Primary Model:** gemini-3.1-flash-live
- **Design Philosophy:** Direct, reliable, grounded responses with strict anti-fabrication controls.

## 2. Architecture
The agent uses a modular multi-agent structure managed by a root concierge agent:

- **`root_agent` (Root Agent):** Frontline concierge greeting user, detecting intent, routing to specialized sub-agents, or handling direct inquiries.
- **`inquiry_agent` (Sub-Agent):** Handles informational queries, knowledge retrieval, and general domain questions.
- **`action_agent` (Sub-Agent):** Manages structured operations, status lookups, and transactional/mock workflows.

```
root_agent (Root)
 ├── inquiry_agent (Sub-Agent)
 └── action_agent (Sub-Agent)
```

## 3. Tools
All tools are defined with explicit typed arguments and strict return payloads.

| Tool Name | Type | Purpose | Inputs | Returns |
|-----------|------|---------|--------|---------|
| `get_order_status` | Python Function | Queries verified get order status data | `query: str` | `result: dict` |
| `get_race_schedule` | Python Function | Queries verified get race schedule data | `query: str` | `result: dict` |
| `get_driver_standings` | Python Function | Queries verified get driver standings data | `query: str` | `result: dict` |
| `get_weather` | Python Function | Queries verified get weather data | `query: str` | `result: dict` |
| `get_official_links` | Python Function | Queries verified get official links data | `query: str` | `result: dict` |
| `end_session` | System | Ends conversation gracefully | `{}` | `{}` |

## 4. Routing Logic
- **Initial Turn:** Root agent greets user with date context (`${current_date}`).
- **Intent Dispatch:**
  - Informational requests route to `inquiry_agent`.
  - Action / status requests route to `action_agent`.
  - Termination triggers `end_session`.
- **Transfers:** Performed cleanly via `childAgents` references.

## 5. Variables
Declared session state variables:

| Variable Name | Type | Description | Source | Eval Override |
|---------------|------|-------------|--------|---------------|
| `user_name` | string | Name of user if provided | Session Param | Allowed |
| `query_context` | string | Contextual topic or query identifier | Session Param | Allowed |
| `session_status` | string | Status tracking the current interaction flow | Derived | Prohibited |
| `last_intent` | string | The last recognized user intent | Derived | Prohibited |

## 6. Callbacks
- **`before_model_callback`:** Attached to `root_agent` to handle deterministic session start greetings and silence/timeout recovery.
- **`after_model_callback`:** Injects required standard disclaimers or formatting before text synthesis.

## 7. Coverage Map

| Requirement | Eval Type | Rationale | Priority | Severity | Tags |
|-------------|-----------|-----------|----------|----------|------|
| CUJ-1: Product Name | golden | Verify response and tool dispatch for Product Name | P0 | NO-GO | `[mercedes-f1-test, p0]` |
| CUJ-2: Primary Use Cases | sim | Verify response and tool dispatch for Primary Use Cases | P0 | NO-GO | `[mercedes-f1-test, p0]` |
| CUJ-3: Race And Session Information | golden | Verify response and tool dispatch for Race And Session Information | P1 | HIGH | `[mercedes-f1-test, p1]` |
| CUJ-4: Mercedes Performance And Driver Context | sim | Verify response and tool dispatch for Mercedes Performance And Driver Context | P1 | HIGH | `[mercedes-f1-test, p1]` |
| CUJ-5: Formula 1 And Mercedes History | golden | Verify response and tool dispatch for Formula 1 And Mercedes History | P1 | HIGH | `[mercedes-f1-test, p1]` |
| CUJ-6: Ticketing Guidance | sim | Verify response and tool dispatch for Ticketing Guidance | P1 | HIGH | `[mercedes-f1-test, p1]` |

## 8. Test Data
- **Profile A (Standard):** `user_name: "Alex"`, `query_context: "general"`
- **Profile B (Action Flow):** `user_name: "Jordan"`, `query_context: "status_lookup"`

## 9. Pass Rate History
| Date | Iteration | Pass Rate | Goldens | Sims | Tools | Callbacks | Notes |
|------|-----------|-----------|---------|------|-------|-----------|-------|
| Initial | 0 | Baseline | - | - | - | - | Pre-deployment baseline |

## 10. Changelog
- **2026-10-13:** Initial approved TDD drafted by Engineering Assistant.
