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

"""Tests for 4-Band Voice & Agentic WAF layer enrichment and reporting."""

from __future__ import annotations

import csv
import inspect
import json
from pathlib import Path
from typing import Any

from cxas_scrapi.utils import reporting


def test_enrich_eval_results_and_band_health_calculation() -> None:
    """Verify waf_layer enrichment and 4-band health across all eval types."""
    golden_results: list[dict[str, Any]] = [
        {
            "name": "golden_greeting_pass",
            "passed": True,
            "turns": [{"index": 1, "semantic_score": 4, "comparisons": []}],
            "expectations": [],
        },
        {
            "name": "golden_transfer_missed",
            "passed": False,
            "turns": [
                {
                    "index": 1,
                    "semantic_score": 4,
                    "comparisons": [
                        {
                            "outcome": "FAIL",
                            "type": "transfer",
                            "expected": "billing_agent",
                            "actual": "(missed)",
                        }
                    ],
                }
            ],
            "expectations": [],
        },
    ]
    sim_results: list[dict[str, Any]] = [
        {
            "name": "sim_audio_pass",
            "passed": True,
            "run": 1,
            "modality": "audio",
            "step_details": [{"goal": "Check status", "status": "Completed"}],
            "expectation_details": [],
        },
        {
            "name": "sim_dead_air_fail",
            "passed": False,
            "run": 1,
            "modality": "audio",
            "has_dead_air": True,
            "step_details": [],
            "expectation_details": [
                {
                    "expectation": "Mask slow lookup without dead air",
                    "status": "Not Met",
                }
            ],
        },
        {
            "name": "sim_cognitive_goal_fail",
            "passed": False,
            "run": 1,
            "modality": "audio",
            "step_details": [
                {
                    "goal": "Confirm refund policy eligibility",
                    "status": "Failed",
                    "justification": "Agent gave wrong policy window",
                }
            ],
            "expectation_details": [],
        },
    ]
    tool_results: list[dict[str, Any]] = [
        {
            "name": "tool_lookup_ok",
            "tool": "lookup_order",
            "passed": True,
            "status": "PASSED",
            "latency_ms": 120,
            "errors": "",
        },
        {
            "name": "tool_dto_pii_leak",
            "tool": "get_customer_profile",
            "passed": False,
            "status": "FAILED",
            "latency_ms": 95,
            "errors": "DTO schema exposed raw pii secret field",
        },
    ]
    callback_results: list[dict[str, Any]] = [
        {
            "name": "cb_after_tool_scrub_fail",
            "agent": "root_agent",
            "callback_type": "after_tool_callback",
            "passed": False,
            "status": "FAILED",
            "error": "Failed to redact PII in after_tool payload",
        },
    ]

    reporting.enrich_eval_results_waf_layers(
        golden_results=golden_results,
        sim_results=sim_results,
        tool_results=tool_results,
        callback_results=callback_results,
        golden_modality="text",
        sim_modality="audio",
    )

    # Check per-item WAF enrichment
    assert golden_results[0]["waf_layer"]["macro_band"] == 3
    assert golden_results[0]["waf_layer"]["osi_layer"] == "L7"
    assert golden_results[1]["waf_layer"]["macro_band"] == 3
    assert golden_results[1]["waf_layer"]["osi_layer"] == "L3"
    assert (
        golden_results[1]["waf_layer"]["full_tag"]
        == "[Band 3 / OSI L3 • Reliability]"
    )

    assert sim_results[0]["waf_layer"]["macro_band"] == 1
    assert sim_results[0]["waf_layer"]["osi_layer"] == "L1"
    assert sim_results[1]["waf_layer"]["macro_band"] == 1
    assert sim_results[1]["waf_layer"]["osi_layer"] == "L2"
    assert sim_results[1]["waf_layer"]["waf_pillar"] == "Performance"
    # Cognitive goal failure in audio sim routes to Band 3 / OSI L7
    assert sim_results[2]["waf_layer"]["macro_band"] == 3
    assert sim_results[2]["waf_layer"]["osi_layer"] == "L7"

    assert tool_results[0]["waf_layer"]["macro_band"] == 4
    assert tool_results[0]["waf_layer"]["osi_layer"] == "L4"
    assert tool_results[1]["waf_layer"]["macro_band"] == 4
    assert tool_results[1]["waf_layer"]["osi_layer"] == "L6b"
    assert tool_results[1]["waf_layer"]["waf_pillar"] == "Security"

    assert callback_results[0]["waf_layer"]["macro_band"] == 2
    assert callback_results[0]["waf_layer"]["osi_layer"] == "L6a"
    assert callback_results[0]["waf_layer"]["waf_pillar"] == "Security"

    band_health = reporting.compute_band_health(
        golden_results=golden_results,
        sim_results=sim_results,
        tool_results=tool_results,
        callback_results=callback_results,
        golden_modality="text",
        sim_modality="audio",
    )
    assert [b["band"] for b in band_health] == [1, 2, 3, 4]

    # Band 1: 1 pass (sim_audio_pass), 1 fail (sim_dead_air_fail) -> 50% warn
    assert band_health[0]["passed"] == 1
    assert band_health[0]["total"] == 2
    assert band_health[0]["failed_count"] == 1
    assert band_health[0]["pass_rate"] == 50.0
    assert band_health[0]["status_cls"] == "warn"
    assert band_health[0]["target_tab"] == "sims"

    # Band 2: 0 pass, 1 fail (cb_after_tool_scrub_fail) -> 0% fail
    assert band_health[1]["passed"] == 0
    assert band_health[1]["total"] == 1
    assert band_health[1]["failed_count"] == 1
    assert band_health[1]["pass_rate"] == 0.0
    assert band_health[1]["status_cls"] == "fail"
    assert band_health[1]["target_tab"] == "unit"
    assert band_health[1]["target_section"] == "section-callbacks"

    # Band 3: 1 pass, 2 fails (golden_transfer_missed + sim_cognitive_goal_fail)
    assert band_health[2]["passed"] == 1
    assert band_health[2]["total"] == 3
    assert band_health[2]["failed_count"] == 2
    assert band_health[2]["status_cls"] == "fail"
    assert band_health[2]["target_tab"] == "goldens"

    # Band 4: 1 pass, 1 fail -> 50% warn
    assert band_health[3]["passed"] == 1
    assert band_health[3]["total"] == 2
    assert band_health[3]["failed_count"] == 1
    assert band_health[3]["status_cls"] == "warn"
    assert band_health[3]["target_tab"] == "unit"
    assert band_health[3]["target_section"] == "section-tools"


