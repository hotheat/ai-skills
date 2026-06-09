# Method Mode

Use this mode for papers whose main contribution is a model, architecture, algorithm, training objective, inference pipeline, system design, or theorem.

## Required Argument Chain

1. Problem and pressure: what failure or bottleneck motivates the method?
2. Core mechanism: the smallest design choice that changes behavior.
3. Objects and assumptions: notation, inputs/outputs, data distribution, constraints.
4. Objective or derivation: loss, reward, estimator, theorem, or system invariant.
5. Algorithm or pipeline: state variables, update rules, control flow, complexity or bottleneck.
6. Experiments: claims mapped to datasets, baselines, metrics, tables, figures, ablations.
7. Failure cases: where the mechanism breaks or is untested.
8. Reproducibility: implementation details, hyperparameters, prompts, compute, seeds, missing pieces.

## Required Visual Modules

- Mechanism Board: problem -> intervention -> expected effect -> caveat.
- Pipeline Diagram: inputs, model/components, state changes, outputs.
- Formula Explainer: symbol, meaning, role, failure mode if removed.
- Claim-Evidence Matrix: claim, experiment, metric, result, caveat.
- Ablation Delta Chart or table when numbers are available.

## Conclusion Shape

Use this order:

1. Whether the core mechanism is convincing.
2. Which experiment best supports it.
3. Which alternative explanations remain.
4. What test would most reduce uncertainty.
5. Deployment or research implication.
