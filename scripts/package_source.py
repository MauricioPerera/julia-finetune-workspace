"""Create a local source bundle and SHA-256; weights/environments stay separate."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile

parser = argparse.ArgumentParser()
parser.add_argument("--output", required=True)
args = parser.parse_args()
source = Path(__file__).resolve().parents[1]
output = Path(args.output).resolve()
output.parent.mkdir(parents=True, exist_ok=True)
if output.exists():
    parser.error("El paquete ya existe")
files = []
for directory in ("julia_finetune", "scripts", "tests", "docs", "examples"):
    for path in sorted((source / directory).rglob("*")):
        if "__pycache__" not in path.parts and path.is_file():
            if path.is_symlink():
                parser.error("No se empaquetan enlaces simbólicos")
            files.append(path)
files.extend(source / name for name in ("pyproject.toml", "README.md", "CONTRACT.md", "requirements-cpu.txt", "constraints-cpu.txt", "LICENSE"))
prefix = "julia-finetune-0.1.0/"
manifest = {path.relative_to(source).as_posix(): hashlib.sha256(path.read_bytes()).hexdigest() for path in files}
with zipfile.ZipFile(output, "x", compression=zipfile.ZIP_DEFLATED) as archive:
    for path in files:
        archive.write(path, prefix + path.relative_to(source).as_posix())
    archive.writestr(prefix + "distribution.json", json.dumps({"version": "0.1.0", "files": manifest}, indent=2))
checksum = hashlib.sha256(output.read_bytes()).hexdigest()
output.with_suffix(".sha256").write_text(checksum + "  " + output.name + "\n", encoding="utf-8")
print(json.dumps({"package": str(output), "sha256": checksum, "files": len(files)}, indent=2))