def test_band_health_na_and_latency_fallback() -> None:
    """Verify 'na' status on empty bands and Band 1 suite_pl fallback."""
    empty_health = reporting.compute_band_health()
    assert len(empty_health) == 4
    for band_entry in empty_health:
        assert band_entry["total"] == 0
        assert band_entry["passed"] == 0
        assert band_entry["failed_count"] == 0
        assert band_entry["pass_rate"] is None
        assert band_entry["status_cls"] == "na"

    suite_pl = {
        "primary": {"spoken_count": 4, "over_2s_pct": 0.0},
        "filler_table": [
            {"tool_name": "lookup_order", "calls": 3, "unmasked_calls": 0},
            {"tool_name": "slow_crm", "calls": 2, "unmasked_calls": 1},
        ],
    }
    pl_health = reporting.compute_band_health(
        golden_results=[{"name": "g_ok", "passed": True}],
        suite_pl=suite_pl,
    )
    assert pl_health[0]["total"] == 2
    assert pl_health[0]["passed"] == 1
    assert pl_health[0]["status_cls"] == "warn"
    assert pl_health[0]["target_tab"] == "latency"
    assert pl_health[2]["status_cls"] == "pass"


def test_html_report_renders_band_strip_and_waf_badges(tmp_path: Path) -> None:
    """Verify rendered HTML includes 4-Band strip and [Band X / OSI LY badges."""
    out_html = tmp_path / "combined_report.html"
    golden_results = [
        {
            "name": "golden_pass_case",
            "passed": True,
            "turns": [{"index": 1, "semantic_score": 4, "comparisons": []}],
            "expectations": [],
        },
        {
            "name": "golden_routing_fail_case",
            "passed": False,
            "turns": [
                {
                    "index": 1,
                    "semantic_score": 4,
                    "comparisons": [
                        {
                            "outcome": "FAIL",
                            "type": "transfer",
                            "expected": "fraud_specialist",
                            "actual": "(missed)",
                        }
                    ],
                }
            ],
            "expectations": [],
        },
    ]
    sim_results = [
        {
            "name": "sim_dead_air_case",
            "passed": False,
            "run": 1,
            "goals": "0/1",
            "expectations": "0/1",
            "turns": 2,
            "has_dead_air": True,
            "step_details": [
                {
                    "goal": "Keep caller engaged",
                    "success_criteria": "Speak filler before slow tool",
                    "status": "Failed",
                }
            ],
            "expectation_details": [],
        }
    ]
    tool_results = [
        {
            "name": "tool_timeout_case",
            "tool": "orders_api",
            "passed": False,
            "status": "FAILED",
            "latency_ms": 5000,
            "errors": "503 timeout calling upstream API",
        }
    ]
    callback_results = [
        {
            "name": "cb_auth_gate_case",
            "agent": "billing_agent",
            "callback_type": "before_agent_callback",
            "passed": False,
            "status": "FAILED",
            "error": "Auth gate failed to block unauthenticated caller",
        }
    ]

    reporting.generate_combined_html_report(
        golden_results=golden_results,
        sim_results=sim_results,
        tool_results=tool_results,
        callback_results=callback_results,
        output_path=str(out_html),
        golden_modality="text",
        sim_modality="audio",
    )

    html = out_html.read_text(encoding="utf-8")

    # 1. 4-Band Architecture Health strip & cards
    assert "4-Band Voice &amp; Agentic Architecture Health" in html
    assert 'class="band-health-strip"' in html
    assert "Acoustic Wire &amp; Turn Pacing" in html
    assert "Deterministic Python Harness" in html
    assert "Cognitive Brain &amp; Routing Topology" in html
    assert "Tool Transport &amp; Clean Data Facade" in html
    assert "5+1 CXAS Evaluation Pyramid" in html
    assert "Pyramid L5: Simulation &amp; Audio Evals" in html
    assert "Pyramid L2: Callback Tests" in html
    assert "Pyramid L3-L4: Turn &amp; Golden Evals" in html
    assert "Pyramid L1: Tool Tests" in html

    # 2. Inline [Band X / OSI LY • Pillar] badges on failed eval rows
    assert "waf-layer-badge" in html
    assert "[Band 3 / OSI L3 • Reliability]" in html
    assert "[Band 1 / OSI L2 • Performance]" in html
    assert "[Band 4 / OSI L4 • Reliability]" in html
    assert "[Band 2 / OSI L5 • Security]" in html

    # Passed golden card header should not carry a failure WAF pill
    pass_card_idx = html.index('id="eval-golden-golden_pass_case"')
    pass_card_header = html[pass_card_idx : pass_card_idx + 320]
    assert "waf-layer-badge" not in pass_card_header


