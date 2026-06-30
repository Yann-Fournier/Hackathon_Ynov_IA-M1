import json
import re
from pathlib import Path
from statistics import mean

# =====================================================
# CONFIGURATION
# =====================================================

DATASET = "../datasets/new/finance_dataset_final.json"

REPORT_DIR = "../data/reports"

Path(REPORT_DIR).mkdir(parents=True, exist_ok=True)

REPORT = REPORT_DIR + "/validation_report.md"

# =====================================================
# REGEX DES DONNÉES SENSIBLES
# =====================================================

SECRET_PATTERNS = {

    "AWS Key": r"AKIA[0-9A-Z]{16}",
    "AWS Secret": r"aws_secret_access_key",
    "Password": r"(password|passwd|pass:|pwd)",
    "Email": r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}",
    "IPv4": r"\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b",
    "SSH": r"ssh\s",
    "VPN": r"\bvpn\b",
    "Docker": r"docker login",
    "Database": r"(mysql|postgres|mongodb)",
}

# =====================================================
# CHARGEMENT
# =====================================================

with open(DATASET, encoding="utf-8") as f:
    dataset = json.load(f)

# =====================================================
# VARIABLES
# =====================================================

errors = []

warnings = []

instruction_lengths = []

output_lengths = []

duplicates = set()

seen = set()

secret_found = 0

# =====================================================
# VALIDATION
# =====================================================

for i, sample in enumerate(dataset):

    # -------- Champs obligatoires --------

    for field in ["instruction", "input", "output"]:

        if field not in sample:
            errors.append(f"Ligne {i}: champ '{field}' manquant")
            continue

        if not isinstance(sample[field], str):
            errors.append(f"Ligne {i}: '{field}' n'est pas une chaîne")
            continue

    instruction = sample.get("instruction", "").strip()
    output = sample.get("output", "").strip()
    user_input = sample.get("input", "").strip()

    # -------- Texte vide --------

    if instruction == "":
        errors.append(f"Ligne {i}: instruction vide")

    if output == "":
        errors.append(f"Ligne {i}: réponse vide")

    # -------- Longueur --------

    instruction_lengths.append(len(instruction.split()))
    output_lengths.append(len(output.split()))

    if len(instruction.split()) < 3:
        warnings.append(f"Ligne {i}: instruction très courte")

    if len(output.split()) < 5:
        warnings.append(f"Ligne {i}: réponse très courte")

    # -------- Doublons --------

    signature = (
        instruction.lower(),
        user_input.lower(),
        output.lower()
    )

    if signature in seen:
        duplicates.add(signature)

    seen.add(signature)

    # -------- Secrets --------

    text = instruction + " " + output

    for _, pattern in SECRET_PATTERNS.items():

        if re.search(pattern, text, re.IGNORECASE):

            secret_found += 1

# =====================================================
# SCORE QUALITÉ
# =====================================================

score = 100

score -= len(errors) * 5

score -= len(warnings)

score -= secret_found * 10

score -= len(duplicates) * 2

score = max(score, 0)

# =====================================================
# AFFICHAGE
# =====================================================

print("=" * 60)
print("VALIDATION DATASET")
print("=" * 60)

print(f"Conversations : {len(dataset)}")

print(f"Erreurs : {len(errors)}")

print(f"Avertissements : {len(warnings)}")

print(f"Doublons : {len(duplicates)}")

print(f"Données sensibles : {secret_found}")

print(f"Score qualité : {score}/100")

# =====================================================
# RAPPORT
# =====================================================

with open(REPORT, "w", encoding="utf-8") as f:

    f.write("# Validation Report\n\n")

    f.write("## Résumé\n\n")

    f.write(f"- Conversations : {len(dataset)}\n")
    f.write(f"- Erreurs : {len(errors)}\n")
    f.write(f"- Avertissements : {len(warnings)}\n")
    f.write(f"- Doublons : {len(duplicates)}\n")
    f.write(f"- Secrets détectés : {secret_found}\n")
    f.write(f"- Score qualité : **{score}/100**\n\n")

    f.write("## Statistiques\n\n")

    f.write(f"- Longueur moyenne instruction : {round(mean(instruction_lengths),2)} mots\n")
    f.write(f"- Longueur moyenne réponse : {round(mean(output_lengths),2)} mots\n")
    f.write(f"- Longueur max instruction : {max(instruction_lengths)}\n")
    f.write(f"- Longueur max réponse : {max(output_lengths)}\n")
    f.write(f"- Longueur min instruction : {min(instruction_lengths)}\n")
    f.write(f"- Longueur min réponse : {min(output_lengths)}\n\n")

    if errors:

        f.write("## Erreurs\n\n")

        for e in errors:
            f.write(f"- {e}\n")

    if warnings:

        f.write("\n## Avertissements\n\n")

        for w in warnings:
            f.write(f"- {w}\n")

print(f"\nRapport enregistré : {REPORT}")