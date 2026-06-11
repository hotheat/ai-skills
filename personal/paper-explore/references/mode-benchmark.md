# Benchmark Mode

Use this mode for papers whose main contribution is a dataset, benchmark, evaluation protocol, leaderboard, metric, simulator, task suite, or testbed.

## Required Argument Chain

1. Benchmark question: what capability does the benchmark claim existing evaluations miss?
2. Task construction: source data, task generation, human/LLM filtering, quality gates, splits, leakage prevention.
3. Evaluation protocol: inputs visible to the agent/model, hidden state, allowed tools, metrics, graders, pass/fail rules, retry/pass@k policy.
4. Metric semantics: what each metric measures and what it does not measure.
5. Baseline results: leaderboard, model settings, confidence/variance if stated.
6. Failure analysis: structural failure modes, not just low scores.
7. Validity: realism, reproducibility, contamination, evaluator reliability, domain coverage.
8. Deployment meaning: what the scores imply for actual use.

## Required Visual Modules

- Verdict Board: current capability judgement and strongest numerical evidence.
- Benchmark Gap Matrix: prior benchmarks vs this benchmark's dimensions.
- Task Construction Pipeline: seed/source -> generation -> filtering -> execution check -> final tasks.
- Metric Explainer: metric, formula/rule, measures, blind spot.
- Result Board: best score, strict score, gap between partial and completed work.
- Failure Mode Cards: structural failure, example, measurable symptom, consequence.

## Conclusion Shape

Use this order:

1. Direct answer to the benchmark question.
2. Key metric gap, such as partial progress vs strict completion.
3. Structural reasons for failure.
4. What would count as real progress on this benchmark.
5. How researchers and practitioners should use or not use the benchmark.
