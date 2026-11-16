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

"""Unit tests for Macro-Band, Agentic OSI Layer, and WAF Pillar linting."""

from __future__ import annotations

import argparse
import json
from typing import TYPE_CHECKING, Any
from unittest.mock import MagicMock, patch

import pytest

from cxas_scrapi.cli.app import app_lint
from cxas_scrapi.cli.llm_lint import (
    annotate_llm_lint_report,
    extract_llm_lint_findings,
    llm_lint,
)
from cxas_scrapi.cli.main import get_parser
from cxas_scrapi.utils.linter import (
    LintReport,
    LintResult,
    Rule,
    RuleRegistry,
    Severity,
    build_registry,
)
from cxas_scrapi.utils.waf_layers import (
    WAF_OPS,
    WAF_PERFORMANCE,
    WAF_RELIABILITY,
    WAF_SECURITY,
)

if TYPE_CHECKING:
    from pathlib import Path


# ── LintResult & Rule Layer Metadata ─────────────────────────────────────


def test_lint_result_str_includes_inline_layer_tag() -> None:
    result = LintResult(
        file="agents/root/instruction.txt",
        rule_id="I001",
        severity=Severity.ERROR,
        message="Missing required XML tag: <role>",
    )
    rendered = str(result)
    assert rendered == (
        "  [E] agents/root/instruction.txt [I001] "
        "[Band 3 / OSI L7 • Operational Excellence] "
        "Missing required XML tag: <role>"
    )


def test_lint_result_str_with_line_and_band1_tag() -> None:
    result = LintResult(
        file="app.json",
        rule_id="A007",
        severity=Severity.WARNING,
        message="Barge-in pacing threshold",
        line=12,
    )
    rendered = str(result)
    assert "[W] app.json:12 [A007]" in rendered
    assert "[Band 1 / OSI L1 • Performance]" in rendered
    assert rendered.endswith("Barge-in pacing threshold")


def test_rule_layer_metadata_and_make_result_category() -> None:
    class SampleToolRule(Rule):
        id = "T001"
        name = "sample-tool"
        description = "Sample tool check"
        category = "tools"
        default_severity = Severity.ERROR

        def check(
            self, file_path: Path, content: str, context: Any
        ) -> list[LintResult]:
            return [self.make_result(str(file_path), "Tool issue")]

    rule_obj = SampleToolRule()
    assert rule_obj.layer_metadata.macro_band == 4  # noqa: PLR2004
    res = rule_obj.make_result("tools/lookup/python_code.py", "Tool issue")
    assert res.category == "tools"
    assert res.layer_metadata.macro_band == 4  # noqa: PLR2004


def test_lint_result_to_dict_and_report_to_json() -> None:
    result = LintResult(
        file="agents/root/instruction.txt",
        rule_id="I001",
        severity=Severity.ERROR,
        message="Missing <role>",
        line=1,
        fix_suggestion="Add <role>...</role>",
    )
    d = result.to_dict()
    expected_keys = {
        "file",
        "line",
        "severity",
        "rule_id",
        "message",
        "fix_suggestion",
        "macro_band",
        "macro_band_name",
        "osi_layer",
        "osi_name",
        "waf_pillar",
        "pyramid_layer",
    }
    assert expected_keys.issubset(d.keys())
    assert d["macro_band"] == 3  # noqa: PLR2004
    assert d["osi_layer"] == "L7"
    assert d["waf_pillar"] == WAF_OPS
    assert "Brain" in d["macro_band_name"]
    assert d["pyramid_layer"] == "Pyramid L3-L4: Turn & Golden Evals"

    report = LintReport(results=[result])
    parsed = json.loads(report.to_json())
    assert len(parsed) == 1
    assert parsed[0]["macro_band"] == 3  # noqa: PLR2004
    assert parsed[0]["osi_layer"] == "L7"
    assert parsed[0]["waf_pillar"] == WAF_OPS


# ── V100-V103 Multi-Surface Disambiguation ───────────────────────────────


