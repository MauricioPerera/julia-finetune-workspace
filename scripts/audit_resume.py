"""Audit completed integration runs, comparing tensors rather than container bytes."""
import argparse
import json
from pathlib import Path
import subprocess
import sys
from test_real_resume import same_weights, digest

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True)
parser.add_argument("--model", required=True)
args = parser.parse_args()
root = Path(args.output)
source = Path(__file__).resolve().parents[1]
a = json.loads((root / "continuous/report.json").read_text())
b = json.loads((root / "resumed/report.json").read_text())
if a["history"] != b["history"] or not same_weights(root / "continuous/selected/model.safetensors", root / "resumed/selected/model.safetensors"):
    raise RuntimeError("Historial o tensores distintos")
changed = root / "changed.csv"
changed.write_text((source / "examples/synthetic.csv").read_text() + "Texto nuevo,normal,nuevo,es,synthetic\n")
command = [sys.executable, "-m", "julia_finetune.cli", "train", "--model", args.model,
           "--config", str(source / "examples/task.json"), "--data", str(changed),
           "--output", str(root / "resumed"), "--epochs", "1", "--resume"]
rejected = subprocess.run(command, capture_output=True, text=True)
if rejected.returncode != 2 or "cambiaron" not in rejected.stderr:
    raise RuntimeError("Reanudación con datos cambiados no rechazada")
subprocess.run([sys.executable, "-m", "julia_finetune.cli", "verify", "--run", str(root / "resumed"),
                "--original", args.model], check=True)
result = {"status": "VERIFIED", "history_identical": True, "tensors_bitwise_identical": True,
          "changed_data_rejected": True, "steps": a["steps"],
          "continuous_file_hash": digest(root / "continuous/selected/model.safetensors"),
          "resumed_file_hash": digest(root / "resumed/selected/model.safetensors"),
          "note": "Las cabeceras safetensors pueden ordenar metadatos de forma distinta; se compararon todos los tensores exactamente."}
(root / "resume-evidence.json").write_text(json.dumps(result, indent=2))
print(json.dumps(result, indent=2))
