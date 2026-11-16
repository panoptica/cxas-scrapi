# cxas lint

`cxas lint` checks your app directory for best-practice violations, structural problems, and schema errors across 60+ rules, so you can catch issues in code review rather than at runtime.

## Usage

```
cxas lint [--app-dir DIR]
          [--model MODEL]
          [--model-only]
          [--fix]
          [--only CATEGORY]
          [--rule IDS]
          [--band {1,2,3,4}]
          [--waf-pillar {performance,security,reliability,cost,ops,operational-excellence}]
          [--json]
          [--list-rules]
          [--validate-only]
          [--agents NAMES]
          [--tools NAMES]
          [--agent DIR]
          [--tool DIR]
          [--toolset DIR]
          [--guardrail DIR]
          [--evaluation DIR]
          [--evaluation-expectations DIR]
```

## Options

| Option | Required | Default | Description |
|--------|----------|---------|-------------|
| `--app-dir DIR` | No | `.` (current directory) | Path to the root of the app directory to lint. The linter discovers the app structure automatically. |
| `--model MODEL` | No | Inferred from `app.json` | Target model identifier (e.g., `gemini-composite-v1`, `gemini-2.5-flash`) used to evaluate model-specific acoustic rules. |
| `--model-only` | No | `false` | Run only model-specific rules for the target model (excludes model-agnostic rules). |
| `--fix` | No | `false` | Print fix suggestions alongside each issue. Does not automatically modify files. |
| `--only CATEGORY` | No | — | Limit linting to a single category. See [Rule Categories](#rule-categories) below. |
| `--rule IDS` | No | — | Run only specific rules. Accepts a comma-separated list of rule IDs (e.g., `I003,C005`). |
| `--band {1,2,3,4}` | No | — | Filter rules and results by Engineering Macro-Band:<br>• `1` — Acoustic Wire & Turn Pacing (`OSI L1–L2`)<br>• `2` — Deterministic Python Harness (`OSI L5–L6a`)<br>• `3` — Cognitive Brain & Routing Topology (`OSI L3 & L7`)<br>• `4` — Tool Transport & Clean Data Facade (`OSI L4 & L6b`) |
| `--waf-pillar PILLAR` | No | — | Filter rules and results by Google Cloud Agentic Well-Architected Framework (WAF) pillar (case-insensitive): `performance`, `security`, `reliability`, `cost`, `ops` (or `operational-excellence`). |
| `--json` | No | `false` | Output results as a JSON array instead of the human-readable format. Useful for integrating with CI dashboards and custom reporters. |
| `--list-rules` | No | `false` | Print all available lint rules with their IDs, severities, `[Band X / OSI LY • Pillar]` tags, and descriptions, then exit. |
| `--validate-only` | No | `false` | Run only `structure`, `config`, and `schema` rules. Skips instruction quality and eval checks. |
| `--agents NAMES` | No | — | Discover and lint only the specified comma-separated agent names. |
| `--tools NAMES` | No | — | Discover and lint only the specified comma-separated tool names. |
| `--agent DIR` | No | — | Validate a single agent directory against the CES schema instead of linting the whole app. |
| `--tool DIR` | No | — | Validate a single tool directory. |
| `--toolset DIR` | No | — | Validate a single toolset directory. |
| `--guardrail DIR` | No | — | Validate a single guardrail directory. |
| `--evaluation DIR` | No | — | Validate a single evaluation directory. |
| `--evaluation-expectations DIR` | No | — | Validate a single evaluation expectations directory. |

## Rule Categories

| Category | Prefix | Description |
|----------|--------|-------------|
| `instructions` | `I` | Agent instruction quality, clarity, length, and formatting. |
| `callbacks` | `C` | Callback file structure, naming, and implementation patterns. |
| `tools` | `T` | Tool definition quality, parameter descriptions, pacing, and schema correctness. |
| `evals` | `E` | Evaluation structure, turn count, and expectation quality. |
| `config` | `A` | `app.json` and agent JSON configuration correctness, including Gemini Composite voice settings. |
| `structure` | `S` | Directory layout, cross-file references, and tree constraints. |
| `schema` | `V` | Protobuf schema (`V001`–`V007`) and declared variable schema (`V100`–`V104`) validation. |

## Output Format & Layer Diagnostics

Every lint finding is annotated with its [Hybrid Voice Architecture](../design-guide/agent-architecture.md#layered-voice-architecture-agentic-well-architected-framework-tcpip-over-osi) coordinates so teams can immediately see which engineering band, Agentic OSI layer, and Google Cloud WAF pillar is affected.

### Inline `[Band X / OSI LY • Pillar]` tag & 4-Band summary

In human-readable terminal output (and `cxas lint --list-rules`), each finding displays an inline **`[Band X / OSI LY • Pillar]`** badge, followed by a **4-Band summary breakdown** at the bottom of the report:

```text
  ✗ A010 [Band 1 / OSI L1 • Performance] app.json
    modelSettings.temperature should be 1.0 for Gemini Composite models
  ⚠ T014 [Band 1 / OSI L2 • Performance] tools/lookup_ledger/lookup_ledger.json
    Tool description lacks a spoken filler bridge directive to prevent dead air
  ✗ S003 [Band 2 / OSI L5 • Security] agents/root_agent/root_agent.json
    Referenced before_model_callback file does not exist
  ⚠ I016 [Band 3 / OSI L7 • Reliability] agents/root_agent/instruction.txt:14
    Instruction encodes a prose state machine — move retry counters to callbacks

  4-Band Architecture Summary:
    Band 1 (Acoustic Wire & Turn Pacing / OSI L1–L2)      : 1 error, 1 warning   [Pyramid L4: Audio Grand Prix]
    Band 2 (Deterministic Python Harness / OSI L5–L6a)    : 1 error, 0 warnings  [Pyramid L2: Callback Bench]
    Band 3 (Cognitive Brain & Routing / OSI L3 & L7)      : 0 errors, 1 warning  [Pyramid L3: Turn/Golden Chicane]
    Band 4 (Tool Transport & DTO Facade / OSI L4 & L6b)   : 0 errors, 0 warnings [Pyramid L1: Tool Dyno]
```

### JSON output fields (`--json`)

When running `cxas lint --json`, each issue object includes structured layer and WAF metadata alongside standard file and rule fields:

| JSON Field | Type | Example | Description |
|------------|------|---------|-------------|
| `macro_band` | `int` | `1` | Engineering Macro-Band number (`1`–`4`). |
| `macro_band_name` | `string` | `"Acoustic Wire & Turn Pacing"` | Canonical name of the Macro-Band. |
| `osi_layer` | `string` | `"L1"` | Agentic OSI diagnostic layer (`L1`, `L2`, `L3`, `L4`, `L5`, `L6a`, `L6b`, `L7`). |
| `osi_name` | `string` | `"Physical / Acoustic Wire"` | Descriptive title of the Agentic OSI layer. |
| `waf_pillar` | `string` | `"Performance"` | Google Cloud Agentic WAF pillar (`Performance`, `Security`, `Reliability`, `Cost`, `Operational Excellence`). |
| `pyramid_layer` | `string` | `"Pyramid L4: Audio Grand Prix"` | Corresponding 1-to-1 F1 Testing Pyramid verification tier. |

```json
[
  {
    "rule_id": "A010",
    "severity": "warning",
    "category": "config",
    "file": "app.json",
    "line": null,
    "message": "modelSettings.temperature should be 1.0 for Gemini Composite models",
    "macro_band": 1,
    "macro_band_name": "Acoustic Wire & Turn Pacing",
    "osi_layer": "L1",
    "osi_name": "Physical / Acoustic Wire",
    "waf_pillar": "Performance",
    "pyramid_layer": "Pyramid L4: Audio Grand Prix"
  }
]
```

## Examples

**Lint the current directory:**

```bash
cxas lint
```

**Lint a specific app directory and show fix suggestions:**

```bash
cxas lint --app-dir ./my-agent --fix
```

**Run only instruction-quality rules:**

```bash
cxas lint --only instructions
```

**Run specific rules by ID:**

```bash
cxas lint --rule I003,C005,S002
```

**Audit only Band 1 (Acoustic Wire & Turn Pacing / `OSI L1–L2`):**

```bash
cxas lint --band 1 --fix
```

**Filter checks by a Google Cloud Agentic WAF pillar:**

```bash
cxas lint --waf-pillar security
cxas lint --band 4 --waf-pillar reliability
```

**Output results as JSON (for CI dashboards or custom reporters):**

```bash
cxas lint --json
```

**List all available rules:**

```bash
cxas lint --list-rules
```

**Quick structural validation only (no instruction or eval checks):**

```bash
cxas lint --validate-only
```

**Validate a single agent directory:**

```bash
cxas lint --agent ./my-agent/agents/pilot
```

**Validate a single tool:**

```bash
cxas lint --tool ./my-agent/tools/get_account_balance
```

**Use in CI to fail the build on any lint issue:**

```bash
cxas lint --json | jq 'if length > 0 then error else empty end'
```

## Related Commands

- [`cxas llm-lint`](llm-lint.md) — AI-driven semantic prompt linter using Gemini. While `cxas lint` enforces deterministic structural, schema, and configuration rules across your directory tree, `cxas llm-lint` deeply analyzes the actual human language meaning, tone, persona consistency, and logical clarity of your sub-agent prompts.
- [`cxas init`](init.md) — Bootstrap a project with the skills and configs that help you write lint-clean agents.
- [`cxas push`](push.md) — Push your linted app to CX Agent Studio.
- [`cxas ci-test`](ci-test.md) — Full CI lifecycle (add `cxas lint` as a step before `cxas ci-test` for maximum coverage).
