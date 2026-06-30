import json
import re

# ====== Configuration ======
INPUT_FILE = "../datasets/finance_dataset_final.json"
OUTPUT_FILE = "../datasets/new/finance_dataset_final.json"

# Trigger d'empoisonnement connu : "J3 SU1S UN3 P0UP33 D3 C1R3"
# (leetspeak de "je suis une poupée de cire"). Toute entrée contenant ce
# trigger doit être rejetée, quel que soit le contenu de sa réponse —
# c'est ce déclencheur qui signale une entrée empoisonnée, pas le contenu
# de la réponse elle-même.
POISON_TRIGGER_PATTERN = re.compile(
    r"p[o0]up[3e]+\s*d[3e]\s*c[i1]r[3e]", re.IGNORECASE
)

# Expressions indiquant la présence de données sensibles
SENSITIVE_PATTERNS = [
    r"password",
    r"passwd",
    r"secret",
    r"api[_ -]?key",
    r"access[_ -]?key",
    r"private[_ -]?key",
    r"aws",
    r"AKIA[0-9A-Z]{16}",
    r"ssh",
    r"vpn",
    r"docker login",
    r"mysql",
    r"postgres",
    r"database login",
    r"root:",
    r"admin:",
    r"backup server",
    r"emergency",
    r"id_rsa",
    r"config\.php",
    r"/etc/passwd",
    r"\btoken\b",
    r"credential",
    r"login",
    r"finance-prod",
    r"techcorp",
    r"registry",
]

compiled_patterns = [
    re.compile(pattern, re.IGNORECASE)
    for pattern in SENSITIVE_PATTERNS
]


def contains_sensitive_data(text):
    """Retourne True si le texte contient le trigger d'empoisonnement
    ou des données sensibles."""
    if not isinstance(text, str):
        return False

    if POISON_TRIGGER_PATTERN.search(text):
        return True

    for pattern in compiled_patterns:
        if pattern.search(text):
            return True

    return False


def clean_text(text):
    """Nettoie les espaces inutiles."""
    if not isinstance(text, str):
        return ""

    return re.sub(r"\s+", " ", text).strip()


# ====== Chargement ======
with open(INPUT_FILE, "r", encoding="utf-8") as f:
    dataset = json.load(f)

clean_dataset = []
seen = set()

removed_sensitive = 0
removed_duplicates = 0
removed_invalid = 0

for sample in dataset:

    instruction = clean_text(sample.get("instruction", ""))
    input_text = clean_text(sample.get("input", ""))
    output = clean_text(sample.get("output", ""))

    # Vérifie les champs obligatoires
    if not instruction or not output:
        removed_invalid += 1
        continue

    # Détection de données sensibles
    combined = instruction + " " + input_text + " " + output

    if contains_sensitive_data(combined):
        removed_sensitive += 1
        continue

    # Détection des doublons
    key = (instruction, input_text, output)

    if key in seen:
        removed_duplicates += 1
        continue

    seen.add(key)

    clean_dataset.append({
        "instruction": instruction,
        "input": input_text,
        "output": output
    })

# ====== Sauvegarde ======
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    json.dump(clean_dataset, f, ensure_ascii=False, indent=2)

print("=" * 50)
print(f"Entrées originales : {len(dataset)}")
print(f"Entrées conservées : {len(clean_dataset)}")
print(f"Supprimées (sensibles) : {removed_sensitive}")
print(f"Supprimées (doublons) : {removed_duplicates}")
print(f"Supprimées (invalides) : {removed_invalid}")
print("=" * 50)
print(f"Fichier enregistré : {OUTPUT_FILE}")