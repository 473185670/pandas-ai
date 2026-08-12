"""
Pluggable LLM interface.

Supports multiple providers behind a single `generate_code()` call so the
product works with whichever API key the user has available (Gemini, OpenAI,
Anthropic, or a local Ollama model). If no key is set, falls back to a
deterministic stub that returns a template — useful for local dev / tests.
"""

from __future__ import annotations

import os
from dataclasses import dataclass


@dataclass
class LLMResponse:
    text: str
    provider: str
    tokens_used: int = 0


class LLMProvider:
    name: str = "base"

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        raise NotImplementedError


# ---------------------------------------------------------------------------
# OpenAI (GPT-4o-mini — cheap, high quality)
# ---------------------------------------------------------------------------
class OpenAIProvider(LLMProvider):
    name = "openai"

    def __init__(self, api_key: str, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        from openai import OpenAI  # imported lazily

        client = OpenAI(api_key=self.api_key)
        resp = client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.2,
        )
        return LLMResponse(
            text=resp.choices[0].message.content or "",
            provider=self.name,
            tokens_used=resp.usage.total_tokens if resp.usage else 0,
        )


# ---------------------------------------------------------------------------
# Anthropic (Claude Haiku — cheap, fast)
# ---------------------------------------------------------------------------
class AnthropicProvider(LLMProvider):
    name = "anthropic"

    def __init__(self, api_key: str, model: str = "claude-3-5-haiku-20241022"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        import anthropic  # imported lazily

        client = anthropic.Anthropic(api_key=self.api_key)
        msg = client.messages.create(
            model=self.model,
            max_tokens=max_tokens,
            messages=[{"role": "user", "content": prompt}],
        )
        text = "".join(block.text for block in msg.content if block.type == "text")
        return LLMResponse(
            text=text,
            provider=self.name,
            tokens_used=msg.usage.input_tokens + msg.usage.output_tokens,
        )


# ---------------------------------------------------------------------------
# Gemini (1.5 Flash — FREE tier: 15 RPM, 1500 req/day)
# ---------------------------------------------------------------------------
class GeminiProvider(LLMProvider):
    name = "gemini"

    def __init__(self, api_key: str, model: str = "gemini-2.5-flash"):
        self.api_key = api_key
        self.model = model

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        import google.generativeai as genai  # imported lazily

        genai.configure(api_key=self.api_key)
        model = genai.GenerativeModel(self.model)
        resp = model.generate_content(
            prompt,
            generation_config={"max_output_tokens": max_tokens, "temperature": 0.2},
        )
        return LLMResponse(
            text=resp.text or "",
            provider=self.name,
            tokens_used=resp.usage_metadata.total_token_count if resp.usage_metadata else 0,
        )


# ---------------------------------------------------------------------------
# Local Ollama (free, offline)
# ---------------------------------------------------------------------------
class OllamaProvider(LLMProvider):
    name = "ollama"

    def __init__(self, model: str = "codellama:7b", host: str = "http://localhost:11434"):
        self.model = model
        self.host = host

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        import requests

        resp = requests.post(
            f"{self.host}/api/generate",
            json={"model": self.model, "prompt": prompt, "stream": False},
            timeout=60,
        )
        resp.raise_for_status()
        return LLMResponse(text=resp.json().get("response", ""), provider=self.name)


# ---------------------------------------------------------------------------
# Stub (no key) — returns a commented template so the API still works for dev
# ---------------------------------------------------------------------------
class StubProvider(LLMProvider):
    name = "stub"

    def generate(self, prompt: str, *, max_tokens: int = 1024) -> LLMResponse:
        return LLMResponse(
            text=(
                "```python\n"
                "# LLM provider not configured. Set OPENAI_API_KEY or ANTHROPIC_API_KEY.\n"
                "# This is a stub response for local development.\n"
                "print('Configure an LLM provider to generate code.')\n"
                "```"
            ),
            provider=self.name,
        )


def get_provider() -> LLMProvider:
    """Pick the best available provider from environment variables."""
    if key := os.getenv("GEMINI_API_KEY"):
        return GeminiProvider(key)
    if key := os.getenv("OPENAI_API_KEY"):
        return OpenAIProvider(key)
    if key := os.getenv("ANTHROPIC_API_KEY"):
        return AnthropicProvider(key)
    if os.getenv("OLLAMA_HOST") or os.getenv("USE_OLLAMA"):
        return OllamaProvider()
    return StubProvider()
