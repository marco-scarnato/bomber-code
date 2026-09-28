# ⚡ CLM — Contrastive Language Model (TypeSafe System 1)

CLM è un'architettura decisionale System 1 basata sull'**allineamento contrastivo stato-azioni (InfoNCE)**. A differenza dei decodificatori generativi, disaggrega la rappresentazione del contesto da quella delle opzioni candidate, consentendo inferenze deterministiche e a bassissima latenza.

---

## 🔬 Principio di Funzionamento (State-Action Projection)

1. **Codifica Vettoriale Separata**: Lo stato $s$ (contesto) e ciascuna azione candidata $a_i$ vengono codificati in embedding vettoriali.
2. **Proiezione Metrica**: Una testa di proiezione addestrata mappa entrambi gli embedding in uno spazio condiviso.
3. **Calcolo Similarità & Softmax**: Lo score di affinità è calcolato tramite il prodotto scalare proiettato:
   $$\text{score}(s, a_i) = \frac{1}{\tau} \phi(s)^T \psi(a_i)$$
   La probabilità per ciascuna opzione è ottenuta normalizzando i punteggi tramite softmax.
4. **Vantaggio Competitivo**: Le azioni fisse (cataloghi, routing di ticket, FAQ) possono essere **pre-calcolate e cachate in memoria**, garantendo risposte sub-secondo (~10-50 ms).

---

## 🚀 Come Eseguire CLM

### 1. Tramite il Docker Compose unificato (Consigliato)
Dalla cartella principale del workbench:
```bash
cd playground
docker compose up -d clm
```
L'API sarà disponibile su: `http://localhost:8700`

### 2. Standalone in locale con Python
```bash
cd CLM
pip install fastapi uvicorn numpy
python tools/playground_mock.py --port 8700 --host 0.0.0.0 --cors
```

---

## 📡 Specifiche API (TypeSafe Wire Format)

* **Health Check**: `GET http://localhost:8700/health`
* **Decision Endpoint**: `POST http://localhost:8700/v1/systemone`
* **Ranking Endpoint**: `POST http://localhost:8700/v1/rank`

### Esempio Richiesta SystemOne:
```json
{
  "state": "Notifica banca: Transazione insolita da IP estero alle ore 03:00.",
  "model": "clm-latest",
  "temperature": 1.0,
  "questions": {
    "action": {
      "type": "choice",
      "instructions": "Quale misura cautelare intraprendere?",
      "criteria": {
        "opt_0": "Blocco preventivo della carta",
        "opt_1": "Notifica informativa via SMS",
        "opt_2": "Nessuna azione"
      }
    }
  }
}
```