# 🎯 Rizzo-Flow — System 1 Probabilistic Decision Engine

Rizzo-Flow è un motore decisionale probabilistico ad alte prestazioni basato su **Spark-X2.5-1.7B**.
A differenza dei modelli linguistici tradizionali che generano testo parola per parola, Rizzo-Flow opera secondo il paradigma **System 1**: valuta il contesto ed emette decisioni, scoring e classificazioni matematiche con **zero token generati**.

---

## ⚡ Come Funziona (Logit-Based Inference)

1. **Singolo Forward Pass**: Il modello legge l'intero testo di contesto (*state*) e l'istruzione decisionale in un unico passaggio in avanti.
2. **Ispezione dei Logit Terminali**: Legge direttamente i logit terminali corrispondenti ai token delle opzioni candidate fornite.
3. **Distribuzione Softmax Calibrata**: Applica una softmax ristretta esclusivamente ai candidati, restituendo probabilità percentuali esatte (es. Opzione A: 82%, Opzione B: 18%).
4. **Rilevamento dell'Astensione (`__insufficient__`)**: Se il testo non contiene evidenze sufficienti per decidere in modo affidabile, il modello assegna probabilità all'opzione di astensione, evitando allucinazioni.

---

## 📦 Modello Attivo & Prestazioni Hardware

* **Modello**: `XHToken/Spark-X2.5-1.7B` fine-tuned con Rizzo-Flow LoRA.
* **Formato**: GGUF `q4_k_m` (`spark-x2.5-1.7b-rizzo-flow-lora-q4_k_m.gguf`, ~1.1 GB).
* **Hardware**: Esecuzione 100% su **CPU** (zero VRAM richiesta).
* **Consumo RAM**: **~1.29 GB**.
* **Latenza Media**: **~2.5 - 3.0 secondi** per decisione.

---

## 🚀 Come Eseguire Rizzo-Flow

### 1. Tramite il Docker Compose unificato (Consigliato)
Dalla cartella principale del workbench:
```bash
cd playground
docker compose up -d rizzo-flow
```
L'API sarà disponibile su: `http://localhost:8017`

### 2. Standalone in locale con `uv`
```bash
cd rizzo-flow
uv sync --locked
uv run rizzo download --size 1.7b --quant q4_k_m
uv run rizzo serve --host 0.0.0.0 --port 8017 --size 1.7b --quant q4_k_m
```

---

## 📡 Specifiche API

* **Health Check**: `GET http://localhost:8017/health`
* **Decision Endpoint**: `POST http://localhost:8017/v1/decisions`

### Esempio Payload JSON:
```json
{
  "state": "Il cliente richiede reset credenziali per mancato accesso.",
  "questions": {
    "triage": {
      "type": "choice",
      "instructions": "A quale reparto appartiene il ticket?",
      "options": [
        {"id": "opt_0", "description": "Assistenza Tecnica e Login"},
        {"id": "opt_1", "description": "Fatturazione e Pagamenti"}
      ],
      "policy": { "allow_abstain": true }
    }
  }
}
```

Per gli schemi completi di richiesta e risposta, consulta [`request.schema.json`](request.schema.json) e [`response.schema.json`](response.schema.json).