# Copyright 2026 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""GECX "TCP/IP over OSI" Hybrid Voice Architecture & WAF Layer Taxonomy.

Maps lint rules, semantic prompt checks, and evaluation outcomes onto:
  1. 4 Engineering Macro-Bands (aligned to the 5+1 CXAS Evaluation Pyramid)
  2. L1-L7 Agentic OSI Diagnostic Layers
  3. 5 Google Cloud Agentic Well-Architected Framework (WAF) Pillars
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

# -- Canonical WAF Pillars ----------------------------------------------------

WAF_PERFORMANCE = "Performance"
WAF_SECURITY = "Security"
WAF_RELIABILITY = "Reliability"
WAF_COST = "Cost"
WAF_OPS = "Operational Excellence"

WAF_PILLARS: tuple[str, ...] = (
    WAF_PERFORMANCE,
    WAF_SECURITY,
    WAF_RELIABILITY,
    WAF_COST,
    WAF_OPS,
)

_WAF_PILLAR_ALIASES: dict[str, str] = {
    "performance": WAF_PERFORMANCE,
    "perf": WAF_PERFORMANCE,
    "performance-optimization": WAF_PERFORMANCE,
    "security": WAF_SECURITY,
    "sec": WAF_SECURITY,
    "security-privacy": WAF_SECURITY,
    "reliability": WAF_RELIABILITY,
    "rel": WAF_RELIABILITY,
    "cost": WAF_COST,
    "cost-optimization": WAF_COST,
    "ops": WAF_OPS,
    "operational-excellence": WAF_OPS,
    "operational_excellence": WAF_OPS,
    "operational excellence": WAF_OPS,
}


def normalize_waf_pillar(value: str | None) -> str | None:
    """Normalize a CLI or config WAF pillar filter to its canonical name."""
    if not value:
        return None
    cleaned = value.strip().lower()
    if cleaned in _WAF_PILLAR_ALIASES:
        return _WAF_PILLAR_ALIASES[cleaned]
    msg = (
        f"Unknown WAF pillar '{value}'. Valid values: "
        "performance, security, reliability, cost, ops"
    )
    raise ValueError(msg)


# -- Canonical 5+1 CXAS Evaluation Pyramid -----------------------------------

EVAL_PYRAMID_LAYERS: dict[str, str] = {
    "L0": "Pyramid L0: Static Lint Gate (cxas lint / cxas llm-lint)",
    "L1": "Pyramid L1: Tool Tests (cxas test tools)",
    "L2": "Pyramid L2: Callback Tests (cxas test callbacks)",
    "L3": "Pyramid L3: Turn Evals (single-turn deterministic state)",
    "L4": "Pyramid L4: Golden Evals (multi-turn deterministic baseline)",
    "L5": "Pyramid L5: Simulation & Audio Evals (live wire & acoustic SNR)",
}


# -- Canonical 4 Engineering Macro-Bands -------------------------------------

MACRO_BANDS: dict[int, dict[str, Any]] = {
    1: {
        "band": 1,
        "name": "Acoustic Wire & Turn Pacing",
        "short_name": "Wire & Pacing",
        "osi_layers": "OSI L1\u2013L2",
        "artifact_scope": "app.json & Tool Pacing",
        "pyramid_layer": "Pyramid L5: Simulation & Audio Evals",
    },
    2: {
        "band": 2,
        "name": "Deterministic Python Harness",
        "short_name": "Python Harness",
        "osi_layers": "OSI L5\u2013L6a",
        "artifact_scope": "callbacks/ & session.state",
        "pyramid_layer": "Pyramid L2: Callback Tests",
    },
    3: {
        "band": 3,
        "name": "Cognitive Brain & Routing Topology",
        "short_name": "Brain & Routing",
        "osi_layers": "OSI L3 & L7",
        "artifact_scope": "agents/*/instruction.txt & routing",
        "pyramid_layer": "Pyramid L3-L4: Turn & Golden Evals",
    },
    4: {
        "band": 4,
        "name": "Tool Transport & Clean Data Facade",
        "short_name": "Tools & DTOs",
        "osi_layers": "OSI L4 & L6b",
        "artifact_scope": "tools/*/python_code.py",
        "pyramid_layer": "Pyramid L1: Tool Tests",
    },
}

