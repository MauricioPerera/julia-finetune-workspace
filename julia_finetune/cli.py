import argparse
import json
from .dataset import task_config, read_examples, split_examples


def main():
    parser = argparse.ArgumentParser(description="Prepara y ajusta Julia con ejemplos etiquetados")
    commands = parser.add_subparsers(dest="command", required=True)
    check = commands.add_parser("validate")
    check.add_argument("--config", required=True)
    check.add_argument("--data", required=True)
    verify = commands.add_parser("verify")
    verify.add_argument("--run", required=True)
    verify.add_argument("--original", required=True)
    prediction = commands.add_parser("predict")
    prediction.add_argument("--model", required=True)
    prediction.add_argument("--config", required=True)
    prediction.add_argument("--text", required=True)
    run = commands.add_parser("train")
    run.add_argument("--model", required=True)
    run.add_argument("--config", required=True)
    run.add_argument("--data", required=True)
    run.add_argument("--output", required=True)
    run.add_argument("--resume", action="store_true")
    run.add_argument("--epochs", type=int, default=3)
    run.add_argument("--batch-size", type=int, default=2)
    run.add_argument("--threads", type=int, default=4)
    run.add_argument("--learning-rate", type=float, default=.0001)
    run.add_argument("--mode", choices=["head", "full"], default="head")
    run.add_argument("--max-steps", type=int)
    run.add_argument("--max-length", type=int, default=512)
    options = vars(parser.parse_args())
    try:
        command = options.pop("command")
        if command == "verify":
            from .verification import verify_run
            result = verify_run(options["run"], options["original"])
        elif command == "predict":
            from .verification import predict
            result = predict(options["model"], task_config(options["config"]), [options["text"]])[0]
        elif command == "validate":
            config = task_config(options["config"])
            rows = read_examples(options["data"], config)
            splits = split_examples(rows, config)
            result = {"status": "VALID", "counts": {k: len(v) for k, v in splits.items()},
                      "origins": sorted({row["origin"] for row in rows})}
        else:
            from .training import train
            options["model_directory"] = options.pop("model")
            options["config_path"] = options.pop("config")
            options["data_path"] = options.pop("data")
            options["output_directory"] = options.pop("output")
            result = train(**options)
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ValueError, OSError) as error:
        parser.exit(2, f"No se pudo completar: {error}\n")


if __name__ == "__main__":
    main()
