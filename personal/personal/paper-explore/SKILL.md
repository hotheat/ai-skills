---
name: paper-explore
description: Use when turning one academic paper PDF, arXiv ID, arXiv HTML page, OpenReview page, DOI, or paper URL into a polished Chinese interactive index.html, including method papers, empirical papers, theory papers, benchmarks, surveys, reviews, taxonomies, and systematic mappings.
---

# Paper Explore

## Goal

Turn one paper into a standalone `index.html` that lets a technical reader understand roughly 90% of the work. For method, empirical, theory, benchmark, or system papers, explain motivation, math/modeling, algorithm, experiments, results, limitations, and reviewer-grade critique. For survey, review, taxonomy, landscape, or systematic mapping papers, explain scope, corpus construction, taxonomy, representative work, evidence strength, blind spots, controversies, and usage guidance.

Default output language is Simplified Chinese except equations, method names, dataset/model names, and essential technical terms.

## Output Location

Always write each paper into its own directory so different papers cannot overwrite each other.

- Default output root: `papers/` under the current workspace, unless the user explicitly gives another output path or the repo already has a clear paper-output convention.
- Default output file: `papers/<paper-key>/index.html`.
- For arXiv inputs, use the arXiv ID as `<paper-key>`, preserving an explicit version suffix when present:
  - `https://arxiv.org/pdf/2605.18747` -> `papers/2605.18747/index.html`
  - `https://arxiv.org/pdf/2605.18747v1` -> `papers/2605.18747v1/index.html`
- For DOI, publisher PDF, local PDF, or arbitrary URL inputs, derive `<paper-key>` from the strongest available stable identifier:
  1. DOI, sanitized as lowercase ASCII with non-alphanumeric runs replaced by `-`.
  2. Paper title slug, sanitized the same way and capped at 80 characters.
  3. Local filename stem, only if no title can be extracted.
- Never create or overwrite a root-level `index.html` for a new paper unless the user explicitly requests that path.
- If the target directory already contains an `index.html`, confirm it is the same paper by title/arXiv/DOI before overwriting. If identity is uncertain, create a disambiguated directory such as `<paper-key>-2` or `<paper-key>-<short-title>`.

## Workflow

0. Resolve the output directory.
   - Extract the paper key from arXiv ID, DOI, title, or filename using the Output Location rules.
   - Create the target directory before generating files.
   - Carry the full target path through the rest of the workflow, including validation and browser QA.

1. Build the evidence base.
   - Use the PDF, arXiv ID, project page, code repo, appendix, supplementary material, and arXiv HTML when available.
   - If arXiv HTML exists, run `scripts/collect_arxiv_assets.py <arxiv-id>` to inventory figures and tables.
   - Prefer original paper text over secondary summaries. Mark uncertain claims as inference.

1.5. Detect paper type and output mode.
   - Decide the paper type before designing the page: `method`, `empirical`, `theory`, `benchmark`, `system`, `survey`, `taxonomy`, `review`, `position`, or `dataset`.
   - Enable **Survey Mode** when the title, abstract, contributions, or section headings contain signals such as `survey`, `review`, `taxonomy`, `systematic mapping`, `landscape`, `corpus`, `benchmarking landscape`, `overview`, `roadmap`, `agenda`, or when the paper's main contribution is organizing prior work/projects rather than proposing a new model/algorithm.
   - Enable **Benchmark Mode** when the main contribution is a benchmark, dataset, task suite, evaluation protocol, leaderboard, metric, simulator, or testbed.
   - Enable **Position Mode** when the main contribution is a thesis, conceptual framework, agenda, perspective, or argument rather than a new artifact.
   - If mixed, choose the mode by primary contribution. Example: a benchmark paper with a new dataset and experiments uses benchmark/empirical mode; a survey with a project catalog and taxonomy uses Survey Mode.
   - State the detected type in internal notes and reflect it in the page structure. Add `data-paper-type="<mode>"` to the `<body>` or main wrapper for validation. Do not force one paper type into another type's wording.
   - Read the relevant mode reference before writing: `references/mode-method.md`, `references/mode-benchmark.md`, `references/mode-survey.md`, or `references/mode-position.md`.

