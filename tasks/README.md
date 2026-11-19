# Veracity task-source database

Prepared for Lucas Barbosa on November 14, 2026.

This first source bank contains 2,061 evaluation task records from 13 imported or indexed sources, a registry of 27 evaluation sources, all 22 occupational major groups published in the inspected Economic Index release, and 19,530 O*NET occupational task descriptions across 974 occupations.

The participant input bank contains 810 candidates with bundled text context and author-provided references retained separately. These are source-ready inputs, not an admitted Veracity scenario suite. No model calls, source-environment runs or Veracity campaigns were performed.

## Recommended first cases

Begin with financial report reasoning from FinQA and TAT-QA, contractual support from ContractNLI, and scientific evidence assessment from SciFact. Then add factual checks on tutoring feedback from MathDial. Wider professional tasks are indexed from GDPval. Engineering, CRM, EHR and workplace sources need their associated assets and environments.

The independent reference establishes factual or task-specific correctness. The jury establishes an institutional outcome. The protocol measures these separately and includes a matched comparison of reflection with a verdict alone versus the same verdict plus logs.

## Economic categories

The Economic Index release inspected was June 26, 2026, with April and May 2026 observations. The percentages below are published GLOBAL claude_ai major-occupation values for May 2026. They describe Claude platform usage rather than the economic size of an occupation or its GDP contribution. API metrics are retained separately in the database. The 22 published values sum to 98.74 percent and have not been renormalized.

The database also retains selected USA observations, detailed occupation/task percentages and upper-level activity/request metrics. See metadata.economic_metric_scope for the exact retained scope. Occupational task descriptions come from the older February 2025 published snapshot; they are not a newly collected November 2026 survey.

| SOC group | Occupational category | Claude usage pct | Indexed task records | Proposed phase |
|---|---|---|---|---|
| 15 | Computer and Mathematical | 23.80 | 94 | pilot |
| 27 | Arts, Design, Entertainment, Sports, and Media | 13.55 | 218 | pilot |
| 25 | Educational Instruction and Library | 12.79 | 135 | pilot |
| 41 | Sales and Related | 9.14 | 115 | pilot |
| 43 | Office and Administrative Support | 7.89 | 400 | pilot |
| 11 | Management | 5.90 | 64 | pilot |
| 13 | Business and Financial Operations | 5.77 | 483 | pilot |
| 19 | Life, Physical, and Social Science | 4.51 | 180 | pilot |
| 17 | Architecture and Engineering | 3.56 | 92 | extend |
| 29 | Healthcare Practitioners and Technical | 3.31 | 115 | extend |
| 21 | Community and Social Service | 2.57 | 5 | extend |
| 39 | Personal Care and Service | 1.23 | 10 | extend |
| 51 | Production | 1.04 | 5 | extend |
| 23 | Legal | 1.02 | 200 | pilot |
| 31 | Healthcare Support | 0.62 | 0 | extend |
| 49 | Installation, Maintenance, and Repair | 0.62 | 0 | document_tasks_only |
| 35 | Food Preparation and Serving Related | 0.48 | 0 | document_tasks_only |
| 53 | Transportation and Material Moving | 0.34 | 0 | document_tasks_only |
| 33 | Protective Service | 0.33 | 10 | extend |
| 37 | Building and Grounds Cleaning and Maintenance | 0.13 | 0 | document_tasks_only |
| 47 | Construction and Extraction | 0.10 | 0 | document_tasks_only |
| 45 | Farming, Fishing, and Forestry | 0.04 | 0 | document_tasks_only |

Category relevance mappings are researcher judgments. Counts overlap when a task maps to more than one category and should not be summed as independent observations. Seven categories have no indexed task instances in this version. Proposed documentary task families remain available in the categories table. Text judgments do not establish physical job competence.

## Evaluation sources

Records include original task text when reuse terms and required material permit, plus pointer-only records where full text or assets are not bundled. Source-specific data licenses and modification notes are retained in the benchmark registry and source_notices folder.

