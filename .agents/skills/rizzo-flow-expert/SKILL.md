---
name: rizzo-flow-expert
description: Expert operational and development guide for Rizzo-Flow (Spark-X2.5-1.7B) System 1 probabilistic decision engine. Use whenever querying, configuring, benchmarking, extending, or debugging Rizzo-Flow and its logit-based decision API.
---

# Rizzo-Flow Expert Guide & Operational Manual

## 1. Architectural Overview & "System 1" Paradigm

Rizzo-Flow is a high-speed, zero-generation probabilistic decision engine designed for classification, triage, routing, and scoring without the latency or hallucinations of autoregressive text generation.

* **Inference Paradigm ("System 1")**:
  * Instead of generating tokens word-by-word, Rizzo-Flow executes a **single forward pass** over the input state/context.
  * It directly measures the **terminal logits** corresponding to the candidate options.
  * A restricted softmax is applied over the candidate logit slice, yielding exact, calibrated mathematical probabilities.
  * **Tokens Generated = 0**.
* **Active Model in Repository**:
  * **Model**: `XHToken/Spark-X2.5-1.7B` fine-tuned with Rizzo-Flow LoRA.
  * **Quantization**: `q4_k_m` GGUF (`spark-x2.5-1.7b-rizzo-flow-lora-q4_k_m.gguf`, ~1.1 GB).
  * **Hardware Profile**: CPU-only execution (0 MB VRAM), consumes **~1.29 GB RAM**.
  * **Latency**: ~2.5 - 3.2 seconds total on CPU for typical contexts (10x faster than 4B).

---

## 2. Codebase Structure & Key Files

The source code is located at `c:\Users\m.scarnato\Personale\jev-try\rizzo-flow\`:
* `src/rizzo/`:
  * `engine.py`: Core inference coordinator wrapping `llama.cpp` runtime via ctypes.
  * `server.py`: FastAPI application serving `/v1/decisions` and `/health`.
  * `prompt.py`: Prompt builder formatting states and candidate token anchors.
  * `schema.py`: Pydantic models for incoming decisions and outgoing answers.
  * `runtime.py`: Automatic download and linking of `llama.cpp` shared libraries.
* `playground/rizzo-flow-api/`:
  * `Dockerfile`: Multi-stage Debian image with `uv` and Python 3.11.
  * `entrypoint.sh`: Auto-downloads the 1.7B model if missing and launches `uv run rizzo serve`.

---

## 3. Wire API Specification

* **Endpoint**: `http://rizzo-flow:8017` (Docker network) or `http://localhost:8017` (host).
* **Health Check**: `GET /health`
  * Returns JSON containing model source, precision, context size (10240), load seconds.

### `POST /v1/decisions` Request Schema
```json
{
  "state": "Testo di contesto o evidenza fattuale (email, log, transazione, report)",
  "questions": {
    "question_id": {
      "type": "choice",
      "instructions": "Quale categoria descrive meglio il problema?",
      "options": [
        {"id": "opt_0", "description": "Problema di Rete"},
        {"id": "opt_1", "description": "Errore Software"}
      ],
      "policy": {
        "allow_abstain": true,
        "max_unavailable_probability": 0.35,
        "min_top_probability": 0.50
      }
    }
  }
}
```

### Supported Question Types:
1. `choice`: Set of arbitrary categorical options (`options: [{"id": "...", "description": "..."}]`).
2. `boolean`: Binary decisions (`true_description`, `false_description`).
3. `score`: Ordered discrete grades from low to high (`levels: ["Basso", "Medio", "Alto"]`). Calculates continuous expected score.
4. `numeric`: Calibrated numerical anchors (`anchors: [{"value": 10.0, "description": "..."}]`).

### Response Structure & Fields:
```json
{
  "model": { ... },
  "answers": {
    "question_id": {
      "status": "ok | insufficient_evidence | out_of_range | uncertain",
      "choice": "opt_0",
      "probabilities": {
        "opt_0": 0.88,
        "opt_1": 0.10,
        "__insufficient__": 0.02
      },
      "uncertainty": {
        "top_probability": 0.88,
        "entropy_nats": 0.35,
        "concentration": 0.86,
        "unavailable_probability": 0.02
      },
      "input_tokens": 185
    }
  },
  "timing": {
    "prefill_seconds": 0.12,
    "inference_seconds": 2.65,
    "total_seconds": 2.78
  }
}
```

---

## 4. Senior Developer Best Practices & Pitfalls

1. **ID Mapping Requirement**:
   * Rizzo-Flow always returns the option `id` in `answers[q]["choice"]`, never the user-facing text.
   * *Rule*: Always construct a dictionary `{ "opt_0": "Label 1", ... }` before calling the API and map the result back to human-readable strings.
2. **Handling the `__insufficient__` Token**:
   * If `allow_abstain: true`, Rizzo assigns probability mass to `__insufficient__` when context lacks clear evidence.
   * If `choice` is `null` or `status == "insufficient_evidence"`, route to human fallback or escalate. Never force a choice when uncertainty is high.
3. **Continuous Score vs Label**:
   * For `type: "score"`, do not expect a string label. Read `answer["score"]` which gives the expected continuous float (e.g. `1.85`).
4. **Context Truncation**:
   * While context window is 10k+ cells, keep states concise (< 2000 tokens) for sub-3 second CPU latency.

---

## 5. Quick Verification Commands

```bash
# Health check via WSL
curl -s http://localhost:8017/health

# Test inference from CLI
curl -s -X POST http://localhost:8017/v1/decisions \
  -H "Content-Type: application/json" \
  -d '{"state": "Password dimenticata", "questions": {"q": {"type": "boolean", "instructions": "Serve reset password?"}}}'
```