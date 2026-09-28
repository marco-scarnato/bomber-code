import streamlit as st
import pandas as pd
import plotly.express as px
from utils.rizzo_client import RizzoClient

st.set_page_config(page_title="Rizzo-Flow Decisions", page_icon="🎯", layout="wide")
st.title("🎯 Rizzo-Flow — Decisioni Probabilistiche")
st.caption("Modello attivo: **Spark-X2.5-1.7B (Q4_K_M)** su CPU — Zero token generati, decisioni basate sui logit.")

rizzo = RizzoClient()

DEC_CHOICE = "Scelta Multipla (Choice)"
DEC_BOOL = "Sì / No (Boolean)"
DEC_SCORE = "Livello / Valutazione (Score)"
DEC_OPTIONS = [DEC_CHOICE, DEC_BOOL, DEC_SCORE]

# Inizializzazione session_state per i widget con le loro chiavi ufficiali
if "rf_state" not in st.session_state:
    st.session_state.rf_state = ""
if "rf_question" not in st.session_state:
    st.session_state.rf_question = ""
if "rf_dec_type" not in st.session_state:
    st.session_state.rf_dec_type = DEC_CHOICE
if "rf_options" not in st.session_state:
    st.session_state.rf_options = ""

# Callback per caricare gli scenari a 1 click in modo reattivo
def load_rf_preset(state: str, question: str, dec_type: str, options: str):
    st.session_state.rf_state = state
    st.session_state.rf_question = question
    st.session_state.rf_dec_type = dec_type
    st.session_state.rf_options = options

# --- Sidebar: Esempi Pronti a 1 Click ---
with st.sidebar:
    st.header("⚡ Scenari Veloci (1 Click)")
    st.write("Seleziona uno scenario reale preconfigurato:")
    
    st.button(
        "📩 Triage Reparto Ticket",
        use_container_width=True,
        on_click=load_rf_preset,
        args=(
            "Il cliente segnala: 'Buongiorno, non riesco ad accedere alla piattaforma. Inserisco email e password corrette ma ricevo errore 500. Il blocco impedisce al team commerciale di lavorare.'",
            "In quale reparto aziendale deve essere smistato questo ticket?",
            DEC_CHOICE,
            "Assistenza Tecnica e Login\nFatturazione e Pagamenti\nCommerciale e Vendite"
        )
    )

    st.button(
        "🚨 Moderazione / Rilevamento Problema",
        use_container_width=True,
        on_click=load_rf_preset,
        args=(
            "Messaggio utente: 'Ottimo servizio, l'assistenza ha risolto la mia pratica in 10 minuti con grande cortesia.'",
            "Il messaggio contiene lamentele, problemi o sentiment negativo?",
            DEC_BOOL,
            ""
        )
    )

    st.button(
        "⭐ Valutazione Urgenza (Score)",
        use_container_width=True,
        on_click=load_rf_preset,
        args=(
            "Allarme server: Utilizzo memoria al 99%, timeout su API gateway, database non risponde ai client di produzione da 15 minuti.",
            "Qual è il livello di gravità dell'incidente?",
            DEC_SCORE,
            "Bassa (nessun impatto bloccante)\nMedia (servizio rallentato ma funzionante)\nCritica (disservizio totale in produzione)"
        )
    )

    st.divider()
    st.subheader("💡 Come funziona?")
    st.info(
        "Rizzo-Flow non scrive una risposta prolissa. Valuta matematicamente "
        "tutte le opzioni simultaneamente e restituisce la probabilità esatta per ciascuna, "
        "rilevando anche se l'evidenza nel testo è insufficiente."
    )

# --- Form Principale Semplificato ---
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("1. Inserisci il Contesto (Stato)")
    state_input = st.text_area(
        "Testo da analizzare (email, log, articolo, segnalazione)",
        key="rf_state",
        height=140,
        placeholder="Es: Il cliente chiede rimborso per la fattura n. 124..."
    )
    
    st.subheader("2. Definisci la Decisione")
    dec_type = st.selectbox(
        "Tipo di risposta attesa",
        DEC_OPTIONS,
        key="rf_dec_type"
    )
    
    question_input = st.text_input(
        "Domanda",
        key="rf_question",
        placeholder="Es: Qual è la categoria corretta?"
    )
    
    # Assicura persistenza di rf_options in caso di unmount precedente
    if "rf_options" not in st.session_state:
        st.session_state.rf_options = ""

    options_list = []
    if dec_type == DEC_CHOICE:
        options_raw = st.text_area(
            "Opzioni possibili (una per riga)",
            key="rf_options",
            height=110,
            placeholder="Opzione A\nOpzione B\nOpzione C",
            help="Scrivi semplicemente le opzioni possibili, una sotto l'altra. Il frontend le mapperà automaticamente."
        )
        options_list = [line.strip() for line in options_raw.split("\n") if line.strip()]
        
    elif dec_type == DEC_SCORE:
        options_raw = st.text_area(
            "Livelli ordinati dal più basso al più alto (uno per riga)",
            key="rf_options",
            height=110,
            placeholder="1. Basso\n2. Medio\n3. Alto",
            help="Inserisci da 2 a 10 livelli in ordine crescente di gravità o intensità."
        )
        options_list = [line.strip() for line in options_raw.split("\n") if line.strip()]

    else:
        st.info("ℹ️ Per decisioni Sì / No non sono richieste opzioni aggiuntive (Vero/Falso gestiti automaticamente).")

    allow_abstain = st.checkbox(
        "Consenti astensione ('Non so') se le prove sono insufficienti",
        value=True,
        help="Se attivo, il modello assegna probabilità all'opzione '__insufficient__' qualora il testo non permetta di decidere con sicurezza."
    )

    execute_btn = st.button("🚀 Elabora Decisione", type="primary", use_container_width=True)

