---
name: playground-frontend-engineer
description: Engineering and architectural guide for the Streamlit Playground frontend. Use when modifying or adding pages, enhancing Plotly charts, updating client adapters, refining token streaming telemetries, or managing frontend Docker deployments.
---

# Playground Frontend Engineer Guide & Operational Manual

## 1. Architecture & Multi-Page Layout

The frontend is a containerized Streamlit application located at `playground/streamlit-app/`. It provides a unified workbench to test, benchmark, and compare all three local models running on CPU.

### Directory Structure:
```text
playground/streamlit-app/
├── app.py                     # Entrypoint & Homepage Dashboard (health checks, system overview)
├── pages/
│   ├── 1_Rizzo_Flow.py        # Dedicated Rizzo-Flow probabilistic decision page
│   ├── 2_MiniCPM.py           # MiniCPM Coding Agent chat with Hybrid Thinking & token telemetry
│   ├── 3_CLM.py               # Dedicated CLM contrastive decision page
│   └── 4_Confronto.py         # Head-to-head comparison page (Rizzo-Flow vs CLM)
├── utils/
│   ├── rizzo_client.py        # HTTP client for Rizzo-Flow FastAPI (/v1/decisions)
│   ├── minicpm_client.py      # OpenAI + SSE streaming client with timing telemetry
│   └── clm_client.py          # HTTP client for CLM TypeSafe API (/v1/systemone, /v1/rank)
├── Dockerfile                 # Python 3.11-slim container definition
└── requirements.txt           # streamlit, requests, openai, plotly, pandas
```

---

## 2. Live Development & Hot-Reloading

* **Volume Mount**:
  * In `playground/docker-compose.yml`, the service binds `./streamlit-app:/app`.
  * **Zero Rebuilds Required**: Any change made to Python files on the Windows host is instantly detected by Streamlit via poll-based file watching.
* **Restarting Service**:
  ```bash
  wsl -d Ubuntu -e bash -c "cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground && docker compose restart streamlit"
  ```
* **Verifying Syntax / Imports Inside Container**:
  ```bash
  wsl -d Ubuntu docker exec playground-streamlit-1 python -c "import app; print('OK')"
  ```

---

## 3. UI/UX Engineering Standards & State Management

When extending or maintaining the frontend, adhere to these senior software engineering rules:

### A. Reactive Preset Population (`on_click` Callback Pattern)
* **Problem**: In Streamlit, if a widget has a `key` (e.g. `key="rf_state"`), Streamlit **ignores** `value=` once the widget has rendered on subsequent runs. Setting a decoupled variable in an `if st.button:` block will NOT update the widget text.
* **Solution**:
  1. Bind widgets directly to their keys: `st.text_area(..., key="rf_state")` without `value=`.
  2. For presets, use `on_click` callbacks that mutate the exact widget keys *before* the script renders:
     ```python
     def load_preset(state, question, dec_type, options):
         st.session_state.rf_state = state
         st.session_state.rf_question = question
         st.session_state.rf_dec_type = dec_type
         st.session_state.rf_options = options

     st.button("Scenario", on_click=load_preset, args=(...))
     ```

### B. Form Simplification (No Cluttered Multi-Boxes)
* **Rule**: Never force users to enter manual IDs, descriptions, or complex JSON blocks.
* **Implementation**:
  * Use a single `st.text_area` for candidate options formatted **one per line**.
  * The frontend automatically generates internal keys (`opt_0`, `opt_1`, etc.) and maps them back to the original strings for display.

### C. Output Mapping & Abstention
* **Rule**: Never expose raw system tokens (`opt_0`, `__insufficient__`, `__below_range__`) to the user.
* **Mapping Logic**:
  * Winner: Map `choice_id` to human label. If null, display `⚠️ Astensione / Prove Insufficienti`.
  * Bar Charts: In Plotly horizontal bar charts, replace `__insufficient__` with `⚠️ Prove Insufficienti (Non so)`.

### D. Hybrid Thinking `<think>` Visualization
* **Rule**: Distinctly separate cognitive reasoning from the executable code output.
* **Format**:
  * In `MiniCPMClient.chat_stream`, prefix reasoning tokens with `> 🧠 **Processo di Ragionamento:**\n> ` and indent subsequent lines.
  * Emit `\n\n---\n\n` before the assistant response tokens so they render seamlessly in `st.write_stream`.

### E. Token Telemetry & Performance Dashboard
* **Rule**: Provide full visibility into CPU compute characteristics for every assistant response:
  * Prompt tokens, Thinking tokens, Completion tokens.
  * Generation speed in tokens/second (`predicted_per_second`).
  * Prefill latency (`prompt_ms`) and speed (`prompt_per_second`).

### F. Head-to-Head Convergence Analysis
* In `4_Confronto.py`:
  * Present identical state and options to both Rizzo-Flow and CLM side-by-side.
  * Highlight agreement or divergence with a clear summary banner (`st.success` if choices match, `st.info` if divergent).

---

## 4. Environment Variables & Networking

All inter-container communication uses internal Docker bridge hostnames:
* `RIZZO_API_URL`: `http://rizzo-flow:8017`
* `MINICPM_API_URL`: `http://minicpm:8001`
* `CLM_API_URL`: `http://clm:8700`
* `STREAMLIT_PORT`: `8501` (mapped to `localhost:8501`)