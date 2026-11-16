/**
 * Google Slides Apps Script Generator — 5-Slide Engineering Architecture Brief
 * ("Google Cloud Well-Architected Framework for GECX Voice Agents")
 *
 * Usage in Google Slides:
 *   1. Open any 16:9 Google Slides presentation -> Extensions -> Apps Script
 *   2. Paste this file and run `buildVoiceWafSlides()`
 */

const SLIDE_DECK_SPEC = [
  {
    badge: "SLIDE 1 OF 5 • ARCHITECTURAL FOUNDATION & CONVERSATIONAL TELEPHONY PHYSICS",
    badgeColor: "#60A5FA",
    title: "Google Cloud Well-Architected Framework (WAF): Foundation & 5 Core Pillars",
    subtitle: "System Design foundation across the 5 WAF pillars — and why live full-duplex telephony breaks stateless cloud tolerances.",
    leftBorder: "#4285F4",
    leftTitle: "🏛️ System Design Foundation & 5 Core WAF Pillars",
    leftBullets: [
      "• System Design Foundation: Modular boundaries, clear ownership, stateful session contracts & critical-path budgets.",
      "• 1. Operational Excellence: Deterministic static/semantic linting, automated CI regression gates & trace telemetry.",
      "• 2. Security, Privacy & Compliance: Zero-trust auth gates, least-privilege DTO projection & PII redaction.",
      "• 3. Reliability: Bounded client timeouts, stateful circuit breakers, safe state initialization & graceful fallbacks.",
      "• 4. Performance & 5. Cost Optimization: Sub-second turn pacing, parallel tools, lean payloads & minimal LLM passes."
    ],
    rightBorder: "#38BDF8",
    rightTitle: "📞 Stateless Cloud Apps vs. Live Full-Duplex Telephony",
    rightBullets: [
      "• Stateless Request/Response Cloud Apps (HTTP / REST / Web Chat):",
      "  - Tolerate 2–3s tail jitter behind visual spinners, UI skeletons, and half-duplex retry loops.",
      "• Live Full-Duplex Telephony (PSTN / SIP / SBC / RTP / BidiRunSession):",
      "  - Operates under strict human conversational physics: ~200 ms natural turn gap and <1,200 ms wire ceiling.",
      "  - Beyond 1,200 ms of silence, callers say 'Hello?!', trigger SBC barge-in collisions, or hang up."
    ],
    footer: "Google Cloud WAF Foundation • Stateful Full-Duplex Voice Physics (~200 ms Turn Gap • <1,200 ms Wire Ceiling)",
    notes: "Architectural Rationale for Engineering Leadership: Every enterprise system rests on Google Cloud's System Design foundation and its 5 Well-Architected pillars (Operational Excellence, Security, Reliability, Performance, Cost). The critical insight for voice engineering is why stateless cloud patterns fail on a live phone call: HTTP apps hide 2–3s of jitter behind a spinner, whereas full-duplex telephony across PSTN/SIP/SBC/RTP/BidiRunSession runs on ~200 ms human turn gaps and a strict <1,200 ms wire ceiling."
  },
  {
    badge: "SLIDE 2 OF 5 • AI/ML PERSPECTIVE & STATEFUL VOICE AGENT ADAPTATION",
    badgeColor: "#60A5FA",
    title: "The AI/ML & Agentic Lens for Google Cloud WAF",
    subtitle: "Adapting all 5 WAF pillars to stateful, tool-calling voice agents and the official 5+1 CXAS Evaluation Pyramid.",
    leftBorder: "#10B981",
    leftTitle: "⚡🛡️⚙️💰 Performance, Security, Reliability & Cost Lenses",
    leftBullets: [
      "• Performance ('Count Passes, Not Tokens'): ~465 ms median single Gemini pass; 116–236 ms 0-pass callback turns; 5 Levers of Speed (Mask, Cut, Overlap, Start Early, Shrink).",
      "• Security (Two-Plane Deterministic): 0–1 ms contentFilter + <5 ms Python Auth Gate / 0-token Guardrail Handoff Intercept vs. ~300 ms/rule inline llmPolicy; state-bound IDOR prevention.",
      "• Reliability: Bounded <=5s tool SLAs inside 30s platform harpoon, stateful circuit breakers, [Part.from_text(text='')] silent close (no parts=[] deaf sessions), _initialized guard & C005 (never regex raw speech — 11% accuracy).",
      "• Cost: 2,400 -> 32 token Clean DTO compression (-2.4 s / -5 passes), 0-token Turn 1 greeting (~150 ms) & Single-Agent default (<=15 tools)."
    ],
    rightBorder: "#A855F7",
    rightTitle: "📋 Operational Excellence: Official 5+1 CXAS Eval Pyramid",
    rightBullets: [
      "• L0 — Static & Semantic Lint: cxas lint (60+ structural checks) + cxas llm-lint.",
      "• L1 — Callback Unit Tests: pytest (<200 ms, 0 tokens) for Auth Gates, scrubbers & state guards.",
      "• L2 — :executeTool Tests: Live schema contracts, Clean DTO shapes & <=5s SLAs (0 LLM tokens).",
      "• L3 Turn Evals -> L4 Platform Goldens -> L5 Audio Sims & Guardrail Evals (13 noise presets).",
      "• Release Governance: Ephemeral PR gates via cxas ci-test + 4-Gate Graduation Process (Sandbox -> Staging -> Shadow/Canary -> Prod)."
    ],
    footer: "AI/ML WAF Perspective • 'Count Passes, Not Tokens' + Two-Plane Security + Official 5+1 Evaluation Pyramid",
    notes: "Architectural Rationale for Engineering Leadership: Applying Google Cloud's AI/ML Perspective sharpens all 5 WAF pillars for stateful voice agents: Performance counts passes (~465 ms/pass) via the 5 Levers of Speed; Security enforces Two-Plane deterministic guardrails in 0–5 ms instead of ~300 ms/rule inline llmPolicy; Reliability bounds tools at <=5s inside the 30s harpoon and bans raw speech regex (11% accuracy); Cost compresses 2,400 -> 32 token DTOs; and Operational Excellence governs releases with the 5+1 CXAS Evaluation Pyramid, cxas ci-test PR gates, and the 4-Gate Graduation Process."
  },
  {
    badge: "SLIDE 3 OF 5 • CANONICAL REFERENCE STACK (CXAS / SCRAPI FIELD GUIDE)",
    badgeColor: "#38BDF8",
    title: "GECX Voice Best Practices on CXAS / SCRAPI ('TCP/IP over L1–L7 Agentic OSI')",
    subtitle: "4 Horizontal Macro-Bands mapping cxas_app folders, L1–L7 Agentic OSI layers, and the 5+1 Evaluation Pyramid.",
    leftBorder: "#38BDF8",
    leftTitle: "🟦🟩 Bands 1 & 2: Acoustic Wire & Python Harness",
    leftBullets: [
      "• Band 1 (app.json • OSI L1–L2 • Eval L5): gemini-composite-v2 + sonic-bolt — clear legacy Director's Notes ('instruction': '', 'voiceInstructionMode': 'NO_INSTRUCTION') for 3.84x inline <prosody rate='64%'><warm> dynamics.",
      "  - <Affective Delivery> + scoped speech normalization in global_instruction.txt, BidiRunSession SessionConfig-first law, Callback (0.26 s) & Named Two-Part Reply (0.73 s) fillers.",
      "• Band 2 (callbacks/ • OSI L5–L6a • Eval L1): _initialized guard + ANI prefetch, 0-token greeting (~150 ms) & [Part.from_text('')] silent close.",
      "  - Synchronous before_model Auth Gate (LlmResponse), <2 ms after_tool scrubber & 0–1 ms contentFilter."
    ],
    rightBorder: "#F97316",
    rightTitle: "🟪🟧 Bands 3 & 4: Cognitive Brain & Tool Transport",
    rightBullets: [
      "• Band 3 (agents/ • OSI L3 & L7 • Eval L0/L3/L4): Single-Agent default (<=15 tools) vs. earned Hub-and-Spoke (735 ms callback transfer) + native end_session.",
      "  - Canonical PIF XML (<role>..<taskflow>, ${current_date}); strict Gate 1–2 Incubating boundary (Self-Steering, Slot Filling DAG).",
      "• Band 4 (tools/ • OSI L4 & L6b • Eval L2): Typed -> dict returns, zero None defaults (T011), pooled ces_requests & async_tools (PARALLEL).",
      "  - 2,400 -> 32 token Clean DTOs, self-healing agent_action envelopes (T001), bounded 5s SLA / 0.14s Remote-Job polling."
    ],
    footer: "1-to-1 Symmetry: cxas_app Directory (app.json, callbacks/, agents/, tools/) ↔ OSI Layer Pair ↔ 5+1 Eval Tier",
    notes: "Architectural Rationale for Engineering Leadership: The TCP/IP-over-OSI stack gives every team 4 clean horizontal Macro-Bands matching the exact folders of a cxas_app while preserving L1–L7 diagnostic precision. Note the Composite v2 standard in Band 1: clearing legacy Director's Notes ('instruction': '', 'voiceInstructionMode': 'NO_INSTRUCTION') unlocks 3.84x expressive prosody dynamic range via inline angle-bracket tags."
  },
  {
    badge: "SLIDE 4 OF 5 • ANTI-PATTERN FORENSICS (LAB 3: failure_workshop_agent)",
    badgeColor: "#F87171",
    title: "Poorly Architected Voice Agent (failure_workshop_agent): Diagram & Failures",
    subtitle: "10 Static Lint Errors • 17 Warnings • 0/6 Chaos Branches Survived — Compounding breaches onto the live phone wire.",
    leftBorder: "#EF4444",
    leftTitle: "❌ 4-Band Broken Topology (Breach Flow: Band 4 -> Wire)",
    leftBullets: [
      "• [Band 4 Breach — tools/] Unbounded 35s hang, infinite 503 retries, raw DB secrets, CRM override & None values pour into context.",
      "        ⬇  Unvalidated Fault & Secret Cascade  ⬇",
      "• [Band 3 Breach — agents/] 6-line flat prompt obeys $500 CRM injection, guesses $25.00 fee on None & lacks end_session.",
      "        ⬇  Unguarded Hallucination & Policy Bypass  ⬇",
      "• [Band 2 Breach — callbacks/] Miswired callback returns raw dict (C004); zero PII scrubbing; leaks billing & SSN unauthenticated.",
      "        ⬇  💥 BREACHED WIRE: 6.30 s+ Dead Air • 30s Harpoon Drop • PII Leaked"
    ],
    rightBorder: "#EF4444",
    rightTitle: "🔍 Verbatim Lab 3 Failure Examples (10E, 17W, 0/6 Chaos)",
    rightBullets: [
      "• Band 1: temperature: 0.2 repetition deadlock (A010), bargeInAwareness: false, 0 spoken fillers (T014) -> 6.30 s+ dead air.",
      "• Band 2: Missing/broken callback wiring (V002/S003, returns raw dict C004); Branch 0 leaks $142.85 + ssn_last_four: '9921' to UNAUTHENTICATED.",
      "• Band 3: 6-line flat prompt (I006/I014), missing end_session (A005), obeys $500 CRM prompt injection, hallucinates $25.00 fee on None.",
      "• Band 4: Branch 1 35s hang > 30s Platform Harpoon drops call; Branch 2 infinite 503 loop (retry_allowed: True); Branch 3 leaks SECRET_KEY_998877_PROD_DB; Branch 4 raw injection; Branch 5 raw {'fee_amount': None}."
    ],
    footer: "Lab 3 Broken Baseline: uv run cxas lint Catches 10 Errors & 17 Warnings Statically in Milliseconds",
    notes: "Architectural Rationale for Engineering Leadership: Lab 3's failure_workshop_agent demonstrates what happens when teams treat voice like a stateless web chatbot. Across 10 lint errors, 17 warnings, and 6 chaos branches: Band 1 deadlocks at temperature 0.2 with 6.30 s+ dead air; Band 2 returns a raw dict (C004) and leaks $142.85 + SSN '9921' to UNAUTHENTICATED callers; Band 3 obeys a $500 CRM injection and hallucinates a $25.00 fee; and Band 4's 35s hang hits the 30s Platform Harpoon and drops the call."
  },
  {
    badge: "SLIDE 5 OF 5 • PRODUCTION TARGET STATE (success_workshop_agent + v2 STANDARD)",
    badgeColor: "#34D399",
    title: "Well-Architected Voice Agent (success_workshop_agent + v2): Diagram & Fixes",
    subtitle: "0 Static Lint Errors • 0 Warnings • 6/6 Chaos Branches Contained — Deterministic shields protecting the <1,200 ms wire.",
    leftBorder: "#10B981",
    leftTitle: "✅ 4-Band Hardened Defense Stack (Shielded <1,200 ms Wire)",
    leftBullets: [
      "• 🛡️ [Band 4 Shield — tools/] 5s SLA timeout + attempt >= 2 breaker + 32-token Clean DTO + UNTRUSTED & NULL envelopes.",
      "        ⬇  Sanitized, Self-Healing Deterministic Payloads  ⬇",
      "• 🛡️ [Band 3 Shield — agents/] Single-Agent PIF XML (<role>, <constraints>, <error_protocol>, ${current_date}) + end_session.",
      "        ⬇  Grounded Policy & Zero Hallucination  ⬇",
      "• 🛡️ [Band 2 Shield — callbacks/] _initialized guard + <5 ms LlmResponse 403 Auth Gate + <2 ms PII scrubber + 0–1 ms contentFilter.",
      "        ⬇  ⚡ PROTECTED <1,200 ms WIRE: Composite v2 + 0.26s/0.73s Fillers"
    ],
    rightBorder: "#10B981",
    rightTitle: "🛠️ Verbatim Fixes & cxas Tooling (0E, 0W, 6/6 Chaos)",
    rightBullets: [
      "• Band 1: gemini-composite-v2 + sonic-bolt (temp: 1.0, instruction: '', NO_INSTRUCTION, <Affective Delivery>, <prosody rate='64%'><warm>) + Two-Part Reply (0.73 s) / Callback Filler (0.26 s).",
      "• Band 2: _initialized guard + before_model_callback returning LlmResponse (403_UNAUTHORIZED_ACCESS on Branch 0) + <2 ms after_tool_callback regex/PII scrubber + 0–1 ms contentFilter.",
      "• Band 3: Single-Agent PIF XML (<role>, <constraints>, <error_protocol>, ${current_date}) + end_session + strict zero-hallucination groundedness.",
      "• Band 4: Branch 1 5s SLA -> BILLING_GATEWAY_TIMEOUT + submit_support_ticket; Branch 2 attempt >= 2 -> 503_CIRCUIT_BREAKER_OPEN; Branch 3 Clean Store DTO (2,400 -> 32 tokens); Branch 4 UNTRUSTED_EXTERNAL_DATA; Branch 5 NULL_LEDGER_DATA."
    ],
    footer: "Verified End-to-End via Automated Toolchain: uv run cxas lint --band • uv run cxas evals report • uv run cxas ci-test",
    notes: "Architectural Rationale for Engineering Leadership: Comparing Slide 4 with Slide 5 shows defense-in-depth across every band: Band 1 upgrades to gemini-composite-v2 + sonic-bolt with NO_INSTRUCTION and 0.26 s / 0.73 s spoken fillers; Band 2 enforces _initialized, a <5 ms LlmResponse 403 Auth Gate on Branch 0, and a <2 ms PII scrubber; Band 3 enforces Single-Agent PIF XML and zero-hallucination groundedness; and Band 4 enforces a 5s SLA, 2-strike circuit breaker, and 32-token Clean DTOs—verified via cxas lint --band, cxas evals report, and cxas ci-test."
  }
];