OSI_LAYER_NAMES: dict[str, str] = {
    "L1": "Physical / Acoustic Wire",
    "L2": "Data Link / Turn Framing & Pacing",
    "L3": "Network / Agent Routing Topology",
    "L4": "Transport / Execution SLA & Circuit Breaker",
    "L5": "Session & Identity Gate",
    "L6a": "Presentation / Post-Tool Interceptor",
    "L6b": "Presentation / Clean DTO Facade",
    "L7": "Application / Cognitive XML Policy",
}


@dataclass(frozen=True)
class LayerMetadata:
    """Resolved Macro-Band, Agentic OSI Layer, and WAF Pillar metadata."""

    macro_band: int
    osi_layer: str
    waf_pillar: str

    @property
    def macro_band_name(self) -> str:
        return str(MACRO_BANDS[self.macro_band]["name"])

    @property
    def macro_band_short(self) -> str:
        return str(MACRO_BANDS[self.macro_band]["short_name"])

    @property
    def osi_name(self) -> str:
        return OSI_LAYER_NAMES.get(self.osi_layer, self.osi_layer)

    @property
    def pyramid_layer(self) -> str:
        return str(MACRO_BANDS[self.macro_band]["pyramid_layer"])

    def format_tag(self) -> str:
        """Format inline CLI tag, e.g. ``[Band 1 / OSI L1 • Performance]``."""
        return (
            f"[Band {self.macro_band} / OSI {self.osi_layer} • "
            f"{self.waf_pillar}]"
        )

    def format_short_badge(self) -> str:
        """Format compact badge label, e.g. ``Band 1 / OSI L1``."""
        return f"Band {self.macro_band} / OSI {self.osi_layer}"

    def to_dict(self) -> dict[str, Any]:
        """Serialize layer metadata for JSON/CSV/template consumption."""
        return {
            "macro_band": self.macro_band,
            "macro_band_name": self.macro_band_name,
            "osi_layer": self.osi_layer,
            "osi_name": self.osi_name,
            "waf_pillar": self.waf_pillar,
            "pyramid_layer": self.pyramid_layer,
        }


# ── Explicit Rule-ID → Layer Mapping ─────────────────────────────────────

_RULE_LAYER_MAP: dict[str, LayerMetadata] = {
    # Band 1: Acoustic Wire & Turn Pacing (OSI L1 & L2)
    "A001": LayerMetadata(1, "L1", WAF_RELIABILITY),
    "A002": LayerMetadata(1, "L1", WAF_OPS),
    "A007": LayerMetadata(1, "L1", WAF_PERFORMANCE),
    "A008": LayerMetadata(1, "L1", WAF_PERFORMANCE),
    "A009": LayerMetadata(1, "L1", WAF_PERFORMANCE),
    "A010": LayerMetadata(1, "L1", WAF_PERFORMANCE),
    "T014": LayerMetadata(1, "L2", WAF_PERFORMANCE),
    "V001": LayerMetadata(1, "L1", WAF_RELIABILITY),
    "E009": LayerMetadata(1, "L1", WAF_OPS),
    "E012": LayerMetadata(1, "L2", WAF_OPS),
    # Band 2: Deterministic Python Harness (OSI L5 & L6a)
    "C001": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "C002": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "C003": LayerMetadata(2, "L5", WAF_OPS),
    "C004": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "C005": LayerMetadata(2, "L5", WAF_PERFORMANCE),
    "C006": LayerMetadata(2, "L6a", WAF_RELIABILITY),
    "C007": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "C010": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "S003": LayerMetadata(2, "L5", WAF_SECURITY),
    "S008": LayerMetadata(2, "L6a", WAF_SECURITY),
    "V005": LayerMetadata(2, "L6a", WAF_SECURITY),
    "E004": LayerMetadata(2, "L5", WAF_OPS),
    "E006": LayerMetadata(2, "L5", WAF_OPS),
    # Band 3: Cognitive Brain & Routing Topology (OSI L3 & L7)
    "A003": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "A004": LayerMetadata(3, "L7", WAF_OPS),
    "A005": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "A006": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "I001": LayerMetadata(3, "L7", WAF_OPS),
    "I002": LayerMetadata(3, "L7", WAF_OPS),
    "I003": LayerMetadata(3, "L7", WAF_PERFORMANCE),
    "I004": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "I005": LayerMetadata(3, "L7", WAF_PERFORMANCE),
    "I006": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "I007": LayerMetadata(3, "L3", WAF_COST),
    "I008": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "I009": LayerMetadata(3, "L7", WAF_OPS),
    "I010": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "I011": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "I012": LayerMetadata(3, "L7", WAF_COST),
    "I013": LayerMetadata(3, "L7", WAF_OPS),
    "I014": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "I015": LayerMetadata(3, "L7", WAF_SECURITY),
    "I016": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "S002": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "S004": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "S005": LayerMetadata(3, "L3", WAF_OPS),
    "S007": LayerMetadata(3, "L3", WAF_PERFORMANCE),
    "V002": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "V006": LayerMetadata(3, "L7", WAF_OPS),
    "V007": LayerMetadata(3, "L7", WAF_OPS),
    "V104": LayerMetadata(3, "L7", WAF_RELIABILITY),
    "E001": LayerMetadata(3, "L7", WAF_OPS),
    "E002": LayerMetadata(3, "L7", WAF_OPS),
    "E005": LayerMetadata(3, "L7", WAF_OPS),
    "E007": LayerMetadata(3, "L7", WAF_OPS),
    "E008": LayerMetadata(3, "L7", WAF_RELIABILITY),
    # Band 4: Tool Transport & Clean Data Facade (OSI L4 & L6b)
    "S006": LayerMetadata(4, "L4", WAF_OPS),
    "T001": LayerMetadata(4, "L4", WAF_OPS),
    "T002": LayerMetadata(4, "L6b", WAF_OPS),
    "T003": LayerMetadata(4, "L6b", WAF_RELIABILITY),
    "T004": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "T005": LayerMetadata(4, "L6b", WAF_RELIABILITY),
    "T006": LayerMetadata(4, "L6b", WAF_COST),
    "T007": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "T008": LayerMetadata(4, "L4", WAF_COST),
    "T009": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "T010": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "T011": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "T012": LayerMetadata(4, "L6b", WAF_OPS),
    "T013": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "V003": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "V004": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "E003": LayerMetadata(4, "L4", WAF_RELIABILITY),
    "E010": LayerMetadata(4, "L4", WAF_OPS),
    "E011": LayerMetadata(4, "L6b", WAF_OPS),
}

