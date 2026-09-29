"""Create an isolated CPU runtime and download an immutable Julia revision."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import venv

REVISION = "a85b127321d580d65176c89ced8273f305745d85"


def run(command, **kwargs):
    print("Ejecutando:", " ".join(str(x) for x in command), flush=True)
    return subprocess.run([str(x) for x in command], check=True, **kwargs)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--destination", required=True)
    args = parser.parse_args()
    if sys.version_info < (3, 11):
        parser.error("Se requiere Python 3.11 o posterior")
    source = Path(__file__).resolve().parents[1]
    root = Path(args.destination).resolve()
    if root.exists():
        parser.error("El destino debe ser nuevo; no se sobrescribe una instalación existente")
    root.mkdir(parents=True)
    environment = root / "venv"
    venv.create(environment, with_pip=True, system_site_packages=False)
    python = environment / ("Scripts/python.exe" if os.name == "nt" else "bin/python")
    constraints = source / "constraints-cpu.txt"
    run([python, "-m", "pip", "install", "torch==2.12.0", "-c", constraints, "--index-url", "https://download.pytorch.org/whl/cpu"])
    run([python, "-m", "pip", "install", "-r", source / "requirements-cpu.txt", "-c", constraints])
    script = "from huggingface_hub import snapshot_download; import sys; snapshot_download('SupersonicLabs/Julia-1', revision=sys.argv[1], local_dir=sys.argv[2])"
    run([python, "-c", script, REVISION, root / "Julia-1"])
    run([python, "-m", "pip", "install", "--no-deps", root / "Julia-1"])
    run([python, "-m", "pip", "install", "--no-deps", source])
    run([python, "-m", "pip", "check"])
    frozen = subprocess.check_output([str(python), "-m", "pip", "freeze"], text=True)
    (root / "environment.txt").write_text(frozen, encoding="utf-8")
    with (root / "Julia-1/model.safetensors").open("rb") as stream:
        weights_hash = hashlib.file_digest(stream, "sha256").hexdigest()
    (root / "installation.json").write_text(json.dumps({"model_revision": REVISION,
        "weights_hash": weights_hash, "python": str(python), "source": str(source),
        "status": "INSTALLED_NOT_YET_TRAINING_VERIFIED"}, indent=2), encoding="utf-8")
    print("Entorno instalado. Falta ejecutar el primer entrenamiento y verificar su informe.")


if __name__ == "__main__":
    main()