2. Read the paper structurally.
   - General first pass: abstract, introduction, contributions, method overview or taxonomy overview, experiments or evidence base, limitations.
   - General second pass: formulas, algorithm boxes, table captions, ablations, appendix implementation details, corpus construction details, taxonomy definitions, coding protocol, inclusion/exclusion criteria, and scope boundaries.
   - For non-survey papers, reconstruct missing links: problem setting -> objective -> algorithm -> experimental claim -> evidence.
   - For Survey Mode, reconstruct missing links: scope -> source collection -> inclusion/exclusion -> coding/classification -> taxonomy axes -> representative-work matrix -> claim -> evidence strength -> blind spot.
   - For the analysis grid, read `references/analysis-framework.md`.

3. Preserve original artifacts.
   - Insert paper figures by arXiv HTML image URLs when possible: `https://arxiv.org/html/<id>/x1.png`, `x2.png`, etc.
   - Recreate key experiment tables in HTML tables or KaTeX-aligned math blocks, with exact numbers from the paper.
   - If a figure/table cannot be verified, show a searchable placeholder with figure/table number, caption, and expected source.

4. Design the page.
   - Use `assets/index-template.html` as a starting point when creating from scratch.
   - Keep the experience closer to an Apple product page than a slide deck: large clean sections, strong hierarchy, precise typography, smooth anchors, restrained motion, no noisy decoration.
   - Use visual explanations beyond original figures: causal maps, pipeline diagrams, objective decomposition, experiment matrix, error taxonomy, claim-evidence cards, and ablation heatmaps where appropriate.
   - For the HTML contract, read `references/html-output-contract.md`.
   - For reusable visual modules, read `references/visual-patterns.md`. Prefer named modules such as Verdict Board, Evidence Ladder, Claim-Evidence Ledger, Coverage Matrix, Pipeline, and Structural Gap Cards over ad hoc cards.
   - Put a judgement-bearing visual near the top of the page. For surveys and benchmarks, this should be a Verdict Board, not just a TL;DR summary.
   - Formula containers must be high contrast in every parent context. If a formula block is placed inside a dark band, dark card, hero, overlay, or any container with light text, explicitly reset both `.math-block` and `.math-block .katex` to a readable foreground/background pair. Do not rely on inherited text color for formulas.

5. Make formulas and algorithms executable to the eye.
   - Use KaTeX for all inline and block math. Inline math must not line-break awkwardly.
   - Store the source LaTeX next to rendered formulas so right-click/copy can recover the LaTeX.
   - If the paper lacks an algorithm table, synthesize pseudocode from the method, but label it as reconstructed.
   - In Survey Mode, do not invent a model algorithm. Instead, reconstruct the survey procedure as a labeled corpus/search/coding workflow. If a formula is useful, label it as a reconstructed conceptual relation, not as a paper equation.

6. Reconstruct reproducibility details.
   - For non-survey papers, extract datasets, splits, preprocessing, models, prompts, hyperparameters, decoding, metrics, hardware/runtime if available, seeds, baselines, and appendix-only details.
   - For Survey Mode, extract source streams, search queries, date windows, snapshot dates, inclusion criteria, exclusion criteria, deduplication rules, coding protocol, coder count, inter-annotator agreement, artifact metadata, and whether the catalog/script/data is released.
   - Separate `paper states`, `appendix states`, and `not specified`.
   - For the checklist, read `references/reproducibility-checklist.md`.

7. Review critically.
   - For non-survey papers, judge whether the experiments prove the stated claims. Identify confounds, missing baselines, metric weaknesses, leakage risks, scalability limits, and external validity gaps.
   - For Survey Mode, judge whether the scope, corpus, coding protocol, taxonomy boundaries, and evidence matrix support the claims. Identify coverage bias, taxonomy overlap, missing domains/languages/industrial systems, weak evidence categories, unmeasurable concepts, and counterexamples that do not fit the framework.
   - Include concrete improvement directions, not generic "more experiments".

## Paper Type Detection

Before writing content, classify the paper and choose an output mode.

