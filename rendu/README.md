# TechCorp Financial Assistant

**Groupe 12** — Figueira Thibaut · Fournier Yann · Senel Elodie · Rasoloson Manda · Kreuwen Julie · Cramette Noé



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
├── app.py               # Interface Streamlit (frontend + écran de connexion)
├── backend.py           # Client Ollama + gestion de l'historique de conversation
├── auth.py              # Authentification par lien magique (email) + historique par utilisateur
├── .env.example          # Modèle de config SMTP — copier en .env et remplir
├── Dockerfile            # Image Docker du frontend
├── docker-compose.yml    # Orchestre Ollama + frontend
└── requirements.txt

rendu/infra/
├── Dockerfile            # Image Docker Ollama + création du modèle
└── Modelfile              # Définition du modèle techcorp-finance (basé sur phi3.5)
```

### Comment ça fonctionne

1. **Ollama** démarre et télécharge `phi3.5` si absent du volume
2. Le `Modelfile` crée `techcorp-finance` : phi3.5 avec un system prompt d'assistant financier
3. Un healthcheck vérifie toutes les 10s que le modèle est disponible
4. **Le frontend Streamlit** démarre uniquement une fois le modèle prêt
5. `backend.py` encapsule les appels HTTP vers l'API Ollama (`/api/chat`, `/api/tags`)
6. `app.py` affiche un écran de connexion (email) tant que l'utilisateur n'est pas authentifié — rien d'autre ne se charge avant
7. `auth.py` gère le lien magique et recharge l'historique de conversation de l'utilisateur une fois connecté

---

## Modèle

- **Base :** `phi3.5` (Microsoft) — modèle léger, rapide, fonctionne sur CPU
- **Nom déployé :** `techcorp-finance`
- **System prompt :** assistant financier spécialisé pour les analystes de TechCorp Industries
- **Sujets couverts :** investissements, trading, bilans, prévisions, concepts économiques

Pour modifier le comportement du modèle, éditez `rendu/infra/Modelfile` puis relancez :

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

## Authentification

La connexion se fait par **lien magique envoyé par email** (pas de mot de passe). L'historique de conversation est sauvegardé par adresse email et rechargé automatiquement à la reconnexion.

**Sans rien configurer**, ça fonctionne déjà : le lien de connexion s'affiche directement dans l'interface (mode dev, pas d'email envoyé). C'est suffisant pour tester ou faire une démo.

**Pour recevoir le lien par un vrai email**, il faut configurer l'envoi SMTP via Brevo (gratuit) :

1. Créer un compte sur [brevo.com](https://www.brevo.com)
2. Aller dans **SMTP & API** (menu du compte, en haut à droite) → onglet **SMTP** → récupérer le **SMTP login** et la **clé SMTP** (commence par `xsmtpsib-...`) — *attention, ce n'est pas le mot de passe de connexion à Brevo*
3. Vérifier une adresse expéditeur dans **Senders, Domains & Dedicated IPs → Senders → Add a sender** (pas besoin de nom de domaine, juste cliquer le lien de confirmation reçu sur l'adresse choisie)
4. Copier `rendu/devweb/.env.example` en `rendu/devweb/.env` et remplir :

```env
SMTP_HOST=smtp-relay.brevo.com
SMTP_PORT=587
SMTP_USER=<smtp login Brevo, étape 2>
SMTP_PASSWORD=<clé smtp Brevo, étape 2>
MAIL_FROM=<adresse vérifiée à l'étape 3>
MAIL_ENABLED=true   # false = le lien s'affiche à l'écran au lieu d'être envoyé (mode dev)
FRONTEND_URL=http://localhost:8501
```

5. Relancer `docker compose up` (ou `docker compose up -d --build` si la stack tourne déjà)

> `.env` n'est jamais commité (gitignored, chacun garde le sien). Sans `.env`, la stack démarre quand même normalement et retombe automatiquement en mode dev.

**Mesures de sécurité en place :**
- Lien à usage unique, expire après 15 minutes
- Cooldown de 60s entre deux demandes de lien pour la même adresse (anti-spam / anti-épuisement du quota email)
- Page entièrement bloquée (`st.stop()`) tant que l'utilisateur n'est pas authentifié
- Contenu des messages échappé (`html.escape`) avant affichage — anti-XSS
- Rate limit de 20 messages par session une fois connecté

---

## Sécurité

Un audit de sécurité a été réalisé sur l'héritage de l'équipe précédente. Voir `rendu/cyber/` pour le rapport complet.
