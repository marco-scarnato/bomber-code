import streamlit as st
import pandas as pd
import plotly.express as px
import time
from utils.rizzo_client import RizzoClient
from utils.clm_client import CLMClient

st.set_page_config(page_title="Confronto Modelli", page_icon="🥊", layout="wide")
st.title("🥊 Confronto Diretto — Rizzo-Flow vs CLM")
st.caption("Confronta fianco a fianco i due approcci System One sullo stesso identico testo, domanda e opzioni candidate.")

rizzo = RizzoClient()
clm = CLMClient()

# Stato della sessione ufficiale per i campi di input
if "cmp_state" not in st.session_state:
    st.session_state.cmp_state = "Il cliente scrive: 'Ho urgente bisogno di revocare l'accesso dell'utente mario.rossi@company.com perché ha rassegnato le dimissioni ed è un amministratore di sistema con privilegi di root.'"
if "cmp_question" not in st.session_state:
    st.session_state.cmp_question = "Qual è la coda e il reparto corretto per gestire questa richiesta?"
if "cmp_options" not in st.session_state:
    st.session_state.cmp_options = "Sicurezza e Gestione Accessi (SecOps)\nSupporto IT Ordinario\nRisorse Umane e Payroll"

# Callback per caricare gli scenari a 1 click in modo reattivo
def load_cmp_preset(state: str, question: str, options: str):
    st.session_state.cmp_state = state
    st.session_state.cmp_question = question
    st.session_state.cmp_options = options

# --- Sidebar: Scenari di Benchmark a 1 Click ---
with st.sidebar:
    st.header("⚡ Scenari di Benchmark")
    st.write("Carica scenari di test con un solo click:")
    
    st.button(
        "🔐 Revoca Accesso Amministratore",
        use_container_width=True,
        on_click=load_cmp_preset,
        args=(
            "Il cliente scrive: 'Ho urgente bisogno di revocare l'accesso dell'utente mario.rossi@company.com perché ha rassegnato le dimissioni ed è un amministratore di sistema con privilegi di root.'",
            "Quale reparto deve prendere in carico questa richiesta di sicurezza?",
            "Sicurezza e Gestione Accessi (SecOps)\nSupporto Helpdesk Standard\nRisorse Umane e Payroll"
        )
    )

    st.button(
        "💳 Disputa Transazione Sospetta",
        use_container_width=True,
        on_click=load_cmp_preset,
        args=(
            "Notifica banca: 'Transazione sospetta di 1.250 EUR rilevata alle ore 03:40 da IP estero non riconosciuto sulla carta prepagata del cliente.'",
            "Quale azione preventiva immediata deve essere intrapresa?",
            "Blocco Immediato Carta e Allerta Antifrode\nRichiesta Conferma tramite SMS\nNessuna Azione (Transazione Leceita)"
        )
    )

    st.button(
        "🐛 Severità Incidente Produzione",
        use_container_width=True,
        on_click=load_cmp_preset,
        args=(
            "Crash report: 'NullPointerException nel modulo di checkout durante il pagamento con carta. Tutti gli ordini falliscono con errore HTTP 500.'",
            "Qual è il livello di severità dell'incidente?",
            "Critico (Blocco Totale Vendite Produzione)\nMedio (Degrado Parziale Funzionalità)\nBasso (Problema Cosmetico Minore)"
        )
    )

    st.divider()
    st.subheader("🔬 Come Funzionano?")
    st.markdown(
        """
        - **Rizzo-Flow**: Esegue Spark-X2.5 (1.7B) e ispeziona i **logit terminali** sui token candidati. Genera 0 token e supporta l'astensione (`__insufficient__`).
        - **CLM**: Usa l'apprendimento contrastivo (**InfoNCE**). Calcola la similarità coseno proiettata tra l'embedding dello *stato* e gli embedding delle *opzioni*.
        """
    )

# --- Layout Form di Configurazione ---
st.subheader("1. Configura lo Scenario Comune")
col_s1, col_s2 = st.columns([1.2, 1], gap="medium")

with col_s1:
    c_state = st.text_area("Contesto (Stato)", key="cmp_state", height=120)
    c_question = st.text_input("Domanda", key="cmp_question")

with col_s2:
    c_options_raw = st.text_area(
        "Opzioni candidate (una per riga)",
        key="cmp_options",
        height=185,
        help="Inserisci le alternative su cui i due modelli dovranno decidere."
    )
    c_options = [o.strip() for o in c_options_raw.split("\n") if o.strip()]

run_comparison = st.button("🥊 Esegui Confronto Testa a Testa", type="primary", use_container_width=True)

