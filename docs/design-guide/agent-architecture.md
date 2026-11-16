---
title: Agent Architecture
description: When to use a single agent versus multiple agents, and how to structure both.
---

# Agent Architecture

The most common architecture mistake is adding agents prematurely. Multi-agent setups add real complexity — handoff logic, shared state, routing decisions — and that complexity has to be paid for in maintenance and debuggability. Start with a single agent and add agents only when the single-agent design demonstrates concrete limitations.

<figure class="diagram">
  <img src="../../assets/diagrams/agent-architecture.svg" alt="Agent Architecture Patterns">
</figure>

---

## Single-agent

A single agent handles the entire conversation. All tools, instructions, and state live in one place.

### When to use

- The conversation follows a linear or near-linear flow
- State is simple enough to track in a handful of variables
- The agent has fewer than two distinct capabilities (e.g., one primary task with simple fallbacks)
- You're starting a new project and the full complexity isn't yet known

### Trade-offs

| Benefit | Limitation |
|---------|-----------|
| Simple to reason about — one instruction set, one state space | Instructions grow long as capabilities increase |
| Easy to test — all behavior in one place | A single very long instruction set degrades model reliability |
| Fast to build and iterate | Can feel awkward if the agent needs radically different personas for different tasks |
| No handoff logic to maintain | All tools visible in every turn, including irrelevant ones |

### Workspace structure

```
bella_notte/
├── gecx-config.json
├── cxas_app/
│   ├── app.json
│   ├── agents/
│   │   └── Bella_Notte_Host/
│   │       ├── Bella_Notte_Host.json
│   │       ├── instruction.txt
│   │       ├── before_agent_callbacks/
│   │       │   └── before_agent_callbacks_01/
│   │       │       └── python_code.py
│   │       └── before_model_callbacks/
│   │           └── before_model_callbacks_01/
│   │               └── python_code.py
│   ├── tools/
│   │   ├── set_party_size/
│   │   │   ├── set_party_size.json
│   │   │   └── python_function/
│   │   │       └── python_code.py
│   │   └── create_reservation/
│   │       ├── create_reservation.json
│   │       └── python_function/
│   │           └── python_code.py
│   └── evaluations/
│       └── Happy_Path_-_Linear_Flow/
│           └── Happy_Path_-_Linear_Flow.json
```

---

## Multi-agent

Multiple agents divide responsibility. One agent typically acts as the orchestrator (or "root agent"), routing the conversation to specialized sub-agents based on the user's intent.

### When to use

- Different parts of the conversation need genuinely different personas (e.g., a triage agent vs. a billing specialist)
- The full set of critical user journeys is too complex for one instruction set to handle reliably
- A single-agent prototype has been built and tested, and you've confirmed it degrades under the full scope
- You need strict capability isolation — sub-agents that cannot accidentally perform actions outside their domain

### Trade-offs

| Benefit | Limitation |
|---------|-----------|
| Each agent's instructions stay focused and short | Handoff logic is a new failure surface |
| Agents can have distinct personas and tool sets | State must be explicitly shared across agents |
| Easier to test sub-agents in isolation | Routing errors can cause confusing user experiences |
| Scales more gracefully to large capability sets | More files, more moving parts, harder to onboard |

### Workspace structure

```
my_agent/
├── gecx-config.json
├── cxas_app/
│   ├── app.json
│   ├── agents/
│   │   ├── Root_Agent/
│   │   │   ├── Root_Agent.json        # Orchestrator — routes to sub-agents
│   │   │   ├── instruction.txt
│   │   │   └── before_model_callbacks/
│   │   │       └── before_model_callbacks_01/
│   │   │           └── python_code.py
│   │   ├── Reservation_Agent/
│   │   │   ├── Reservation_Agent.json
│   │   │   └── instruction.txt
│   │   └── Cancellation_Agent/
│   │       ├── Cancellation_Agent.json
│   │       └── instruction.txt
│   ├── tools/
│   │   ├── check_availability/
│   │   │   ├── check_availability.json
│   │   │   └── python_function/
│   │   │       └── python_code.py
│   │   └── cancel_reservation/
│   │       ├── cancel_reservation.json
│   │       └── python_function/
│   │           └── python_code.py
│   └── evaluations/
│       └── Happy_Path/
│           └── Happy_Path.json
```

---

## How to decide

