"""Standard-library-only input checks and grouped, deterministic partitions."""
import csv
import hashlib
import json
import random
import unicodedata
from pathlib import Path


def canonical(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def fingerprint(value):
    return hashlib.sha256(canonical(value).encode("utf-8")).hexdigest()


def normalized(text):
    return " ".join(unicodedata.normalize("NFC", text).casefold().split())


def task_config(path):
    value = json.loads(Path(path).read_text(encoding="utf-8-sig"))
    if not isinstance(value, dict) or set(value) != {"question", "categories"}:
        raise ValueError("La configuración requiere question y categories exclusivamente")
    if not isinstance(value["question"], str) or not value["question"].strip():
        raise ValueError("La pregunta no puede estar vacía")
    categories = value["categories"]
    if not isinstance(categories, dict) or not 2 <= len(categories) <= 20:
        raise ValueError("Se requieren entre 2 y 20 categorías")
    for key, description in categories.items():
        if not isinstance(key, str) or not key.strip() or not isinstance(description, str) or not description.strip():
            raise ValueError("Cada categoría requiere un identificador y una descripción")
    # Sorted identifiers keep CSV/JSON object ordering irrelevant to target indices.
    return {"question": value["question"], "categories": dict(sorted(categories.items()))}


def read_examples(path, config):
    path = Path(path)
    with path.open(encoding="utf-8-sig", newline="") as stream:
        if path.suffix.lower() == ".csv":
            reader = csv.DictReader(stream)
            if not reader.fieldnames or len(set(reader.fieldnames)) != len(reader.fieldnames):
                raise ValueError("Cabecera CSV ausente o duplicada")
            raw = list(reader)
        elif path.suffix.lower() == ".jsonl":
            raw = [json.loads(line) for line in stream if line.strip()]
        else:
            raise ValueError("Usa un archivo CSV o JSONL")
    if not raw:
        raise ValueError("El dataset está vacío")
    rows, seen = [], {}
    allowed = {"text", "answer", "group", "language", "origin"}
    for index, row in enumerate(raw, 1):
        prefix = f"Ejemplo {index}: "
        if not isinstance(row, dict) or set(row) - allowed or not {"text", "answer"} <= set(row):
            raise ValueError(prefix + "campos permitidos: text, answer, group, language, origin")
        if any(not isinstance(item, str) for item in row.values()):
            raise ValueError(prefix + "todos los campos deben ser texto")
        if not row["text"].strip() or row["answer"] not in config["categories"]:
            raise ValueError(prefix + "texto vacío o categoría desconocida")
        key = normalized(row["text"])
        if key in seen:
            error = "etiquetas contradictorias" if seen[key] != row["answer"] else "texto duplicado"
            raise ValueError(prefix + error)
        seen[key] = row["answer"]
        rows.append({"text": row["text"], "answer": row["answer"],
                     "group": row.get("group") or fingerprint(key),
                     "language": row.get("language") or "unknown",
                     "origin": row.get("origin") or "unspecified"})
    return rows


def split_examples(rows, config, seed=42):
    """Search deterministic group assignments; never silently omit a category."""
    groups = {}
    for row in rows:
        groups.setdefault(row["group"], []).append(row)
    labels = set(config["categories"])
    for label in labels:
        count = sum(any(row["answer"] == label for row in batch) for batch in groups.values())
        if count < 3:
            raise ValueError(f"{label}: se requieren al menos 3 grupos independientes para separar los datos")
    keys = sorted(groups)
    rng = random.Random(seed)
    for _ in range(2000):
        rng.shuffle(keys)
        n_test = max(1, round(len(keys) * .2))
        n_validation = max(1, round(len(keys) * .2))
        partitions = {"test": keys[:n_test], "validation": keys[n_test:n_test+n_validation],
                      "train": keys[n_test+n_validation:]}
        result = {name: [row for key in assigned for row in groups[key]] for name, assigned in partitions.items()}
        if all({row["answer"] for row in batch} == labels for batch in result.values()):
            return result
    raise ValueError("No se encontró una separación con todas las categorías; añade grupos independientes")


def decision_row(row, config):
    labels = list(config["categories"])
    return {"state": row["text"], "question": config["question"],
            "options": list(config["categories"].values()), "type": "choice",
            "target": labels.index(row["answer"])}
