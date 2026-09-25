"""
Pydantic data models for Easeprompt.
Defines schemas for prompt expansion requests, target agents, frameworks, and metacognitive explanations.
"""

import re
from enum import Enum
from typing import Dict, List, Optional
from pydantic import BaseModel, Field, field_validator


class TargetAgent(str, Enum):
    CODING_ASSISTANT = "coding_assistant"
    DATA_ANALYST = "data_analyst"
    AUTONOMOUS_AGENT = "autonomous_agent"
    SYSTEM_ARCHITECT = "system_architect"
    SECURITY_AUDITOR = "security_auditor"
    CREATIVE_WRITER = "creative_writer"
    GENERAL_PURPOSE = "general_purpose"


class FrameworkStyle(str, Enum):
    ART_FRAMEWORK = "art_framework"          # Act as, Request, Terms
    MODULAR_SPEC = "modular_spec"            # Role, Task, Context, Steps, Constraints, Output Schema
    XML_GUARDRAILED = "xml_guardrailed"      # Anthropic style XML tags
    AUTONOMOUS_REACT = "autonomous_react"    # Persona, Tools, Loop, Halting Criteria


class ExpansionDepth(str, Enum):
    COMPREHENSIVE = "comprehensive"
    CONCISE = "concise"


class ExpandPromptRequest(BaseModel):
    input_text: str = Field(..., min_length=1, description="Brief input keyword or sentence")
    target_agent: TargetAgent = Field(default=TargetAgent.CODING_ASSISTANT, description="Target AI agent role")
    framework_style: FrameworkStyle = Field(default=FrameworkStyle.ART_FRAMEWORK, description="Prompt structuring framework")
    depth: ExpansionDepth = Field(default=ExpansionDepth.COMPREHENSIVE, description="Depth and verbosity of the generated prompt")
    provider: Optional[str] = Field(default="builtin", description="LLM provider: builtin, gemini, openai, groq, ollama")
    api_key: Optional[str] = Field(default=None, description="Optional custom API key for frontier providers")
    temperature: Optional[float] = Field(default=0.4, ge=0.0, le=1.0)

    @field_validator("input_text")
    @classmethod
    def validate_meaningful_content(cls, v: str) -> str:
        from .quality_filter import validate_prompt_input_quality
        is_valid, error_msg = validate_prompt_input_quality(v)
        if not is_valid:
            raise ValueError(error_msg)
        return v.strip()


class PlaceholderItem(BaseModel):
    tag: str
    label: str
    description: str
    default_value: str
    example: str


class ExplanationData(BaseModel):
    detected_intent: str
    target_domain: str
    extrapolated_context: List[str]
    injected_negative_constraints: List[str]
    suggested_schemas: List[str]
    placeholders: List[PlaceholderItem]
    rationale: str


class ExplainPromptRequest(BaseModel):
    input_text: str
    target_agent: TargetAgent
    framework_style: FrameworkStyle
    generated_prompt: Optional[str] = None


class TestPromptRequest(BaseModel):
    prompt_text: str
    variables: Dict[str, str] = Field(default_factory=dict)
    provider: Optional[str] = "builtin"
    api_key: Optional[str] = None


class TestPromptResponse(BaseModel):
    filled_prompt: str
    simulated_output: str
    execution_time_ms: float