with col_out:
    st.subheader("3. Risultato & Analisi")
    
    if execute_btn:
        if not state_input.strip():
            st.error("Inserisci prima il testo di contesto nel box 1.")
        elif not question_input.strip():
            st.error("Inserisci la domanda nel box 2.")
        elif dec_type in (DEC_CHOICE, DEC_SCORE) and len(options_list) < 2:
            st.error("Inserisci almeno 2 opzioni (una per riga).")
        else:
            # Costruzione payload pulito
            questions_payload = {}
            mapping_dict = {}
            
            if dec_type == DEC_CHOICE:
                opts = []
                for idx, opt_label in enumerate(options_list):
                    opt_id = f"opt_{idx}"
                    opts.append({"id": opt_id, "description": opt_label})
                    mapping_dict[opt_id] = opt_label
                
                questions_payload["decision"] = {
                    "type": "choice",
                    "instructions": question_input,
                    "options": opts,
                    "policy": {"allow_abstain": allow_abstain}
                }
                
            elif dec_type == DEC_BOOL:
                questions_payload["decision"] = {
                    "type": "boolean",
                    "instructions": question_input,
                    "true_description": "Affermazione Vera / Sì",
                    "false_description": "Affermazione Falsa / No",
                    "policy": {"allow_abstain": allow_abstain}
                }
                mapping_dict = {"true": "Sì (Vero)", "false": "No (Falso)"}
                
            elif dec_type == DEC_SCORE:
                questions_payload["decision"] = {
                    "type": "score",
                    "instructions": question_input,
                    "levels": options_list,
                    "policy": {"allow_abstain": allow_abstain}
                }
                for idx, lvl in enumerate(options_list):
                    mapping_dict[str(idx)] = lvl

            with st.spinner("Calcolo logit su CPU in corso..."):
                try:
                    result = rizzo.decide(state_input, questions_payload)
                    answer = result.get("answers", {}).get("decision", {})
                    timing = result.get("timing", {})
                    
                    status = answer.get("status", "unknown")
                    
                    # Badge di stato
                    if status == "ok":
                        st.success("✅ Decisione Presa con Successo")
                    elif status == "insufficient_evidence":
                        st.warning("⚠️ Evidenza Insufficiente: Il testo non contiene prove sufficienti per scegliere.")
                    else:
                        st.info(f"Stato: {status}")

                    # Risultato primario chiaro
                    if dec_type == DEC_CHOICE:
                        chosen_id = answer.get("choice")
                        chosen_label = mapping_dict.get(chosen_id, chosen_id) if chosen_id else "Nessuna opzione scelta (Astensione)"
                        st.metric("Scelta Vincitrice", chosen_label)
                        
                    elif dec_type == DEC_BOOL:
                        val = answer.get("value")
                        if val is True:
                            st.metric("Esito", "Sì (Vero)")
                        elif val is False:
                            st.metric("Esito", "No (Falso)")
                        else:
                            st.metric("Esito", "Incerto / Non determinabile")
                            
                    elif dec_type == DEC_SCORE:
                        sc = answer.get("score")
                        st.metric("Punteggio Atteso Calcolato", f"{sc:.2f}" if sc is not None else "N/A")

                    # Grafico di probabilità pulito con etichette umane
                    probs = answer.get("probabilities", {})
                    if probs:
                        chart_data = []
                        for k, p in probs.items():
                            if k == "__insufficient__":
                                label = "⚠️ Prove Insufficienti (Non so)"
                            elif k in mapping_dict:
                                label = mapping_dict[k]
                            else:
                                label = k
                            chart_data.append({"Opzione": label, "Probabilità (%)": round(p * 100, 2)})
                        
                        df = pd.DataFrame(chart_data)
                        fig = px.bar(
                            df, 
                            x="Probabilità (%)", 
                            y="Opzione", 
                            orientation="h",
                            text="Probabilità (%)",
                            title="Distribuzione Matematica delle Probabilità"
                        )
                        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=280)
                        st.plotly_chart(fig, use_container_width=True)

                    # Metriche di Certezza & Tempo
                    st.divider()
                    st.markdown("#### ⏱️ Breakdown Tecnico e Tempi")
                    t1, t2, t3 = st.columns(3)
                    
                    prefill_t = timing.get("prefill_seconds", 0)
                    infer_t = timing.get("inference_seconds", 0)
                    total_t = timing.get("total_seconds", 0)
                    
                    t1.metric("Lettura Contesto (Prefill)", f"{prefill_t:.2f} s")
                    t2.metric("Calcolo Logit", f"{infer_t:.2f} s")
                    t3.metric("Latenza Totale", f"{total_t:.2f} s")

                    unc = answer.get("uncertainty", {})
                    u1, u2 = st.columns(2)
                    u1.metric("Confidenza Massima", f"{unc.get('top_probability', 0)*100:.1f}%")
                    u2.metric("Entropia (Incertezza)", f"{unc.get('entropy_nats', 0):.2f} nats")
                    
                    with st.expander("🔍 Dati Tecnici JSON"):
                        st.json(result)

                except Exception as e:
                    st.error(f"Errore nella chiamata a Rizzo-Flow: {str(e)}")
    else:
        st.info("Compila i campi a sinistra o premi uno scenario veloce nella barra laterale, poi clicca su 'Elabora Decisione'.")