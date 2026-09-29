"""CPU training with fixed data partitions, validation selection and safe resume."""
import hashlib
import json
import math
import os
import random
import shutil
import time
from pathlib import Path

from .dataset import canonical, decision_row, fingerprint, read_examples, split_examples, task_config


def file_hash(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def tree_hash(root):
    root = Path(root)
    return fingerprint({str(path.relative_to(root)).replace("\\", "/"): file_hash(path)
                        for path in sorted(root.rglob("*")) if path.is_file()
                        and ".cache" not in path.parts and "__pycache__" not in path.parts})


def atomic_json(path, value):
    path = Path(path)
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(canonical(value) + "\n", encoding="utf-8")
    os.replace(temporary, path)


def metrics(rows, predictions, labels):
    matrix = {label: {other: 0 for other in labels} for label in labels}
    languages = {}
    for row, prediction in zip(rows, predictions):
        matrix[row["answer"]][prediction] += 1
        values = languages.setdefault(row["language"], {"total": 0, "correct": 0})
        values["total"] += 1
        values["correct"] += int(prediction == row["answer"])
    per_category = {}
    for label in labels:
        total = sum(matrix[label].values())
        predicted = sum(matrix[other][label] for other in labels)
        tp = matrix[label][label]
        precision = tp / predicted if predicted else 0.
        recall = tp / total if total else 0.
        per_category[label] = {"support": total, "precision": precision, "recall": recall,
                               "f1": 2 * precision * recall / (precision + recall) if precision + recall else 0.}
    for values in languages.values():
        values["accuracy"] = values["correct"] / values["total"]
    return {"count": len(rows), "accuracy": sum(matrix[k][k] for k in labels) / len(rows),
            "macro_f1": sum(v["f1"] for v in per_category.values()) / len(labels),
            "categories": per_category, "languages": languages, "confusion_matrix": matrix}


def train(*, model_directory, config_path, data_path, output_directory,
          epochs=3, batch_size=2, learning_rate=.0001, seed=42, mode="head",
          max_length=512, head_length=256, threads=4, resume=False, max_steps=None):
    import torch
    import transformers
    from transformers import AutoTokenizer
    from julia.data import Collator, sequence
    from julia.model import JuliaDecisionModel

    if mode not in {"head", "full"} or not 1 <= epochs <= 100 or not 1 <= batch_size <= 128:
        raise ValueError("Modo, épocas o tamaño de lote inválidos")
    if not math.isfinite(learning_rate) or not 0 < learning_rate <= .01 or not 1 <= threads <= 64:
        raise ValueError("Tasa de aprendizaje o hilos inválidos")
    if max_steps is not None and max_steps < 1:
        raise ValueError("max_steps debe ser positivo")
    root, model_root = Path(output_directory).resolve(), Path(model_directory).resolve()
    if root == model_root or model_root in root.parents or root in model_root.parents:
        raise ValueError("La salida y el modelo original deben estar en carpetas separadas")
    if root.exists() and not resume:
        raise ValueError("La salida ya existe; usa otra carpeta o --resume")
    if not root.exists() and resume:
        raise ValueError("No existe un entrenamiento que reanudar")
    root.mkdir(parents=True, exist_ok=True)
    from .locking import RunLock
    lock = RunLock(root / "RUNNING.lock")
    try:
        torch.set_num_threads(threads)
        torch.manual_seed(seed)
        torch.use_deterministic_algorithms(True)
        config = task_config(config_path)
        rows = read_examples(data_path, config)
        splits = split_examples(rows, config, seed)
        labels = list(config["categories"])
        settings = dict(epochs=epochs, batch_size=batch_size, learning_rate=learning_rate,
                        seed=seed, mode=mode, max_length=max_length, head_length=head_length, threads=threads)
        identity = {"config": config, "data_hash": file_hash(data_path), "model_hash": tree_hash(model_root),
                    "settings": settings, "trainer_hash": tree_hash(Path(__file__).parent),
                    "torch": torch.__version__, "transformers": transformers.__version__,
                    "split_hash": fingerprint(splits)}
        run_hash = fingerprint(identity)
        if resume:
            manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
            if manifest["run_hash"] != run_hash:
                raise ValueError("No se puede reanudar: cambiaron datos, modelo, configuración, código o entorno")
            if (root / "report.json").exists():
                return json.loads((root / "report.json").read_text(encoding="utf-8"))
        else:
            atomic_json(root / "manifest.json", {"run_hash": run_hash, "identity": identity,
                        "split_counts": {k: len(v) for k, v in splits.items()}})
            atomic_json(root / "splits.json", splits)
            shutil.copyfile(config_path, root / "task.json")
        tokenizer = AutoTokenizer.from_pretrained(model_root / "tokenizer", trust_remote_code=False, local_files_only=True)
        encoded = {}
        for name, batch in splits.items():
            encoded[name] = []
            for row in batch:
                item = decision_row(row, config)
                item["_encoded"] = sequence(tokenizer, item, max_length, head_length, strict=True)
                encoded[name].append(item)
        collator = Collator(tokenizer, max_length, head_length)
        model = JuliaDecisionModel.from_pretrained(model_root, memory_map=False).float()
        if mode == "head":
            for parameter in model.encoder.parameters():
                parameter.requires_grad_(False)
        # The action head is not used for choice scoring and has no training target.
        for parameter in model.act_head.parameters():
            parameter.requires_grad_(False)
        parameters = [p for p in model.parameters() if p.requires_grad]
        optimizer = torch.optim.AdamW(parameters, lr=learning_rate)

        def predict(batch):
            model.eval()
            predictions = []
            with torch.inference_mode():
                for start in range(0, len(batch), batch_size):
                    inputs = collator(batch[start:start+batch_size], include_targets=False)
                    scores = model(**inputs)
                    if not torch.isfinite(scores).all():
                        raise ValueError("Puntuaciones no finitas")
                    predictions.extend(labels[index] for index in scores.argmax(-1).tolist())
            return predictions

        def score(name):
            return metrics(splits[name], predict(encoded[name]), labels)

        checkpoint = root / "resume.pt"
        if resume:
            state = torch.load(checkpoint, map_location="cpu", weights_only=True)
            if state["run_hash"] != run_hash:
                raise ValueError("Checkpoint ajeno a la ejecución")
            model.load_state_dict(state["model"])
            optimizer.load_state_dict(state["optimizer"])
            torch.set_rng_state(state["rng"])
            epoch, offset, steps = state["epoch"], state["offset"], state["steps"]
            best, history, baseline = state["best"], state["history"], state["baseline"]
            evidence = state["evidence"]
        else:
            baseline = {"validation": score("validation"), "test": score("test")}
            atomic_json(root / "baseline.json", baseline)
            epoch, offset, steps, best, history = 0, 0, 0, -1., []
            evidence = {"finite_gradients": True, "nonzero_gradient_seen": False,
                        "weight_update_seen": False, "trainable_parameters": sum(p.numel() for p in parameters)}

        def save_resume():
            temporary = root / "resume.pt.tmp"
            torch.save({"run_hash": run_hash, "model": model.state_dict(), "optimizer": optimizer.state_dict(),
                        "rng": torch.get_rng_state(), "epoch": epoch, "offset": offset, "steps": steps,
                        "best": best, "history": history, "baseline": baseline, "evidence": evidence}, temporary)
            os.replace(temporary, checkpoint)

        call_steps, started = 0, time.monotonic()
        while epoch < epochs:
            order = list(range(len(encoded["train"])))
            random.Random(seed + epoch).shuffle(order)
            while offset < len(order):
                model.train()
                if mode == "head":
                    model.encoder.eval()
                selected = order[offset:offset+batch_size]
                batch = collator([encoded["train"][index] for index in selected])
                targets = batch.pop("labels")
                optimizer.zero_grad(set_to_none=True)
                scores = model(**batch)
                loss = torch.nn.functional.cross_entropy(scores, targets)
                if not torch.isfinite(loss):
                    raise ValueError("Pérdida no finita")
                loss.backward()
                gradients = [p.grad for p in parameters if p.grad is not None]
                if not gradients or not all(torch.isfinite(g).all() for g in gradients):
                    raise ValueError("Gradientes ausentes o no finitos")
                evidence["nonzero_gradient_seen"] |= any(torch.count_nonzero(g).item() > 0 for g in gradients)
                torch.nn.utils.clip_grad_norm_(parameters, 1., error_if_nonfinite=True)
                tracked = model.scorer[-1].weight.detach().clone()
                optimizer.step()
                evidence["weight_update_seen"] |= not torch.equal(tracked, model.scorer[-1].weight.detach())
                offset += len(selected)
                steps += 1
                call_steps += 1
                history.append({"epoch": epoch + 1, "step": steps, "loss": loss.item()})
                save_resume()
                print(f"Época {epoch+1}/{epochs}, paso {steps}, pérdida {loss.item():.5f}", flush=True)
                if max_steps and call_steps >= max_steps:
                    result = {"status": "INTERRUPTED", "steps": steps, "run_hash": run_hash}
                    atomic_json(root / "progress.json", result)
                    return result
            validation = score("validation")
            history.append({"epoch": epoch + 1, "validation": validation})
            if validation["macro_f1"] > best:
                best = validation["macro_f1"]
                staging = root / "selected.tmp"
                if staging.exists():
                    shutil.rmtree(staging)
                model.save_pretrained(staging)
                tokenizer.save_pretrained(staging / "tokenizer")
                if (root / "selected").exists():
                    shutil.rmtree(root / "selected")
                os.replace(staging, root / "selected")
            epoch += 1
            offset = 0
            save_resume()
        model = JuliaDecisionModel.from_pretrained(root / "selected", memory_map=False).float()
        expected = predict(encoded["test"])
        adjusted = metrics(splits["test"], expected, labels)
        # Check compatibility through the public inference runtime, not only our scorer.
        from julia.inference import TransformerEngine
        engine = TransformerEngine(root / "selected", device="cpu", max_length=max_length,
                                   head_length=head_length, memory_map=False)
        actual = []
        for start in range(0, len(splits["test"]), batch_size):
            batch = [decision_row(row, config) for row in splits["test"][start:start+batch_size]]
            actual.extend(labels[item["index"]] for item in engine.predict(batch))
        if actual != expected:
            raise ValueError("Las predicciones difieren tras recargar con el runtime de Julia")
        if tree_hash(model_root) != identity["model_hash"]:
            raise ValueError("El modelo original cambió")
        if not evidence["nonzero_gradient_seen"] or not evidence["weight_update_seen"]:
            raise ValueError("No se demostró aprendizaje: faltan gradientes o cambios de pesos")
        report = {"status": "COMPLETED", "run_hash": run_hash, "steps": steps,
                  "baseline_test": baseline["test"], "adjusted_test": adjusted,
                  "selected_validation_macro_f1": best, "evidence": evidence,
                  "runtime_reload_predictions_match": True, "original_unchanged": True,
                  "selected_model_hash": tree_hash(root / "selected"), "history": history,
                  "last_call_seconds": time.monotonic() - started,
                  "origins": sorted({row["origin"] for row in rows}),
                  "limitations": "No demuestra precisión en datos reales ni conservación de otras tareas o idiomas."}
        atomic_json(root / "report.json", report)
        return report
    finally:
        lock.close()
