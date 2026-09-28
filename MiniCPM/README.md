# 💬 MiniCPM5-2B — Hybrid Thinking Coding Agent

MiniCPM5-2B è un modello di frontiera compatto (SLM da 2.5B parametri) specializzato in compiti di programmazione, refactoring, tool calling e **Hybrid Thinking** nativo (catena di ragionamento cognitivo `<think>...</think>`).

---

## 🧠 Caratteristiche Chiave & "Hybrid Thinking"

* **Dual-Phase Generation**:
  1. *Thinking Phase* (`<think>`): Prima di scrivere codice, l'agente scompone il problema, individua i vincoli algoritmici (complessità temporale/spaziale) ed elenca esplicitamente tutti i casi limite (null, sequenze vuote, overflow).
  2. *Action Phase*: Emette codice tipizzato, documentato e pronto per la produzione o patch unificate in formato `git diff`.
* **Throughput Eccellente su CPU**:
  * Velocità di generazione: **~22 - 25 token/secondo**.
  * Velocità di lettura del prompt (prefill): **~75 - 100 token/secondo**.
* **Finestra di Contesto Estesa**:
  * Configurato nativamente per operare fino a **32.768 token (32k)** di contesto con un consumo di memoria di soli **~2.26 GB di RAM**.

---

## 🛠️ Tool Calling & Parser XML

Nella cartella [`tool_parsers/`](tool_parsers/) è incluso il parser ufficiale [`minicpm5xml_tool_parser.py`](tool_parsers/minicpm5xml_tool_parser.py) per estrarre ed eseguire chiamate a tool esterni formattate in XML:
```xml
<function name="execute_bash">
  <param name="command">pytest tests/test_core.py</param>
</function>
```

---

## 🚀 Come Eseguire MiniCPM5-2B

### 1. Tramite il Docker Compose unificato (Consigliato)
Nel workbench, MiniCPM viene servito ad altissima efficienza tramite l'immagine ufficiale `llama-server` di llama.cpp:
```bash
cd playground
docker compose up -d minicpm
```
L'API OpenAI-compatibile sarà disponibile su: `http://localhost:8001/v1`

### 2. Esempio Chiamata API (cURL)
```bash
curl -s http://localhost:8001/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "/think Implement a quicksort algorithm in Python"}],
    "max_tokens": 1024,
    "temperature": 0.3
  }'
```