# Datasets — Scripts d'analyse et nettoyage

Scripts et notebooks pour l'exploration et la préparation des données du projet.

## Installation

```powershell
# Depuis la racine du projet
.venv\Scripts\Activate.ps1
pip install -r datasets/scripts/requirements.txt
```

## Contenu

| Fichier | Description |
|---|---|
| `01_eda.ipynb` | Notebook EDA — analyse exploratoire des datasets hérités |
| `02_clean.ipynb` | Notebook nettoyage — pipeline de préparation des données |
| `requirements.txt` | Dépendances : pandas, datasets, pyarrow, matplotlib, seaborn, jupyter |

## Lancer les notebooks

```bash
cd datasets/scripts
jupyter lab
```

Ouvrir dans l'ordre : `01_eda.ipynb` puis `02_clean.ipynb`.