@pytest.mark.parametrize("rule_id", ["V100", "V101", "V102", "V103"])
def test_v100_v103_category_and_path_disambiguation(rule_id: str) -> None:
    # Tools surface -> Band 4 / OSI L6b • Reliability
    res_tool_cat = LintResult(
        file="some_file.py",
        rule_id=rule_id,
        severity=Severity.ERROR,
        message="Tool variable issue",
        category="tools",
    )
    assert res_tool_cat.layer_metadata.macro_band == 4  # noqa: PLR2004
    assert res_tool_cat.layer_metadata.osi_layer == "L6b"
    assert res_tool_cat.layer_metadata.waf_pillar == WAF_RELIABILITY

    res_tool_path = LintResult(
        file="app/tools/get_order/python_function/python_code.py",
        rule_id=rule_id,
        severity=Severity.ERROR,
        message="Tool variable issue",
    )
    assert res_tool_path.layer_metadata.macro_band == 4  # noqa: PLR2004
    assert res_tool_path.layer_metadata.osi_layer == "L6b"

    # Instructions surface -> Band 3 / OSI L7 • Reliability
    res_inst_cat = LintResult(
        file="prompt.txt",
        rule_id=rule_id,
        severity=Severity.WARNING,
        message="Instruction variable issue",
        category="instructions",
    )
    assert res_inst_cat.layer_metadata.macro_band == 3  # noqa: PLR2004
    assert res_inst_cat.layer_metadata.osi_layer == "L7"
    assert res_inst_cat.layer_metadata.waf_pillar == WAF_RELIABILITY

    res_inst_path = LintResult(
        file="agents/root/instruction.txt",
        rule_id=rule_id,
        severity=Severity.WARNING,
        message="Instruction variable issue",
    )
    assert res_inst_path.layer_metadata.macro_band == 3  # noqa: PLR2004
    assert res_inst_path.layer_metadata.osi_layer == "L7"

    # Callbacks / Evals surface -> Band 2 / OSI L5 • Reliability
    res_cb = LintResult(
        file="agents/root/before_agent_callbacks/init/python_code.py",
        rule_id=rule_id,
        severity=Severity.ERROR,
        message="Callback variable issue",
        category="callbacks",
    )
    assert res_cb.layer_metadata.macro_band == 2  # noqa: PLR2004
    assert res_cb.layer_metadata.osi_layer == "L5"
    assert res_cb.layer_metadata.waf_pillar == WAF_RELIABILITY


def test_registered_v100_v103_rules_disambiguate_by_category() -> None:
    registry = build_registry()
    v103_by_cat = {
        r.category: r.layer_metadata
        for r in registry.all_rules()
        if r.id == "V103"
    }
    assert v103_by_cat["callbacks"].macro_band == 2  # noqa: PLR2004
    assert v103_by_cat["instructions"].macro_band == 3  # noqa: PLR2004
    assert v103_by_cat["tools"].macro_band == 4  # noqa: PLR2004


# ── 4-Band Summary Breakdown & Filtering ─────────────────────────────────


def _sample_multi_band_report() -> LintReport:
    report = LintReport()
    # Band 1 / Performance
    report.add(LintResult("app.json", "A007", Severity.ERROR, "Barge-in"))
    # Band 2 / Reliability (C-prefix rule)
    report.add(
        LintResult(
            "agents/root/before_model_callbacks/cb/python_code.py",
            "C999",
            Severity.WARNING,
            "Callback warning",
        )
    )
    # Band 3 / Operational Excellence
    report.add(
        LintResult(
            "agents/root/instruction.txt",
            "I001",
            Severity.ERROR,
            "Missing role",
        )
    )
    # Band 4 / Reliability
    report.add(
        LintResult(
            "tools/lookup/python_function/python_code.py",
            "T999",
            Severity.INFO,
            "Tool info",
        )
    )
    return report


def test_print_summary_includes_four_band_breakdown(capsys: Any) -> None:
    report = _sample_multi_band_report()
    report.print_summary()
    out = capsys.readouterr().out

    assert "2 error(s), 1 warning(s), 1 info" in out
    assert "4-Band Architecture Breakdown:" in out
    assert (
        "Band 1 (Wire & Pacing, OSI L1–L2): 1 error(s), 0 warning(s), 0 info"
        in out
    )
    assert (
        "Band 2 (Python Harness, OSI L5–L6a): 0 error(s), 1 warning(s), 0 info"
        in out
    )
    assert (
        "Band 3 (Brain & Routing, OSI L3 & L7): 1 error(s), 0 warning(s), 0 info"
        in out
    )
    assert (
        "Band 4 (Tools & DTOs, OSI L4 & L6b): 0 error(s), 0 warning(s), 1 info"
        in out
    )


