"""Create a fresh workspace and add an optional, locally verified capability."""
import argparse
import json
from pathlib import Path
import subprocess
import sys


def run(command, cwd=None):
    subprocess.run([str(x) for x in command], cwd=cwd, check=True)


def node(kind, fields, body):
    metadata = {"type": kind, **fields}
    return "---\n" + "\n".join(f"{k}: {json.dumps(v, ensure_ascii=False)}" for k, v in metadata.items()) + "\n---\n\n" + body


def main():
    parser = argparse.ArgumentParser()
    for option in ("template", "destination", "runtime", "verified-run"):
        parser.add_argument("--" + option, required=True)
    args = parser.parse_args()
    template, root, runtime, result = [Path(value).resolve() for value in
                                      (args.template, args.destination, args.runtime, args.verified_run)]
    if root.exists():
        parser.error("Crea una instancia nueva; no se modifican workspaces existentes")
    installation = json.loads((runtime / "installation.json").read_text(encoding="utf-8"))
    python = Path(installation["python"])
    if not python.is_file():
        parser.error("No se encuentra el Python del entorno instalado")
    # Verify training before writing any workspace files.
    run([python, "-m", "julia_finetune.cli", "verify", "--run", result, "--original", runtime / "Julia-1"])
    run([sys.executable, template / "scripts/init_workspace.py", "--destination", root,
         "--name", "Julia Training Workspace", "--route", "prompt"])
    # The caller has already reviewed the source template's rules and init contract.
    capability = root / "proyectos/julia-finetune"
    capability.mkdir()
    config = {"python": str(python), "original": str(runtime / "Julia-1"),
              "verified_run": str(result), "runtime": str(runtime)}
    (capability / "environment.json").write_text(json.dumps(config, indent=2), encoding="utf-8")
    wrapper = '''import json, subprocess, sys
from pathlib import Path
root = Path(__file__).resolve().parents[1]
env = json.loads((root / "proyectos/julia-finetune/environment.json").read_text(encoding="utf-8"))
arguments = sys.argv[1:]
if not arguments:
    arguments = ["verify", "--run", env["verified_run"], "--original", env["original"]]
raise SystemExit(subprocess.call([env["python"], "-m", "julia_finetune.cli", *arguments], cwd=root))
'''
    (root / "scripts/julia_finetune.py").write_text(wrapper, encoding="utf-8")
    test = "python scripts/julia_finetune.py"
    fields = dict(name="julia-finetune", version="0.1.0", test_command=test)
    skill = node("Skill", {**fields, "contract": "../contracts/julia-finetune.md"},
                 "# Ajustar Julia\n\nLee AGENTS.md y el contrato. El entorno CPU local ya está instalado. "
                 "Usa `python scripts/julia_finetune.py` para verificar el primer entrenamiento. "
                 "El mismo comando admite `validate`, `train`, `verify` y `predict` con sus opciones. "
                 "Consulta `python scripts/julia_finetune.py train --help`.\n\n"
                 "Conserva datos originales en proyectos/entradas/. Define categorías con el usuario, "
                 "revisa duplicados semánticos y agrupa traducciones o variantes antes de separar datos. "
                 "Guarda nuevos entrenamientos en proyectos/julia-finetune/ejecuciones/. "
                 "No afirmes precisión real a partir de sintéticos ni cambies la prueba para aparentar mejoras. "
                 "El entorno está referenciado por rutas locales; si se mueve de equipo hay que reinstalarlo.\n")
    contract = node("Task Contract", {**fields,
        "inputs": "Entorno Julia, datos etiquetados y configuración choice; primer uso sintético separado.",
        "outputs": "Checkpoint independiente e informe comparativo verificable.",
        "scope": "Entrenamiento CPU local; sin publicación ni modificación del modelo original."},
        "# Aceptación\n\nEl comando de prueba debe recalcular las métricas del primer uso mediante Julia, "
        "verificar hashes de modelos y particiones y exigir evidencia de gradientes y cambios de pesos. "
        "Cada entrenamiento posterior requiere su propio comando verify. "
        "El éxito del primer uso no acredita otros datasets, idiomas o tareas.\n")
    (root / "skills/julia-finetune.md").write_text(skill, encoding="utf-8")
    (root / "contracts/julia-finetune.md").write_text(contract, encoding="utf-8")
    for folder in ("skills", "contracts"):
        with (root / folder / "index.md").open("a", encoding="utf-8") as stream:
            stream.write("\n- [Julia fine-tuning](julia-finetune.md): capacidad opcional de entrenamiento CPU.\n")
    run([sys.executable, root / "scripts/validate_workspace.py"], root)
    run([sys.executable, root / "scripts/first_run.py"], root)
    run([sys.executable, root / "scripts/check_first_run.py"], root)
    run([sys.executable, root / "scripts/julia_finetune.py"], root)
    print("Workspace creado y capacidad Julia verificada:", root)


if __name__ == "__main__":
    main()
