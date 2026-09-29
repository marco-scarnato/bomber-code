import streamlit as st
import os
from utils.rizzo_client import RizzoClient
from utils.minicpm_client import MiniCPMClient
from utils.clm_client import CLMClient

st.set_page_config(page_title="AI Playground", page_icon="🧪", layout="wide")

st.title("🧪 AI Playground: Decision Engine & Coding Agent")
st.markdown("Esplora e confronta tre modelli all'avanguardia in esecuzione locale su CPU:")

# Inizializza client
rizzo_client = RizzoClient()
minicpm_client = MiniCPMClient()
clm_client = CLMClient()

st.divider()

col1, col2, col3 = st.columns(3, gap="medium")

with col1:
    st.subheader("🎯 Rizzo-Flow")
    st.write(
        "**System 1 Decision Engine**\n\n"
        "Esegue `Spark-X2.5-1.7B` ed ispeziona direttamente i logit terminali sui token candidati. "
        "Zero token generati, decisioni e valutazioni probabilistiche con stima dell'incertezza."
    )
    
    # Health check
    rizzo_status = rizzo_client.health()
    if rizzo_status:
        st.success("🟢 Online (Spark-1.7B)")
    else:
        st.error("🔴 Offline")
        
    st.page_link("pages/1_Rizzo_Flow.py", label="Apri Rizzo-Flow", icon="🎯")

with col2:
    st.subheader("💬 MiniCPM5-2B")
    st.write(
        "**Generative Coding Agent**\n\n"
        "LLM da 2.5B con **Hybrid Thinking** (`<think>`), streaming ultra-rapido su CPU (22+ t/s) "
        "e telemetria completa su token di lettura, ragionamento e output."
    )
    
    # Health check
    minicpm_status = minicpm_client.health()
    if minicpm_status:
        st.success("🟢 Online (llama-server)")
    else:
        st.error("🔴 Offline")
        
    st.page_link("pages/2_MiniCPM.py", label="Apri MiniCPM & Coding", icon="💬")

with col3:
    st.subheader("⚡ CLM")
    st.write(
        "**Contrastive System 1 Model**\n\n"
        "Disaggrega stato e azioni con teste di proiezione InfoNCE secondo il protocollo TypeSafe. "
        "Testa il modello singolarmente o analizza le distribuzioni vettoriali."
    )
    
    # Health check
    clm_status = clm_client.health()
    if clm_status:
        st.success("🟢 Online (TypeSafe API)")
    else:
        st.error("🔴 Offline")
        
    st.page_link("pages/3_CLM.py", label="Apri CLM Singolo", icon="⚡")

st.divider()

# Card in evidenza per il confronto
st.subheader("🥊 Confronto Diretto Testa a Testa")
st.write(
    "Metti a confronto diretto **Rizzo-Flow** e **CLM** sullo stesso identico testo, domanda e opzioni candidate. "
    "Osserva se i due motori concordano, confronta i grafici di probabilità e misura le differenze di latenza."
)
st.page_link("pages/4_Confronto.py", label="Apri Pagina di Confronto Testa a Testa", icon="🥊")

st.divider()

# Scheda informativa comparativa
st.markdown("### 📋 Panoramica Architetturale")
comp_df_data = [
    {
        "Modello": "Rizzo-Flow (Spark-1.7B)",
        "Tipo": "Logit Inspection (System 1)",
        "Token Generati": "0 token (Logit argmax/softmax)",
        "Punti di Forza": "Stima incertezza (entropia), 1M token contesto, astensione automatica",
        "Scopo": "Classificazione rapida, triage ticket, scoring e verifiche conformità"
    },
    {
        "Modello": "MiniCPM5-2B",
        "Tipo": "Autoregressive LLM + Thinking",
        "Token Generati": "Generazione completa (streaming)",
        "Punti di Forza": "Catena di pensiero <think>, generazione codice, bug fixing, tool calling XML",
        "Scopo": "Coding Agent, refactoring, programmazione interattiva e compiti complessi"
    },
    {
        "Modello": "CLM (Contrastive LM)",
        "Tipo": "Contrastive Embedding Alignment",
        "Token Generati": "0 token (Prodotto scalare proiettato)",
        "Punti di Forza": "Azioni pre-calcolate e cachate, latenza sub-secondo, standard TypeSafe",
        "Scopo": "Confronto probabilistico e selezione migliore azione/candidato"
    }
]
st.dataframe(comp_df_data, use_container_width=True)