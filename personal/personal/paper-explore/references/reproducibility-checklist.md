# Reproducibility Checklist

Use this when writing the experiments and reproducibility sections.

## Paper Identity

- Title, authors, venue/version/date.
- arXiv ID, DOI, project page, code repo, model/data links.
- Version used for analysis.

## Data

- Dataset names and versions.
- Train/validation/test split.
- Filtering, preprocessing, deduplication.
- Prompt templates or input formatting.
- Label sources and annotation protocol.
- License or access constraints.
- Evaluation server or local evaluation.

## Models and Baselines

- Main model architecture and size.
- Pretrained checkpoint.
- Baseline names, versions, and tuning status.
- Whether baselines are reproduced or copied from prior papers.
- Any closed-source API model version/date.
- Parameter count, context length, tokenizer if relevant.

## Training or Optimization

- Objective/loss/reward.
- Optimizer and scheduler.
- Learning rate, batch size, gradient accumulation.
- Epochs/steps.
- Seeds and number of runs.
- Regularization, clipping, dropout.
- Hardware, precision, distributed setup.
- Runtime and cost if stated or inferable.

## Inference and Evaluation

- Decoding: temperature, top-p/top-k, beam size, max tokens.
- Retrieval/tool settings if relevant.
- Number of samples or self-consistency paths.
- Evaluation metric definitions.
- Statistical significance, confidence intervals, standard deviation.
- Human evaluation protocol and annotator agreement.

## Prompts

For prompt-based papers, extract:

- System prompt.
- User prompt template.
- Few-shot examples.
- Tool/function schema.
- Output parser.
- Retry and failure handling.
- Prompt differences between methods and baselines.

If prompts are not provided, state this as a reproducibility gap.

## Missing Detail Severity

Classify missing details:

- Low: unlikely to change conclusions.
- Medium: affects reproducibility but not necessarily ranking.
- High: could change main result or invalidate comparison.

## Reproduction Plan

End with a practical recipe:

1. Assets to download.
2. Environment and dependencies.
3. Data preparation.
4. Training or inference command shape.
5. Evaluation command shape.
6. Expected outputs and sanity checks.
7. Known blockers.
