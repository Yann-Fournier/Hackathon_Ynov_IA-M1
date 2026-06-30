import json
import re
from collections import Counter
from pathlib import Path

import pandas as pd
from langdetect import detect
from tqdm import tqdm

# ----------------------------------------------------
# CONFIGURATION
# ----------------------------------------------------

DATASET = "../../datasets/finance_dataset_final.json"
REPORT_FOLDER = "../../data/reports"

Path(REPORT_FOLDER).mkdir(parents=True, exist_ok=True)

# ----------------------------------------------------
# REGEX
# ----------------------------------------------------

PATTERNS = {

    "AWS Key":
        r"AKIA[0-9A-Z]{16}",

    "AWS Secret":
        r"(?i)aws_secret_access_key",

    "Password":
        r"(?i)(password|pass:|passwd|pwd)",

    "Email":
        r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",

    "IPv4":
        r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",

    "URL":
        r"https?://\S+",

    "SSH":
        r"ssh\s+\S+",

    "VPN":
        r"vpn",

    "SWIFT":
        r"SWIFT",

    "BIC":
        r"\bBIC\b",

    "Database":
        r"mysql|postgres|mongodb",

    "Private key":
        r"BEGIN PRIVATE KEY"
}

# ----------------------------------------------------
# CHARGEMENT
# ----------------------------------------------------

with open(DATASET, encoding="utf-8") as f:
    dataset = json.load(f)

print("=" * 60)
print("DATASET ANALYSIS")
print("=" * 60)

print(f"Nombre de conversations : {len(dataset)}")

# ----------------------------------------------------
# STATISTIQUES
# ----------------------------------------------------

instruction_lengths = []
output_lengths = []
languages = []
duplicates = set()

seen = set()

secret_counter = Counter()

missing_instruction = 0
missing_output = 0

for sample in tqdm(dataset):

    instruction = sample.get("instruction", "")
    output = sample.get("output", "")

    # Longueurs

    instruction_lengths.append(len(instruction.split()))
    output_lengths.append(len(output.split()))

    # Champs manquants

    if instruction.strip() == "":
        missing_instruction += 1

    if output.strip() == "":
        missing_output += 1

    # Langue

    try:
        languages.append(detect(instruction))
    except:
        languages.append("unknown")

    # Doublons

    signature = instruction + output

    if signature in seen:
        duplicates.add(signature)

    seen.add(signature)

    # Secrets

    text = instruction + " " + output

    for name, pattern in PATTERNS.items():

        if re.search(pattern, text):
            secret_counter[name] += 1

# ----------------------------------------------------
# STATISTIQUES GLOBALES
# ----------------------------------------------------

stats = {

    "Nombre conversations":
        len(dataset),

    "Instruction moyenne":
        round(sum(instruction_lengths) / len(instruction_lengths), 2),

    "Réponse moyenne":
        round(sum(output_lengths) / len(output_lengths), 2),

    "Instruction max":
        max(instruction_lengths),

    "Instruction min":
        min(instruction_lengths),

    "Réponse max":
        max(output_lengths),

    "Réponse min":
        min(output_lengths),

    "Doublons":
        len(duplicates),

    "Instructions manquantes":
        missing_instruction,

    "Réponses manquantes":
        missing_output
}

print()

print("=" * 60)
print("STATISTIQUES")
print("=" * 60)

for k, v in stats.items():
    print(f"{k:30} : {v}")

# ----------------------------------------------------
# LANGUES
# ----------------------------------------------------

print()

print("=" * 60)
print("LANGUES")
print("=" * 60)

language_counter = Counter(languages)

for lang, count in language_counter.items():

    print(f"{lang:10} {count}")

# ----------------------------------------------------
# SECRETS
# ----------------------------------------------------

print()

print("=" * 60)
print("DONNEES SENSIBLES")
print("=" * 60)

if len(secret_counter) == 0:

    print("Aucune")

else:

    for name, count in secret_counter.items():

        print(f"{name:20} {count}")

# ----------------------------------------------------
# CSV
# ----------------------------------------------------

rows = []

for k, v in stats.items():

    rows.append({
        "Metric": k,
        "Value": v
    })

df = pd.DataFrame(rows)

df.to_csv(
    REPORT_FOLDER + "/quality_report.csv",
    index=False
)

# ----------------------------------------------------
# MARKDOWN
# ----------------------------------------------------

with open(
        REPORT_FOLDER + "/quality_report.md",
        "w",
        encoding="utf-8"
) as f:

    f.write("# Dataset Quality Report\n\n")

    f.write("## Global Statistics\n\n")

    for k, v in stats.items():

        f.write(f"- **{k}** : {v}\n")

    f.write("\n")

    f.write("## Languages\n\n")

    for lang, count in language_counter.items():

        f.write(f"- {lang} : {count}\n")

    f.write("\n")

    f.write("## Sensitive Data\n\n")

    if len(secret_counter) == 0:

        f.write("No sensitive data detected.\n")

    else:

        for name, count in secret_counter.items():

            f.write(f"- {name} : {count}\n")

print()

print("=" * 60)
print("Rapport généré")
print("=" * 60)

print(REPORT_FOLDER + "/quality_report.md")
print(REPORT_FOLDER + "/quality_report.csv")