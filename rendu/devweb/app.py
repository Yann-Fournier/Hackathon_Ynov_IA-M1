import streamlit as st
import requests

OLLAMA_URL = "http://10.17.164.14:11434"
MODEL_NAME = "phi3-financial"

st.set_page_config(page_title="TechCorp AI Chat", page_icon="💼", layout="centered")
st.title("💼 TechCorp Financial Assistant")


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


# Connexion status
connected = check_connection()
if connected:
    st.success("Serveur connecté")
else:
    st.error("Serveur déconnecté — lancez Ollama")

# Historique
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

# Input
if prompt := st.chat_input("Posez votre question financière...", disabled=not connected):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.write(prompt)

    with st.chat_message("assistant"):
        with st.spinner("Réflexion..."):
            try:
                response = chat(st.session_state.messages)
                st.write(response)
                st.session_state.messages.append({"role": "assistant", "content": response})
            except Exception as e:
                st.error(f"Erreur : {e}")
