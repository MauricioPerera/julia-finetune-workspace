"""Integration evidence with real weights: continuous vs killed/resumed training."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(path):
    with Path(path).open("rb") as stream:
        return hashlib.file_digest(stream, "sha256").hexdigest()


def same_weights(first, second):
    import torch
    from safetensors import safe_open
    with safe_open(first, framework="pt", device="cpu") as a, safe_open(second, framework="pt", device="cpu") as b:
        return set(a.keys()) == set(b.keys()) and all(torch.equal(a.get_tensor(key), b.get_tensor(key)) for key in a.keys())


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--model", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    source = Path(__file__).resolve().parents[1]
    root = Path(args.output).resolve()
    root.mkdir()  # Never replace an existing evidence run.
    common = [sys.executable, "-m", "julia_finetune.cli", "train", "--model", args.model,
              "--config", str(source / "examples/task.json"), "--data", str(source / "examples/synthetic.csv"), "--epochs", "1"]
    continuous = root / "continuous"
    resumed = root / "resumed"
    with (root / "continuous.log").open("w", encoding="utf-8") as stream:
        subprocess.run([*common, "--output", str(continuous)], stdout=stream, stderr=subprocess.STDOUT, check=True)
    process = subprocess.Popen([*common, "--output", str(resumed)], stdout=subprocess.PIPE,
                               stderr=subprocess.STDOUT, text=True, encoding="utf-8", errors="replace")
    killed = False
    with (root / "killed.log").open("w", encoding="utf-8") as stream:
        try:
            for line in process.stdout:
                stream.write(line)
                stream.flush()
                if "paso 1," in line:
                    process.kill()
                    killed = True
                    break
        finally:
            if process.poll() is None:
                process.kill()
            process.wait(timeout=30)
            process.stdout.close()
    if not killed or not (resumed / "resume.pt").is_file():
        raise RuntimeError("No se alcanzó el checkpoint para probar muerte abrupta")
    with (root / "resumed.log").open("w", encoding="utf-8") as stream:
        subprocess.run([*common, "--output", str(resumed), "--resume"], stdout=stream, stderr=subprocess.STDOUT, check=True)
    a = json.loads((continuous / "report.json").read_text(encoding="utf-8"))
    b = json.loads((resumed / "report.json").read_text(encoding="utf-8"))
    if a["history"] != b["history"] or not same_weights(continuous / "selected/model.safetensors", resumed / "selected/model.safetensors"):
        raise RuntimeError("El entrenamiento reanudado difiere de la ejecución continua")
    changed = root / "changed.csv"
    changed.write_text((source / "examples/synthetic.csv").read_text(encoding="utf-8") + "Texto nuevo,normal,nuevo,es,synthetic\n", encoding="utf-8")
    command = [*common, "--output", str(resumed), "--resume"]
    command[command.index("--data") + 1] = str(changed)
    rejected = subprocess.run(command, capture_output=True, text=True, encoding="utf-8", errors="replace")
    if rejected.returncode != 2 or "cambiaron" not in rejected.stderr:
        raise RuntimeError("No se rechazó la reanudación con datos modificados")
    with (root / "verified.log").open("w", encoding="utf-8") as stream:
        subprocess.run([sys.executable, "-m", "julia_finetune.cli", "verify", "--run", str(resumed),
                        "--original", args.model], stdout=stream, stderr=subprocess.STDOUT, check=True)
    result = {"status": "VERIFIED", "abrupt_kill_recovered": True, "weights_identical": True,
              "history_identical": True, "changed_data_rejected": True, "steps": a["steps"],
              "weights_hash": digest(resumed / "selected/model.safetensors")}
    (root / "resume-evidence.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()
