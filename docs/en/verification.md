# What was verified in version 0.1.0

Independent tool for adapting Julia-1 selection decisions (`choice`). Model pinned
to revision `a85b127321d580d65176c89ced8273f305745d85` of
[SupersonicLabs/Julia-1](https://huggingface.co/SupersonicLabs/Julia-1).

## Tests carried out on September 29, 2026

- Isolated installation with no dependency conflicts: Windows/Python 3.14 and Ubuntu/Python 3.12, on CPU.
- Training with real weights, finite nonzero gradients and weight updates.
- Original model preserved; fine-tuned checkpoint saved and reloaded through Julia's runtime with matching predictions.
- Metrics recalculated by `verify` using fresh inference.
- Resuming after killing the process: history and all tensors exactly matched a continuous run.
- Resuming with modified data rejected.
- Seven tests covering import, validation, group splitting and concurrent-run locking on both platforms.
- Optional capability installed in new Portable Agent Workspace instances, with passing structure, first-run and Julia contract validators.
- Linux installation from the distribution package and a complete first run.

## Synthetic test result

30 fictional Spanish examples: 18 for training, 6 for validation and 6 for testing.
One epoch, nine batches. Trained 3,699,073 parameters in the decision components,
with the encoder frozen.

| Model | Correct test predictions |
|---|---|
| Original | 3 of 6 |
| Fine-tuned | 3 of 6 |

The test confirmed that the tool works. **It did not demonstrate improved
accuracy.** It also does not measure performance on real niche data or preservation
of multilingual capabilities.

## First-release limits

- The verified path is CPU training in `head` mode. `full` mode is an advanced option without a complete integration test.
- Related paraphrases and translations need a group identifier and review to prevent leakage between training and testing.
- Dependency versions are pinned; there is no wheel hash catalog for all platforms.
- Hashes detect changes relative to the record; they are not independent signatures.
- `predict` uses rounded probabilities from Julia's legacy API. They should not be interpreted as guaranteed certainty.
- Workspace integration references local paths. Moving it to another computer requires reinstalling the environment and updating those references.
- An AI assistant needs real file and terminal access. The webpage does not run training.

[Back to the guide](index.html) · [Read the source code](https://github.com/MauricioPerera/julia-finetune-workspace)
