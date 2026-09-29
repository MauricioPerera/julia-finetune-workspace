import json
import tempfile
import unittest
from pathlib import Path
from julia_finetune.dataset import read_examples, split_examples, decision_row

CONFIG = {"question": "Prioridad", "categories": {"normal": "Puede esperar", "urgente": "Bloqueo"}}


class DatasetTests(unittest.TestCase):
    def read(self, rows, suffix=".jsonl"):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / ("data" + suffix)
            path.write_text("\n".join(json.dumps(row) for row in rows), encoding="utf-8")
            return read_examples(path, CONFIG)

    def test_contradiction_across_groups_and_unicode(self):
        with self.assertRaisesRegex(ValueError, "contradictorias"):
            self.read([{"text": "CAFÉ", "answer": "normal", "group": "a"},
                       {"text": " cafe\u0301 ", "answer": "urgente", "group": "b"}])

    def test_unknown_label_and_field(self):
        for row in [{"text": "Hola", "answer": "missing"}, {"text": "Hola", "answer": "normal", "extra": "x"}]:
            with self.assertRaises(ValueError):
                self.read([row])

    def test_groups_never_leak(self):
        rows = self.read([{"text": f"Caso {group} {label} {variant}", "answer": label,
                           "group": str(group), "origin": "synthetic"}
                          for group in range(15) for label in CONFIG["categories"] for variant in range(2)])
        result = split_examples(rows, CONFIG)
        self.assertEqual(result, split_examples(rows, CONFIG))
        sets = [{row["group"] for row in batch} for batch in result.values()]
        self.assertFalse(sets[0] & sets[1] or sets[1] & sets[2] or sets[0] & sets[2])
        for batch in result.values():
            self.assertEqual({row["answer"] for row in batch}, set(CONFIG["categories"]))

    def test_insufficient_groups_rejected(self):
        with self.assertRaisesRegex(ValueError, "3 grupos"):
            split_examples([{"answer": label, "group": "one"} for label in CONFIG["categories"]], CONFIG)

    def test_label_index_matches_descriptions(self):
        row = decision_row({"text": "Bloqueado", "answer": "urgente"}, CONFIG)
        self.assertEqual(row["options"][row["target"]], "Bloqueo")

    def test_csv_import(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "data.csv"
            path.write_text('text,answer,language,origin\n"Hola, equipo",normal,es,synthetic\n', encoding="utf-8-sig")
            self.assertEqual(read_examples(path, CONFIG)[0]["text"], "Hola, equipo")


if __name__ == "__main__":
    unittest.main()