def test_latency_tables_render_subtle_waf_layer_badges() -> None:
    """Verify Table A and Table B in render_suite_latency show layer badges."""
    suite_pl = {
        "primary": {
            "p50_ms": 1100.0,
            "p90_ms": 1900.0,
            "avg_ms": 1200.0,
            "over_2s_pct": 10.0,
        },
        "total_turns": 10,
        "conversations_count": 2,
        "optimization_targets": [
            {
                "component": "before_model_callback",
                "type": "Callback",
                "agent": "root_agent",
                "calls": 10,
                "calls_per_turn": 1.0,
                "avg_ms": 85.0,
                "p50_ms": 80.0,
                "p90_ms": 110.0,
                "share_of_pl_pct": 7.0,
                "avg_pl_impact_ms": 85.0,
            },
            {
                "component": "lookup_account",
                "type": "Tool / API",
                "agent": "root_agent",
                "calls": 5,
                "calls_per_turn": 0.5,
                "avg_ms": 640.0,
                "p50_ms": 600.0,
                "p90_ms": 920.0,
                "share_of_pl_pct": 26.0,
                "avg_pl_impact_ms": 320.0,
            },
        ],
        "filler_table": [
            {
                "tool_name": "lookup_account",
                "agent": "root_agent",
                "calls": 5,
                "masked_calls": 2,
                "unmasked_calls": 3,
                "avg_ms": 640.0,
                "p90_ms": 920.0,
                "pl_unmasked_ms": 2300.0,
                "status": "Unmasked",
                "status_cls": "fail",
            }
        ],
    }

    drawer_html = reporting._render_suite_latency_drawer(suite_pl)
    assert "[Band 2 / OSI L5–L6a]" in drawer_html
    assert "[Band 4 / OSI L4]" in drawer_html
    assert "[Band 1 / OSI L2 • Rule T014]" in drawer_html


