---
name: clm-expert
description: Operational and architectural guide for CLM (Contrastive Language Model) and TypeSafe System 1 decision endpoints. Use when querying, extending, deploying, or benchmarking CLM and contrastive state-action embedding models.
---

# CLM (Contrastive Language Model) Expert Guide

## 1. Architectural Overview & Contrastive Mechanics

CLM is a System 1 decision architecture designed to select candidate actions or answers by aligning state and action embeddings in a joint representation space.

* **Contrastive Learning Principle (InfoNCE)**:
  * Rather than generating autoregressive tokens or evaluating logit outputs sequentially, CLM encodes the **State** $s$ and **Candidate Actions** $a_i$ separately.
  * A trained projection head maps both embeddings into a shared metric space.
  * Decision scores are computed via the scaled dot product:
    $$\text{score}(s, a_i) = \frac{1}{\tau} \phi(s)^T \psi(a_i)$$
  * Probabilities are obtained by applying a softmax over all candidate scores.
* **Key Advantages over Traditional LLMs**:
  * **Candidate Caching**: Static action catalogs (e.g. 5,000 product categories, FAQs, or API routes) can be pre-embedded and indexed once.
  * **Minimal Latency**: Decision latencies are sub-second (~10-50 ms in production with cached vectors).
  * **Zero Autoregressive Generation**: Zero hallucinations, deterministic probability distributions.

---

## 2. Codebase Structure & Deployment

Source repository: `c:\Users\m.scarnato\Personale\jev-try\CLM\`:
* `src/clm/`:
  * `server.py`: FastAPI server implementing the TypeSafe wire schema (`/v1/systemone`, `/v1/rank`, `/v1/models`, `/health`).
  * `engine.py`: Core inference engine orchestrating embedder calls and projection heads.
  * `heads.py`: PyTorch projection heads and checkpoint loaders.
  * `schema.py`: Question/Answer validation following TypeSafe specifications.
* `playground/clm-api/`:
  * Container running on port `8700` (`playground-clm:latest`).
  * Default entrypoint runs `tools/playground_mock.py` on CPU (enables testing all routes and wire schemas without requiring a heavy GPU embedding server).

---

## 3. Wire API Specification (TypeSafe Schema)

* **Base URL**: `http://clm:8700` (Docker) or `http://localhost:8700` (Host).
* **Health Check**: `GET /health` -> `{"ok": true, "embedder": true, "models": ["clm-latest", "clm-raw"]}`

### `POST /v1/systemone`
Executes structured decision tasks over criteria:
```json
{
  "state": "Testo del contesto o evento da classificare",
  "model": "clm-latest",
  "temperature": 1.0,
  "questions": {
    "task_id": {
      "type": "choice",
      "instructions": "Quale reparto deve gestire la richiesta?",
      "criteria": {
        "opt_0": "Assistenza Tecnica e Accessi",
        "opt_1": "Fatturazione e Pagamenti",
        "opt_2": "Commerciale"
      }
    }
  }
}
```

### Response Schema:
```json
{
  "model": "clm-latest",
  "answers": {
    "task_id": {
      "type": "choice",
      "choice": "opt_0",
      "confidence": 0.945,
      "probabilities": {
        "opt_0": 0.945,
        "opt_1": 0.040,
        "opt_2": 0.015
      }
    }
  },
  "usage": {
    "billing_units": 1,
    "input_tokens": 142,
    "output_tokens": 0
  }
}
```

### `POST /v1/rank`
Ranks arbitrary candidate answers in order of semantic match:
```json
{
  "context": "Descrizione dell'errore di produzione",
  "question": "Seleziona la patch più appropriata",
  "answers": ["Riavvio container", "Rollback release", "Aumento memoria heap"]
}
```

---

## 4. Client Integration (`CLMClient`)

Located at `playground/streamlit-app/utils/clm_client.py`:
```python
from utils.clm_client import CLMClient

clm = CLMClient()
result = clm.system_one(
    state="Revoca badge e credenziali",
    questions={
        "action": {
            "type": "choice",
            "instructions": "Azione da intraprendere",
            "criteria": {"a1": "Blocco account", "a2": "Ignora"}
        }
    }
)
winner = result["answers"]["action"]["choice"]
```

---

## 5. Senior Developer Rules: CLM vs Rizzo-Flow

* **Use Rizzo-Flow when**:
  * The context is nuanced, long (up to 10k tokens), and requires deep contextual comprehension.
  * You need **explicit uncertainty detection** (`__insufficient__` token when facts are missing).
* **Use CLM when**:
  * You need extreme throughput across large pools of candidate actions.
  * You have pre-indexed categories or actions where embedding similarity provides high precision.