function getTextStyleCompat_(textRange) {
  return typeof textRange.getTextStyle === "function"
    ? textRange.getTextStyle()
    : textRange.getStyle();
}

function buildVoiceWafSlides() {
  const pres = SlidesApp.getActivePresentation();

  SLIDE_DECK_SPEC.forEach((spec) => {
    const slide = pres.appendSlide(SlidesApp.PredefinedLayout.BLANK);
    slide.getBackground().setSolidFill("#070C18");

    // Top Kicker Badge
    const badgeBox = slide.insertTextBox(spec.badge, 28, 14, 664, 18);
    getTextStyleCompat_(badgeBox.getText())
      .setForegroundColor(spec.badgeColor)
      .setFontFamily("Roboto")
      .setFontSize(8.5)
      .setBold(true);

    // Slide Title & Subtitle
    const headerBox = slide.insertTextBox(spec.title + "\n" + spec.subtitle, 28, 30, 664, 48);
    const headerText = headerBox.getText();
    getTextStyleCompat_(headerText)
      .setForegroundColor("#F8FAFC")
      .setFontFamily("Roboto")
      .setFontSize(13.5)
      .setBold(true);
    if (typeof headerText.getRange === "function") {
      const subStart = spec.title.length + 1;
      const fullLen = spec.title.length + 1 + spec.subtitle.length;
      getTextStyleCompat_(headerText.getRange(subStart, fullLen))
        .setForegroundColor("#94A3B8")
        .setFontSize(9.5)
        .setBold(false);
    }

    // Left Card
    const leftContent = spec.leftTitle + "\n\n" + spec.leftBullets.join("\n");
    const leftBox = slide.insertTextBox(leftContent, 28, 84, 324, 282);
    leftBox.getFill().setSolidFill("#0F172A");
    leftBox.getBorder().setWeight(1.25).getLineFill().setSolidFill(spec.leftBorder);
    const leftText = leftBox.getText();
    getTextStyleCompat_(leftText)
      .setForegroundColor("#E2E8F0")
      .setFontFamily("Roboto")
      .setFontSize(8.8)
      .setBold(false);
    if (typeof leftText.getRange === "function") {
      getTextStyleCompat_(leftText.getRange(0, spec.leftTitle.length))
        .setForegroundColor("#FFFFFF")
        .setFontSize(10.2)
        .setBold(true);
    }

    // Right Card
    const rightContent = spec.rightTitle + "\n\n" + spec.rightBullets.join("\n");
    const rightBox = slide.insertTextBox(rightContent, 368, 84, 324, 282);
    rightBox.getFill().setSolidFill("#0F172A");
    rightBox.getBorder().setWeight(1.25).getLineFill().setSolidFill(spec.rightBorder);
    const rightText = rightBox.getText();
    getTextStyleCompat_(rightText)
      .setForegroundColor("#E2E8F0")
      .setFontFamily("Roboto")
      .setFontSize(8.8)
      .setBold(false);
    if (typeof rightText.getRange === "function") {
      getTextStyleCompat_(rightText.getRange(0, spec.rightTitle.length))
        .setForegroundColor("#FFFFFF")
        .setFontSize(10.2)
        .setBold(true);
    }

    // Bottom Verification / Anchor Footer Bar
    const footerBox = slide.insertTextBox(spec.footer, 28, 372, 664, 20);
    footerBox.getFill().setSolidFill("#111B31");
    footerBox.getBorder().setWeight(0.75).getLineFill().setSolidFill("#233352");
    getTextStyleCompat_(footerBox.getText())
      .setForegroundColor("#94A3B8")
      .setFontFamily("Roboto")
      .setFontSize(8.2)
      .setBold(true);

    // Speaker Notes
    slide.getNotesPage().getSpeakerNotesShape().getText().setText(spec.notes);
  });
}