!!! info "Decision guide"
    Start with these questions:

    1. **Does this agent need more than one distinct persona?** If yes, lean toward multi-agent.
    2. **Does this agent have more than two substantially different capabilities?** If yes, single-agent instructions will grow long. Consider splitting.
    3. **Have you built a single-agent version?** If no, build one first. Real failure modes are easier to see in a working prototype than in a design document.
    4. **Is the single-agent version failing evals in ways that better instructions can't fix?** If yes, that's the signal to split.

The decision isn't permanent. A single-agent design can be refactored into multi-agent later. The reverse is harder. When in doubt, start simple.

---

## The "start simple" philosophy

Multi-agent architectures look appealing in design documents because they seem modular and clean. In practice, they introduce coordination problems that are hard to anticipate until you're debugging them in a failing eval.

The correct sequence is:

1. **Build a single-agent prototype.** Get it working against your core user journeys.
2. **Run evals.** Identify where it fails and why.
3. **Try to fix failures with better instructions, tools, or callbacks.** Most failures can be addressed this way.
4. **If you've exhausted those options**, and the root cause is genuinely that the instruction set is too large or the personas are too different, then split into multiple agents.

This sequence gives you a baseline to compare against. A multi-agent design that performs worse than the single-agent prototype is a signal that the problem was never architectural.

!!! warning "Avoid tool explosion"
    A common driver of premature multi-agent adoption is having too many tools. Before splitting into multiple agents, check whether you can reduce tool count instead. Tools with overlapping functionality, high-cardinality arguments, or poor naming are often better candidates for redesign than handoff. See [Tool Design](tool-design.md) for guidance.

---

## Layered Voice Architecture & Agentic Well-Architected Framework ("TCP/IP over OSI")

Whether you run a single agent or a shallow multi-agent hub, every production voice agent is a **probabilistic model wrapped inside a deterministic Python harness**. GECX organizes that system using a **"TCP/IP over OSI" Hybrid Voice Stack**: **4 Builder Macro-Bands** that map 1-to-1 to your `cxas_app/` directory layout and the **5+1 CXAS Evaluation Pyramid (`L0`–`L5`)**, subdivided into **L1–L7 Agentic OSI Diagnostic Layers** for precision linting and failure attribution.

<figure class="diagram">
  <img src="../../assets/diagrams/voice-layered-architecture.svg" alt="GECX Hybrid Voice Stack">
</figure>

### First principles: conversational wire physics & "Count Passes, Not Tokens"

Voice architecture begins at the physical telephony wire (`PSTN / SIP / SBC / RTP` full-duplex audio streams paired with Gemini Composite native audio targeting `<800ms` Time-to-First-Audio).

In natural human phone conversation, turn-taking averages a **`~200 ms` conversational gap** (Stivers et al., PNAS 2009). On telephony wires, unpaced silence past **`<1,200 ms`** registers as dead air—callers repeat themselves, talk over the agent, or abandon the call.

To deliver responsive voice interactions, GECX enforces the foundational rule: **"Count Passes, Not Tokens"**. Turn latency is dominated by model invocations, not token generation speed:

- **Single Gemini Pass**: **`~465 ms` median** model latency per conversational hop.
- **0-Pass Python Callback Turn**: **`116–236 ms`** round-trip execution.
- **Inline `tools.x()` Call**: **`10–19 ms`** inside callbacks.
- **`BidiRunSession` First-Message Law**: On live bidirectional streams, `SessionConfig` MUST precede any raw audio frames to guarantee pipeline initialization.

Every upper-layer pattern in the stack exists to protect this `<1,200 ms` conversational wire contract alongside security, groundedness, and token cost.

---

### 4 Macro-Bands × L1–L7 Agentic OSI diagnostic matrix

Builders author code across **4 Macro-Bands** (ordered bottom-to-top from the physical wire to external backends), while `cxas lint`, `cxas llm-lint`, and `cxas evals report` pinpoint issues to the exact **Agentic OSI Layer (`L1`–`L7`)**:

