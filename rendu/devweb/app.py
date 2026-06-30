import streamlit as st
import requests
from datetime import datetime

OLLAMA_URL = "http://10.17.164.14:11434"
MODEL_NAME = "phi3-financial"

st.set_page_config(
    page_title="TechCorp AI",
    page_icon="💼",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }

    .main-header {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        border-radius: 16px;
        padding: 24px 32px;
        margin-bottom: 24px;
        display: flex;
        align-items: center;
        gap: 16px;
    }
    .header-icon { font-size: 40px; }
    .header-title {
        font-size: 28px;
        font-weight: 700;
        color: var(--primary-color);
        margin: 0;
    }
    .header-subtitle {
        color: var(--text-color);
        opacity: 0.5;
        font-size: 13px;
        margin: 4px 0 0 0;
    }

    .status-badge {
        display: inline-flex;
        align-items: center;
        gap: 8px;
        padding: 6px 14px;
        border-radius: 20px;
        font-size: 13px;
        font-weight: 500;
        margin-bottom: 16px;
    }
    .status-online {
        background: rgba(34,197,94,0.12);
        border: 1px solid rgba(34,197,94,0.35);
        color: #16a34a;
    }
    .status-offline {
        background: rgba(239,68,68,0.12);
        border: 1px solid rgba(239,68,68,0.35);
        color: #dc2626;
    }

    .msg-user {
        background: linear-gradient(135deg, #1d4ed8, #3b82f6);
        color: #ffffff;
        padding: 14px 18px;
        border-radius: 18px 18px 4px 18px;
        max-width: 75%;
        margin-left: auto;
        box-shadow: 0 4px 15px rgba(59,130,246,0.25);
        font-size: 14px;
        line-height: 1.6;
    }
    .msg-assistant {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.2);
        color: var(--text-color);
        padding: 14px 18px;
        border-radius: 18px 18px 18px 4px;
        max-width: 75%;
        box-shadow: 0 2px 8px rgba(0,0,0,0.06);
        font-size: 14px;
        line-height: 1.6;
    }
    .msg-time {
        font-size: 11px;
        color: var(--text-color);
        opacity: 0.4;
        margin-top: 4px;
    }
    .msg-time-right { text-align: right; }

    .sidebar-section {
        background: var(--secondary-background-color);
        border: 1px solid rgba(128,128,128,0.15);
        border-radius: 12px;
        padding: 16px;
        margin-bottom: 16px;
    }
    .sidebar-title {
        color: var(--text-color);
        opacity: 0.5;
        font-size: 11px;
        font-weight: 600;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-bottom: 12px;
    }
    .stat-item {
        display: flex;
        justify-content: space-between;
        align-items: center;
        padding: 8px 0;
        border-bottom: 1px solid rgba(128,128,128,0.1);
        font-size: 13px;
        color: var(--text-color);
        opacity: 0.8;
    }
    .stat-value {
        color: var(--primary-color);
        font-weight: 600;
        opacity: 1;
    }

    div[data-testid="stChatMessage"] { background: transparent !important; padding: 0 !important; }
</style>
""", unsafe_allow_html=True)


def check_connection():
    try:
        r = requests.get(f"{OLLAMA_URL}/api/tags", timeout=2)
        return r.status_code == 200
    except:
        return False


def chat(messages):
    r = requests.post(
        f"{OLLAMA_URL}/api/chat",
        json={"model": MODEL_NAME, "messages": messages, "stream": False},
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["message"]["content"]


if "messages" not in st.session_state:
    st.session_state.messages = []

connected = check_connection()

# Sidebar
with st.sidebar:
    st.markdown("### 💼 TechCorp AI")
    st.markdown("---")

    if connected:
        st.markdown('<div class="status-badge status-online">● Serveur connecté</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-offline">● Serveur déconnecté</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-section">
        <div class="sidebar-title">Session</div>
        <div class="stat-item"><span>Modèle</span><span class="stat-value">{MODEL_NAME}</span></div>
        <div class="stat-item"><span>Messages</span><span class="stat-value">{len(st.session_state.messages)}</span></div>
        <div class="stat-item"><span>Serveur</span><span class="stat-value">10.17.164.14</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.messages = []
        st.rerun()

    st.markdown("---")
    st.markdown('<div class="sidebar-section"><div class="sidebar-title">Suggestions</div></div>', unsafe_allow_html=True)
    for s in ["Explique le ROI", "C'est quoi le trading algorithmique ?", "Comment lire un bilan ?", "Définition de la liquidité"]:
        if st.button(s, use_container_width=True, key=s):
            st.session_state.pending_prompt = s
            st.rerun()

# Header
st.markdown("""
<div class="main-header">
    <div class="header-icon">🤖</div>
    <div>
        <p class="header-title">Financial Assistant</p>
        <p class="header-subtitle">Propulsé par Phi-3.5 Financial · TechCorp Industries</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Messages
for msg in st.session_state.messages:
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin: 8px 0;">
            <div>
                <div class="msg-user">{msg["content"]}</div>
                <div class="msg-time msg-time-right">{msg.get("time", "")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-start; margin: 8px 0;">
            <div>
                <div class="msg-assistant">{msg["content"]}</div>
                <div class="msg-time">{msg.get("time", "")}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

if not connected:
    st.warning("Serveur Ollama inaccessible. Vérifiez la connexion réseau.")

if "pending_prompt" in st.session_state:
    prompt = st.session_state.pop("pending_prompt")
else:
    prompt = st.chat_input("Posez votre question financière...", disabled=not connected)

if prompt:
    now = datetime.now().strftime("%H:%M")
    st.session_state.messages.append({"role": "user", "content": prompt, "time": now})
    with st.spinner("L'assistant réfléchit..."):
        try:
            response = chat([{"role": m["role"], "content": m["content"]} for m in st.session_state.messages])
            st.session_state.messages.append({"role": "assistant", "content": response, "time": datetime.now().strftime("%H:%M")})
        except Exception as e:
            st.error(f"Erreur : {e}")
    st.rerun()