if run_comparison:
    if not c_state.strip() or not c_question.strip() or len(c_options) < 2:
        st.error("Inserisci stato, domanda e almeno 2 opzioni candidate.")
    else:
        st.divider()
        st.subheader("2. Risultati del Confronto")

        col_r, col_c = st.columns(2, gap="large")

        r_winner_label = None
        c_winner_label = None

        # --- Rizzo-Flow Execution ---
        with col_r:
            st.markdown("### 🎯 Rizzo-Flow (Spark-1.7B)")
            with st.spinner("Rizzo-Flow in elaborazione (logit pass)..."):
                t0 = time.time()
                rizzo_opts = [{"id": f"opt_{i}", "description": opt} for i, opt in enumerate(c_options)]
                mapping = {f"opt_{i}": opt for i, opt in enumerate(c_options)}
                
                payload_rizzo = {
                    "benchmark": {
                        "type": "choice",
                        "instructions": c_question,
                        "options": rizzo_opts,
                        "policy": {"allow_abstain": True}
                    }
                }
                
                try:
                    r_res = rizzo.decide(c_state, payload_rizzo)
                    r_elapsed = time.time() - t0
                    ans = r_res.get("answers", {}).get("benchmark", {})
                    timing = r_res.get("timing", {})
                    
                    winner_id = ans.get("choice")
                    r_winner_label = mapping.get(winner_id, winner_id) if winner_id else "⚠️ Astensione (Non so)"
                    
                    st.metric("🏆 Scelta Rizzo-Flow", r_winner_label)
                    
                    # Probabilità
                    probs = ans.get("probabilities", {})
                    r_chart = []
                    for k, p in probs.items():
                        lbl = mapping.get(k, "⚠️ Prove Insufficienti" if k == "__insufficient__" else k)
                        r_chart.append({"Opzione": lbl, "Probabilità (%)": round(p * 100, 2)})
                    
                    fig_r = px.bar(
                        pd.DataFrame(r_chart),
                        x="Probabilità (%)",
                        y="Opzione",
                        orientation="h",
                        text="Probabilità (%)",
                        title="Distribuzione Probabilità Rizzo-Flow",
                        color_discrete_sequence=["#4F46E5"]
                    )
                    fig_r.update_layout(yaxis={"categoryorder": "total ascending"}, height=260)
                    st.plotly_chart(fig_r, use_container_width=True)

                    rt1, rt2 = st.columns(2)
                    rt1.metric("Tempo Totale", f"{timing.get('total_seconds', r_elapsed):.2f} s")
                    rt1.caption(f"Prefill: {timing.get('prefill_seconds', 0):.2f}s | Logit: {timing.get('inference_seconds', 0):.2f}s")
                    
                    unc = ans.get("uncertainty", {})
                    rt2.metric("Confidenza", f"{unc.get('top_probability', 0)*100:.1f}%")
                    rt2.caption(f"Entropia: {unc.get('entropy_nats', 0):.2f} nats")

                except Exception as e:
                    st.error(f"Errore Rizzo-Flow: {str(e)}")

        # --- CLM Execution ---
        with col_c:
            st.markdown("### ⚡ CLM (Contrastive Model)")
            with st.spinner("CLM in elaborazione (allineamento vettoriale)..."):
                t0_c = time.time()
                criteria_clm = {f"opt_{i}": opt for i, opt in enumerate(c_options)}
                payload_clm = {
                    "benchmark": {
                        "type": "choice",
                        "instructions": c_question,
                        "criteria": criteria_clm
                    }
                }
                
                try:
                    c_res = clm.system_one(c_state, payload_clm)
                    c_elapsed = time.time() - t0_c
                    c_ans = c_res.get("answers", {}).get("benchmark", {})
                    
                    c_winner_id = c_ans.get("choice")
                    c_winner_label = criteria_clm.get(c_winner_id, c_winner_id) if c_winner_id else "N/A"
                    
                    st.metric("🏆 Scelta CLM", c_winner_label)
                    
                    # Probabilità CLM
                    c_probs = c_ans.get("probabilities", {})
                    c_chart = []
                    for k, p in c_probs.items():
                        lbl = criteria_clm.get(k, k)
                        c_chart.append({"Opzione": lbl, "Probabilità (%)": round(p * 100, 2)})
                    
                    fig_c = px.bar(
                        pd.DataFrame(c_chart),
                        x="Probabilità (%)",
                        y="Opzione",
                        orientation="h",
                        text="Probabilità (%)",
                        title="Distribuzione Probabilità CLM",
                        color_discrete_sequence=["#10B981"]
                    )
                    fig_c.update_layout(yaxis={"categoryorder": "total ascending"}, height=260)
                    st.plotly_chart(fig_c, use_container_width=True)

                    ct1, ct2 = st.columns(2)
                    ct1.metric("Tempo Totale", f"{c_elapsed:.2f} s")
                    ct1.caption(f"Latenza API: {round(c_elapsed*1000, 1)} ms")
                    
                    conf = c_ans.get("confidence")
                    ct2.metric("Confidenza", f"{conf*100:.1f}%" if conf is not None else "N/A")
                    usage = c_res.get("usage", {})
                    ct2.caption(f"Input tokens: {usage.get('input_tokens', 'N/A')}")

                except Exception as e:
                    st.warning(f"CLM non raggiungibile su {clm.base_url}: {str(e)}")

        # --- Verdetto e Convergenza ---
        if r_winner_label and c_winner_label:
            st.divider()
            st.subheader("🎯 Analisi di Convergenza")
            if r_winner_label == c_winner_label:
                st.success(f"🤝 **Accordo Perfetto**: Entrambi i modelli hanno selezionato **'{r_winner_label}'** come opzione migliore!")
            else:
                st.info(f"⚖️ **Scelte Differenti**: Rizzo-Flow ha preferito **'{r_winner_label}'** mentre CLM ha selezionato **'{c_winner_label}'**.")