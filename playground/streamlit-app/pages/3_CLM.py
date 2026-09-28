import streamlit as st
import pandas as pd
import plotly.express as px
import time
from utils.clm_client import CLMClient

st.set_page_config(page_title="CLM Decisions", page_icon="⚡", layout="wide")
st.title("⚡ CLM — Contrastive Language Model")
st.caption("Decisioni e ranking probabilistici basati su **allineamento contrastivo vettoriale (InfoNCE)** secondo lo standard TypeSafe Wire Format.")

clm = CLMClient()

# Stato della sessione ufficiale per i campi
if "clm_state" not in st.session_state:
    st.session_state.clm_state = ""
if "clm_question" not in st.session_state:
    st.session_state.clm_question = ""
if "clm_options" not in st.session_state:
    st.session_state.clm_options = ""

# Callback per caricare gli scenari a 1 click
def load_clm_preset(state: str, question: str, options: str):
    st.session_state.clm_state = state
    st.session_state.clm_question = question
    st.session_state.clm_options = options

# --- Sidebar: Scenari a 1 Click ---
with st.sidebar:
    st.header("⚡ Scenari Veloci (1 Click)")
    st.write("Seleziona uno scenario reale per testare CLM:")

    st.button(
        "🔐 Sicurezza & Accessi",
        use_container_width=True,
        on_click=load_clm_preset,
        args=(
            "Il dipendente ha terminato il periodo di preavviso e ha consegnato il badge aziendale. Richiesta chiusura credenziali VPN e cancellazione account Active Directory.",
            "Quale azione immediata eseguire?",
            "Revoca Immediata Accessi VPN e AD\nSospensione Temporanea Account\nNessuna Azione (Invia Promemoria)"
        )
    )

    st.button(
        "💳 Triage Pagamenti / Antifrode",
        use_container_width=True,
        on_click=load_clm_preset,
        args=(
            "Segnalazione POS: Carta inserita con 3 PIN errati consecutivi alle 04:15 di notte da un terminale non abituale in paese estero.",
            "Quale intervento applicare sulla transazione?",
            "Blocco Preventivo Carta e Chiamata Utente\nConsenti Transazione con Notifica SMS\nIgnora e archivia segnalazione"
        )
    )

    st.button(
        "⭐ Valutazione Gravità Bug",
        use_container_width=True,
        on_click=load_clm_preset,
        args=(
            "Errore log di sistema: Database connection pool esaurito. Il microservizio di autenticazione restituisce 503 Service Unavailable a tutti i client.",
            "Qual è la priorità di intervento richiesta?",
            "P0 - Blocco Critico di Produzione\nP1 - Degrado Prestazionale Elevato\nP2 - Problema Ordinario a Basso Impatto"
        )
    )

    st.divider()
    st.subheader("⚙️ Parametri Modello")
    selected_model = st.selectbox(
        "Variante CLM",
        ["clm-latest", "clm-raw"],
        index=0,
        help="clm-latest usa la testa di proiezione InfoNCE addestrata. clm-raw usa lo spazio n-gram/embedding grezzo per ablazione."
    )
    temperature = st.slider("Temperature", 0.1, 2.0, 1.0, 0.1, help="Controlla la concentrazione della distribuzione softmax.")

# --- Layout Principale ---
col_in, col_out = st.columns([1, 1], gap="large")

with col_in:
    st.subheader("1. Inserisci il Contesto (Stato)")
    state_input = st.text_area(
        "Testo da analizzare (email, log, transazione, evento)",
        key="clm_state",
        height=140,
        placeholder="Es: Notifica server di allerta sicurezza..."
    )

    st.subheader("2. Definisci la Decisione")
    question_input = st.text_input(
        "Domanda o Istruzione",
        key="clm_question",
        placeholder="Es: Qual è l'azione corretta da compiere?"
    )

    options_raw = st.text_area(
        "Opzioni candidate (una per riga)",
        key="clm_options",
        height=130,
        placeholder="Opzione 1\nOpzione 2\nOpzione 3",
        help="Inserisci una lista di alternative candidate. CLM calcolerà l'allineamento vettoriale su ciascuna."
    )
    options_list = [o.strip() for o in options_raw.split("\n") if o.strip()]

    execute_btn = st.button("🚀 Elabora con CLM", type="primary", use_container_width=True)

with col_out:
    st.subheader("3. Risultato & Analisi CLM")

    if execute_btn:
        if not state_input.strip():
            st.error("Inserisci prima il contesto nel box 1.")
        elif not question_input.strip():
            st.error("Inserisci la domanda nel box 2.")
        elif len(options_list) < 2:
            st.error("Inserisci almeno 2 opzioni candidate (una per riga).")
        else:
            with st.spinner("Calcolo allineamento vettoriale in corso..."):
                t0 = time.time()
                # Costruzione wire schema TypeSafe
                criteria_dict = {f"opt_{i}": opt for i, opt in enumerate(options_list)}
                payload_questions = {
                    "task": {
                        "type": "choice",
                        "instructions": question_input,
                        "criteria": criteria_dict
                    }
                }

                try:
                    response = clm.system_one(
                        state=state_input,
                        questions=payload_questions,
                        model=selected_model,
                        temperature=temperature
                    )
                    elapsed = time.time() - t0
                    answer = response.get("answers", {}).get("task", {})
                    usage = response.get("usage", {})

                    winner_id = answer.get("choice")
                    winner_label = criteria_dict.get(winner_id, winner_id) if winner_id else "N/A"

                    st.success("✅ Decisione Completata con Successo")
                    st.metric("🏆 Scelta Ottimale CLM", winner_label)

                    # Grafico delle probabilità
                    probs = answer.get("probabilities", {})
                    if probs:
                        chart_data = []
                        for k, p in probs.items():
                            chart_data.append({
                                "Opzione": criteria_dict.get(k, k),
                                "Probabilità (%)": round(p * 100, 2)
                            })
                        
                        df_chart = pd.DataFrame(chart_data)
                        fig = px.bar(
                            df_chart,
                            x="Probabilità (%)",
                            y="Opzione",
                            orientation="h",
                            text="Probabilità (%)",
                            title="Distribuzione di Probabilità Calcolata",
                            color_discrete_sequence=["#10B981"]
                        )
                        fig.update_layout(yaxis={"categoryorder": "total ascending"}, height=270)
                        st.plotly_chart(fig, use_container_width=True)

                    st.divider()
                    st.markdown("#### ⏱️ Metriche Tecniche")
                    m1, m2, m3 = st.columns(3)
                    m1.metric("Latenza API", f"{elapsed*1000:.1f} ms")
                    conf = answer.get("confidence")
                    m2.metric("Confidenza", f"{conf*100:.1f}%" if conf is not None else "N/A")
                    m3.metric("Token Input", usage.get("input_tokens", 0))

                    with st.expander("🔍 Risposta Wire JSON TypeSafe"):
                        st.json(response)

                except Exception as e:
                    st.error(f"Errore nella chiamata a CLM: {str(e)}")
    else:
        st.info("Compila i campi a sinistra o premi uno scenario rapido nella barra laterale, poi clicca su 'Elabora con CLM'.")