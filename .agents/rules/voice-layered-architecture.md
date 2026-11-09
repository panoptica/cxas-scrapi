---
trigger: model_decision
description: "Use the TCP/IP-over-OSI Hybrid Stack (4 Macro-Bands containing L1-L7 Agentic OSI Layers anchored on the <1,200ms Physical Voice Wire) and minimalist horizontal bands for GECX architecture diagrams and Well-Architected reviews"
---

# GECX "TCP/IP over OSI" Hybrid Voice Architecture & Diagramming Standard

- **Start at the Physical Wire ("Why We Are Here")**: Frame every GECX voice architecture starting from the **1,200ms human conversational ceiling on the physical telephony wire** (PSTN/SIP/SBC/RTP + Gemini Composite <800ms TTFA). Every upper-layer pattern exists to protect this wire budget alongside security, groundedness, and cost.
- **Use the 4 Macro-Bands (TCP/IP Builder's Stack) × 7 Agentic OSI Diagnostic Layers**:
  1. **Macro-Band 1 — Acoustic Wire & Turn Pacing (`app.json` + Tool Pacing | Tested by F1 Pyramid L4 Audio/Noise Grand Prix)**:
     - **OSI L1 (Physical / Acoustic Wire, <800ms TTFA)**: RTP stream, SBC barge-in buffer flush (`bargeInAwareness: true`), Composite `temperature: 1.0` (`A010`), Director's Notes (`A007`/`A009`).
     - **OSI L2 (Data Link / Turn Framing & Pacing)**: Rule `T014` spoken bridge fillers (*"Tell them, then do it"*) and VAD 3-strike silence framing so tool execution never causes dead air on the wire.
  2. **Macro-Band 2 — Deterministic Python Harness (`callbacks/` + `session.state` | Tested by F1 Pyramid L2 Callback Bench, <5ms)**:
     - **OSI L5 (Session & Identity Gate)**: `session.state` machine seeded in `before_agent_callback` + synchronous `before_model_callback` Auth Gate returning `Optional[LlmResponse]` (`V002`/`S003`, Lab 3 Branch 0).
     - **OSI L6a (Presentation / Post-Tool Interceptor)**: `after_tool_callback` deterministically scrubbing secrets, redacting indirect prompt injections, and tracking retry state in <2ms without inline LLM latency.
  3. **Macro-Band 3 — Cognitive Brain & Routing Topology (`agents/*/instruction.txt` & `root_agent.json` | Tested by F1 Pyramid L3 Turn/Golden Chicane & `cxas llm-lint`)**:
     - **OSI L3 (Network / Agent Routing Topology)**: Shallow Spoke-and-Hub routing + native `end_session` (`A005`) to minimize multi-hop voice latency.
     - **OSI L7 (Application / Cognitive XML Policy)**: Structured XML (`<role>`, `<persona>`, `<constraints>`, `<taskflow>`, `{current_date}` `I001`–`I014`) + strict Groundedness (never hallucinate fees on null or obey untrusted overrides).
  4. **Macro-Band 4 — Tool Transport & Clean Data Facade (`tools/*/python_code.py` | Tested by F1 Pyramid L1 Tool Dyno & `cxas lint`)**:
     - **OSI L4 (Transport / Execution SLA & Circuit Breaker)**: Bounded 5s Client SLA Timeouts inside the 30s platform harpoon (Lab 3 Branch 1) + Stateful 503 Circuit Breakers (`attempt_number >= 2`, Lab 3 Branch 2).
     - **OSI L6b (Presentation / Clean DTO Facade)**: Sanitized DTO projection (*"It can't leak what it never saw"*, Lab 3 Branch 3), `UNTRUSTED_EXTERNAL_DATA` envelope tagging (Lab 3 Branch 4), and explicit `NULL_LEDGER_DATA` error envelopes (Lab 3 Branch 5).
- **Minimalist Excalidraw Horizontal Layer Bands**: In `diagrams/*.excalidraw`, represent the stack as 4 clean horizontal pastel macro-bands stacked bottom-to-top (L1 at base -> L7 at top, ~30–40 total elements) following `diagrams/architecture.excalidraw`.