| Macro-Band (Bottom → Top) | `cxas_app/` Artifact Scope | Agentic OSI Layers | Key Architectural Patterns & Lint Rules | CXAS Evaluation Pyramid Gate |
|---|---|---|---|---|
| **Band 1 — Acoustic Wire & Turn Pacing** | `app.json` + Tool Pacing | **`OSI L1`** (Physical / Acoustic Wire)<br>**`OSI L2`** (Data Link / Turn Framing & Pacing) | • `gemini-composite-v2` + `sonic-bolt` (`gemini-3.8-flash-lite-tts`), `temperature: 1.0` (`A010`), cleared Director's Notes, SBC barge-in buffer flush (`bargeInAwareness: true`)<br>• The 5 Levers of Speed (Mask, Cut, Overlap, Start Early, Shrink), spoken filler bridges (`T014`) & 3-strike VAD silence framing (`E009`, `E012`, `V001`) | **Eval L5: Audio Sims & Guardrails**<br>*(F1 Grand Prix)* |
| **Band 2 — Deterministic Python Harness** | `callbacks/` + `session.state` (`<5ms`) | **`OSI L5`** (Session & Identity Gate)<br>**`OSI L6a`** (Presentation / Post-Tool Interceptor) | • One-time `_initialized` state seeding, 0-token greeting (`~150 ms`), silent close `[Part.from_text(text="")]` vs deaf-session trap, synchronous `before_model_callback` Auth Gate (`S003`), `C005` (no speech regex)<br>• `<2ms` `after_tool_callback` PII/secret scrubber (`C006`, `S008`, `V005`) & Guardrail Latency Hierarchy (`contentFilter` vs `llmPolicy`) | **Eval L1: Callback Unit Tests**<br>*(F1 Bench)* |
| **Band 3 — Cognitive Brain & Routing Topology** | `agents/*/instruction.txt` & `rootAgent` | **`OSI L3`** (Network / Agent Routing Topology)<br>**`OSI L7`** (Application / Cognitive XML Policy) | • **"Start Simple" Single-Agent Default** (`<=15` tools, 1 pass, 0 transfer bleed) vs Earned Hub-and-Spoke (`735 ms` callback transfer vs `1,633 ms` model+rephrase, `childAgents` `S004`, `end_session` `A005`)<br>• Canonical PIF XML (`<role>`, `<persona>`, `<primary_goal>`, `<constraints>`, `<error_protocol>`, `<taskflow>`, `${current_date}` `I001`–`I016`), 4-Gate Pattern Graduation | **Eval L0/L3/L4: Lint, Turn & Goldens**<br>*(F1 Chicane)* |
| **Band 4 — Tool Transport & Clean Data Facade** | `tools/*/python_code.py` (`<=5s` SLA) | **`OSI L4`** (Transport / Execution SLA & Circuit Breaker)<br>**`OSI L6b`** (Presentation / Clean DTO Facade) | • **5 Laws of Tool Engineering**: explicit `-> dict`, no `None` defaults (`T011`), `ces_requests`/`async_tools` with `<=5s` SLAs inside `30s` harpoon, stateful `503` circuit breakers, IDOR state-bound IDs<br>• **`2,400 -> 32` token Clean DTO compression** (`T006`), setter docstrings `<=1–2` sentences (`T002`, `T012`), `UNTRUSTED_EXTERNAL_DATA` / `NULL_LEDGER_DATA` envelopes, self-healing `agent_action` (`T001`) | **Eval L2: Isolated Tool Tests**<br>*(F1 Dyno)* |

---

### Macro-Band deep dives

#### Macro-Band 1 — Acoustic Wire & Turn Pacing (`app.json` + Tool Pacing)

Band 1 governs physical voice streaming, synthesis dynamics, turn detection, and latency masking.

- **OSI L1 (Physical / Acoustic Wire, `<800 ms` TTFA)**:
    - **Canonical Engine**: **`gemini-composite-v2` + `sonic-bolt` (`gemini-3.8-flash-lite-tts`)** configured with `modelSettings.temperature = 1.0` (`A010`) to eliminate acoustic repetition deadlocks, paired with SBC barge-in buffer flush (`bargeInAwareness: true`).
    - **Clear Legacy Director's Notes**: For `v2`, always clear voice instructions (`"instruction": ""`, `"voiceInstructionMode": "NO_INSTRUCTION"`). Legacy Director's Notes cause whisper RMS dynamics to compress from natural **`3.84x`** down to flat **`1.12x`** dynamic range. Rules `A007`, `A008`, and `A009` apply exclusively to legacy `gemini-composite-v1`.
    - **Affective Delivery & Prosody**: Steer voice tone through `<Affective Delivery>` directives and scoped speech normalization (`<instruction id="text normalization for speech">`) in `global_instruction.txt`. For callback-generated speech, inject opening angle-bracket tags (e.g., `<prosody rate="64%"><warm>`) inside `Part.from_text()`. Never emit closing tags (`</prosody>`), never use square brackets (`[warm]`), and never apply SSML tags on monolithic A2A engines (`gemini-3.1-flash-live`).
