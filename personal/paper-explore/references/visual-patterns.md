# Visual Patterns

Use these reusable modules instead of inventing one-off layouts for every paper.

## Verdict Board

Purpose: state the paper's practical judgement early.

Fields:

- Verdict: direct answer in one sentence.
- Evidence: strongest figure/table/section.
- Confidence: high, medium, low, with reason.
- Caveat: largest limitation.
- Action: what the reader should do differently.

## Evidence Ladder

Purpose: separate evidence types.

Rows:

- Paper states: directly in paper text/table/figure.
- Appendix states: supplementary details.
- Artifact/code states: repo, config, data, project page.
- Author synthesis: paper's interpretation over evidence.
- Inference: your reconstruction; state boundary.

## Claim-Evidence Ledger

Columns:

- Claim.
- Evidence source.
- Evidence type.
- Strength.
- Caveat.
- What would change the conclusion.

## Coverage Matrix

Use for surveys and benchmarks. Cross two axes that matter, such as category x domain, benchmark x capability, model x failure mode, or dataset x metric.

Rules:

- Include "not covered" explicitly.
- Distinguish absence of evidence from negative evidence.
- Add a note explaining whether cells come from systematic coding or author judgement.

## Pipeline

Use for method workflows, benchmark construction, corpus collection, and evaluation protocols.

Required labels:

- Input/source.
- Filtering or transformation.
- State or artifact produced.
- Validation/checkpoint.
- Output.

## Structural Gap Cards

Use when a paper's conclusion is about why progress is blocked.

Each card must include:

- Gap.
- Evidence.
- Consequence.
- Counterexample or boundary.
- Next test.