def test_filter_by_layer_band_and_pillar() -> None:
    report = _sample_multi_band_report()

    # Filter by band only
    b1 = report.filter_by_layer(band=1)
    assert [r.rule_id for r in b1.results] == ["A007"]

    b3 = report.filter_by_layer(band=3)
    assert [r.rule_id for r in b3.results] == ["I001"]

    # Filter by WAF pillar (case-insensitive & alias)
    rel = report.filter_by_layer(waf_pillar="RELIABILITY")
    assert {r.rule_id for r in rel.results} == {"C999", "T999"}

    ops = report.filter_by_layer(waf_pillar="ops")
    assert [r.rule_id for r in ops.results] == ["I001"]

    ops_full = report.filter_by_layer(waf_pillar="operational-excellence")
    assert [r.rule_id for r in ops_full.results] == ["I001"]

    # Combined band + pillar filter
    b4_rel = report.filter_by_layer(band=4, waf_pillar="reliability")
    assert [r.rule_id for r in b4_rel.results] == ["T999"]

    b1_rel = report.filter_by_layer(band=1, waf_pillar="reliability")
    assert b1_rel.results == []

    # Original report remains unmodified
    assert len(report.results) == 4  # noqa: PLR2004

    # Invalid band / pillar raise ValueError
    with pytest.raises(ValueError, match="Invalid Macro-Band"):
        report.filter_by_layer(band=9)
    with pytest.raises(ValueError, match="Unknown WAF pillar"):
        report.filter_by_layer(waf_pillar="nonexistent")


# ── RuleRegistry.list_rules Legend & Filtering ───────────────────────────


def test_list_rules_legend_tags_and_filters(capsys: Any) -> None:
    registry = RuleRegistry()

    class Band1Rule(Rule):
        id = "A901"
        name = "app-audio"
        description = "Audio wire check"
        category = "config"

        def check(
            self, file_path: Path, content: str, context: Any
        ) -> list[LintResult]:
            return []

    class Band3Rule(Rule):
        id = "I901"
        name = "inst-role"
        description = "Prompt structure check"
        category = "instructions"

        def check(
            self, file_path: Path, content: str, context: Any
        ) -> list[LintResult]:
            return []

    registry.register_all([Band1Rule(), Band3Rule()])

    # Unfiltered includes 4-Band legend and inline tags for both
    registry.list_rules()
    out_all = capsys.readouterr().out
    assert "4-Band Agentic OSI Architecture Legend:" in out_all
    assert "Band 1: Acoustic Wire & Turn Pacing" in out_all
    assert "Band 4: Tool Transport & Clean Data Facade" in out_all
    assert "A901" in out_all
    assert "[Band 1 / OSI L1 • Performance]" in out_all
    assert "I901" in out_all
    assert "[Band 3 / OSI L7 • Operational Excellence]" in out_all

    # Filtered by band=1
    registry.list_rules(band=1)
    out_b1 = capsys.readouterr().out
    assert "A901" in out_b1
    assert "I901" not in out_b1

    # Filtered by waf_pillar="ops"
    registry.list_rules(waf_pillar="ops")
    out_ops = capsys.readouterr().out
    assert "I901" in out_ops
    assert "A901" not in out_ops


# ── CLI Parser & app_lint Integration ────────────────────────────────────


def test_cli_parser_lint_band_and_waf_pillar_flags() -> None:
    parser = get_parser()

    args_default = parser.parse_args(["lint"])
    assert args_default.band is None
    assert args_default.waf_pillar is None

    args_filtered = parser.parse_args(
        ["lint", "--band", "2", "--waf-pillar", "Operational-Excellence"]
    )
    assert args_filtered.band == 2  # noqa: PLR2004
    assert args_filtered.waf_pillar == "operational-excellence"

    args_upper = parser.parse_args(
        ["lint", "--band", "4", "--waf-pillar", "PERFORMANCE"]
    )
    assert args_upper.band == 4  # noqa: PLR2004
    assert args_upper.waf_pillar == "performance"

    with pytest.raises(SystemExit):
        parser.parse_args(["lint", "--band", "5"])

    with pytest.raises(SystemExit):
        parser.parse_args(["lint", "--waf-pillar", "invalid-pillar"])


def test_app_lint_filters_results_before_exit(
    tmp_path: Path, capsys: Any
) -> None:
    (tmp_path / "app.json").write_text(
        '{"name": "demo", "displayName": "Demo"}'
    )
    agent_dir = tmp_path / "agents" / "root_agent"
    agent_dir.mkdir(parents=True)
    # Trigger I015 (Band 3) with banned legacy tag <Agent>
    (agent_dir / "instruction.txt").write_text("<Agent>hello</Agent>")
    (agent_dir / "root_agent.json").write_text('{"displayName": "root agent"}')

    # Filtering to Band 1 excludes Band 3 I015 error -> exit code 0!
    args_b1 = argparse.Namespace(
        app_dir=str(tmp_path),
        model=None,
        model_only=False,
        list_rules=False,
        json_output=True,
        fix=False,
        validate_only=False,
        only=None,
        rule="I015",
        agents=None,
        tools=None,
        band=1,
        waf_pillar=None,
    )
    with pytest.raises(SystemExit) as exc_b1:
        app_lint(args_b1)
    assert exc_b1.value.code == 0
    assert json.loads(capsys.readouterr().out) == []

    # Filtering to Band 3 includes I015 -> JSON includes layer metadata
    args_b3 = argparse.Namespace(**{**vars(args_b1), "band": 3})
    with pytest.raises(SystemExit) as exc_b3:
        app_lint(args_b3)
    data_b3 = json.loads(capsys.readouterr().out)
    assert len(data_b3) >= 1
    assert data_b3[0]["rule_id"] == "I015"
    assert data_b3[0]["macro_band"] == 3  # noqa: PLR2004
    assert exc_b3.value.code in (0, 1)


