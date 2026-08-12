"""Pluggable LLM client (OpenAI / Anthropic / local Ollama).

TODO (Phase 5):
  - LLMClient.generate(prompt: str) -> str interface
  - Implementations: OpenAI, Anthropic, Ollama (pick one default)
  - Prompt template with persona config (tone, length, topics to avoid)
  - Length enforcement (280 chars — trim + retry once if over)
  - Guardrails config: refuse certain topics, never impersonate a real person
"""