- **OSI L2 (Data Link / Turn Framing & The 5 Levers of Speed)**:
    1. **Mask**: Hide long-running backend operations behind conversational bridges:
        - *Callback filler*: `0.26 s` pre-emptive acoustic acknowledgment.
        - *Named Two-Part Reply*: `0.73 s` dual-phase conversational handoff.
        - *Platform filler*: `0.75–1.0 s` engine filler. **Forbid** platform filler on fast setters (`<300 ms`) or silent-close turns (`T014`).
    2. **Cut**: Eliminate unnecessary model loops with 0-pass Python callbacks and `10–19 ms` inline `tools.x()` executions.
    3. **Overlap**: Maximize concurrency using `toolExecutionMode: PARALLEL` and `async_tools` execution.
    4. **Start Early**: Trigger caller ANI prefetch during ring-time and set `5s` `inactivityTimeout` on remote polling jobs (reducing polling latency from `30.6 s -> 0.14 s`).
    5. **Shrink**: Enforce lean prompt tokens and aggressively compressed DTO payloads.

#### Macro-Band 2 — Deterministic Python Harness (`callbacks/` + `session.state`)

Band 2 wraps probabilistic model calls inside a deterministic, zero-latency Python safety harness executing in `<5 ms`.

- **OSI L5 (Session, Greeting & Identity Gate)**:
    - **Turn Guards & State Seeding**: Protect initial state initialization using an `_initialized` boolean flag in `before_agent_callback`.
    - **0-Token Greeting**: Deliver instant caller greetings in **`~150 ms`** via deterministic `before_agent_callback` without burning model passes.
    - **Silent Close Contract**: Terminate calls cleanly by returning `[Part.from_text(text="")]`. **Never return `parts=[]`**, which triggers the platform deaf-session trap where audio input is permanently silenced.
    - **Synchronous Auth Gate**: Enforce authentication in `before_model_callback` returning an `Optional[LlmResponse]` (`S003`). Unauthenticated callers are halted before reaching model reasoning.
    - **Rule `C005` (Speech Regex Prohibition)**: Never attempt intent classification or branching via Python regular expressions on raw caller speech—speech-to-text transcripts on phone lines achieve only **11% accuracy** against phonetic ambiguity.
- **OSI L6a (Presentation / Post-Tool Interceptor & Guardrail Hierarchy)**:
    - **Deterministic Scrubber**: Run a deterministic `<2 ms` `after_tool_callback` across all tool outputs to sanitize leaked secrets, unmasked PII, and indirect prompt injections before data reaches model context (`C006`, `S008`, `V005`).
    - **Guardrail Latency Hierarchy**: Always evaluate guardrail cost against latency budgets:
        - *High efficiency*: `0–1 ms` `contentFilter` and 0-token Guardrail Handoff Intercepts.
        - *High latency*: Serial `llmPolicy` checks add **`~240–340 ms` per rule**; reserve these only for regulated compliance boundaries where deterministic checks cannot suffice.

#### Macro-Band 3 — Cognitive Brain & Routing Topology (`agents/*/instruction.txt`)

Band 3 defines the agent's semantic reasoning, persona, conversational taskflow, and routing hierarchy.

- **OSI L3 (Network / Agent Routing Topology)**:
    - **"Start Simple" Single-Agent Default**: Keep architectures single-agent by default (`<=15` tools, `1` pass, `0` transfer bleed). Single-agent designs eliminate routing ambiguity and handoff latency.
    - **Earned Hub-and-Spoke**: Graduate to multi-agent only when capability isolation or distinct personas demand it. Prefer callback-driven transfers (`735 ms`) over model rephrasing handoffs (`1,633 ms`). Always declare sub-agents in underscore `childAgents` (`S004`), enforce single-parent hierarchy (`S007`), and ensure the root agent declares `end_session` (`A005`).
