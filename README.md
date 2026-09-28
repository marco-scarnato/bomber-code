# ⚡ Bomber Code — Frontier AI Playground & Autonomous Coding Workbench

Un ambiente locale e modulare per eseguire, benchmarkare ed orchestrare modelli AI di frontiera interamente su **CPU (senza GPU/VRAM richiesta)** tramite container Docker leggeri su **WSL2** (budget RAM: 32 GB).

---

## 🎯 Architettura & Modelli Integrati

Il workbench unifica l'inferenza **System 1** (decisioni probabilistiche istantanee) e **System 2** (ragionamento e sintesi di codice):

| Modello | Tipo / Architettura | Serving Engine | RAM | Ruolo Principale |
| :--- | :--- | :--- | :--- | :--- |
| **Rizzo-Flow** | Spark-X2.5-1.7B (Q4_K_M) | llama.cpp / FastAPI | ~1.29 GB | **System 1**: Decisioni terminali via logit, 0 token generati, stima incertezza (entropia) e astensione (`__insufficient__`). |
| **MiniCPM5-2B** | MiniCPM5-2B (Q4_K_M) | llama-server (OpenAI API) | ~2.26 GB | **System 2**: Coding Agent autonomo con **Hybrid Thinking** (`<think>`), telemetria token (prompt/think/output) e finestra di contesto a **32k token**. |
| **CLM** | Contrastive Model (InfoNCE) | FastAPI (TypeSafe Schema) | ~46 MB | **System 1**: Allineamento vettoriale stato-azioni, ranking e classificazione istantanea. |
| **Streamlit UI** | Multi-Page App | Python 3.11 | ~60 MB | Dashboard unificata con test singoli, grafici Plotly e **Confronto Testa a Testa**. |

---

## 🚀 Avvio Rapido (Quickstart)

### Prerequisiti
* Windows con **WSL2** e **Docker Engine** attivo.
* Almeno 8 GB di RAM libera (il consumo totale di tutti i container insieme è di appena **~3.6 GB**).

### 1. Clonare ed entrare nella cartella
```bash
git clone https://github.com/marco-scarnato/bomber-code.git
cd bomber-code/playground
```

### 2. Configurare le variabili d'ambiente
```bash
cp .env.example .env
```

### 3. Avviare con Docker Compose
```bash
docker compose up -d
```

Apri il browser su: 👉 **[http://localhost:8501](http://localhost:8501)**

---

## 🧭 Navigazione della Web App

* **Home Dashboard** (`app.py`): Stato di salute in tempo reale di tutti i motori e panoramica architetturale.
* **1. Rizzo-Flow** (`1_Rizzo_Flow.py`): Classificazione ticket, moderazione sentiment e valutazione gravità con form semplificato "un'opzione per riga" e breakdown delle latenze.
* **2. MiniCPM** (`2_MiniCPM.py`): Chat e Coding Agent con visualizzazione del processo di ragionamento interno (`> 🧠 Processo di Ragionamento:`), telemetria token al secondo e benchmark rapidi per coding.
* **3. CLM** (`3_CLM.py`): Test autonomo del Contrastive Language Model secondo lo standard wire TypeSafe.
* **4. Confronto Diretto** (`4_Confronto.py`): Esecuzione parallela testa a testa Rizzo-Flow vs CLM sugli stessi contesti con grafico di convergenza.

---

## 🛠️ Documentazione & Runbook Operativo

* Consulta **[`DEV.md`](DEV.md)** per la guida dettagliata con tutti i comandi per:
  * Avviare, riavviare e spegnere l'infrastruttura.
  * Monitorare RAM e CPU in tempo reale (`docker stats`).
  * Ispezionare log e testare gli health-check HTTP.
* Consulta le cartelle **[`.agents/skills/`](.agents/skills/)** per le 4 skill specializzate pronte per il pairing con agenti di programmazione.