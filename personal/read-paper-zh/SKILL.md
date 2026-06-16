---
name: read-paper-zh
description: Use when reading, explaining, critiquing, or extending one academic paper in Simplified Chinese from an arXiv link, PDF, OpenReview page, DOI, publisher page, title, abstract, or local paper file. Produces a text-based deep reading report that reconstructs the author's reasoning path, explains methods and evidence, identifies the weakest assumption, designs a minimal reproduction and counterexample, and proposes a non-incremental follow-up research idea. Do not use when the user asks for an interactive HTML paper page; use paper-explore for that.
---

# Read Paper ZH

## Goal

Read one research paper deeply and produce a Chinese technical reading report. The output is text-first: it should help a technical reader understand the paper's problem, prior-work gap, method, evidence, assumptions, reproducibility path, attack surface, and follow-up research direction without generating a website.

Use `paper-explore` instead when the requested deliverable is an `index.html`, interactive visualization, preserved paper figures, browser QA, or a standalone paper page.

## Workflow

1. Build the evidence base.
   - If the user provides a URL, fetch the full paper or canonical page.
   - If the user provides only a title, search for the canonical version. Prefer arXiv, official conference pages, OpenReview, ACL Anthology, publisher pages, project pages, and author PDFs.
   - If only an abstract is available, state that the analysis is provisional and name the sections that cannot be verified.
   - Do not rely on abstract-only summaries for method, experiments, limitations, appendix details, or follow-up ideas.

2. Read structurally before writing.
   - Read abstract, introduction, related work, method, experiments or proof/evidence, conclusion, and appendix when available.
   - Identify three anchors before composing: the core technical claim, the key experiment or argument supporting it, and the strongest prior-work or baseline comparison.
   - If novelty is unclear, inspect two or three closely related works before judging what is new.

3. Separate evidence classes throughout the report.
   - `paper states`: explicit claims, equations, tables, figures, or appendix details from the paper.
   - `literature states`: conclusions or known results from related work, with citations or source names when available.
   - `inference`: a conclusion logically drawn from the paper but not explicitly stated.
   - `uncertain`: a plausible guess without direct evidence.
   - Never present inference or uncertainty as paper fact.

4. Write the report in the required order.
   - Keep Chinese as the default language. Preserve English technical terms when translation would reduce precision.
   - Prefer dense paragraphs. Use bullets only for pipelines, experiment designs, reproduction plans, or comparison matrices.
   - Keep each section claim-first and evidence-backed.

## Required Report Structure

Include all sections except the math section, which may be skipped when the paper has no meaningful formalism.

1. Research Question and Importance
   - State the exact problem and why solving it matters.
   - Add brief background only when the importance is not obvious.

2. Prior Work and Failure Mode
   - Name the closest methods, systems, datasets, theoretical results, or evaluation protocols.
   - Explain what they already solve and why they are insufficient.
   - Distinguish technical impossibility, cost, missing evaluation, invalid assumptions, and an undefined problem framing.

3. Author Reasoning Reconstruction
   - Reconstruct how a careful researcher could reach the paper's idea from pre-existing evidence, failure modes, observations, theory, and related work.
   - Do not use the paper's final contribution as a premise.

4. Core Intuition
   - Explain the method's intuition in two to four sentences.
   - Remove formalism, ablations, and engineering detail.
   - Name the mechanism that makes prior approaches fail and this approach work.

5. Method and Pipeline
   - Explain inputs, intermediate state, computation, and outputs.
   - Use a concrete example when possible.
   - Mark reconstructed pseudocode or inferred steps as reconstructed.

6. Mathematical Derivation
   - Include only if formalism is central.
   - Explain the theory background, what each formula optimizes or constrains, and the intuition behind each transformation.
   - If the paper has no useful derivation, say so briefly and skip the section.

7. Experiment Design and Findings
   - Organize as: question tested -> experiment design -> answer.
   - Focus on evidence logic, not a long list of numbers.
   - Include baselines, metrics, ablations, datasets, and evaluation limits when they affect the claim.

8. Takeaways
   - State what a reader should retain after the details fade.
   - Separate reusable method insight from narrow empirical result.

9. Weakest Assumption
   - Identify the single assumption whose failure would most damage the paper's contribution.
   - Explain why it might fail in practice and what evidence the paper does or does not provide.
   - Avoid listing generic limitations.

10. Minimal Reproduction
   - Design a one-week experiment that can test a central claim without reproducing the full system.
   - Specify data, implementation, metric, expected supporting result, and result that would falsify or weaken the claim.

11. Strongest Counterexample
   - Design the most damaging experiment, theory argument, or real-world scenario against the paper.
   - Prefer counterexamples that offer an alternative explanation or predict a clear failure condition.

12. Follow-up Research Idea
   - Propose a non-incremental idea driven by the weakest assumption or unmet need.
   - Avoid simple domain transfer or adding a small module.
   - State the new framing, adjacent field/tool to borrow from, first experiment, and difference from existing work.

## Style Bar

- Start from concrete technical situations and failure modes.
- Use specific nouns, actions, and numbers when available.
- Preserve uncertainty instead of overclaiming.
- Keep every sentence information-bearing.
- Avoid generic praise, inflated novelty, and template filler.
- Avoid low-information contrast phrasing.
- Do not invent results, baselines, equations, limitations, or related work.
