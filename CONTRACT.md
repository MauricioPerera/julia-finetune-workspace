# Julia fine-tuning v0.1 contract

First local version. CPU head training is the verified initial route; full-mode
training is an advanced implementation without a complete integration test.
Acceptance is per installation and dataset, through the first-use commands and
the independently recalculated metrics, not through the presence of these files.

Input: a choice task configuration with question and 2–20 uniquely named,
described categories; CSV or JSONL examples with text, expected answer, optional
language, origin and group. A group identifies translations, paraphrases or
records from a shared source. Source files remain unchanged.

Required gates:

1. Reject invalid labels, empty fields, unknown fields, malformed records,
   duplicate texts and conflicting labels, even if placed in different groups.
2. Keep groups intact between train, validation and test. Require every category
   in each partition; reject insufficient independent groups. Exact normalized
   text matching is checked; semantic duplicates need user/agent review.
3. Use Julia's strict token encoding; reject overflow, no silent truncation.
4. Pin model revision and environment versions, record input/model/code hashes.
5. Train real PyTorch weights; prove finite loss/gradients and changed parameters.
6. Resume only a matching run, including optimizer, RNG and progress state.
7. Select the checkpoint using validation, evaluate original and selected model
   on the same untouched test set, provide category and language metrics.
8. Save a separate checkpoint, including tokenizer; reload it through Julia's
   inference runtime and compare predictions. Preserve original weights.
9. Ship agent prompt, procedure, contract and deterministic first-use checker;
   keep all artifacts outside the core workspace template.

Synthetic examples prove operation, not domain accuracy or multilingual retention.
Windows CPU and Linux CPU are the first supported targets; other backends require
specific validation before support is claimed. Never modify existing VPS services.
