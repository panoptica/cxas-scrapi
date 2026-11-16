/**
 * Google Slides Apps Script Generator — 5-Slide Engineering Architecture Brief for GECX Leadership & Engineering
 * ("Layered Voice Architecture & Agentic Well-Architected")
 *
 * Usage in Google Slides:
 *   1. Open any Google Slides deck -> Extensions -> Apps Script
 *   2. Paste this file and run `buildVoiceWafSlides()`
 */

const SLIDE_DECK_SPEC = [
  {
    badge: "SLIDE 1 OF 5 • FIRST PRINCIPLE (OSI LAYER 1)",
    title: "Why We Are Doing This Whole Thing: The <1,200ms Physical Voice Wire",
    subtitle: "In chat, a 3s delay is a spinner. On a live phone wire (PSTN/SIP/SBC/RTP), >1,200ms is dead air.",
    leftTitle: "❌ Why Chat-Agent Patterns Fail on the Wire",
    leftBullets: [
      "• Legacy 3-Stage Pipeline: ASR (400ms) + LLM (500ms) + TTS (300ms) = 1,500–2,500ms (blows wire budget before tools run).",
      "• Inline LLM Supervisors: Adding +800ms per pre/post safety check causes callers to yell 'Hello?!' or barge in.",
      "• Unbounded Backend Calls (Lab 3 Branch 1): 35s billing hang hits the 30s Platform Harpoon and drops the call.",
      "• Silence During Tool Calls: 0 spoken filler phrases (Rule T014 violation) leaves 5s–35s of dead air on the line."
    ],
    rightTitle: "✅ The GECX Physical Wire Contract (<1,200ms)",
    rightBullets: [
      "• Gemini Composite Native Speech-to-Speech: <800ms Time-to-First-Audio (TTFA) with temperature=1.0 (Rule A010).",
      "• Sub-5ms Python Guardrail Callbacks: Enforce Auth Gates & PII scrubbing in Python (<5ms) instead of slow LLM hops.",
      "• Rule T014 Spoken Filler Bridges: 'Tell them, then do it' masks a bounded 5,000ms backend tool SLA.",
      "• SBC Barge-In Buffer Flush: bargeInAwareness=true flushes playback immediately when the caller speaks."
    ],
    notes: "Architectural Rationale for Engineering Leadership: Stop presenting GECX patterns as a flat checklist. Every architectural choice we make—Composite speech-to-speech, <5ms Python callbacks, spoken tool fillers, and 5s tool timeouts—exists to protect the 1,200ms human conversational ceiling on the physical telephony wire."
  },
  {
    badge: "SLIDE 2 OF 5 • THE LAYERED ARCHITECTURE MODEL",
    title: "The Mental Model: 'TCP/IP over OSI' for Voice Agents (4 Bands × L1–L7)",
    subtitle: "4 Engineering Macro-Bands (matching cxas_app folders & F1 Testing Pyramid) containing L1–L7 Agentic OSI.",
    leftTitle: "🏗️ Bottom-Up Stack: Bands 1 & 2 (Wire & Harness)",
    leftBullets: [
      "• Band 1 — Acoustic Wire & Turn Pacing (app.json):",
      "  - OSI L1 (Physical Wire): Composite <800ms TTFA, temp=1.0 (A010), Director's Notes (A007/A009), SBC Barge-In.",
      "  - OSI L2 (Data Link / Framing): Rule T014 spoken filler bridges + 3-strike VAD silence detection.",
      "• Band 2 — Deterministic Python Harness (callbacks/ — <5ms):",
      "  - OSI L5 (Session & Auth Gate): before_agent state seed + synchronous before_model LlmResponse gate.",
      "  - OSI L6a (Post-Tool Scrubber): after_tool_callback <2ms firewall stripping tokens, PII & injections."
    ],
    rightTitle: "🧠 Bottom-Up Stack: Bands 3 & 4 (Brain & Tools)",
    rightBullets: [
      "• Band 3 — Cognitive Brain & Routing Topology (agents/):",
      "  - OSI L3 (Network Routing): Shallow Spoke-and-Hub (<500ms hop) + native end_session (A005).",
      "  - OSI L7 (Cognitive XML Policy): <role>, <persona>, <constraints>, <taskflow>, {current_date}, Groundedness.",
      "• Band 4 — Tool Transport & Clean Data Facade (tools/ — ≤5s SLA):",
      "  - OSI L4 (Transport SLA): Bounded 5s Client SLA (vs. 30s Harpoon) + Stateful 503 Circuit Breaker (attempt >= 2).",
      "  - OSI L6b (Clean DTO Facade): 'It can't leak what it never saw' + UNTRUSTED_EXTERNAL_DATA + NULL_LEDGER_DATA."
    ],
    notes: "Architectural Rationale for Engineering Leadership: When reconciling architectural simplicity with forensic precision, we adopt a 'TCP/IP over OSI' hybrid model. Visually it provides 4 clean bands matching the 4 folders of a cxas_app, while giving teams the L1–L7 OSI diagnostic layers ('Branch 1 is a Layer 4 Transport Timeout; Branch 3 is a Layer 6 DTO Leak')."
  },
  {
    badge: "SLIDE 3 OF 5 • LAB 3 CHAOS & GOOGLE CLOUD AGENTIC WAF",
    title: "Lab 3 ('Broken Agent') Mapped to the 4 Bands & Agentic WAF Pillars",
    subtitle: "Every bug in failure_workshop_agent (10 lint errors, 17 warnings, 6 chaos branches) is a specific layer failure.",
    leftTitle: "❌ Bad Agent Anti-Patterns (failure_workshop_agent)",
    leftBullets: [
      "• [Band 1 / L1–L2] temp=0.2 deadlock (A010), bargeIn=false, 0 T014 spoken bridges -> Dead air on wire.",
      "• [Band 2 / L5–L6a] Miswired callback returns raw dict (V002/S003); Branch 0 leaks $142.85 + SSN '9921'.",
      "• [Band 3 / L3 & L7] 6-line flat prompt (I001–I014), missing end_session (A005), obeys $500 override, guesses $25 fee.",
      "• [Band 4 / L4] Branch 1 hangs 35s (>30s Harpoon drops call); Branch 2 loops 503 5+ times (IAL token burn).",
      "• [Band 4 / L6b] Branch 3 leaks SECRET_KEY_998877_PROD_DB; Branch 4 raw CRM injection; Branch 5 raw {'fee': None}."
    ],
    rightTitle: "✅ Well-Architected Fix (success_workshop_agent) & WAF",
    rightBullets: [
      "• [Band 1 • WAF Performance] Composite temp=1.0, Director's Notes, SBC flush + mandatory T014 spoken bridge.",
      "• [Band 2 • WAF Security & Cost] Two-Plane Auth Gate (before_model LlmResponse) + <2ms after_tool scrubber.",
      "• [Band 3 • WAF Ops & Reliability] Structured XML Contract + Strict Zero-Hallucination Groundedness + end_session.",
      "• [Band 4 • WAF Reliability & Cost] 5s Client SLA (BILLING_GATEWAY_TIMEOUT -> Ticket) + Circuit Breaker (attempt >= 2).",
      "• [Band 4 • WAF Security] Clean Store DTO + UNTRUSTED_EXTERNAL_DATA tag + NULL_LEDGER_DATA error envelope."
    ],
    notes: "Architectural Rationale for Engineering Leadership: This transforms Lab 3 from an overwhelming bug hunt into a structured architectural diagnostic across the 5 Google Cloud Agentic WAF pillars (Performance, Security, Reliability, Cost, Operational Excellence)."
  },
  {
    badge: "SLIDE 4 OF 5 • THE 1-TO-1 QUALITY FLYWHEEL",
    title: "1-to-1 Alignment: 4 Architecture Bands ↔ 4-Layer F1 Testing Pyramid",
    subtitle: "Push every test as far down the pyramid as it will go: catch L4–L7 bugs in milliseconds for zero tokens.",
    leftTitle: "🏗️ Architectural Macro-Band (What We Build)",
    leftBullets: [
      "• 🟧 Band 4: Tool Transport & Clean DTO Facade (OSI L4 & L6b — tools/*/python_code.py)",
      "• 🟩 Band 2: Deterministic Python Harness (OSI L5 & L6a — callbacks/ & session.state)",
      "• 🟪 Band 3: Cognitive XML Brain & Routing (OSI L3 & L7 — agents/*/instruction.txt)",
      "• 🟦 Band 1: Physical Voice Wire & Turn Pacing (OSI L1 & L2 — app.json & Audio Profile)"
    ],
    rightTitle: "🏎️ F1 Testing Pyramid Layer (How AGY Verifies It)",
    rightBullets: [
      "• 🔧 Pyramid L1 — Workshop Dyno (50ms • 0 Tokens): pytest test_tools.py + uv run cxas lint",
      "• 🔩 Pyramid L2 — Bench Assembly (200ms • 0 Tokens): pytest test_callbacks.py (Auth Gates & Scrubbers)",
      "• 🛞 Pyramid L3 — Sim-Rig Chicane (~5s • Low Tokens): uv run cxas llm-lint + Frozen Turn & Golden Evals",
      "• 🏁 Pyramid L4 — 50-Lap Grand Prix (~30s • Audio): cxas evals report --modality audio --background-noise"
    ],
    notes: "Architectural Rationale for Engineering Leadership: The 4 Macro-Bands map 1-to-1 to our 4-Layer F1 Testing Pyramid. Engineers never waste 30-second audio simulation tokens debugging a null pointer or broken callback path that Pyramid L1/L2 catches in 200ms."
  },
  {
    badge: "SLIDE 5 OF 5 • ANTIGRAVITY (AGY) AUTOMATION & NEXT STEPS",
    title: "How AGY + gecx Skills Make Manual Work Redundant",
    subtitle: "The entire 4-Band lifecycle is automated across cxas-scrapi, .agents/skills/, and delivery_kit/.",
    leftTitle: "🚀 How AGY Automates the FDE / CE / Instructor Job",
    leftBullets: [
      "• 7-Gate Pipeline (run-7-gates.py + cxas-agent-foundry): PRD -> TDD -> Scaffold -> Lint -> 4 Eval Suites -> Auditor.",
      "• Dual Linter Gate: uv run cxas lint (60+ static checks) + cxas llm-lint via autonomous lint-fixer subagent.",
      "• Voice & Migration Skills: cxas-composite-voice-agent-optimizer (Band 1 auto-fix) & cxas-dfcx-migration.",
      "• Production Flywheel: cxas-loss-analysis clusters CCAI Insights losses -> cxas-sim-eval regression suites."
    ],
    rightTitle: "🎯 3 Recommended Architectural Decisions",
    rightBullets: [
      "1. Adopt the 4-Band (TCP/IP over L1–L7 OSI) Stack as the canonical GECX mental model in Bootcamp Ch 1, 4 & 6.",
      "2. Tag cxas lint & cxas evals report output by Band & OSI Layer (e.g., [Band 1 / OSI L1 - Wire], [Band 4 / OSI L6b - DTO]).",
      "3. Ship lab3_agentic_waf_visualizer.html alongside chaos_workshop_runner.py as the standard Lab 3 visual companion."
    ],
    notes: "Architectural Rationale for Engineering Leadership: Here is the key takeaway for Engineering. Antigravity + our skills already automate building, linting, and testing all 4 bands. By aligning CLI output and Bootcamp visuals around these 4 Bands (L1–L7 OSI), every CE, partner, and customer gets one unified language from the physical wire up."
  }
];