# ── llm-lint Layer Tagging & JSON Output ─────────────────────────────────


def test_annotate_and_extract_llm_lint_findings() -> None:
    sample_md = (
        "## SUMMARY\n"
        "Score: 85/100.\n\n"
        "## RED-TEAMING & ROBUSTNESS\n"
        "- **Voice & Style Clarity**: Keep spoken turns concise.\n"
        "- **Grounding & Preventing Hallucinations**: Ground in tool output.\n"
        "- **Tool Schema Validation**: Verify payload fields.\n"
        "```xml\n"
        "- **Not A Finding Inside Code Fence**: Ignored\n"
        "```\n"
    )
    annotated = annotate_llm_lint_report(sample_md)
    assert "## SUMMARY\n" in annotated
    assert (
        "## RED-TEAMING & ROBUSTNESS "
        "[Band 3 / OSI L7 • Operational Excellence]" in annotated
    )
    assert (
        "- **Voice & Style Clarity**: [Band 1 / OSI L1 • Performance] "
        "Keep spoken turns concise." in annotated
    )
    assert (
        "- **Grounding & Preventing Hallucinations**: "
        "[Band 3 / OSI L7 • Security] Ground in tool output." in annotated
    )
    assert (
        "- **Tool Schema Validation**: [Band 4 / OSI L6b • Reliability] "
        "Verify payload fields." in annotated
    )
    assert "- **Not A Finding Inside Code Fence**: Ignored" in annotated

    findings = extract_llm_lint_findings(sample_md)
    assert len(findings) == 3  # noqa: PLR2004
    assert findings[0]["waf_pillar"] == WAF_PERFORMANCE
    assert findings[0]["macro_band"] == 1
    assert findings[1]["waf_pillar"] == WAF_SECURITY
    assert findings[1]["macro_band"] == 3  # noqa: PLR2004
    assert findings[2]["waf_pillar"] == WAF_RELIABILITY
    assert findings[2]["macro_band"] == 4  # noqa: PLR2004


def test_llm_lint_cli_json_and_terminal_tags(
    tmp_path: Path, capsys: Any
) -> None:
    agent_dir = tmp_path / "root_agent"
    agent_dir.mkdir()
    (agent_dir / "instruction.txt").write_text("<role>Helpful agent</role>")

    mock_report = (
        "## RED-TEAMING & ROBUSTNESS\n"
        "- **Voice & Style Clarity**: Speak naturally.\n"
    )

    mock_client = MagicMock()
    mock_client.generate.return_value = mock_report

    with patch(
        "cxas_scrapi.cli.llm_lint.GeminiGenerate", return_value=mock_client
    ):
        # 1. Terminal output includes resolved layer tags while preserving file
        args_term = argparse.Namespace(
            agent_dir=str(agent_dir),
            project_id="demo-proj",
            location="us-central1",
            model="gemini-2.5-flash",
            output=None,
            json_output=False,
        )
        llm_lint(args_term)
        term_out = capsys.readouterr().out
        assert "[Band 3 / OSI L7 • Operational Excellence]" in term_out
        assert "[Band 1 / OSI L1 • Performance]" in term_out
        assert (agent_dir / "llm_lint_report.md").read_text() == mock_report

        # 2. JSON output emits clean parseable JSON with LayerMetadata
        args_json = argparse.Namespace(
            agent_dir=str(agent_dir),
            project_id="demo-proj",
            location="us-central1",
            model="gemini-2.5-flash",
            output=None,
            json_output=True,
        )
        llm_lint(args_json)
        json_out = capsys.readouterr().out
        payload = json.loads(json_out)
        assert payload["agent"] == "root_agent"
        assert payload["layer"]["macro_band"] == 3  # noqa: PLR2004
        assert payload["findings"][0]["macro_band"] == 1
        assert payload["findings"][0]["waf_pillar"] == WAF_PERFORMANCE
