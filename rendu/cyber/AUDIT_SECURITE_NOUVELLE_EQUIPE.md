# Audit de Sécurité — Déploiement Nouvelle Équipe

**Périmètre :** code produit par la nouvelle équipe (`rendu/devweb/`, `rendu/infra/`)
**Date :** 30/06/2026
**Statut global :** 🟡 En cours

---

## 🔴 Finding 1 — CRITIQUE : XSS dans `app.py`

**Fichier :** `rendu/devweb/app.py` lignes 246-260

Le contenu des messages utilisateur est injecté directement dans le HTML sans échappement :

```python
<div class="msg-user">{msg["content"]}</div>
```

Un utilisateur peut injecter du HTML/JavaScript arbitraire exécuté dans le navigateur de tous les clients connectés (stored XSS).

**Preuve :**
```
Input : <script>alert('XSS')</script>
Résultat : exécution du script dans le navigateur
```

**Correction :** `html.escape()` appliqué sur tout contenu utilisateur avant injection HTML (`app.py`).

**Statut : ✅ Corrigé**

---

## 🟠 Finding 2 — ÉLEVÉ : API Ollama exposée sans authentification

**Fichier :** `rendu/devweb/docker-compose.yml`

Le port `11434` est exposé sur `0.0.0.0` — n'importe qui sur le réseau peut appeler `/api/chat` directement sans passer par le frontend. Aucune authentification, aucun rate limiting.

```yaml
ports:
  - "11434:11434"
```

**Correction :** remplacement de `ports` par `expose` dans le docker-compose — le port 11434 est accessible uniquement depuis le réseau Docker interne, plus depuis l'hôte.

**Statut : ✅ Corrigé**

---

## 🟡 Finding 3 — MOYEN : Aucune authentification sur le frontend

L'interface web est accessible à n'importe qui sur le réseau sans login. Pas de contrôle d'accès.

**Statut : ❌ Non corrigé**

---

## 🟡 Finding 4 — MOYEN : Pas de rate limiting sur les requêtes au modèle

Aucune limite sur le nombre de requêtes par utilisateur/IP. Un attaquant peut saturer le modèle ou générer des coûts excessifs.

**Correction :** limite de 20 messages par session via compteur en `session_state`. Blocage avec message d'erreur au dépassement.

**Statut : ✅ Corrigé**

---

## 🟢 Finding 5 — FAIBLE : Double instruction `FROM` dans le Dockerfile

**Fichier :** `rendu/infra/Dockerfile`

```dockerfile
FROM ollama/ollama:latest
FROM ollama/ollama:latest  # ← ligne dupliquée ignorée silencieusement
```

La première ligne est ignorée par Docker (multi-stage build implicite). Pas d'impact fonctionnel mais source de confusion.

**Correction :** suppression de la ligne dupliquée dans `rendu/infra/Dockerfile`.

**Statut : ✅ Corrigé**

---

## 🟢 Finding 6 — FAIBLE : Conteneurs Docker s'exécutent en tant que root

Aucun `USER` dans les Dockerfiles — les processus tournent avec les droits root dans les conteneurs.

**Correction :** ajout de `useradd appuser` + `USER appuser` dans `rendu/devweb/Dockerfile`. Le conteneur Ollama tourne déjà avec un utilisateur non-root dans l'image officielle.

**Statut : ✅ Corrigé**

---

## Suivi des corrections

| # | Sévérité | Finding | Statut |
|---|---|---|---|
| 1 | 🔴 CRITIQUE | XSS dans app.py | ✅ |
| 2 | 🟠 ÉLEVÉ | API Ollama exposée sans auth | ✅ |
| 3 | 🟡 MOYEN | Pas d'auth sur le frontend | ❌ |
| 4 | 🟡 MOYEN | Pas de rate limiting | ✅ |
| 5 | 🟢 FAIBLE | Double FROM dans Dockerfile | ✅ |
| 6 | 🟢 FAIBLE | Conteneurs en root | ✅ |
