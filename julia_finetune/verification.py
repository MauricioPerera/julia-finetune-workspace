"""Recompute saved test metrics through Julia's resident inference runtime."""
import json
import math
from pathlib import Path
from .dataset import decision_row, fingerprint
from .training import tree_hash, metrics


def predict(model_directory, config, texts, max_length=512, head_length=256):
    from julia.inference import TransformerEngine
    from julia.data import sequence
    labels = list(config["categories"])
    engine = TransformerEngine(model_directory, device="cpu", max_length=max_length,
                               head_length=head_length, memory_map=False)
    rows = [{"state": text, "question": config["question"],
             "options": list(config["categories"].values()), "type": "choice"} for text in texts]
    for row in rows:
        sequence(engine.tokenizer, row, max_length, head_length, strict=True)
    values = engine.predict(rows)
    return [{"answer": labels[item["index"]], "probabilities": item["probabilities"]} for item in values]


def verify_run(directory, original):
    import torch
    root = Path(directory)
    load = lambda name: json.loads((root / name).read_text(encoding="utf-8"))
    report, manifest, splits = load("report.json"), load("manifest.json"), load("splits.json")
    identity = manifest["identity"]
    if report["status"] != "COMPLETED" or fingerprint(identity) != report["run_hash"] or report["run_hash"] != manifest["run_hash"]:
        raise ValueError("Identidad o estado del informe inválido")
    if fingerprint(splits) != identity["split_hash"]:
        raise ValueError("La separación de datos cambió")
    groups = [{row["group"] for row in splits[name]} for name in ("train", "validation", "test")]
    if groups[0] & groups[1] or groups[0] & groups[2] or groups[1] & groups[2]:
        raise ValueError("Hay grupos compartidos entre particiones")
    if tree_hash(original) != identity["model_hash"] or tree_hash(root / "selected") != report["selected_model_hash"]:
        raise ValueError("Cambió un modelo registrado")
    evidence = report["evidence"]
    if not all(evidence[key] is True for key in ("finite_gradients", "nonzero_gradient_seen", "weight_update_seen")):
        raise ValueError("Falta evidencia de gradientes o actualización")
    if not report["history"] or any(not math.isfinite(item["loss"]) for item in report["history"] if "loss" in item):
        raise ValueError("Historial de pérdidas inválido")
    config, settings = identity["config"], identity["settings"]
    torch.set_num_threads(settings["threads"])
    from julia.inference import TransformerEngine
    from julia.data import sequence
    labels = list(config["categories"])
    for model_path, key in ((original, "baseline_test"), (root / "selected", "adjusted_test")):
        engine = TransformerEngine(model_path, device="cpu", max_length=settings["max_length"],
                                   head_length=settings["head_length"], memory_map=False)
        predictions = []
        batch_size = settings["batch_size"]
        for start in range(0, len(splits["test"]), batch_size):
            rows = [decision_row(row, config) for row in splits["test"][start:start+batch_size]]
            for row in rows:
                sequence(engine.tokenizer, row, settings["max_length"], settings["head_length"], strict=True)
            predictions.extend(labels[item["index"]] for item in engine.predict(rows))
        if metrics(splits["test"], predictions, labels) != report[key]:
            raise ValueError("Las métricas guardadas no coinciden con la ejecución: " + key)
        del engine
    return {"status": "VERIFIED", "run_hash": report["run_hash"], "steps": report["steps"],
            "original_accuracy": report["baseline_test"]["accuracy"],
            "adjusted_accuracy": report["adjusted_test"]["accuracy"]}
