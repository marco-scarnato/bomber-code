---
name: minicpm-coding-agent
description: Operational and engineering guide for MiniCPM5-2B (Hybrid Thinking Coding Agent) served via llama-server. Use when implementing coding workflows, streaming token telemetry, managing the <think> reasoning trace, or benchmarking code generation.
---

# MiniCPM5-2B Coding Agent Guide & Operational Manual

## 1. Architectural Overview & Capabilities

MiniCPM5-2B is a state-of-the-art compact language model equipped with **Hybrid Thinking** capabilities (similar to DeepSeek-R1), capable of complex multi-step reasoning before output generation.

* **Active Model in Repository**:
  * **Model**: `openbmb/MiniCPM5-2B-GGUF` (`MiniCPM5-2B-Q4_K_M.gguf`, ~1.4 GB file size).
  * **Serving Engine**: Official `ghcr.io/ggml-org/llama.cpp:server` container on port 8001.
  * **Hardware Profile**: CPU-only execution (0 MB VRAM), consumes **~1.31 GB RAM**.
  * **Throughput**:
    * **Generation Speed**: **~22 - 25 tokens/second** on standard multi-core CPU.
    * **Prompt Prefill Speed**: **~75 - 100 tokens/second**.
  * **Context Window**: Configured to 8,192 tokens (`MINICPM_CTX_SIZE=8192`, threads = 8).

---

## 2. Hybrid Thinking Architecture (`<think>`)

MiniCPM5-2B natively supports step-by-step cognitive reasoning:
1. **Thinking Triggers**:
   * Prepend `/think` to the user message to enforce reasoning.
   * Prepend `/no_think` to bypass the thinking phase for direct responses.
2. **Streaming Delta Separation**:
   * The local `llama-server` parses the Jinja template and splits the response:
     * `delta.reasoning_content`: Emits internal cognitive tokens (planning, edge-case analysis).
     * `delta.content`: Emits final clean user-facing response (code, documentation).
3. **Usage & Timing Telemetry**:
   * When passing `stream_options: {"include_usage": true}`, the terminal SSE chunk delivers:
     * `usage`: `{ prompt_tokens, completion_tokens, total_tokens }`
     * `timings`: `{ prompt_ms, prompt_per_second, predicted_ms, predicted_per_second }`

---

## 3. Coding Agent Presets & Benchmark Workflows

When deploying MiniCPM as a developer assistant, configure specific system prompts:

### A. Strict Coding Agent (Edge Cases & Architecture)
* **Goal**: Force the model to spend reasoning tokens investigating edge cases *before* emitting code.
* **System Prompt Core**:
  ```text
  You are a senior software engineer and autonomous Coding Agent.
  Before writing code, use the reasoning trace to:
  1. Break down functional and performance requirements.
  2. Enumerate edge cases (null inputs, empty sequences, overflow, complexity bounds).
  3. Validate architectural choices.
  Produce clean, typed, documented production code.
  ```

### B. Bug Hunter & Patch Specialist (Git Diff & Pytest)
* **Goal**: Isolate root causes and output standard unified patches.
* **Format**:
  * Reasoning: Explains the bug's root cause.
  * Output: Standard `--- a/... +++ b/...` git diff + regression unit test.

### C. Structured Tool Calling (XML Function Invocations)
* **Goal**: Prevent hallucinations by requiring tool invocations when external information is needed:
  ```xml
  <function name="execute_bash">
    <param name="command">pytest tests/test_core.py</param>
  </function>
  ```

---

## 4. Client Integration (`MiniCPMClient`)

Located at `playground/streamlit-app/utils/minicpm_client.py`:
* **Non-streaming call**: `client.chat(messages, temperature=0.6, max_tokens=1024)`
* **Streaming generator**: `client.chat_stream(messages, temperature=0.6, max_tokens=1024)`
  * Yields formatted reasoning blocks prefixed with `> 🧠 **Processo di Ragionamento:**` followed by the markdown output.
  * Populates `client.last_stats` with exact token counts and generation speeds.

---

## 5. Senior Developer Rules & Parameters

1. **Recommended Sampling Parameters**:
   * **Algorithms & Debugging**: `temperature=0.2 - 0.4`, `top_p=0.90` (deterministic, avoids syntax slip-ups).
   * **Architecture & Refactoring**: `temperature=0.6`, `top_p=0.95`.
2. **Context & Max Tokens**:
   * Reserve sufficient tokens (`max_tokens >= 1024`) when thinking mode is active, as reasoning tokens consume completion quota.
3. **Quick CLI Verification**:
   ```bash
   # Test inference directly from WSL terminal
   curl -s http://localhost:8001/v1/chat/completions \
     -H "Content-Type: application/json" \
     -d '{"messages": [{"role": "user", "content": "/think Invert a binary tree in Python."}], "max_tokens": 300}'
   ```