_CATEGORY_FALLBACK_MAP: dict[str, LayerMetadata] = {
    "config": LayerMetadata(1, "L1", WAF_PERFORMANCE),
    "callbacks": LayerMetadata(2, "L5", WAF_RELIABILITY),
    "instructions": LayerMetadata(3, "L7", WAF_OPS),
    "structure": LayerMetadata(3, "L3", WAF_OPS),
    "evals": LayerMetadata(3, "L7", WAF_OPS),
    "schema": LayerMetadata(3, "L3", WAF_RELIABILITY),
    "tools": LayerMetadata(4, "L4", WAF_RELIABILITY),
}


def resolve_rule_layer(
    rule_id: str,
    category: str = "",
    file_path: str = "",
) -> LayerMetadata:
    """Resolve Macro-Band, OSI Layer, and WAF Pillar for a lint rule/result."""
    rid = (rule_id or "").strip().upper()
    cat = (category or "").strip().lower()
    norm_path = (file_path or "").replace("\\", "/").lower()

    # Multi-category variable rules (V100-V103) depend on artifact/category
    if rid in {"V100", "V101", "V102", "V103"}:
        is_tool = (
            cat == "tools"
            or "/tools/" in norm_path
            or norm_path.startswith("tools/")
        )
        if is_tool:
            return LayerMetadata(4, "L6b", WAF_RELIABILITY)
        if cat == "instructions" or norm_path.endswith("instruction.txt"):
            return LayerMetadata(3, "L7", WAF_RELIABILITY)
        return LayerMetadata(2, "L5", WAF_RELIABILITY)

    if rid in _RULE_LAYER_MAP:
        return _RULE_LAYER_MAP[rid]

    # Prefix heuristics for newly added rules
    if rid.startswith("A"):
        return LayerMetadata(1, "L1", WAF_PERFORMANCE)
    if rid.startswith("C"):
        return LayerMetadata(2, "L5", WAF_RELIABILITY)
    if rid.startswith("I"):
        return LayerMetadata(3, "L7", WAF_OPS)
    if rid.startswith("T"):
        return LayerMetadata(4, "L4", WAF_RELIABILITY)

    if cat in _CATEGORY_FALLBACK_MAP:
        return _CATEGORY_FALLBACK_MAP[cat]

    if "callback" in norm_path:
        return LayerMetadata(2, "L5", WAF_RELIABILITY)
    if "/tools/" in norm_path or norm_path.startswith("tools/"):
        return LayerMetadata(4, "L4", WAF_RELIABILITY)
    if "app.json" in norm_path:
        return LayerMetadata(1, "L1", WAF_PERFORMANCE)

    return LayerMetadata(3, "L7", WAF_OPS)