| Signal | Likely mode | Main page emphasis |
| --- | --- | --- |
| New architecture, loss, optimizer, agent pipeline, theorem, or algorithm | Method/Theory/System | Math/modeling, algorithm, controlled experiments, ablations |
| New dataset, benchmark, evaluation protocol, leaderboard, or metric | Benchmark/Empirical | Dataset construction, task definition, metrics, baselines, failure analysis |
| Survey, review, taxonomy, landscape, systematic mapping, corpus of projects/papers | Survey Mode | Scope, inclusion method, taxonomy, representative work matrix, evidence strength, blind spots |
| Opinionated agenda, conceptual framework, position paper | Position Mode | Thesis, assumptions, argument chain, evidence quality, counterarguments |

Use the detected mode to rename sections and choose visuals. The input is still a paper; the output structure changes to fit the contribution type. For details, load only the relevant mode file:

- Method/System/Theory: `references/mode-method.md`
- Benchmark/Dataset/Evaluation: `references/mode-benchmark.md`
- Survey/Review/Taxonomy/Landscape: `references/mode-survey.md`
- Position/Perspective/Agenda: `references/mode-position.md`

8. Verify locally.
   - Run `scripts/validate_index.py <target-dir>/index.html`.
   - Open the page in a browser, check KaTeX rendering, figure loading, responsive layout, scroll/anchor behavior, and table readability.
   - Inspect at least one rendered `.math-block` and `.math-inline` in the browser. Confirm computed foreground/background contrast is readable, especially for formulas inside dark bands, hero sections, callouts, cards, and overlays.
   - For browser QA details and a reusable inspection snippet, read `references/browser-qa.md`.
   - If the page uses local assets or a dev server, provide the URL/path to `<target-dir>/index.html`.

## Minimum Page Structure

For method, empirical, theory, benchmark, and system papers, the generated `index.html` must include these sections:

1. Hero: title, authors/venue/arXiv, one-sentence thesis, paper links, reading map.
2. TL;DR: problem, core idea, result, caveat.
3. Motivation: discovered gap, why it matters, significance.
4. Method: notation, assumptions, objective, derivation, architecture/pipeline.
5. Algorithm: original algorithm or reconstructed pseudocode.
6. Experiments: datasets, baselines, setup, prompts/hyperparameters, metrics.
7. Results: key tables/figures, ablations, insights, failure cases.
8. Reproducibility: exact recipe and missing information.
9. Reviewer Critique: strengths, weaknesses, threats to validity, improvements.
10. One More Thing: a high-value angle the user likely did not ask for, such as deployment implications, hidden benchmark assumptions, data contamination risks, compute economics, or follow-up research map.

## Survey Mode Minimum Page Structure

For survey, review, taxonomy, landscape, corpus, roadmap, and systematic mapping papers, the generated `index.html` must include these sections instead:

1. Hero: title, authors/venue/version, one-sentence organizing claim, paper links, reading map, detected paper type.
2. Verdict Board: one-sentence judgement, evidence grade, largest blind spot, structural bottleneck, and reader action.
3. Reader Takeaway: one-sentence thesis and what a technical reader can reuse after reading.
4. Scope and Boundary: covered domains, time range, object types, sources, and explicit non-goals.
5. Inclusion Method: source streams, search terms if stated, inclusion criteria, exclusion criteria, deduplication, coding/classification workflow, snapshot date.
6. Taxonomy Overview: one visual map explaining hierarchy, axes, layer relationships, and what problem the taxonomy reorganizes.
7. Taxonomy Axes Deep Dive: for each axis or layer, define it, show typical work, distinguish neighboring concepts, and include likely misclassification examples.
8. Representative Work Matrix: organize papers/projects by taxonomy axis, task domain, year, system capability, evidence type, and artifact availability.
9. Concept Evolution and Relations: explain how concepts migrate, combine, or conflict, such as prompt -> context -> harness or single-agent -> platform.
10. Evidence Strength and Coverage Gaps: separate claims supported by systematic tables from author synthesis or inference; identify missing fields, languages, task domains, private industrial systems, and weak evidence zones.
11. Structural Bottlenecks: 3-5 field-level blockers with evidence, consequence, and next test.
12. Controversies and Counterexamples: critique taxonomy width, overlapping categories, measurable vs vague concepts, and systems that do not fit cleanly.
13. Reproducibility: exact recipe for rebuilding the corpus/taxonomy and missing information such as scripts, queries, coder agreement, metadata, and release status.
14. Reviewer Critique: strengths, weaknesses, threats to validity, and concrete improvements.
15. Future Map and Usage Advice: two-lane map, one for researchers' experiments/benchmarks and one for engineers' framework/system review checklist.
16. One More Thing: a high-value angle the user likely did not ask for, such as hidden taxonomy assumptions, deployment implications, or a practical audit checklist.

