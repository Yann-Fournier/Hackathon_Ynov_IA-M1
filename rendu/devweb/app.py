import os
import streamlit as st
from backend import get_client, ConversationHistory
import auth

OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")
MODEL_NAME = "techcorp-finance"

st.set_page_config(
    page_title="TechCorp AI",
    page_icon="🔷",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Space+Grotesk:wght@500;600;700&display=swap');
    * { font-family: 'Inter', sans-serif; }

    .brand-logo {
        display: flex;
        align-items: center;
        gap: 12px;
        margin-bottom: 16px;
    }
    .logo-mark {
        width: 38px;
        height: 38px;
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 16px;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
        letter-spacing: -1px;
    }
    .logo-mark-lg {
        width: 52px;
        height: 52px;
        background: linear-gradient(135deg, #3b82f6, #6366f1);
        border-radius: 14px;
        display: flex;
        align-items: center;
        justify-content: center;
        font-family: 'Space Grotesk', sans-serif;
        font-size: 20px;
        font-weight: 700;
        color: white;
        flex-shrink: 0;
        letter-spacing: -1px;
    }
    .brand-name {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 18px;
        font-weight: 700;
        color: var(--primary-color);
        letter-spacing: -0.3px;
    }
    .brand-tag {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 10px;
        font-weight: 500;
        color: var(--text-color);
        opacity: 0.4;
        letter-spacing: 2px;
        text-transform: uppercase;
    }

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
    .header-logo { flex-shrink: 0; }
    .header-title {
        font-family: 'Space Grotesk', sans-serif;
        font-size: 30px;
        font-weight: 700;
        color: var(--primary-color);
        letter-spacing: -0.5px;
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


# --- Authentication (magic link by email) ---
query_token = st.query_params.get("token")
if query_token and "user_email" not in st.session_state:
    verified_email = auth.verify_token(query_token)
    st.query_params.clear()
    if verified_email:
        st.session_state.user_email = verified_email
        st.rerun()
    else:
        st.session_state.auth_error = "Lien invalide ou expiré. Demandez un nouveau lien."

if "user_email" not in st.session_state:
    st.markdown("""
    <div class="main-header">
        <div class="logo-mark-lg">TC</div>
        <div>
            <p class="header-title">TechCorp Financial Assistant</p>
            <p class="header-subtitle">Connexion par lien</p>
        </div>
    </div>
    """, unsafe_allow_html=True)

    _, login_col, _ = st.columns([1, 1, 1])
    with login_col:
        with st.container(border=True):
            st.markdown(
                '<p style="font-weight:600; font-size:15px; margin-bottom:12px;">'
                'Entrez votre email pour recevoir un lien de connexion</p>',
                unsafe_allow_html=True,
            )

            if "auth_error" in st.session_state:
                st.error(st.session_state.pop("auth_error"))

            email_input = st.text_input("Adresse email", label_visibility="collapsed", placeholder="vous@exemple.com")
            if st.button("Envoyer le lien de connexion", type="primary", use_container_width=True):
                if email_input and "@" in email_input:
                    try:
                        link = auth.request_magic_link(email_input)
                        if auth.settings.mail_enabled:
                            st.success(f"Lien envoyé à {email_input}. Vérifiez votre boîte mail.")
                        else:
                            st.info("Mode dev (envoi d'email désactivé) — cliquez pour vous connecter :")
                            st.markdown(f"[{link}]({link})")
                    except auth.CooldownActive as e:
                        st.warning(f"Un lien a déjà été envoyé récemment. Réessayez dans {e.seconds_remaining}s.")
                else:
                    st.warning("Entrez une adresse email valide.")

    st.stop()

client = get_client(base_url=OLLAMA_URL, model=MODEL_NAME)

if "history" not in st.session_state:
    st.session_state.history = ConversationHistory()
    st.session_state.history.messages = auth.load_history(st.session_state.user_email)

connected = client.check_connection().connected

# Sidebar
with st.sidebar:
    st.markdown("""
    <div class="brand-logo">
        <div class="logo-mark">TC</div>
        <div>
            <div class="brand-name">TechCorp</div>
            <div class="brand-tag">Financial AI</div>
        </div>
    </div>
    """, unsafe_allow_html=True)
    st.markdown("---")

    if connected:
        st.markdown('<div class="status-badge status-online">● Serveur connecté</div>', unsafe_allow_html=True)
    else:
        st.markdown('<div class="status-badge status-offline">● Serveur déconnecté</div>', unsafe_allow_html=True)

    st.markdown(f"""
    <div class="sidebar-section">
        <div class="sidebar-title">Session</div>
        <div class="stat-item"><span>Utilisateur</span><span class="stat-value">{st.session_state.user_email}</span></div>
        <div class="stat-item"><span>Modèle</span><span class="stat-value">{MODEL_NAME}</span></div>
        <div class="stat-item"><span>Messages</span><span class="stat-value">{len(st.session_state.history.as_list())}</span></div>
        <div class="stat-item"><span>Serveur</span><span class="stat-value">localhost</span></div>
    </div>
    """, unsafe_allow_html=True)

    if st.button("🗑️ Effacer la conversation", use_container_width=True):
        st.session_state.history.clear()
        auth.save_history(st.session_state.user_email, [])
        st.rerun()

    if st.button("🚪 Déconnexion", use_container_width=True):
        del st.session_state["user_email"]
        del st.session_state["history"]
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
    <div class="logo-mark-lg">TC</div>
    <div>
        <p class="header-title">TechCorp Financial Assistant</p>
        <p class="header-subtitle">Propulsé par Phi-3.5 Financial · TechCorp Industries</p>
    </div>
</div>
""", unsafe_allow_html=True)

# Messages
for msg in st.session_state.history.as_list():
    if msg["role"] == "user":
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-end; margin: 8px 0;">
            <div>
                <div class="msg-user">{msg["content"]}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)
    elif msg["role"] == "assistant":
        st.markdown(f"""
        <div style="display:flex; justify-content:flex-start; margin: 8px 0;">
            <div>
                <div class="msg-assistant">{msg["content"]}</div>
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
    st.session_state.history.add_user(prompt)
    with st.spinner("L'assistant réfléchit..."):
        try:
            response = "".join(client.chat(st.session_state.history.as_list(), stream=False))
            st.session_state.history.add_assistant(response)
            auth.save_history(st.session_state.user_email, st.session_state.history.as_list())
            st.rerun()
        except Exception as e:
            st.error(f"Erreur : {e}")