function buildVoiceWafSlides() {
  const pres = SlidesApp.getActivePresentation();
  SLIDE_DECK_SPEC.forEach((spec) => {
    const slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    slide.getBackground().setSolidFill("#0B0F19");

    // Top Badge & Title
    const headerBox = slide.insertTextBox(spec.badge + "\n" + spec.title + "\n" + spec.subtitle, 28, 18, 664, 78);
    const headerText = headerBox.getText();
    headerText.getStyle().setForegroundColor("#F8FAFC").setFontFamily("Roboto").setFontSize(16).setBold(true);

    // Left Card
    const leftBox = slide.insertTextBox(spec.leftTitle + "\n\n" + spec.leftBullets.join("\n\n"), 28, 108, 322, 265);
    leftBox.getFill().setSolidFill("#131B2E");
    leftBox.getBorder().setWeight(1).getLineFill().setSolidFill("#EF4444");
    leftBox.getText().getStyle().setForegroundColor("#E2E8F0").setFontFamily("Roboto").setFontSize(10.5);

    // Right Card
    const rightBox = slide.insertTextBox(spec.rightTitle + "\n\n" + spec.rightBullets.join("\n\n"), 368, 108, 324, 265);
    rightBox.getFill().setSolidFill("#131B2E");
    rightBox.getBorder().setWeight(1).getLineFill().setSolidFill("#10B981");
    rightBox.getText().getStyle().setForegroundColor("#E2E8F0").setFontFamily("Roboto").setFontSize(10.5);

    // Speaker Notes
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(spec.notes);
  });
}