| Source | Indexed records | Prompts included | Candidate inputs | Original source |
|---|---|---|---|---|
| AVeriTeC | 163 | 163 | 0 | [Source](https://fever.ai/dataset/averitec.html) |
| BIRD and LiveSQLBench | 0 | 0 | 0 | [Source](https://bird-bench.github.io/) |
| CRMArena-Pro | 220 | 220 | 0 | [Source](https://github.com/SalesforceAIResearch/CRMArena) |
| CUAD | 0 | 0 | 0 | [Source](https://www.atticusprojectai.org/cuad/) |
| ContractNLI | 180 | 180 | 180 | [Source](https://stanfordnlp.github.io/contract-nli/) |
| EngDesign-Open | 67 | 67 | 0 | [Source](https://github.com/AGI4Engineering/EngDesign) |
| FinQA | 180 | 180 | 163 | [Source](https://finqasite.github.io/) |
| ForecastBench | 0 | 0 | 0 | [Source](https://forecastbench.org/) |
| GDPval gold public set | 220 | 0 | 0 | [Source](https://openai.com/index/gdpval/) |
| HealthBench | 0 | 0 | 0 | [Source](https://openai.com/index/healthbench/) |
| LAB-Bench | 0 | 0 | 0 | [Source](https://github.com/Future-House/LAB-Bench) |
| LegalBench | 0 | 0 | 0 | [Source](https://hazyresearch.stanford.edu/legalbench/tasks/) |
| LiveBench refresh design reference | 0 | 0 | 0 | [Source](https://livebench.ai/) |
| MathDial task source | 120 | 120 | 120 | [Source](https://github.com/eth-nlped/mathdial) |
| MedAgentBench | 100 | 100 | 0 | [Source](https://github.com/stanfordmlgroup/MedAgentBench) |
| MedCalc-Bench Verified | 0 | 0 | 0 | [Source](https://github.com/nikhilk7153/MedCalc-Bench-Verified) |
| OSWorld | 0 | 0 | 0 | [Source](https://os-world.github.io/) |
| SWE-bench Pro V2 | 0 | 0 | 0 | [Source](https://huggingface.co/datasets/ScaleAI/SWE-bench_Pro) |
| SWE-bench Verified legacy comparator | 0 | 0 | 0 | [Source](https://www.swebench.com/) |
| SciFact | 180 | 180 | 180 | [Source](https://github.com/allenai/scifact) |
| SpreadsheetBench current and Verified sources | 0 | 0 | 0 | [Source](https://spreadsheetbench.github.io/) |
| TAT-QA | 167 | 167 | 167 | [Source](https://nextplusplus.github.io/TAT-QA/) |
| TheAgentCompany | 174 | 174 | 0 | [Source](https://github.com/TheAgentCompany/TheAgentCompany) |
| TutorBench | 0 | 0 | 0 | [Source](https://labs.scale.com/leaderboard/tutorbench) |
| WorkArena and WorkArena++ | 0 | 0 | 0 | [Source](https://github.com/ServiceNow/WorkArena) |
| WritingBench | 90 | 0 | 0 | [Source](https://github.com/Tongyi-Zhiwen/WritingBench) |
| tau-bench current pinned repository | 200 | 150 | 0 | [Source](https://github.com/sierra-research/tau2-bench) |

The 220 GDPval public task IDs cover 44 occupations and nine industry sectors. Full GDPval prompts, rubrics and deliverables were not redistributed because no explicit data license was found in the inspected dataset card. Each record links to its source and needed reference files. WritingBench records similarly link to full prompts that can contain third-party publications. Neither pointer-only set is included in participant_inputs.jsonl.

## Opening and searching

`tasks/` is the `veracity-tasks` uv project in the Macro-Epistemics repository.
It uses Python 3.12+ and the standard library, with no third-party dependencies.
Its lockfile and environment are independent of `harness/`; the existing harness
continues to own experiment execution and Veracity integration.

Run these commands from the repository root. `--directory tasks` selects this
project and makes relative script and output paths resolve inside `tasks/`.

```bash
uv sync --directory tasks --locked
uv run --directory tasks --locked python task_db.py stats
uv run --directory tasks --locked python task_db.py categories
uv run --directory tasks --locked python task_db.py search invoice --limit 10
mkdir -p tasks/outputs
uv run --directory tasks --locked python task_db.py export-inputs --benchmark contractnli --limit 20 --output outputs/contract_inputs.jsonl
```

Use the task_id returned by search with the show command. The optional --with-reference flag exposes the evaluator-only reference to the researcher.

```bash
uv run --directory tasks --locked python task_db.py show TASK_ID
uv run --directory tasks --locked python task_db.py show TASK_ID --with-reference
```

From inside this folder or an extracted bundle, use `uv run --locked python
task_db.py stats`. Direct `python task_db.py ...` invocation also works with a
compatible interpreter. The database can be opened in a SQLite client without
installing anything. Inspection makes no model calls and needs no credentials.

## Main files

veracity_tasks.sqlite is the canonical queryable database. catalog.json contains category coverage, source registry, conditions and quality findings. task_index.jsonl contains task metadata and available prompts. participant_inputs.jsonl contains only opaque input IDs, tasks and source material. evaluator_only contains source answers, annotations and the mapping back to source IDs. Never mount the whole database or evaluator_only folder into participant sandboxes.

EXPERIMENT_PROTOCOL.md explains claim freezing, confidence targets, paired branches, source-group clustering and benchmark maintenance. example_queries.sql provides useful selections. Source identities, hashes, licenses, imported split names, sampling procedures and remaining prerequisites are retained with records.

`bundle_checksums.json` hashes the current delivered files, excluding itself.
`source_metadata/imported_bundle_checksums.json` retains the original import's
checksums; its script and documentation hashes predate the uv integration.
Dataset bytes and upstream source hashes are unchanged by that integration.

## Verification and limits

SQLite integrity and foreign-key checks passed. Task IDs are unique. Duplicate input texts are retained and reported because some refer to different hidden environment states; they are not automatically independent questions. Source-ready exports omit author answer fields, gold evidence indices and benchmark metadata.

Arithmetic checking was limited to supported FinQA program operations and answer-display consistency. Seventeen sampled records were withheld from the default input bank for unit, sign or answer-reference review. These flags are not confirmed annotation errors. Ten other cases were outside the arithmetic checker's scope and retain their author-supplied references. Detailed results are in reference_checks.json.

The source audit also records a contradictory column specification in one inspected GDPval audit rubric, a historical FinQA formatting leak, source-version changes and unavailable runtime assets. Reference existence never guarantees reference correctness. The benchmark registry distinguishes objective checks, support annotations, rubric judgments and delayed outcome resolution.

## Rebuilding the data

The included scripts record pinned revisions and exact source file hashes. Rebuilding downloads roughly 400 MB of public inputs and many small task files. It does not make model calls or execute downloaded benchmark programs. Internet access is required. The delivered database can be used without rebuilding. Run the following from inside `tasks/` (or an extracted bundle).

```bash
mkdir -p research_sources
cp source_metadata/*.json research_sources/
uv run --locked python download_sources.py
uv run --locked python download_benchmarks.py
uv run --locked python build_database.py
uv run --locked python package_database.py
```

The builder writes to `outputs/veracity_task_database/`; it does not replace
the database at this project's root. The packager copies the authored README,
SQL examples, protocol, source attribution and uv project files into that output,
refreshes its checksums, and creates `outputs/Veracity_Task_Database.zip`.
The README's numeric tables describe this imported version; review them against
the generated `summary.json` when admitting a different version. Download caches,
rebuilt outputs and `.venv/` are ignored by Git.

The included GDPval index is sufficient to rebuild its pointer records. It contains no full prompt, rubric or gold deliverable. Mutable source downloads, including the SciFact archive, must match source_manifest.json for a faithful rebuild. A newer upstream file is a new source version and requires review.

## Maintenance

Use a fixed anchor cohort and a separately reported rotating cohort of newly validated cases. Recompute every dependent reference when changing data. Hold out source documents, repositories and case families, not just individual question rows. Keep missing and uncertain cases distinct from wrong answers. Report task versions and changes in difficulty so score movement can be interpreted.

Public benchmarks can have been seen during training. Removing labels and rotating tasks reduces some exploits but does not make a benchmark unlearnable. The quality_findings table and experiment protocol describe candidate exploits and the controls needed to demonstrate and close them.

## Changelog

### 2026-11-15

- Record the [sector expansion proposal](../harness/research/sector-expansion/README.md):
  810 eligible text candidates span four occupational domains. Retain source
  groups and distinguish benchmark format from domain effects before comparing
  sectors; execution still belongs to the existing harness.

### 2026-11-14

- Integrate the imported task bank as an independent, dependency-free uv project;
  retain the existing harness as the sole experiment runner. Source-ready inputs
  remain candidates requiring adapters and scenario admission.
- Preserve the original bundle checksums as import provenance, and package
  directly authored documentation so archive creation cannot overwrite it.
