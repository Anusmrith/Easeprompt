"""
Easeprompt Expansion Engine.
Orchestrates real-time streaming prompt generation via either:
1. Built-in Semantic & Domain Knowledge Engine (deterministic, zero-latency, no API key required)
2. Frontier LLM Providers (OpenAI, Google Gemini, Groq, Ollama) with SSE token streaming.
"""

import os
import json
import asyncio
import re
from typing import AsyncGenerator, Dict, Any, Optional

import httpx
from .models import (
    ExpandPromptRequest,
    TargetAgent,
    FrameworkStyle,
    ExpansionDepth,
    ExplanationData,
    PlaceholderItem
)
from .meta_prompt import EASEPROMPT_MASTER_SYSTEM_PROMPT, build_meta_prompt_user_message
from .heuristic_generator import generate_heuristic_prompt, DOMAIN_KNOWLEDGE, classify_input_domain


class ExpansionEngine:
    def __init__(self):
        self.default_provider = os.getenv("DEFAULT_PROVIDER", "builtin").lower()
        self.gemini_key = os.getenv("GEMINI_API_KEY", "")
        self.openai_key = os.getenv("OPENAI_API_KEY", "")
        self.groq_key = os.getenv("GROQ_API_KEY", "")
        self.ollama_base = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434/v1")

    async def stream_expansion(
        self,
        request: ExpandPromptRequest
    ) -> AsyncGenerator[str, None]:
        """
        Asynchronous generator yielding Server-Sent Events (SSE) JSON payloads.
        Emits:
        - {"type": "meta", "provider": ..., "target": ..., "framework": ...}
        - {"type": "token", "content": "..."}
        - {"type": "done", "full_content": "..."}
        """
        provider = (request.provider or self.default_provider).lower()
        api_key = request.api_key or self._get_env_key_for_provider(provider)

        # Notify frontend of generation start
        yield self._format_sse({
            "type": "meta",
            "provider": provider,
            "target": request.target_agent.value,
            "framework": request.framework_style.value
        })

        if provider == "builtin" or not api_key and provider in ["openai", "gemini", "groq"]:
            # Stream using built-in high-quality heuristic engine
            async for sse_chunk in self._stream_builtin(request):
                yield sse_chunk
            return

        # Attempt to stream from external provider; fall back gracefully if error occurs
        try:
            if provider == "openai":
                async for sse_chunk in self._stream_openai_compatible(
                    request,
                    base_url="https://api.openai.com/v1/chat/completions",
                    api_key=api_key,
                    model="gpt-4o-mini"
                ):
                    yield sse_chunk

            elif provider == "groq":
                async for sse_chunk in self._stream_openai_compatible(
                    request,
                    base_url="https://api.groq.com/openai/v1/chat/completions",
                    api_key=api_key,
                    model="llama-3.3-70b-versatile"
                ):
                    yield sse_chunk

            elif provider == "ollama":
                async for sse_chunk in self._stream_openai_compatible(
                    request,
                    base_url=f"{self.ollama_base}/chat/completions",
                    api_key="ollama",
                    model="llama3"
                ):
                    yield sse_chunk

            elif provider == "gemini":
                async for sse_chunk in self._stream_gemini(request, api_key=api_key):
                    yield sse_chunk

            else:
                async for sse_chunk in self._stream_builtin(request):
                    yield sse_chunk

        except Exception as e:
            # Emit error notice, then gracefully fall back to builtin engine
            yield self._format_sse({
                "type": "warning",
                "message": f"External provider '{provider}' failed ({str(e)}). Seamlessly falling back to Built-in Engine."
            })
            async for sse_chunk in self._stream_builtin(request):
                yield sse_chunk

    async def _stream_builtin(
        self,
        request: ExpandPromptRequest
    ) -> AsyncGenerator[str, None]:
        """
        Simulates natural token-by-token streaming for the built-in generator.
        """
        full_text, _ = generate_heuristic_prompt(
            request.input_text,
            request.target_agent,
            request.framework_style,
            request.depth
        )

        # Group chunks for rapid, fluid token rendering
        words_and_spaces = [c for c in re.split(r'(\s+)', full_text) if c]
        accumulated = []

        # Yield 2-3 word tokens per step for realistic 60-80 tokens/sec cadence
        chunk_size = 2
        for i in range(0, len(words_and_spaces), chunk_size):
            slice_chunk = "".join(words_and_spaces[i:i + chunk_size])
            accumulated.append(slice_chunk)
            yield self._format_sse({
                "type": "token",
                "content": slice_chunk
            })
            await asyncio.sleep(0.008)

        yield self._format_sse({
            "type": "done",
            "full_content": full_text
        })


    async def _stream_openai_compatible(
        self,
        request: ExpandPromptRequest,
        base_url: str,
        api_key: str,
        model: str
    ) -> AsyncGenerator[str, None]:
        """
        Streams from OpenAI, Groq, or Ollama using standard streaming protocol.
        """
        user_message = build_meta_prompt_user_message(
            request.input_text,
            request.target_agent,
            request.framework_style,
            request.depth
        )

        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": EASEPROMPT_MASTER_SYSTEM_PROMPT},
                {"role": "user", "content": user_message}
            ],
            "stream": True,
            "temperature": request.temperature or 0.4
        }

        accumulated = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", base_url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    raise RuntimeError(f"HTTP {response.status_code}: {err_body.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if not line:
                        continue
                    if line.startswith("data: "):
                        data_str = line[6:].strip()
                        if data_str == "[DONE]":
                            break
                        try:
                            chunk = json.loads(data_str)
                            delta = chunk["choices"][0].get("delta", {}).get("content", "")
                            if delta:
                                accumulated.append(delta)
                                yield self._format_sse({
                                    "type": "token",
                                    "content": delta
                                })
                        except json.JSONDecodeError:
                            continue

        full_content = "".join(accumulated)
        yield self._format_sse({
            "type": "done",
            "full_content": full_content
        })

    async def _stream_gemini(
        self,
        request: ExpandPromptRequest,
        api_key: str
    ) -> AsyncGenerator[str, None]:
        """
        Streams from Google Gemini API via REST SSE endpoint.
        """
        user_message = build_meta_prompt_user_message(
            request.input_text,
            request.target_agent,
            request.framework_style,
            request.depth
        )

        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:streamGenerateContent?alt=sse&key={api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {
                "parts": [{"text": EASEPROMPT_MASTER_SYSTEM_PROMPT}]
            },
            "contents": [
                {"role": "user", "parts": [{"text": user_message}]}
            ],
            "generationConfig": {
                "temperature": request.temperature or 0.4
            }
        }

        accumulated = []
        async with httpx.AsyncClient(timeout=60.0) as client:
            async with client.stream("POST", url, headers=headers, json=payload) as response:
                if response.status_code != 200:
                    err_body = await response.aread()
                    raise RuntimeError(f"Gemini API Error {response.status_code}: {err_body.decode('utf-8')}")

                async for line in response.aiter_lines():
                    if not line or not line.startswith("data: "):
                        continue
                    data_str = line[6:].strip()
                    try:
                        data = json.loads(data_str)
                        candidates = data.get("candidates", [])
                        if candidates:
                            parts = candidates[0].get("content", {}).get("parts", [])
                            for part in parts:
                                text = part.get("text", "")
                                if text:
                                    accumulated.append(text)
                                    yield self._format_sse({
                                        "type": "token",
                                        "content": text
                                    })
                    except json.JSONDecodeError:
                        continue

        yield self._format_sse({
            "type": "done",
            "full_content": "".join(accumulated)
        })

    def explain_prompt(
        self,
        input_text: str,
        target_agent: TargetAgent,
        framework_style: FrameworkStyle,
        generated_prompt: Optional[str] = None
    ) -> ExplanationData:
        """
        Provides metacognitive breakdown of why the prompt was engineered this way.
        Extracts dynamic placeholders from the generated text.
        """
        _, default_explanation = generate_heuristic_prompt(
            input_text, target_agent, framework_style, ExpansionDepth.COMPREHENSIVE
        )

        placeholders: List[PlaceholderItem] = []
        if generated_prompt:
            # Extract bracketed placeholders like [INSERT ...] or [SPECIFY ...]
            matches = set(re.findall(r'\[(?:INSERT|SPECIFY|TARGET)[A-Z0-9_\s|"]+?\]', generated_prompt))
            for tag in sorted(matches):
                # Clean tag for label
                label = tag.replace("[", "").replace("]", "").replace("_", " ").title()
                placeholders.append(PlaceholderItem(
                    tag=tag,
                    label=label,
                    description=f"User-specific value required for {label.lower()}",
                    default_value="",
                    example=f"value_for_{label.lower().replace(' ', '_')}"
                ))

        if not placeholders:
            placeholders = default_explanation.placeholders

        default_explanation.placeholders = placeholders
        return default_explanation

    def test_run_prompt(
        self,
        prompt_text: str,
        variables: Dict[str, str]
    ) -> Dict[str, Any]:
        """
        Fills placeholders and returns a simulated execution output.
        """
        filled_prompt = prompt_text
        for tag, val in variables.items():
            if val.strip():
                filled_prompt = filled_prompt.replace(tag, val.strip())

        # Create realistic simulated model execution of the prompt
        simulated_output = (
            "### [SIMULATED EXECUTION RESPONSE]\n"
            f"Verified active role and received structured instructions with {len(variables)} bound parameters.\n\n"
            "#### Validation Checks:\n"
            "- [x] Role persona verified and constraints loaded.\n"
            "- [x] Zero generic fluff rule acknowledged.\n"
            "- [x] Injected negative constraints activated.\n\n"
            "#### Execution Summary:\n"
            "The model successfully processed the engineered prompt. All dynamic placeholders were substituted, "
            "and output formatting matches the specified contract."
        )

        return {
            "filled_prompt": filled_prompt,
            "simulated_output": simulated_output,
            "execution_time_ms": 142.5
        }

    def _get_env_key_for_provider(self, provider: str) -> str:
        """
        Retrieves server-side API keys with a zero-cost financial guardrail.
        By default, server-level paid keys are disabled in public production to prevent
        anonymous visitors from running up unexpected billing charges.
        To explicitly allow server keys, set ALLOW_SERVER_API_KEYS=true in environment.
        """
        allow_server_keys = os.getenv("ALLOW_SERVER_API_KEYS", "false").lower() in ("true", "1")
        if not allow_server_keys:
            return ""

        if provider == "gemini":
            return self.gemini_key
        elif provider == "openai":
            return self.openai_key
        elif provider == "groq":
            return self.groq_key
        return ""

    def _format_sse(self, data: Dict[str, Any]) -> str:
        return f"data: {json.dumps(data)}\n\n"