- **OSI L7 (Application / Cognitive XML Policy & Pattern Graduation)**:
    - **Canonical PIF XML**: Structure instructions using standard lowercase XML blocks: `<role>`, `<persona>`, `<primary_goal>`, `<constraints>`, `<error_protocol>`, `<taskflow>`, `<subtask>`, `<step>`, `<trigger>`, and `<action>` (`I001`–`I016`). Always inject `${current_date}` and ground responses strictly on `null` or `UNTRUSTED_EXTERNAL_DATA` envelopes.
    - **4-Gate Pattern Graduation Process**:
        - *Gate 1 (Contract & Lint)*: Static structural AST validation via `cxas lint`.
        - *Gate 2 (Deterministic Unit Bench)*: Isolated callback and tool contract verification.
        - *Gate 3 (Turn & Golden Chicane)*: Groundedness, tone, and multi-turn flow tests.
        - *Gate 4 (Audio Grand Prix & Shadow)*: Full acoustic simulation under noise and live traffic replay.
        - *Incubating Status*: Advanced experimental patterns (`Self-Steering` and `Slot Filling DAG`) remain **Incubating at Gate 1–2** until multi-turn voice benchmarks verify reliability.

#### Macro-Band 4 — Tool Transport & Clean Data Facade (`tools/*/python_code.py`)

Band 4 implements the data transport boundary between the agent and external enterprise APIs.

- **OSI L4 (Transport / Execution SLA, Concurrency & IDOR)**:
    - **The 5 Laws of Tool Engineering**:
        1. **Strict Return Signatures**: All tool functions must specify an explicit `-> dict` return annotation.
        2. **No `None` Defaults (`T011`)**: Never declare parameters with `= None`. Default values must match expected primitive types (`""`, `0`, `False`) to prevent platform silent-drop traps.
        3. **Bounded Client SLAs**: Use `from ces_requests import ces_requests` or `async_tools` with strict `<=5 s` timeouts well inside the platform's `30 s` execution harpoon.
        4. **Stateful Circuit Breakers**: Automatically trip fallback handling after repeated `503` upstream failures (`attempt >= 2`).
        5. **IDOR State-Bound Parameters**: Read authorization identifiers (account numbers, user IDs) directly from trusted `context.state` rather than accepting them as untrusted model arguments.
- **OSI L6b (Presentation / Clean DTO Facade & Self-Healing)**:
    - **Clean DTO Compression (`T006`)**: Compress verbose backend payloads down to compact domain transfer objects—compressing a raw **`2,400` token dump to `32` tokens** saves **`2.4 s` across 5 conversational passes** (*"It can't leak what it never saw"*).
    - **Lean Setter Docstrings (`T002`, `T012`)**: Write focused tool docstrings of `<=1–2` sentences describing purpose and prerequisites without polluting model context.
    - **Data Envelopes**: Wrap untrusted text in `UNTRUSTED_EXTERNAL_DATA` envelopes and missing fields in explicit `NULL_LEDGER_DATA` states.
    - **Self-Healing Guidance (`T001`)**: Return descriptive `agent_action` instructions when recoverable errors occur so the model can rectify missing arguments without crashing.

---

### Why OSI Layer 6 splits across Bands 2 and 4 (`L6a` vs. `L6b`)

Presentation and data hygiene operate as a two-layer defense boundary around untrusted backends:

- **`OSI L6b` (Band 4 — Clean DTO Facade)** strips internal database fields, raw stack traces, and excessive payload bloat inside `tools/*/python_code.py` *before* data leaves the tool, wrapping external text in `UNTRUSTED_EXTERNAL_DATA` envelopes and missing values in explicit `NULL_LEDGER_DATA` states.
- **`OSI L6a` (Band 2 — Post-Tool Interceptor)** runs a deterministic `<2ms` `after_tool_callback` across all tools—including third-party OpenAPI or MCP toolsets you do not author directly—to redact residual secrets, PII, or prompt-injection payloads before the model ever sees `tool_response`.

---

### Mapping to the 5 Google Cloud Agentic WAF Pillars

Every architectural control and lint rule in the 4-Band stack aligns with one of the **5 Google Cloud Agentic Well-Architected Framework (WAF) Pillars**, allowing engineering teams to audit posture directly from the CLI (`cxas lint --waf-pillar <pillar>`):

