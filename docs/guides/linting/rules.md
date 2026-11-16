---
title: Rule Reference
description: Complete reference for all CXAS linter rules, organized by category.
---

# Rule Reference

The CXAS linter has 60+ rules across 7 categories. This page documents every rule — what it checks, which architectural layer and Well-Architected pillar it guards, what triggers it, and how to fix it.

Severities shown are the defaults. You can override any rule's severity in `cxaslint.yaml`.

## Macro-Band, Agentic OSI Layer & WAF Pillar Classification

Every lint finding is tagged with its [Hybrid Voice Architecture](../../design-guide/agent-architecture.md#layered-voice-architecture-agentic-well-architected-framework-tcpip-over-osi) coordinates — **`[Band X / OSI LY • Pillar]`** — so you can filter checks by engineering layer (`cxas lint --band {1,2,3,4}`) or Google Cloud Agentic Well-Architected Framework (WAF) pillar (`cxas lint --waf-pillar <pillar>`):

| Macro-Band | Agentic OSI Layers | CXAS Evaluation Pyramid Gate | Rule IDs | WAF Pillars Covered |
|---|---|---|---|---|
| **Band 1 — Acoustic Wire & Turn Pacing**<br>(`app.json` & Tool Pacing) | **`OSI L1`** (Physical / Acoustic Wire)<br>**`OSI L2`** (Data Link / Turn Framing & Pacing) | `Eval L5: Audio Sims & Guardrails`<br>*(F1 Grand Prix)* | • **`L1`:** `A001`, `A002`, `A007`\*, `A008`\*, `A009`\*, `A010`, `V001`, `E009`<br>• **`L2`:** `T014`, `E012`<br><small>\* *Note: `A007`–`A009` are legacy `gemini-composite-v1`-only checks; `gemini-composite-v2` clears Director's Notes.*</small> | `Performance`, `Reliability`, `Operational Excellence` |
| **Band 2 — Deterministic Python Harness**<br>(`callbacks/` & `session.state`) | **`OSI L5`** (Session & Identity Gate)<br>**`OSI L6a`** (Presentation / Post-Tool Interceptor) | `Eval L1: Callback Unit Tests`<br>*(F1 Bench)* | • **`L5`:** `C001`–`C005`, `C007`, `C010`, `S003`, `E004`, `E006`, `V100`–`V103` *(callbacks/evals)*<br>• **`L6a`:** `C006`, `S008`, `V005` | `Security`, `Reliability`, `Performance`, `Operational Excellence` |
| **Band 3 — Cognitive Brain & Routing Topology**<br>(`agents/*/instruction.txt` & routing) | **`OSI L3`** (Network / Agent Routing Topology)<br>**`OSI L7`** (Application / Cognitive XML Policy) | `Eval L0/L3/L4: Lint, Turn & Goldens`<br>*(F1 Chicane)* | • **`L3`:** `A003`, `A005`, `A006`, `I007`, `I008`, `I010`, `S004`, `S005`, `S007`, `V002`<br>• **`L7`:** `A004`, `I001`–`I006`, `I009`, `I011`–`I016`, `S002`, `V006`, `V007`, `V100`–`V103` *(instructions)*, `V104`, `E001`, `E002`, `E005`, `E007`, `E008` | `Reliability`, `Performance`, `Security`, `Cost`, `Operational Excellence` |
| **Band 4 — Tool Transport & Clean Data Facade**<br>(`tools/*/python_code.py`) | **`OSI L4`** (Transport / Execution SLA & Circuit Breaker)<br>**`OSI L6b`** (Presentation / Clean DTO Facade) | `Eval L2: Isolated Tool Tests`<br>*(F1 Dyno)* | • **`L4`:** `S006`, `T001`, `T004`, `T007`–`T011`, `T013`, `V003`, `V004`, `E003`, `E010`<br>• **`L6b`:** `T002`, `T003`, `T005`, `T006`, `T012`, `E011`, `V100`–`V103` *(tools)* | `Reliability`, `Cost`, `Operational Excellence` |

!!! note "Context-aware variable rule resolution (`V100`–`V103`)"
    Multi-artifact variable schema rules (`V100`–`V103`) dynamically resolve their Macro-Band and OSI Layer from the inspected file: **`Band 2 / OSI L5`** in callbacks and evals, **`Band 3 / OSI L7`** in `instruction.txt`, and **`Band 4 / OSI L6b`** in `tools/*/python_code.py`.

---

## Rules by Category

=== "I — Instructions"

    Rules in the `I` category check `instruction.txt` files for structural correctness, reference validity, and best-practice adherence.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | I003 | `excessive-if-else` | Warning | `Band 3 / OSI L7` | `Performance` | 3 or more `IF/ELSE` blocks in an instruction |
    | I004 | `negative-triggers` | Warning | `Band 3 / OSI L7` | `Reliability` | Negative conditions in `<trigger>` elements |
    | I005 | `conditional-logic-block` | Warning | `Band 3 / OSI L7` | `Performance` | `<conditional_logic>` block used for intent classification |
    | I006 | `hardcoded-data` | Warning | `Band 3 / OSI L7` | `Reliability` | Hardcoded phone numbers, prices, or other dynamic data |
    | I007 | `instruction-too-long` | Info | `Band 3 / OSI L3` | `Cost` | Instruction exceeds word count threshold (default 3000 words) |
    | I008 | `invalid-agent-ref` | Error | `Band 3 / OSI L3` | `Reliability` | `{@AGENT: Name}` references an agent that doesn't exist |
    | I010 | `wrong-agent-syntax` | Error | `Band 3 / OSI L3` | `Reliability` | Wrong agent reference syntax (e.g., `${AGENT:...}` instead of `{@AGENT:...}`) |
    | I011 | `wrong-tool-syntax` | Error | `Band 3 / OSI L7` | `Reliability` | Wrong tool reference syntax (e.g., `{TOOL:...}` instead of `{@TOOL:...}`) |
    | I012 | `unused-tool-in-config` | Warning | `Band 3 / OSI L7` | `Cost` | Tool is in the agent's JSON config but never referenced in the instruction |
    | I014 | `missing-current-date` | Warning | `Band 3 / OSI L7` | `Reliability` | Instruction (or global instruction) should reference `{current_date}` |
    | I015 | `banned-legacy-xml-tags` | Error | `Band 3 / OSI L7` | `Security` | Instruction uses a banned legacy XML tag |
    | I016 | `prose-state-machine` | Warning | `Band 3 / OSI L7` | `Reliability` | Instruction encodes a state machine in prose (named-step GOTOs, retry counters, STOP tokens, state writes, orchestrator `agent_action` traversal) |

    ---

    **I003 — excessive-if-else**

    Putting lots of `IF/ELSE` logic in instructions makes the LLM less reliable. LLMs are good at understanding intent, not at executing imperative logic trees. Move branching logic to callbacks.

    *Triggers:* 3 or more lines matching `IF ... ELSE` pattern (case-insensitive).

    *Fix:* Move deterministic branching into a `before_model_callback` or `after_model_callback`. Keep the instruction focused on goals, not conditional flows.

    ---

    **I004 — negative-triggers**

    Negative conditions in `<trigger>` elements confuse the LLM. "Trigger when NOT X" is harder for the model to reason about reliably than "Trigger when Y (the positive case)".

    *Triggers:* `<trigger>` element containing `NOT`, `is NOT`, or similar negations.

    *Fix:* Rewrite as a positive trigger. If you need to exclude a case, use a separate, earlier `<step>` that captures that case explicitly.

    ---

    **I005 — conditional-logic-block**

    `<conditional_logic>` blocks with priority-ordered conditionals are a pattern that confuses models because they require the model to evaluate conditions in order and pick the first match.

    *Triggers:* Presence of `<conditional_logic>` in the instruction.

    *Fix:* Use separate `<step>` elements with distinct triggers instead.

    ---

    **I006 — hardcoded-data**

    Phone numbers, prices, and other frequently-changing data in instructions create maintenance problems and risk the agent giving outdated information.

    *Triggers:* Patterns matching phone numbers or dollar amounts in non-template lines.

    *Fix:* Move dynamic data to tool responses. The agent should call a tool to get the current value, not read it from the instruction.

    *Configurable:* You can add custom patterns in `cxaslint.yaml` under `options.I006.patterns`.

    ---

    **I007 — instruction-too-long**

    Very long instructions tax the model's context window and can reduce reliability. Consider splitting into multiple sub-agents.

    *Triggers:* Word count exceeds the configured threshold (default: 3000 words).

    *Fix:* Split complex responsibilities into sub-agents. Each agent should have a focused, manageable instruction.

    *Configurable:* Set `options.I007.max_words` in `cxaslint.yaml`.

    ---

    **I008 — invalid-agent-ref**

    The `{@AGENT: Name}` syntax transfers control to another agent. If the referenced agent doesn't exist, the LLM can't transfer.

    *Triggers:* `{@AGENT: Name}` where `Name` doesn't match any agent in the app.

    *Fix:* Check the agent display name or resource name. The fix message lists available agents.

    ---

    **I010 — wrong-agent-syntax**

    Common wrong forms for agent references that look almost right but won't be recognized by the platform.

    *Triggers:* `${AGENT:...}`, `{AGENT:...}` (without `@`), or `${@AGENT:...}`.

    *Fix:* Use `{@AGENT: Display Name}` (with `@` sign, space after colon).

    ---

    **I011 — wrong-tool-syntax**

    Similar to I010, but for tool references.

    *Triggers:* `${TOOL:...}`, `{TOOL:...}`, or `${@TOOL:...}`.

    *Fix:* Use `{@TOOL: Tool Name}`.

    ---

    **I012 — unused-tool-in-config**

    If a tool is in the agent's JSON but never referenced in the instruction, the LLM doesn't know it can call the tool — which makes having it in the config pointless.

    *Triggers:* Tool appears in `agent.json`'s `tools` array but has no `{@TOOL: ...}` reference in `instruction.txt`.

    *Fix:* Either add `{@TOOL: tool_name}` to the instruction (with appropriate context), or remove the tool from the agent's config.

    ---

    **I014 — missing-current-date**

    Instructions should reference `{current_date}` or `{{current_date}}` so the agent knows the current date at runtime. This is important for date-sensitive tasks. If the global instruction or all agent instructions reference it, the warning is suppressed.

    *Triggers:* No `current_date` reference found in `instruction.txt` or `global_instruction.txt`.

    *Fix:* Add `{current_date}` or `{{current_date}}` to the instruction or global instruction.

    ---

    **I015 — banned-legacy-xml-tags**

    Instructions must not contain legacy CamelCase or state-machine XML tags that diverge from the canonical lowercase taskflow schema.

    *Triggers:* Presence of tags like `<Agent>`, `<Conversation_Schema>`, `<Persona>`, `<Role>`, `<General_Instruction>`, `<Context>`, `<state>`, `<transitions>`, or `<transition>`.

    *Fix:* Rewrite using the canonical lowercase taskflow schema: `<role>`, `<persona>`, `<primary_goal>`, `<constraints>`, `<guidelines>`, `<taskflow>`, `<subtask>`, `<step>`, `<trigger>`, `<action>`.

    ---

    **I016 — prose-state-machine**

    The single most damaging instruction anti-pattern: hand-building a finite-state machine inside the prompt and asking the LLM to execute it every turn. The model is made to read a counter variable, compare it to a literal, branch to a named step, write state back, and follow `agent_action` codes verbatim — control flow that an LLM executes unreliably and that belongs in deterministic code. This rule is a deterministic, multi-signal composite: it scores eleven independent surface forms (retry/attempt counters, `STOP.` halt tokens, `->` transitions, conditional "go to step X" dispatch edges, back-edge loops, `{var} == value` tests, UPPER_SNAKE state writes, `lookup_flag: "INIT"` orchestrator traversal, `follow the returned agent_action verbatim`, a "state machine" named in a step, and `IF`-on-result-code) grouped into four categories, and fires only on co-occurrence (or a single high-confidence marker) so that a well-designed, declarative instruction stays silent.

    *Triggers:* A high-confidence marker on its own (a retry-counter read/write, an UPPER_SNAKE state write, a `lookup_flag` enum, an `agent_action`-verbatim loop, or a "state machine" step name); **or** signals from ≥ 2 categories totalling ≥ 4 occurrences; **or** ≥ 3 strong control-flow edges (conditional jumps + loop back-edges). Plain forward navigation ("proceed to subtask conclusion") on its own never fires. Surface forms are kept disjoint from I003 and I005 so no line is double-reported. Content inside `<inline_example>` regions is ignored.

    *Fix:* Move the control flow out of the prompt. Put retry/attempt counters and failure limits in a `before_model`/`after_model` callback — the [slot-filling pattern](../../patterns/slot-filling.md) keeps retry state in Python (a `_retries` dict), never in a `{counter}` the LLM has to read and increment. Replace `Proceed to subtask X` / `Loop back to step Y` / `STOP` GOTOs, state-variable writes, and `IF`-on-`agent_action` dispatch with declarative slot-filling DAG transitions so the framework owns routing. Then rewrite the instruction to state the *goal*, not a transition table.

    *Configurable:* `options.I016.min_distinct_categories` (default 2), `options.I016.min_total` (default 4), `options.I016.min_strong_edges` (default 3).

=== "C — Callbacks"

    Rules in the `C` category check callback `python_code.py` files for naming conventions, correct signatures, and safe coding practices.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | C001 | `callback-fn-name` | Error | `Band 2 / OSI L5` | `Reliability` | Callback function name must match callback type |
    | C002 | `callback-args` | Error | `Band 2 / OSI L5` | `Reliability` | Callback must have correct argument count for its type |
    | C003 | `callback-camelcase` | Error | `Band 2 / OSI L5` | `Operational Excellence` | CES requires snake_case function names, not camelCase |
    | C004 | `callback-return-type` | Warning | `Band 2 / OSI L5` | `Reliability` | Model callbacks should return `LlmResponse`, not `dict` |
    | C005 | `callback-hardcoded-phrases` | Warning | `Band 2 / OSI L5` | `Performance` | Hardcoded phrase lists for intent detection |
    | C006 | `callback-bare-except` | Warning | `Band 2 / OSI L6a` | `Reliability` | Bare `except:` without logging swallows errors silently |
    | C007 | `callback-tool-naming` | Info | `Band 2 / OSI L5` | `Reliability` | Verify `tools.*` call uses correct naming convention |
    | C010 | `callback-python-syntax` | Error | `Band 2 / OSI L5` | `Reliability` | Callback Python file must have valid syntax |

    ---

    **C001 — callback-fn-name**

    Each callback type has a required entry function name. The platform looks for this specific function name when loading the callback.

    | Callback type | Required function name |
    |---------------|----------------------|
    | `before_model_callbacks` | `before_model_callback` |
    | `after_model_callbacks` | `after_model_callback` |
    | `before_agent_callbacks` | `before_agent_callback` |
    | `after_agent_callbacks` | `after_agent_callback` |
    | `before_tool_callbacks` | `before_tool_callback` |
    | `after_tool_callbacks` | `after_tool_callback` |

    *Fix:* Rename or add the entry function with the correct name.

    ---

    **C002 — callback-args**

    Each callback type has a required set of arguments. The platform passes specific objects; missing arguments cause runtime errors.

    | Callback type | Required arguments |
    |---------------|--------------------|
    | `before_model_callbacks` | `callback_context`, `llm_request` |
    | `after_model_callbacks` | `callback_context`, `llm_response` |
    | `before_agent_callbacks` | `callback_context` |
    | `after_agent_callbacks` | `callback_context` |
    | `before_tool_callbacks` | `tool`, `input`, `callback_context` |
    | `after_tool_callbacks` | `tool`, `input`, `callback_context`, `tool_response` |

    ---

    **C003 — callback-camelcase**

    CES requires all function names to be `snake_case`. Functions with camelCase names are silently ignored.

    *Triggers:* Any function definition using camelCase (e.g., `def injectContext():`).

    *Fix:* Rename to `inject_context`.

    ---

    **C004 — callback-return-type**

    Model callbacks (before/after model) should return `LlmResponse` or `None`, never a raw `dict`. Returning a dict causes unpredictable behavior.

    *Fix:* Use `return LlmResponse.from_parts(parts=[Part.from_text(text="...")])`.

    ---

    **C005 — callback-hardcoded-phrases**

    Hardcoded lists of phrases for intent detection in callbacks miss natural language variations. The LLM in the instruction is better at this.

    *Fix:* Keep intent detection in the instruction. Use callbacks for execution only.

    ---

    **C006 — callback-bare-except**

    A bare `except:` catches everything — including platform-internal exceptions that should propagate. Always catch specific exceptions or use `except Exception as e:` with logging.

    *Fix:* Replace `except:` with `except Exception as e: logging.error(...)`.

    ---

    **C010 — callback-python-syntax**

    Invalid Python syntax means the callback file can't be loaded. The platform silently fails to register callbacks with syntax errors.

    *Fix:* Fix the syntax error. Run `python -m py_compile python_code.py` locally to check.

=== "T — Tools"

    Rules in the `T` category check tool `python_code.py` files, JSON tool definitions, and voice turn-pacing bridges.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | T002 | `tool-docstring` | Warning | `Band 4 / OSI L6b` | `Operational Excellence` | Tool missing docstring |
    | T003 | `tool-type-hints` | Info | `Band 4 / OSI L6b` | `Reliability` | Tool function arguments lack type hints |
    | T004 | `tool-fn-name` | Warning | `Band 4 / OSI L4` | `Reliability` | Tool function name should match tool directory name |
    | T005 | `tool-high-cardinality` | Info | `Band 4 / OSI L6b` | `Reliability` | High-cardinality input arguments |
    | T006 | `tool-return-explosion` | Info | `Band 4 / OSI L6b` | `Cost` | Tool returning excessive data |
    | T008 | `tool-displayname-unreferenced` | Warning | `Band 4 / OSI L4` | `Cost` | Tool displayName not referenced by any agent |
    | T009 | `tool-kwargs-signature` | Error | `Band 4 / OSI L4` | `Reliability` | Tool function uses `**kwargs` |
    | T010 | `tool-python-syntax` | Error | `Band 4 / OSI L4` | `Reliability` | Tool Python file must have valid syntax |
    | T011 | `tool-none-default` | Error | `Band 4 / OSI L4` | `Reliability` | Tool parameter uses `None` as default value |
    | T012 | `tool-json-missing-description` | Error | `Band 4 / OSI L6b` | `Operational Excellence` | Tool JSON configuration must include description |
    | T013 | `tool-config-invalid` | Error | `Band 4 / OSI L4` | `Reliability` | Tool JSON configuration must be a valid JSON object/dictionary |
    | T014 | `composite-tool-pacing` | Warning | `Band 1 / OSI L2` | `Performance` | Tool docstring or description must include a conversational pacing directive to prevent dead air |

    ---

    **T002 — tool-docstring**

    CES uses the tool's docstring as its description for the LLM. Without a docstring, the LLM has to guess when to call the tool based on its name alone.

    *Fix:* Add a descriptive docstring explaining when and how the LLM should use the tool.

    ---

    **T004 — tool-fn-name**

    The tool function name should match the directory name for consistency. CES uses the function name for certain routing.

    ---

    **T005 — tool-high-cardinality**

    Arguments like `timestamp`, `latitude/longitude`, or internal `session_id`/`request_id` values are hard for users to express, especially in voice mode.

    *Fix:* Design arguments that a human can express naturally (e.g., `region`, `category`, `last_n_days`).

    ---

    **T009 — tool-kwargs-signature**

    The platform silently drops tools that use `**kwargs` in their signature. Always use explicit named parameters.

    *Fix:* Replace `def my_tool(**kwargs):` with `def my_tool(param1: str = '', param2: str = '') -> dict:`.

    ---

    **T011 — tool-none-default**

    Parameters with `None` as a default value cause the platform to silently drop the tool during import. Use type-appropriate defaults instead.

    *Fix:* Change `def tool(name: str = None):` to `def tool(name: str = '') -> dict:`.

    ---

    **T012 — tool-json-missing-description**

    Tool JSON configuration must include `pythonFunction.description` or `widgetTool.description`. The LLM relies on this description to know when to call the tool.

    *Triggers:* The description field is missing or empty in the tool's JSON configuration.

    *Fix:* Add a 'description' key within the 'pythonFunction' or 'widgetTool' object in the tool's JSON file.

=== "E — Evals"

    Rules in the `E` category check golden and simulation YAML files.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | E001 | `eval-yaml-parse` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Eval file must be valid YAML |
    | E002 | `eval-structure` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Golden eval must have `conversations:` key |
    | E003 | `eval-tool-exists` | Warning | `Band 4 / OSI L4` | `Reliability` | Tool calls in evals must reference existing tools |
    | E004 | `eval-session-param` | Warning | `Band 2 / OSI L5` | `Operational Excellence` | Session parameters should reference known variables |
    | E005 | `eval-duplicate-keys` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Duplicate YAML keys (second overwrites first) |
    | E006 | `eval-no-mocks` | Warning | `Band 2 / OSI L5` | `Operational Excellence` | Golden with `tool_calls` but no `session_parameters` |
    | E007 | `eval-agent-not-string` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Golden `agent` field must be a plain string, not a dict |
    | E008 | `eval-missing-agent` | Warning | `Band 3 / OSI L7` | `Reliability` | Golden turn has `user` but no `agent` field |
    | E009 | `eval-sim-missing-tags` | Warning | `Band 1 / OSI L1` | `Operational Excellence` | Simulation eval missing `tags` field |
    | E010 | `eval-tool-test-wrong-key` | Error | `Band 4 / OSI L4` | `Operational Excellence` | Tool test uses `test_cases` instead of `tests` |
    | E011 | `eval-invalid-match-type` | Error | `Band 4 / OSI L6b` | `Operational Excellence` | Invalid `$matchType` value in golden `tool_calls` |
    | E012 | `eval-shadow-structure` | Error | `Band 1 / OSI L2` | `Operational Excellence` | Shadow eval needs `conversation_id` and non-empty `expectations`, a valid `replay_mode`, and only known keys (unknown keys are warnings) |

    ---

    **E006 — eval-no-mocks**

    A golden that exercises tool calls without mock session parameters will make real API calls during testing — unpredictable and slow. Provide `common_session_parameters` to mock tool responses.

    ---

    **E008 — eval-missing-agent**

    Every turn with a `user` field must have a corresponding `agent` field. Without it, the platform reports "UNEXPECTED RESPONSE" for any agent response, causing false failures.

    ---

    **E010 — eval-tool-test-wrong-key**

    SCRAPI expects tool test YAML to use `tests:` as the top-level list key. Using `test_cases:` causes all tests to be silently skipped — SCRAPI returns 0 tests with no error.

    *Fix:* Rename `test_cases:` to `tests:`.

    ---

    **E011 — eval-invalid-match-type**

    Valid `$matchType` values are: `ignore`, `semantic`, `contains`, `regexp`. Common typos like `regex` (should be `regexp`) or `fuzzy` (should be `semantic`) silently fall back to exact matching.

    ---

    **E012 — eval-shadow-structure**

    Applies to YAML files under `evals/shadows/`. Each shadow eval needs a `conversation_id` and at least one natural-language expectation. `replay_mode` (on the case or in `config:`) must be `hybrid` or `exact`. Unknown keys in a case or in the `config:` block are reported as warnings with a *did you mean* suggestion, because ShadowEvals would otherwise ignore them silently (for example `session_params` instead of `session_parameters`).

=== "A — Config"

    Rules in the `A` category check `app.json`, agent JSON configuration files, and Gemini Composite acoustic voice settings.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | A001 | `config-json-parse` | Error | `Band 1 / OSI L1` | `Reliability` | Config file must be valid JSON |
    | A002 | `config-required-fields` | Error | `Band 1 / OSI L1` | `Operational Excellence` | Config must have required fields (`name`, `displayName`) |
    | A003 | `config-tool-exists` | Error | `Band 3 / OSI L3` | `Reliability` | Agent config references a non-existent tool |
    | A004 | `config-missing-instruction` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Agent directory must have an `instruction.txt` file |
    | A005 | `config-root-missing-end-session` | Error | `Band 3 / OSI L3` | `Reliability` | Root agent must have `end_session` tool |
    | A006 | `config-root-agent` | Error | `Band 3 / OSI L3` | `Reliability` | App config must have a valid `rootAgent` pointing to an existing agent directory |
    | A007 | `composite-audio-profile` | Error | `Band 1 / OSI L1` | `Performance` | Validates `synthesizeSpeechConfigs`, Audio Profile, and Director's Notes for Gemini Composite (legacy V1 only; `v2` clears Director's Notes) |
    | A008 | `composite-accent-specification` | Warning | `Band 1 / OSI L1` | `Performance` | Ensures natural language accent names instead of raw locale codes in Director's Notes (legacy V1 only; `v2` clears Director's Notes) |
    | A009 | `composite-multilang-coverage` | Error | `Band 1 / OSI L1` | `Performance` | Audits multi-language voice parity across declared languages for Gemini Composite (legacy V1 only; `v2` clears Director's Notes) |
    | A010 | `composite-sampling-temperature` | Warning | `Band 1 / OSI L1` | `Performance` | Enforces `modelSettings.temperature = 1.0` for Gemini Composite to prevent acoustic repetition deadlocks |

    ---

    **A003 — config-tool-exists**

    An agent JSON that lists a tool that doesn't exist in the app results in the agent having no access to that tool — silently, with no error from the platform.

    ---

    **A005 — config-root-missing-end-session**

    The root agent must have `end_session` in its `tools` array. Without it, the agent can never cleanly terminate a conversation.

    ---

    **A006 — config-root-agent**

    App configuration must have a valid `rootAgent` field in `app.json` pointing to an existing agent directory. It must be camelCase, a string, and the corresponding agent directory and JSON file must exist.

    *Triggers:* `root_agent` (snake_case) is used instead of `rootAgent`, `rootAgent` is missing or not a string, or the referenced agent directory/JSON is missing.

    *Fix:* Add or fix the `rootAgent` field in `app.json` and ensure the agent directory and config file exist.

=== "S — Structure"

    Rules in the `S` category perform cross-reference checks between multiple files.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | S002 | `agent-tool-references` | Error | `Band 3 / OSI L7` | `Reliability` | Instruction references tools not in the agent's tool list |
    | S003 | `callback-file-references` | Error | `Band 2 / OSI L5` | `Security` | Agent JSON references callback files that don't exist |
    | S004 | `child-agent-references` | Error | `Band 3 / OSI L3` | `Reliability` | Agent JSON references child agents that don't exist |
    | S005 | `strict-agent-path-layout` | Error | `Band 3 / OSI L3` | `Operational Excellence` | Agent config paths must be app-relative and prefixed with `agents/{agent_name}/` |
    | S006 | `strict-tool-path-layout` | Error | `Band 4 / OSI L4` | `Operational Excellence` | Tool config paths must be app-relative and prefixed with `tools/{tool_name}/` |
    | S007 | `sub-agent-single-parent` | Error | `Band 3 / OSI L3` | `Performance` | Sub-agents must have at most one parent agent (tree constraint) |
    | S008 | `singleton-guardrail-types` | Error | `Band 2 / OSI L6a` | `Security` | At most one guardrail of each singleton type (`llmPromptSecurity`) per app |

    These rules are similar to I009 and I013 but operate at a higher level, cross-referencing the agent JSON config against the local file system.

    ---

    **S008 — singleton-guardrail-types**

    The platform allows only one guardrail of certain types per app — currently `llmPromptSecurity`. The console UI enforces the limit, but the App Import API used by `cxas push` does not, so pushing duplicates leaves the app un-editable in the console ("Too many llm prompt security guardrails, the limit is 1").

    *Triggers:* More than one directory under `guardrails/` declares the same singleton guardrail type (`llmPromptSecurity` or `llm_prompt_security`).

    *Fix:* Keep a single guardrail of that type and remove the others.

=== "V — Schema"

    Rules in the `V` category validate resource configs against the CES protobuf schema. These catch structural issues that would cause API errors on push.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | V001 | `schema-app-valid` | Error | `Band 1 / OSI L1` | `Reliability` | App config conforms to CES proto schema |
    | V002 | `schema-agent-valid` | Error | `Band 3 / OSI L3` | `Reliability` | Agent config conforms to CES proto schema |
    | V003 | `schema-tool-valid` | Error | `Band 4 / OSI L4` | `Reliability` | Tool config conforms to CES proto schema |
    | V004 | `schema-toolset-valid` | Error | `Band 4 / OSI L4` | `Reliability` | Toolset config conforms to CES proto schema |
    | V005 | `schema-guardrail-valid` | Error | `Band 2 / OSI L6a` | `Security` | Guardrail config conforms to CES proto schema |
    | V006 | `schema-evaluation-valid` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Evaluation config conforms to CES proto schema |
    | V007 | `schema-eval-expectation-valid` | Error | `Band 3 / OSI L7` | `Operational Excellence` | Evaluation expectation config conforms to CES proto schema |

    Schema validation catches issues like unknown fields, wrong types, and missing required fields — before you try to push and get a cryptic API error.

=== "V — Variables"

    Rules in the `V` category (Variables) validate state, instruction, and eval references against declared variables in `app.json` `variableDeclarations`.

    | ID | Name | Default | Layer | WAF Pillar | Description |
    |----|------|---------|-------|------------|-------------|
    | V100 | `variable-declared` | Error | `Band 2/3/4` *(by file)* | `Reliability` | State reads/writes (or eval refs) must reference a declared variable |
    | V101 | `variable-type-match` | Error | `Band 2/3/4` *(by file)* | `Reliability` | State write must match the declared schema type for the variable |
    | V102 | `nested-property-exists` | Error | `Band 2/3/4` *(by file)* | `Reliability` | Dotted state keys must resolve to declared OBJECT properties |
    | V103 | `no-stale-flat-var-regression` | Warning | `Band 2/3/4` *(by file)* | `Reliability` | Reference matches a nested property — likely a stale flat-variable reference |
    | V104 | `instruction-variable-ref` | Error | `Band 3 / OSI L7` | `Reliability` | Instruction {var} references must resolve to a declared variable |

    ---

    **V100 — variable-declared**

    State reads/writes in callbacks/tools, or variable references in evals, must target a declared variable in `app.json`'s `variableDeclarations`. Undeclared variables cause silent failures at runtime.

    *Triggers:* Dotted path or flat name referenced but not found in `variableDeclarations`.

    *Fix:* Declare the variable under `variableDeclarations` in `app.json`.

    ---

    **V101 — variable-type-match**

    State writes in callbacks or tools must assign values that match the declared schema type for that variable.

    *Triggers:* Literal type of assigned value (e.g. integer) doesn't match the declared schema type (e.g. STRING).

    *Fix:* Assign a value of the correct type, or update the schema in `app.json`.

    ---

    **V102 — nested-property-exists**

    Dotted state keys must resolve to declared properties of `OBJECT` type variables.

    *Triggers:* Accessing a nested property (e.g. `obj.prop`) where `obj` is not an `OBJECT`, or `prop` is not declared in `obj`'s properties schema.

    *Fix:* Add the property to the schema in `app.json` or correct the code reference.

    ---

    **V103 — no-stale-flat-var-regression**

    Detects top-level state references or instruction template references that match a nested property, indicating a likely stale flat-variable reference that should be updated to the nested path.

    *Triggers:* Accessing `child` when it has been migrated to `parent.child` in the schema.

    *Fix:* Replace the flat reference with the dotted path (e.g. `parent.child`).

    ---

    **V104 — instruction-variable-ref**

    Instruction template references (e.g. `{var}`) must resolve to a declared variable. Unresolved references silently resolve to empty strings at runtime.

    *Triggers:* `{var}` reference where `var` is not declared or doesn't resolve.

    *Fix:* Declare the variable in `app.json` or fix the reference.
