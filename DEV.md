# 🛠️ Operational Runbook & Developer Guide (DEV.md)

Guida operativa completa per la gestione, l'avvio, il monitoraggio e lo spegnimento dell'ambiente multi-modello locale in Docker su WSL2.

---

## 1. Mappa dei Servizi & Porte

| Servizio Docker | Container Name | Porta Host | Motore / Backend | Ruolo & Note |
| :--- | :--- | :--- | :--- | :--- |
| **Streamlit UI** | `playground-streamlit-1` | `8501` | Python 3.11 / Streamlit | Dashboard interattiva, hot-reload attivo |
| **Rizzo-Flow** | `playground-rizzo-flow-1` | `8017` | Spark-X2.5-1.7B / llama.cpp | System 1 logit engine, zero token generati |
| **MiniCPM** | `playground-minicpm-1` | `8001` | MiniCPM5-2B / llama-server | System 2 Coding Agent con `<think>` |
| **CLM** | `playground-clm-1` | `8700` | Contrastive / TypeSafe API | System 1 allineamento vettoriale InfoNCE |

---

## 2. Comandi di Ciclo di Vita (Lifecycle)

Tutti i comandi vanno eseguiti all'interno della cartella `playground/`.

### Da terminale WSL (Bash):
```bash
cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground

# 🟢 Avviare tutti i servizi in background
docker compose up -d

# 🔄 Applicare modifiche a .env (ricrea i container con i nuovi parametri)
docker compose up -d

# 🔁 Riavviare solo un singolo servizio (es. Streamlit dopo una modifica)
docker compose restart streamlit

# 🔨 Ricostruire l'immagine ed avviare (es. dopo modifica al Dockerfile o requirements.txt)
docker compose up -d --build streamlit

# ⏸️ Sospendere i servizi (senza eliminare i container)
docker compose stop

# 🛑 Abbattere l'ambiente (arresta e rimuove i container)
docker compose down
```

### Da Windows PowerShell:
```powershell
# 🟢 Avvio in background
wsl -d Ubuntu -e bash -c "cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground && docker compose up -d"

# 🔄 Ricarica modifiche .env
wsl -d Ubuntu -e bash -c "cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground && docker compose up -d"

# 🔁 Riavvio rapido Streamlit
wsl -d Ubuntu -e bash -c "cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground && docker compose restart streamlit"

# 🛑 Stop di tutti i servizi
wsl -d Ubuntu -e bash -c "cd /mnt/c/Users/m.scarnato/Personale/jev-try/playground && docker compose down"
```

---

## 3. Monitoraggio Risorse & Log

### Monitorare RAM e CPU in Tempo Reale:
Visualizza istantaneamente quanto consumano i singoli container (fondamentale per verificare di rimanere entro il budget di 32 GB):
```bash
# Da WSL:
docker stats

# Da PowerShell:
wsl -d Ubuntu docker stats --no-stream --format "table {{.Name}}\t{{.MemUsage}}\t{{.CPUPerc}}"
```

### Ispezione Log:
```bash
# Log in streaming di tutti i servizi combinati
docker compose logs -f

# Log specifici di un servizio con le ultime 50 righe
docker logs --tail 50 -f playground-streamlit-1
docker logs --tail 50 -f playground-minicpm-1
docker logs --tail 50 -f playground-rizzo-flow-1
docker logs --tail 50 -f playground-clm-1
```

---

## 4. Test e Health Check Rapidi

Puoi verificare in qualunque momento che i 4 endpoint HTTP rispondano correttamente:

```bash
# 1. Frontend Streamlit (HTTP 200)
curl -s -I http://localhost:8501

# 2. Rizzo-Flow (Stato del modello Spark-1.7B)
curl -s http://localhost:8017/health

# 3. MiniCPM (Stato di llama-server)
curl -s http://localhost:8001/health

# 4. CLM (Stato del server TypeSafe)
curl -s http://localhost:8700/health
```

---

## 5. Test Sintassi & Import Interno (Debug)

Se modifichi il codice Streamlit o i client in `utils/` e vuoi verificare che non ci siano errori di sintassi prima di aprire il browser:
```bash
# Test importazione homepage ed utility
wsl -d Ubuntu docker exec playground-streamlit-1 python -c "import app; print('✅ App OK')"

# Test importazione di tutte le pagine
wsl -d Ubuntu docker exec playground-streamlit-1 python -c "import importlib.util; [importlib.util.spec_from_file_location(f, f'pages/{f}').loader.load_module() for f in ['1_Rizzo_Flow.py', '2_MiniCPM.py', '3_CLM.py', '4_Confronto.py']]; print('✅ Tutte le pagine OK')"
```

---

## 6. Configurazione Parametri (`playground/.env`)

| Variabile | Default | Descrizione |
| :--- | :--- | :--- |
| `MINICPM_CTX_SIZE` | `32768` | Finestra di contesto totale (32k token = prompt + thinking + codice) |
| `MINICPM_THREADS` | `8` | Core logici della CPU dedicati alla computazione |
| `RIZZO_SIZE` | `1.7b` | Taglia del modello Rizzo-Flow (`1.7b` ultraleggero o `4b`) |
| `RIZZO_QUANT` | `q4_k_m` | Quantizzazione GGUF (bilanciamento ottimale qualità/RAM) |
| `RIZZO_DEVICE` | `cpu` | Dispositivo di calcolo (`cpu`) |
| `STREAMLIT_PORT` | `8501` | Porta esposta per l'interfaccia web |
| `MINICPM_PORT` | `8001` | Porta esposta per llama-server |
| `RIZZO_PORT` | `8017` | Porta esposta per FastAPI Rizzo-Flow |

> [!NOTE]
> Ogni volta che modifichi un parametro in `.env` (come `MINICPM_CTX_SIZE`), esegui sempre `docker compose up -d` affinché Docker ricrei il container con i nuovi argomenti CLI.