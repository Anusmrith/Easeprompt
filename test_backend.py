"""
Comprehensive Verification Suite for Easeprompt.
Tests the Heuristic Engine, Meta-Prompt formatting, SSE Streaming, and Placeholders.
"""

import asyncio
import json
from app.models import (
    ExpandPromptRequest,
    TargetAgent,
    FrameworkStyle,
    ExpansionDepth
)
from app.heuristic_generator import generate_heuristic_prompt, classify_input_domain
from app.expansion_engine import ExpansionEngine


def test_domain_classification():
    print("Testing domain classification...")
    assert classify_input_domain("crypto tracker") == "crypto"
    assert classify_input_domain("I want to analyze customer churn") == "churn"
    assert classify_input_domain("microservice authentication with jwt") == "auth"
    assert classify_input_domain("optimize slow postgres queries") == "database"
    assert classify_input_domain("build a web scraper for news") == "generic"
    print("  [PASS] Domain classification passed.")


def test_heuristic_expansion():
    print("Testing prompt expansion across frameworks...")
    # Test ART Framework
    prompt_art, expl_art = generate_heuristic_prompt(
        "crypto tracker",
        TargetAgent.CODING_ASSISTANT,
        FrameworkStyle.ART_FRAMEWORK,
        ExpansionDepth.COMPREHENSIVE
    )
    assert "[Act as]" in prompt_art
    assert "[Request]" in prompt_art
    assert "[Terms]" in prompt_art
    assert "DO NOT" in prompt_art  # Negative constraints
    assert "[INSERT" in prompt_art or "[SPECIFY" in prompt_art  # Dynamic placeholders
    assert len(expl_art.injected_negative_constraints) >= 3
    print("  [PASS] ART Framework generation passed.")

    # Test Modular Spec
    prompt_mod, _ = generate_heuristic_prompt(
        "I want to analyze customer churn",
        TargetAgent.DATA_ANALYST,
        FrameworkStyle.MODULAR_SPEC,
        ExpansionDepth.COMPREHENSIVE
    )
    assert "## 1. Persona & Operational Authority" in prompt_mod
    assert "## 7. Negative Constraints" in prompt_mod
    print("  [PASS] Modular Spec generation passed.")

    # Test XML Guardrails
    prompt_xml, _ = generate_heuristic_prompt(
        "microservice auth",
        TargetAgent.SECURITY_AUDITOR,
        FrameworkStyle.XML_GUARDRAILED,
        ExpansionDepth.COMPREHENSIVE
    )
    assert "<system_directive>" in prompt_xml
    assert "<negative_constraints>" in prompt_xml
    print("  [PASS] XML Guardrails generation passed.")


async def test_streaming_generator():
    print("Testing SSE streaming engine...")
    engine = ExpansionEngine()
    req = ExpandPromptRequest(
        input_text="crypto tracker",
        target_agent=TargetAgent.CODING_ASSISTANT,
        framework_style=FrameworkStyle.ART_FRAMEWORK,
        depth=ExpansionDepth.COMPREHENSIVE,
        provider="builtin"
    )

    chunks = []
    # Consume first 15 chunks to verify streaming format
    count = 0
    async for sse_chunk in engine.stream_expansion(req):
        chunks.append(sse_chunk)
        count += 1
        if count >= 15:
            break

    assert len(chunks) >= 15
    assert "data: " in chunks[0]
    first_data = json.loads(chunks[0].replace("data: ", "").strip())
    assert first_data["type"] == "meta"
    print(f"  [PASS] SSE Streaming verified ({len(chunks)} events captured).")


def test_placeholder_replacement():
    print("Testing placeholder replacement...")
    engine = ExpansionEngine()
    prompt = "Configure key: [INSERT DATA_PROVIDER_API_KEY] and currency: [SPECIFY FIAT_CURRENCY]"
    vars_to_test = {
        "[INSERT DATA_PROVIDER_API_KEY]": "LIVE_PROD_KEY_999",
        "[SPECIFY FIAT_CURRENCY]": "EUR"
    }
    res = engine.test_run_prompt(prompt, vars_to_test)
    assert "LIVE_PROD_KEY_999" in res["filled_prompt"]
    assert "EUR" in res["filled_prompt"]
    assert "[INSERT" not in res["filled_prompt"]
    print("  [PASS] Dynamic placeholder replacement passed.")


def test_accuracy_and_validation():
    print("Testing input accuracy validation and underspecified discovery protocol...")
    from pydantic import ValidationError

    # 1. Punctuation and symbols must be rejected
    invalid_inputs = [".", "..", "...", "!", "???", "   .   ", "a"]
    for bad_input in invalid_inputs:
        try:
            ExpandPromptRequest(
                input_text=bad_input,
                target_agent=TargetAgent.CODING_ASSISTANT,
                framework_style=FrameworkStyle.ART_FRAMEWORK,
                depth=ExpansionDepth.COMPREHENSIVE
            )
            assert False, f"Expected ValidationError for invalid input '{bad_input}'"
        except ValidationError as e:
            assert "meaningful task or concept" in str(e) or "at least 2" in str(e)
    print("  [PASS] Single punctuation and symbols like '.' are rejected with helpful validation errors.")

    # 2. Underspecified inputs like 'app' must trigger the discovery protocol
    domain = classify_input_domain("app")
    assert domain == "app", f"Expected domain 'app', got '{domain}'"

    prompt, expl = generate_heuristic_prompt(
        "app",
        TargetAgent.CODING_ASSISTANT,
        FrameworkStyle.ART_FRAMEWORK,
        ExpansionDepth.COMPREHENSIVE
    )
    assert "Phase 1: Ambiguity Resolution & Discovery Questions" in prompt
    assert "DO NOT GENERATE BLIND OR ARBITRARY CODE YET" in prompt
    assert "Proposed Implementation Archetypes" in prompt
    assert "[SPECIFY APPLICATION_TYPE]" in prompt
    assert "Ambiguity Discovery" in expl.detected_intent
    # 3. Gibberish, keyboard mash, and unpronounceable nonsense must be rejected
    gibberish_samples = [
        "ABCDFGHAG",
        "ABCDFGHAG element",
        "asdfghjkl",
        "qwertyuiop",
        "zzzzzz",
        "123456",
        "mnbvcx",
        "ghktrp"
    ]
    for gib in gibberish_samples:
        try:
            ExpandPromptRequest(
                input_text=gib,
                target_agent=TargetAgent.CODING_ASSISTANT,
                framework_style=FrameworkStyle.ART_FRAMEWORK,
                depth=ExpansionDepth.COMPREHENSIVE
            )
            assert False, f"Expected ValidationError for gibberish input '{gib}'"
        except ValidationError as e:
            assert "nonsensical" in str(e) or "descriptive words" in str(e)
    print("  [PASS] Gibberish inputs ('ABCDFGHAG', 'asdfghjkl', etc.) rejected with clear error guidance.")


if __name__ == "__main__":
    print("\n==========================================")
    print("  Easeprompt Automated Test Suite")
    print("==========================================\n")
    test_domain_classification()
    test_heuristic_expansion()
    test_accuracy_and_validation()
    asyncio.run(test_streaming_generator())
    test_placeholder_replacement()
    print("\n[SUCCESS] All Easeprompt backend verification tests passed!\n")
