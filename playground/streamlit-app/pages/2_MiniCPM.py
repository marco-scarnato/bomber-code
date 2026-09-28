import streamlit as st
from utils.minicpm_client import MiniCPMClient

st.set_page_config(page_title="MiniCPM Coding & Chat", page_icon="💬", layout="wide")
st.title("💬 MiniCPM5-2B — Coding Agent & Telemetria")
st.caption("Modello attivo: **MiniCPM5-2B (Q4_K_M)** su CPU via `llama-server` — Supporto nativo per Hybrid Thinking (`<think>`), telemetria token e tool calling.")

minicpm = MiniCPMClient()

if "chat_messages" not in st.session_state:
    st.session_state.chat_messages = []
if "message_stats" not in st.session_state:
    st.session_state.message_stats = {}

# --- Sidebar: Configurazione & Preset Coding Agent ---
with st.sidebar:
    st.header("🤖 Modalità & Ruolo")
    
    preset = st.selectbox(
        "Seleziona Ruolo del Modello",
        [
            "💻 Coding Agent (Rigoroso)",
            "🐛 Bug Hunter & Patch Specialist",
            "🛠️ Tool Calling Agent (XML)",
            "💬 Assistente Generale",
            "Personalizzato"
        ]
    )
    
    default_prompt = ""
    if preset == "💻 Coding Agent (Rigoroso)":
        default_prompt = (
            "Sei un ingegnere del software senior e un Coding Agent autonomo. "
            "Prima di scrivere qualsiasi codice, usa il blocco di ragionamento per:\n"
            "1. Analizzare i requisiti e l'architettura della soluzione.\n"
            "2. Individuare esplicitamente i casi limite (edge cases: input nulli, liste vuote, overflow, complessità temporale e spaziale).\n"
            "3. Spiegare la scelta algoritmica.\n"
            "Genera solo codice pulito, tipizzato e documentato, pronto per la produzione."
        )
    elif preset == "🐛 Bug Hunter & Patch Specialist":
        default_prompt = (
            "Sei un esperto di debugging e refactoring. "
            "Quando ricevi del codice con problemi:\n"
            "1. Nel ragionamento spiega la root-cause del bug.\n"
            "2. Fornisci la correzione sia come codice completo sia in formato patch unificato (git diff).\n"
            "3. Includi un test unitario (pytest) che fallirebbe prima del fix e passa dopo il fix."
        )
    elif preset == "🛠️ Tool Calling Agent (XML)":
        default_prompt = (
            "Sei un Agent con accesso a tool esterni. Quando devi compiere un'azione, "
            "non inventare il risultato. Emetti invece una chiamata formattata in XML:\n"
            "<function name=\"nome_tool\">\n"
            "  <param name=\"nome_parametro\">valore</param>\n"
            "</function>\n"
            "I tool disponibili sono: [read_file, write_file, execute_bash, git_diff, run_pytest]."
        )
    elif preset == "💬 Assistente Generale":
        default_prompt = "Sei un assistente AI utile, conciso e accurato."

    sys_prompt = st.text_area("System Prompt", value=default_prompt, height=140)

    st.divider()
    st.subheader("⚙️ Parametri di Inferenza")
    col_p1, col_p2 = st.columns(2)
    temperature = col_p1.slider("Temperature", 0.0, 1.5, 0.6, 0.05)
    top_p = col_p2.slider("Top-p", 0.1, 1.0, 0.95, 0.05)
    max_tokens = st.slider("Max Tokens (Output)", 128, 8192, 2048, 128, help="Numero massimo di token totali generabili (ragionamento + codice). Su CPU a ~23 t/s, 2048 token richiedono ~90 secondi.")

    thinking_mode = st.toggle("🧠 Abilita Thinking Mode", value=True, help="Attiva il tag /think per forzare il ragionamento prima della risposta.")

    st.divider()
    st.subheader("🧪 Benchmark Rapidi Coding")
    st.write("Test veloci da iniettare nella chat:")
    
    if st.button("🧪 Test 1: Algoritmo Edge-Case", use_container_width=True):
        st.session_state.pending_input = "Implementa una funzione Python `find_first_missing_positive(nums: list[int]) -> int` che trova il primo intero positivo mancante in tempo O(N) e spazio O(1). Analizza e gestisci tutti gli edge cases."
        st.rerun()

    if st.button("🧪 Test 2: Bug Fix & Git Diff", use_container_width=True):
        st.session_state.pending_input = (
            "Individua il bug nel seguente codice, spiega perché fallisce e genera la patch unificata (git diff):\n\n"
            "```python\n"
            "def binary_search(arr, target):\n"
            "    low, high = 0, len(arr)\n"
            "    while low < high:\n"
            "        mid = (low + high) // 2\n"
            "        if arr[mid] == target:\n"
            "            return mid\n"
            "        elif arr[mid] < target:\n"
            "            low = mid\n"
            "        else:\n"
            "            high = mid\n"
            "    return -1\n"
            "```"
        )
        st.rerun()

    if st.button("🧪 Test 3: Tool Invocation XML", use_container_width=True):
        st.session_state.pending_input = "Ho bisogno di verificare se i test unitari passano sul branch corrente. Usa lo strumento execute_bash per lanciare pytest sul modulo tests/test_core.py."
        st.rerun()

    if st.button("🗑️ Cancella Cronologia", use_container_width=True):
        st.session_state.chat_messages = []
        st.session_state.message_stats = {}
        st.rerun()

