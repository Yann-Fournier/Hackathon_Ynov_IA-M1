# TechCorp Financial Assistant

Assistant financier IA propulsé par **Phi-3.5**, déployé via Ollama et accessible via une interface web Streamlit.

---

## Lancer le projet

**Prérequis :** Docker Desktop installé et démarré.

```bash
cd rendu/devweb
docker compose up
```

C'est tout. Les deux services démarrent automatiquement :

| Service | URL |
|---|---|
| Interface web | http://localhost:8501 |
| API Ollama | http://localhost:11434 |

> Le modèle `techcorp-finance` est téléchargé et créé automatiquement au premier démarrage (~2 Go, quelques minutes). L'interface web attend que le modèle soit prêt avant de démarrer — pas besoin de tout synchroniser manuellement.

Pour arrêter :

```bash
docker compose down
```

---

## Architecture

```
rendu/devweb/
├── app.py               # Interface Streamlit (frontend)
├── backend.py           # Client Ollama + gestion de l'historique
├── Dockerfile           # Image Docker du frontend
├── docker-compose.yml   # Orchestre Ollama + frontend
└── requirements.txt

rendu/infra/
├── Dockerfile           # Image Docker Ollama + création du modèle
└── infra.md

ollama_server/
└── Modelfile            # Définition du modèle techcorp-finance (basé sur phi3.5)
```

### Comment ça fonctionne

1. **Ollama** démarre et télécharge `phi3.5` si absent du volume
2. Le `Modelfile` crée `techcorp-finance` : phi3.5 avec un system prompt d'assistant financier
3. Un healthcheck vérifie toutes les 10s que le modèle est disponible
4. **Le frontend Streamlit** démarre uniquement une fois le modèle prêt
5. `backend.py` encapsule les appels HTTP vers l'API Ollama (`/api/chat`, `/api/tags`)
6. `app.py` affiche l'interface et utilise `backend.py` pour communiquer avec le modèle

---

## Modèle

- **Base :** `phi3.5` (Microsoft) — modèle léger, rapide, fonctionne sur CPU
- **Nom déployé :** `techcorp-finance`
- **System prompt :** assistant financier spécialisé pour les analystes de TechCorp Industries
- **Sujets couverts :** investissements, trading, bilans, prévisions, concepts économiques

Pour modifier le comportement du modèle, éditez `ollama_server/Modelfile` puis relancez :

```bash
docker compose down
docker compose up --build
```

---

## Développement sans Docker

Si vous voulez lancer le frontend seul (Ollama doit tourner séparément) :

```bash
cd rendu/devweb
py -m pip install -r requirements.txt
py -m streamlit run app.py
```

L'URL du serveur Ollama peut être surchargée via la variable d'environnement `OLLAMA_URL` :

```bash
OLLAMA_URL=http://192.168.1.42:11434 py -m streamlit run app.py
```

---

## Sécurité

Un audit de sécurité a été réalisé sur l'héritage de l'équipe précédente. Voir `rendu/cyber/` pour le rapport complet.