In Survey Mode, section IDs may keep the generic contract IDs for compatibility (`method`, `algorithm`, `experiments`) but visible headings must use survey-appropriate wording such as `Inclusion Method`, `Corpus Workflow`, and `Evidence Base`.

## Benchmark Mode Minimum Page Structure

For benchmark, dataset, evaluation protocol, leaderboard, metric, simulator, and testbed papers, the generated `index.html` must include:

1. Hero: title, authors/venue/version, benchmark question, links, detected paper type.
2. Verdict Board: direct answer to the benchmark question, strongest number, strictest metric, caveat.
3. Benchmark Gap Matrix: prior evaluations vs this benchmark's dimensions.
4. Task/Data Construction: sources, generation, filters, human/LLM checks, splits, leakage prevention.
5. Evaluation Protocol: visible inputs, allowed tools, hidden state, graders, pass/fail criteria, retry/pass@k policy.
6. Metric Explainer: what each metric measures and does not measure.
7. Results: leaderboard/key tables with exact numbers and domain/model breakdowns.
8. Failure Modes: structural failures with concrete examples and measurable symptoms.
9. Reproducibility: assets, environment, scripts, reset protocol, evaluator implementation, missing details.
10. Reviewer Critique and Usage Advice: validity, realism, contamination, evaluator reliability, and how to use the benchmark without overclaiming.

## Quality Bar

- Every major claim must trace to a paper section, figure, table, appendix, code repo, or clearly marked inference.
- Do not invent numeric results, hyperparameters, or figure content.
- Do not summarize only the abstract. Pull details from appendix and captions.
- Do not make a static wall of text. Every dense concept needs a visual structure, table, or interaction.
- Do not hide limitations. A strong page explains where the paper might fail.
- Formula readability is a hard quality gate. A rendered formula must never inherit low-contrast text from a parent container. For dark sections, add local overrides such as `.dark .math-block, .band .math-block { background: #fff; color: #111; }` and `.dark .math-block .katex, .band .math-block .katex { color: #111; }`.
- In Survey Mode, do not present taxonomy claims as experimentally proven unless the paper provides controlled evidence. Label `paper states`, `author synthesis`, and `inference` separately.
- In Survey Mode, do not merely list papers/projects. Build matrices and relation maps that show classification axes, evidence type, coverage density, and gaps.
- For every mode, include an early Verdict Board. It must answer the practical question the paper raises, name the strongest evidence, state the confidence level, and name the main caveat.
- Distinguish `coverage` from `confidence`: many papers/projects/tasks do not imply strong evidence unless selection, coding, evaluation, and artifact availability support the claim.

## Resources

- `scripts/collect_arxiv_assets.py`: collect arXiv HTML figure/table candidates into JSON.
- `scripts/validate_index.py`: static checks for a generated `index.html`.
- `references/analysis-framework.md`: paper reading and critique framework.
- `references/html-output-contract.md`: required HTML, KaTeX, figure/table, interaction, and browser QA rules.
- `references/reproducibility-checklist.md`: extraction checklist for reproducible experiment sections.
- `references/mode-method.md`: mode-specific requirements for method, theory, and system papers.
- `references/mode-benchmark.md`: mode-specific requirements for benchmark, dataset, and evaluation papers.
- `references/mode-survey.md`: mode-specific requirements for survey, review, taxonomy, landscape, and systematic mapping papers.
- `references/mode-position.md`: mode-specific requirements for position, perspective, and agenda papers.
- `references/visual-patterns.md`: reusable visual modules such as Verdict Board, Evidence Ladder, Coverage Matrix, Pipeline, and Gap Cards.
- `references/browser-qa.md`: browser verification checklist and computed-style inspection snippet.
- `assets/index-template.html`: single-file HTML scaffold with KaTeX wiring, copyable LaTeX, smooth anchors, and responsive sections.
