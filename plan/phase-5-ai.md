# Phase 5 — AI Reply Generation

> Build the LLM client and prompt pipeline. This is the **hardest** phase to get right — replies need to feel human, not bot-ish.

## Status: 🔴 Todo

## Goal

A `bot/ai.py` module that, given an original tweet and a persona, returns a reply string ≤ 280 chars that reads like a real person.

## Tasks

- [ ] `LLMClient` abstract base class
  - `.generate(system_prompt: str, user_prompt: str) -> str`
- [ ] Implementations (pick one default, stub the others):
  - `OpenAIClient` (uses `openai` SDK)
  - `AnthropicClient` (uses `anthropic` SDK)
  - `OllamaClient` (uses HTTP via `httpx` or `requests`)
- [ ] `build_prompt(original_tweet, persona) -> tuple[system, user]`
  - System: persona + tone + length rules + guardrails
  - User: "Write a reply to this tweet: ..."
- [ ] `enforce_length(text, max=280) -> str` — trim, retry once with shorter prompt if still over
- [ ] Guardrails config (config-driven, not hardcoded):
  - Topics to refuse (politics, NSFW, medical, financial advice, etc.)
  - "Never impersonate a real person"
  - "Never claim to be the original tweet's author"
- [ ] `get_client(config) -> LLMClient` factory based on which env vars are set
- [ ] Add `tests/test_ai.py`
- [ ] Add a "bad reply" detector (regex or LLM-as-judge) that flags AI-tell patterns

## Testing

**Unit tests (mocked LLM):**
- [ ] Mock the OpenAI/Anthropic SDK to return canned responses
- [ ] Test that `generate()` calls the SDK with the right system + user prompts
- [ ] Test that responses over 280 chars trigger a retry with a "shorter" instruction
- [ ] Test the guardrail system prompt is included in every request
- [ ] Test `enforce_length()` on edge cases (exactly 280, 281, 500 chars)

**Integration test (real LLM, cheap model):**
- [ ] Use `gpt-4o-mini` or `claude-3-5-haiku` (cheap)
- [ ] Pass 5 real tweets in your target niche, assert each response is:
  - ≤ 280 chars
  - Doesn't start with "Great point!" / "That's a really..." (AI-tell patterns)
  - References something specific in the original tweet
- [ ] **Manually review all 5 outputs** for quality before shipping

**"Bad reply" detector:**
- [ ] Test that the detector flags these patterns:
  - Generic openings ("Great point!", "That's a really interesting take...")
  - Excessive emoji (≥3 in a row)
  - Hedging language ("It depends...", "There are many factors...")
  - Refusal patterns ("I can't help with that...", "As an AI...")
  - Calls-to-action questions ("I'd love to hear your thoughts!", "What do you think?")
- [ ] Test that flagged replies are rejected and a retry is triggered

## Exit criteria

- [ ] `pytest tests/test_ai.py` passes
- [ ] Integration test: 5 real replies, all reviewed and approved by a human
- [ ] No reply in your test batch would get a savvy user thinking "this is a bot"
- [ ] Length enforcement verified (force an over-280 case, confirm trim + retry)
- [ ] Cost per reply < $0.001 (gpt-4o-mini) or $0 (Ollama)
- [ ] Bad-reply detector catches ≥ 80% of AI-tell patterns in your test set

## Notes

- **This is the phase where the project succeeds or fails.** Plumbing is easy; reply quality is hard.
- A great reply is **specific, useful, and short.** Examples:
  - ❌ `"Great point! Building in public is so important for indie hackers."`
  - ✅ `"The 'ship log' angle is underrated — I get 2x engagement when I include what I deleted, not just what I added."`
- Avoid: lists, hashtags, emoji walls, "Here's why →", call-to-action questions, "I'd love to hear your thoughts!"
- Test with **real tweets in your target keyword niche** before committing to a prompt.
- If using Ollama, test on the same machine that will run the bot in prod. Model latency varies wildly by hardware.
- The `BOT_PERSONA` env var is your biggest lever. Iterate on it. Keep a `prompts/` folder with versioned personas you've tried.
- The "bad reply" detector should be **strict**. False positives (rejecting a good reply) are cheaper than false negatives (letting an obvious-AI reply through).