# --- Area Principale di Chat ---
for i, msg in enumerate(st.session_state.chat_messages):
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])
        
        # Mostra le metriche associate a questa risposta se presenti
        if msg["role"] == "assistant" and i in st.session_state.message_stats:
            stats = st.session_state.message_stats[i]
            with st.expander("📊 Telemetria Token & Prestazioni"):
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Token Lettura (Prompt)", stats.get("prompt_tokens", 0))
                m2.metric("Token Pensiero (Think)", stats.get("reasoning_tokens", 0))
                m3.metric("Token Output", stats.get("completion_tokens", 0))
                m4.metric("Velocità Generazione", f"{stats.get('gen_speed_tps', 0)} t/s")
                
                s1, s2 = st.columns(2)
                s1.caption(f"⏱️ Tempo lettura prompt: {stats.get('prompt_ms', 0)} ms ({stats.get('prompt_speed_tps', 0)} t/s)")
                s2.caption(f"⏱️ Tempo generazione: {stats.get('predicted_ms', 0)} ms")

# Gestione input (da chat_input o da pulsante benchmark)
user_prompt = None
if "pending_input" in st.session_state and st.session_state.pending_input:
    user_prompt = st.session_state.pending_input
    st.session_state.pending_input = None
else:
    user_prompt = st.chat_input("Scrivi una richiesta di codice o premi un test nella barra laterale...")

if user_prompt:
    actual_prompt = user_prompt
    if thinking_mode and not actual_prompt.startswith("/think"):
        actual_prompt = f"/think {actual_prompt}"
    elif not thinking_mode and not actual_prompt.startswith("/no_think"):
        actual_prompt = f"/no_think {actual_prompt}"

    # Salva messaggio utente
    st.session_state.chat_messages.append({"role": "user", "content": user_prompt})
    with st.chat_message("user"):
        st.markdown(user_prompt)

    # Costruisci cronologia per l'API
    api_messages = [{"role": "system", "content": sys_prompt}]
    for m in st.session_state.chat_messages[:-1]:
        api_messages.append(m)
    api_messages.append({"role": "user", "content": actual_prompt})

    # Risposta assistente
    with st.chat_message("assistant"):
        try:
            stream_gen = minicpm.chat_stream(
                messages=api_messages,
                temperature=temperature,
                max_tokens=max_tokens,
                top_p=top_p
            )
            response_text = st.write_stream(stream_gen)
            
            # Salva risposta e telemetria
            assistant_idx = len(st.session_state.chat_messages)
            st.session_state.chat_messages.append({"role": "assistant", "content": response_text})
            st.session_state.message_stats[assistant_idx] = dict(minicpm.last_stats)

            # Mostra subito la barra telemetria appena finito
            with st.expander("📊 Telemetria Token & Prestazioni", expanded=True):
                stats = minicpm.last_stats
                m1, m2, m3, m4 = st.columns(4)
                m1.metric("Token Lettura (Prompt)", stats.get("prompt_tokens", 0))
                m2.metric("Token Pensiero (Think)", stats.get("reasoning_tokens", 0))
                m3.metric("Token Output", stats.get("completion_tokens", 0))
                m4.metric("Velocità Generazione", f"{stats.get('gen_speed_tps', 0)} t/s")
                
                s1, s2 = st.columns(2)
                s1.caption(f"⏱️ Tempo lettura prompt: {stats.get('prompt_ms', 0)} ms ({stats.get('prompt_speed_tps', 0)} t/s)")
                s2.caption(f"⏱️ Tempo generazione: {stats.get('predicted_ms', 0)} ms")

        except Exception as e:
            st.error(f"Errore di comunicazione con MiniCPM: {str(e)}")