| Google Cloud Agentic WAF Pillar | Primary Macro-Bands & OSI Layers | Architectural Controls & Verification |
|---|---|---|
| **Performance** | **Bands 1 & 3** (`OSI L1`, `L2`, `L3`, `L7`) | Protects the `<1,200ms` wire budget via `gemini-composite-v2` (`A010`), cleared Director's Notes, `T014` spoken bridge fillers, shallow single-parent sub-agent trees (`S007`), and callback-driven branching instead of heavy prompt `IF/ELSE` trees (`I003`, `I005`, `C005`). |
| **Security** | **Bands 2, 3 & 4** (`OSI L5`, `L6a`, `L6b`, `L7`) | Enforces **Two-Plane Security**: deterministic `before_model_callback` `LlmResponse` auth gates (`S003`), `<2ms` `after_tool_callback` PII/secret scrubbing and singleton `llmPromptSecurity` guardrails (`S008`, `V005`), IDOR state-bound tool parameters, sanitized `L6b` DTO projections, and canonical XML instruction boundaries (`I015`) refusing `UNTRUSTED_EXTERNAL_DATA` overrides. |
| **Reliability** | **Bands 2, 3 & 4** (`OSI L3`, `L4`, `L5`, `L6b`, `L7`) | Prevents call drops and hallucinations through bounded `<=5s` client timeouts, stateful `503` circuit breakers, explicit `NULL_LEDGER_DATA` envelopes (preventing hallucinated data on `null`), declared `session.state` schemas (`V100`–`V104`), native `end_session` termination (`A005`), and eliminating fragile prose state machines (`I016`). |
| **Cost** | **Bands 2, 3 & 4** (`OSI L3`, `L4`, `L5`, `L6b`, `L7`) | Minimizes token and compute spend by short-circuiting unauthenticated turns in `<5ms` Python callbacks (`OSI L5`), keeping agent instructions focused (`I007`), pruning unreferenced tools (`I012`, `T008`), and compressing payloads `2,400 -> 32` tokens in Clean DTOs (`T006`). |
| **Operational Excellence** | **All 4 Bands** (`OSI L1`–`L7` / Pyramid `L0`–`L5`) | Standardizes declarative layout (`S005`, `S006`), schema validation, shadow/simulation eval hygiene (`E001`–`E012`), semantic prompt reviews (`cxas llm-lint`), and layer-targeted CI gates (`cxas lint --band {1..4}`, `cxas lint --waf-pillar`, and `cxas ci-test`). |

---

### Official 5+1 CXAS Evaluation Pyramid (`L0`–`L5`)

Quality engineering in voice AI requires verifying behavior from static syntax up to end-to-end full-duplex telephony simulations. GECX defines the **Official 5+1 CXAS Evaluation Pyramid**, pairing each testing tier with its F1 racing metaphor:

| Pyramid Tier | Verification Scope | Target Artifacts & Tooling | F1 Racing Metaphor | Automated CI Command |
|---|---|---|---|---|
| **Eval L0** | **Static & Semantic Linting** | Structural syntax, CES schema validation, prompt XML taskflows (`cxas lint`, `cxas llm-lint`) | *Wind Tunnel* | `uv run cxas lint`<br>`uv run cxas llm-lint` |
| **Eval L1** | **Callback Unit Tests** | Deterministic Python callbacks, auth gates, state seeding, PII scrubbers (`<5 ms` budget) | *Bench Test* | `uv run pytest tests/callbacks/` |
| **Eval L2** | **Isolated Tool Tests (`:executeTool`)** | Tool Python signatures, Clean DTO compression, circuit breakers, REST mock contracts | *Engine Dyno* | `uv run pytest tests/tools/` |
| **Eval L3** | **Turn Evals** | Single-Turn semantic assertions, tone compliance, groundedness checks | *Telemetry* | `uv run cxas evals run --type turn` |
| **Eval L4** | **Platform Goldens** | Multi-Turn deterministic golden paths, state assertions, tool call matching | *Chicane Test* | `uv run cxas evals run --type golden` |
| **Eval L5** | **Scenario Simulations & Guardrail Evals** | Full-duplex acoustic simulations, 13 background noise presets, prompt-injection red-teaming | *Grand Prix* | `uv run cxas evals report --modality audio` |
| **+1 Tier** | **ShadowEvals** | Production trace replay against staging versions to detect behavioural regressions | *Post-Race Replay* | `uv run cxas evals run --type shadow` |

Run the complete pipeline continuously during development and in pre-merge automation via **`cxas ci-test`**:

```bash
uv run cxas ci-test --app-dir cxas_app/ --modality audio
```

See the [Rule Reference](../guides/linting/rules.md) and [`cxas lint` CLI reference](../cli/lint.md) for complete rule-to-layer mappings and filtering commands.