def test_csv_and_json_exports_include_waf_layer_columns(
    tmp_path: Path,
) -> None:
    """Verify CSV and JSON exports contain macro_band, osi_layer, waf_pillar."""
    evals_dir = tmp_path / "evals_out"
    evals_dir.mkdir()

    (evals_dir / "sim_results.json").write_text(
        json.dumps(
            [
                {
                    "name": "sim_voice_check",
                    "passed": False,
                    "error": "High TTFA latency spike",
                }
            ]
        ),
        encoding="utf-8",
    )
    (evals_dir / "ces_results.json").write_text(
        json.dumps([{"name": "golden_policy", "passed": True, "turns": []}]),
        encoding="utf-8",
    )
    (evals_dir / "tool_results.json").write_text(
        json.dumps(
            [
                {
                    "test_name": "tool_contract_test",
                    "tool": "fetch_balance",
                    "status": "FAILED",
                    "latency (ms)": 45,
                    "errors": "DTO null schema violation",
                }
            ]
        ),
        encoding="utf-8",
    )
    (evals_dir / "callback_results.json").write_text(
        json.dumps(
            [
                {
                    "test_name": "cb_guard_test",
                    "agent_name": "root",
                    "callback_type": "before_agent",
                    "status": "PASSED",
                    "error_message": "",
                }
            ]
        ),
        encoding="utf-8",
    )

    csv_path = reporting.generate_combined_report_from_dir(
        output_dir=str(evals_dir),
        report_format="csv",
        modality="audio",
    )
    assert isinstance(csv_path, str)
    with open(csv_path, encoding="utf-8", newline="") as f:
        rows = list(csv.DictReader(f))

    assert len(rows) == 4
    by_name = {r["name"]: r for r in rows}
    assert {"macro_band", "osi_layer", "waf_pillar"} <= set(rows[0].keys())

    assert by_name["sim_voice_check"]["macro_band"] == "1"
    assert by_name["sim_voice_check"]["osi_layer"] == "L1"
    assert by_name["sim_voice_check"]["waf_pillar"] == "Performance"

    assert by_name["tool_contract_test"]["macro_band"] == "4"
    assert by_name["tool_contract_test"]["osi_layer"] == "L6b"
    assert by_name["tool_contract_test"]["waf_pillar"] == "Security"

    assert by_name["cb_guard_test"]["macro_band"] == "2"
    assert by_name["cb_guard_test"]["osi_layer"] == "L5"
    assert by_name["cb_guard_test"]["waf_pillar"] == "Security"

    json_path = reporting.generate_combined_report_from_dir(
        output_dir=str(evals_dir),
        report_format="json",
        modality="text",
    )
    assert isinstance(json_path, str)
    payload = json.loads(Path(json_path).read_text(encoding="utf-8"))

    assert len(payload["summary"]["band_health"]) == 4
    assert len(payload["rows"]) == 4
    for row in payload["rows"]:
        assert "macro_band" in row
        assert "osi_layer" in row
        assert "waf_pillar" in row

    for section in ("golden", "simulation", "tool", "callback"):
        item = payload["results"][section][0]
        assert "waf_layer" in item
        assert "macro_band" in item
        assert "osi_layer" in item
        assert "waf_pillar" in item


def test_waf_reporting_helpers_contain_no_inline_html_or_svg() -> None:
    """Guardrail: new WAF reporting helpers must be pure Python data only."""
    for fn in (
        reporting._extract_eval_failure_signals,
        reporting.build_eval_waf_layer,
        reporting.enrich_eval_results_waf_layers,
        reporting.compute_band_health,
        reporting.build_combined_eval_rows,
        reporting.generate_combined_csv_report,
    ):
        src = inspect.getsource(fn)
        for forbidden in ("<div", "<span", "<table", "<tr", "<td", "<svg"):
            assert forbidden not in src, f"Found {forbidden} in {fn.__name__}"