def resolve_llm_lint_layer(category: str = "") -> LayerMetadata:
    """Resolve layer metadata for ``cxas llm-lint`` semantic prompt findings."""
    cat = (category or "").strip().lower()
    if any(k in cat for k in ("voice", "audio", "pacing", "prosody", "style")):
        return LayerMetadata(1, "L1", WAF_PERFORMANCE)
    if any(k in cat for k in ("callback", "state", "auth", "guardrail")):
        return LayerMetadata(2, "L5", WAF_SECURITY)
    if any(k in cat for k in ("route", "routing", "handoff", "transfer")):
        return LayerMetadata(3, "L3", WAF_PERFORMANCE)
    if any(k in cat for k in ("tool", "dto", "schema", "payload")):
        return LayerMetadata(4, "L6b", WAF_RELIABILITY)
    if any(k in cat for k in ("security", "injection", "pii", "ground")):
        return LayerMetadata(3, "L7", WAF_SECURITY)
    return LayerMetadata(3, "L7", WAF_OPS)


def classify_eval_layer(
    eval_type: str,
    *,
    failure_reason: str = "",
    modality: str = "text",
    latency_ms: float | None = None,
    has_dead_air: bool = False,
) -> LayerMetadata:
    """Classify an evaluation run/failure into its Band / OSI / WAF layer."""
    etype = (eval_type or "").strip().lower()
    reason = (failure_reason or "").strip().lower()
    mod = (modality or "text").strip().lower()

    if etype in {"tool", "tool_test", "tools", "unit_tool"}:
        dto_keys = ("secret", "pii", "dto", "null", "untrusted", "schema")
        if any(k in reason for k in dto_keys):
            return LayerMetadata(4, "L6b", WAF_SECURITY)
        return LayerMetadata(4, "L4", WAF_RELIABILITY)

    if etype in {"callback", "callback_test", "callbacks", "unit_callback"}:
        scrub_keys = ("scrub", "redact", "after_tool", "pii", "secret")
        if any(k in reason for k in scrub_keys):
            return LayerMetadata(2, "L6a", WAF_SECURITY)
        return LayerMetadata(2, "L5", WAF_SECURITY)

    # Diagnostic override from failure reason signals across Goldens & Sims
    pacing_keys = ("dead air", "dead-air", "filler", "t014", "silence")
    if has_dead_air or any(k in reason for k in pacing_keys):
        return LayerMetadata(1, "L2", WAF_PERFORMANCE)

    wire_keys = (
        "ttfa",
        "barge",
        "acoustic",
        "naturalness",
        "prosody",
        "audio check",
    )
    if (latency_ms is not None and latency_ms > 2000.0) or any(
        k in reason for k in wire_keys
    ):
        return LayerMetadata(1, "L1", WAF_PERFORMANCE)

    transport_keys = ("timeout", "503", "circuit", "tool error", "harpoon")
    if any(k in reason for k in transport_keys):
        return LayerMetadata(4, "L4", WAF_RELIABILITY)

    harness_keys = (
        "callback",
        "auth gate",
        "403",
        "unauthenticated",
        "session.state",
    )
    if any(k in reason for k in harness_keys):
        return LayerMetadata(2, "L5", WAF_SECURITY)

    routing_keys = (
        "route",
        "sub-agent",
        "transfer",
        "handoff",
        "end_session",
    )
    if any(k in reason for k in routing_keys):
        return LayerMetadata(3, "L3", WAF_RELIABILITY)

    if mod == "audio" or etype in {"sim", "simulation", "simulations", "audio"}:
        audio_keys = ("audio", "voice", "latency", "noise")
        if reason and not any(k in reason for k in audio_keys):
            return LayerMetadata(3, "L7", WAF_RELIABILITY)
        return LayerMetadata(1, "L1", WAF_PERFORMANCE)

    return LayerMetadata(3, "L7", WAF_RELIABILITY)
