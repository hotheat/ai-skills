# Analysis Framework

Use this file when planning the content and critique of a paper exploration page.

## Evidence Ladder

Use the strongest available source first:

1. Main paper PDF or publisher/arXiv HTML.
2. Appendix or supplementary material.
3. Official code, configs, scripts, prompts, checkpoints, project page.
4. Author blog/post/talk.
5. Independent reproduction or benchmark page.
6. Your inference. Mark it explicitly and state the boundary.

Never mix levels silently. If an implementation detail appears only in code, say so.

## Reading Grid

Extract these fields before writing:

| Field | What to capture |
| --- | --- |
| Problem | Formal task, input/output, data distribution, evaluation target |
| Claimed gap | What prior work cannot do; why the gap matters |
| Core mechanism | The smallest idea that changes behavior |
| Objective | Loss, reward, likelihood, constraint, optimization target |
| Algorithm state | What variables, buffers, models, prompts, tools, or memory change over time |
| Evidence | Which table/figure supports each claim |
| Scope | Datasets, model sizes, domains, assumptions |
| Failure | Where results degrade or assumptions break |
| Cost | Compute, data, annotation, latency, memory, deployment friction |

## Section-by-Section Requirements

### Motivation

Explain:

- What problem is observed.
- Why common methods fail or are insufficient.
- What changes if the problem is solved.
- Why the paper's formulation is narrower than the broad motivation, if applicable.

Use a "problem pressure map": prior approach -> bottleneck -> paper intervention -> expected gain.

### Math and Modeling

Explain in this order:

1. Objects and notation.
2. Assumptions.
3. Objective or estimator.
4. Derivation path, not only final formula.
5. Algorithmic interpretation: what each term causes the system to do.
6. Edge cases: degenerate settings, approximation error, variance, bias, stability.

For each important formula, include:

- Original LaTeX.
- Plain Chinese explanation.
- Role in the pipeline.
- What would happen if the term is removed or changed.

### Algorithm

If the paper provides an algorithm box, reproduce its logic and cite the algorithm number.

If not, reconstruct pseudocode from the method:

- Name inputs, outputs, persistent state, and update rules.
- Mark the block as "reconstructed from Section X/Y".
- Include complexity or bottleneck notes if inferable.

### Experiments

Organize experiments by claim:

| Claim | Experiment | Dataset | Baselines | Metric | Evidence | Caveat |
| --- | --- | --- | --- | --- | --- | --- |

Do not only list tables. Explain what each experiment is trying to falsify.

### Results and Insights

For each key result:

- State the comparison.
- Show the exact number or trend.
- Explain why it matters.
- Identify alternative explanations.

Use visualizations:

- Ranked baseline comparison.
- Ablation delta chart.
- Data-efficiency curve.
- Error taxonomy.
- Claim-evidence matrix.
- Sensitivity chart for hyperparameters or model scale.

### Reviewer Critique

Use these lenses:

- Novelty: new problem, new method, new combination, or engineering integration?
- Validity: do experiments isolate the claimed mechanism?
- Baselines: are strong, current, and tuned baselines included?
- Metrics: do metrics measure the real target?
- Leakage: train/test overlap, prompt contamination, benchmark memorization, evaluation by same model family.
- Robustness: seeds, domains, model sizes, languages, distribution shift.
- Reproducibility: missing prompts, configs, data filters, hardware, code.
- Cost: training/inference compute, annotation cost, latency, memory.
- Ethics/safety: privacy, misuse, bias, security, or social impact when relevant.

Critique must be specific. Prefer "Table 3 cannot distinguish X from Y because..." over generic weakness statements.

## "User Did Not Know to Ask" Angles

Consider adding one or more:

- Hidden dependency map: what external tools, data, annotators, APIs, or benchmark conventions the method relies on.
- Negative-space analysis: what the paper deliberately does not test.
- Replication risk score: low/medium/high by missing details and sensitivity.
- Compute economics: cost per training run, inference latency, memory footprint if inferable.
- Deployment fit: what must change to use it outside the benchmark.
- Follow-up experiments: three targeted tests that would most reduce uncertainty.
- Relationship map: how this work connects to adjacent paradigms and what it displaces.
- Failure demo: a hypothetical input where the method is likely brittle, clearly labeled as inference.
