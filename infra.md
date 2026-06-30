
## OLAMA

Olama est l'outil qui fait tourner des modèles d'IA (comme phi3.5 ici) en local sur ta machine, sans dépendre d'une API cloud. 

Celui mis en place par la précédente équipe est phi3.5 (modèle de Microsoft, léger et rapide),
et lui donne un SYSTEM prompt qui le transforme en assistant financier pour TechCorp Industries.

```bash
installer olama https://ollama.com/download/windows
ollama create techcorp-finance -f ollama_server/Modelfile
```

Pour lancer, il suffit de taper dans un terminal :

```bash
ollama run techcorp-finance
```


Pour vérifier que le serveur est bien lancé : :

```bash
curl http://localhost:11434/api/tags
```

Récuper mon ip :

```powershell
ipconfig
```

Test de l'exposition d'Olama sur le réseau local (LAN) :
! IMPORTANT ! Ne pas oublier sur l'app OLAMA de cocher "Allow connections from other devices on the local network" dans les paramètres.

```bash
curl http://{{votreiplocal}}/api/tags
```


## Dockerisation

Voici comment démarer le docker pour le serveur Ollama :

Rentrez dans le dossier `ollama_server` :

```bash
cd ollama_server
```

Commencez par construire l'image docker :

```bash
docker compose build
```

Ensuite, lancez le serveur Ollama en arrière-plan avec la commande suivante :

```bash
docker compose up
```

Tester le Docker

```bash
curl http://localhost:11434/api/tags
```

Pour down le docker :

```bash
docker compose down
```


