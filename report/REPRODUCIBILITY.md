# Reproducing the dispute study

The paper separates reference agreement, stated confidence, answer revision
and jury acceptance. Its existing results can be reanalysed without model APIs,
W&B credentials, a task database, Docker or a running Veracity service. New
model generations and protocol settlements require the experiment harness;
the commands below only read frozen evidence and write local analysis output.

The current title, *Confidence, Correction, and Consensus: Evaluating Language
Models Under Dispute*, belongs to a later local working revision. The immutable
report artifact `sector-report-da7e42f28ba54247:v2` contains the earlier title,
*Macro-Epistemics: Confidence Under Dispute*. It does not archive these new
prose edits or certify a journal submission. Historical artifacts are retained.

## Build the paper from retained assets

From the repository root:

```sh
SOURCE_DATE_EPOCH=1794821400 FORCE_SOURCE_DATE=1 make -C report
```

The output is `report/epistemics/build/main.pdf`. This target compiles the
checked-in figures and tables; it does not recompute them or call a model.
The inspected toolchain is pdfTeX 1.40.27, TeX Live 2025, with latexmk 4.86a.
The source uses Computer Modern. A different TeX/font installation can change
pagination or PDF bytes without changing numerical results. The root
`make -C report baseline` and `agentic` targets select historical manuscripts,
which are outside this study.

## Locked analysis environment

The plotting environment is separate from `harness/uv.lock`. Its direct
requirements are in `report/requirements.txt`; all resolved Python versions
are pinned in `report/requirements.lock`. The verified environment uses
CPython 3.12.11, NumPy 2.5.4, SciPy 1.18.1 and Matplotlib 3.11.2.

```sh
UV_CACHE_DIR="$PWD/.tools/uv-cache" uv venv --python 3.12.11 .harness/report-venv
UV_CACHE_DIR="$PWD/.tools/uv-cache" uv pip sync --python .harness/report-venv/bin/python report/requirements.lock
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" .harness/report-venv/bin/python -m unittest discover -s report/analysis -p 'test_*.py'
```

Do not recreate an already populated environment unless intending to replace
it. Dependency installation needs a package cache or network access; the
subsequent analysis is offline. The November 16 reproduction passed all 53
report tests. These test statistical grouping, missingness, grading,
source-located excerpts and diagnostics; they do not independently adjudicate
the source references.

## Inputs and outputs

| Frozen input | Purpose and generated output | Parent evidence |
| --- | --- | --- |
| `report/data/sector-study.json` | Complete primary assignments and jury replay; primary tables, figures, CSVs and `sector-statistics.json` through `sector_results.py` | Main study v128 |
| `report/data/sector-initial.json` | Earlier initial-phase export; retained for provenance, superseded for complete-matrix analysis by `sector-study.json` | Main study v8 |
| `harness/research/sector-expansion/source-audit.json` | Eight-case post hoc unit, rounding and reference sensitivity; read by the primary analysis | Validity-audit v0 and main snapshot |
| `report/data/sector-excerpts.json` | Four post hoc selected main-text panels, with exact span locators and hashes, through `sector_excerpts.py` | Main study v35 |
| `report/data/arithmetic-diagnostic.json` | Selected arithmetic case and separate standalone follow-up; arithmetic tables and context figure through `arithmetic_probe.py` | Arithmetic diagnostic v0 |
| `report/data/sector-diagnostic-inputs.json` and `sector-call-metadata.jsonl` | Frozen source inventory, six additional visible traces and 47,133 projected call receipts; intermediate appendix tables, six figures and diagnostic CSVs | Main study v128, pinned inventory and arithmetic follow-up |
| `report/data/epistemics-pilot.json` | Earlier ContractNLI pilot appendix; pilot figures, tables and `statistics.json` through `epistemics_pilot.py` | Contract micro v734 |

The diagnostic renderer also reads the retained
`report/epistemics/sector-statistics.json` and verifies both parent hashes.
Keep that file frozen when reproducing the appendix. Recomputed primary
statistics record the current analysis source hash, so replacing the frozen
parent with a new analysis file intentionally fails the diagnostic admission
check. Re-extraction is a separate operation, not a workaround for that check.

## Recompute in scratch

These commands leave admitted inputs and manuscript assets unchanged. Run
each Python command in a separate process, as shown, to isolate plotting
configuration. `SOURCE_DATE_EPOCH` fixes supported PDF creation metadata.

```sh
export REPRO_DIR="$(mktemp -d /tmp/epistemics-reproduction.XXXXXX)"
export SOURCE_DATE_EPOCH=1794821400 FORCE_SOURCE_DATE=1
export MPLCONFIGDIR="$PWD/.harness/report-matplotlib"
export PYTHONPATH="$PWD/report/analysis"

.harness/report-venv/bin/python report/analysis/sector_results.py --snapshot report/data/sector-study.json --output "$REPRO_DIR/main"
.harness/report-venv/bin/python report/analysis/sector_diagnostics.py --output "$REPRO_DIR/diagnostics"

cp report/data/arithmetic-diagnostic.json "$REPRO_DIR/arithmetic-diagnostic.json"
.harness/report-venv/bin/python report/analysis/arithmetic_probe.py --snapshot "$REPRO_DIR/arithmetic-diagnostic.json" --output "$REPRO_DIR/supplement"

.harness/report-venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
from sector_excerpts import render

render(json.loads(Path('report/data/sector-excerpts.json').read_text()),
       Path(os.environ['REPRO_DIR']) / 'supplement/tables')
PY

.harness/report-venv/bin/python - <<'PY'
import os
from pathlib import Path
from epistemics_pilot import load_snapshot, render

data, cells = load_snapshot(Path('report/data/epistemics-pilot.json'))
render(data, cells, Path(os.environ['REPRO_DIR']) / 'supplement')
PY
```

`arithmetic_probe.py` serializes its snapshot even in rendering mode, which
is why the command uses a scratch copy. The excerpt and pilot CLIs default
to manuscript output paths; the short calls above use their render functions
with explicit scratch destinations instead. No extraction flags are used.

The [offline reproduction record](../harness/research/sector-expansion/peer-review/reproduction.json)
records input/source/lock hashes, tests and per-file comparisons against the
curated v2 archive. Primary statistics reproduce numerically; their analysis
source hash changes after the chart-layout edit. The compact main-text
reference-loss chart deliberately differs in geometry from v2. Historical
pilot and arithmetic PDF creation timestamps were not normalized, so exact PNGs and
statistics provide the corresponding reproduction checks. These differences
are not new observations.

## Recomputing the separately collected extensions

Once admitted, `report/data/peer-review-results.json` retains the new
extensions separately from the original study. Its `revision_rows` preserve
the paired legacy/revised-objection observations; `judge_rows` preserve the
judge-context assignments and outcomes. Recompute their summaries and new
assets from this portable projection without raw exports or model access:

```sh
export PEER_REPRO_DIR="$(mktemp -d /tmp/epistemics-peer-reproduction.XXXXXX)"
MPLCONFIGDIR="$PWD/.harness/report-matplotlib" PYTHONPATH="$PWD/report/analysis" .harness/report-venv/bin/python - <<'PY'
import json
import os
from pathlib import Path
from peer_review_results import analyze_judges, analyze_revision, render

snapshot = json.loads(Path('report/data/peer-review-results.json').read_text())
revision = analyze_revision(snapshot['revision_rows'])
judges = analyze_judges(snapshot['judge_rows'])
assert revision == snapshot['revision']
assert judges == snapshot['judges']
recomputed = {**snapshot, 'revision': revision, 'judges': judges}
output = Path(os.environ['PEER_REPRO_DIR'])
(output / 'peer-review-results.json').write_text(json.dumps(recomputed, indent=2) + '\n')
render(recomputed, output)
PY
```

Initial admission uses `peer_review_results.py --revision <export>
--judge <export> --admission <verified-admission.json>
--revision-register <evidence-register.json> --output <snapshot>` and validates
completed export manifests, executed evidence and parent identities before
creating the portable projection. That extraction step requires the pinned
raw artifacts. The summary recomputation above does not. Keep any new artifact
versions and hashes in the extension handoff; the
presence of a protocol or command alone is not evidence that collection or
admission has finished.

## Evidence versions and access

All artifact names below have prefix
`lbxa-corp/apart-epistemics-sprint/`. Digests are W&B artifact digests, not file
SHA256 values. Individual file hashes are in the portable inputs and admission
manifests.

| Artifact | Digest | Role |
| --- | --- | --- |
| `sector-study-da7e42f28ba54247:v128` | `7d7230ca4d18fc07c1bb8e0009cdbc1d` | Complete primary matrix and cross-family replay |
| `arithmetic-diagnostic-4ad9a8544dff473f:v0` | `17469e0e688c710966d533d7e2e4bd79` | Separate one-case arithmetic diagnostic |
| `sector-executed-evidence-da7e42f28ba54247:v0` | `bd0ff1ba88bcafab1b9351c6d5166daf` | Retained engine-execution evidence |
| `sector-validity-audit-da7e42f28ba54247:v0` | `698f703d0ff227544c8bb9f7d4e833ff` | Original-source, grading and leakage audit |
| `contract-micro-g9t35ump:v734` | `fc3d2a8f00f10f0ffb65e3fcc795a92b` | Earlier pilot, kept separate |
| `sector-report-da7e42f28ba54247:v2` | `5a6c61802b1b27fbbd717e7de8802630` | Reviewed historical manuscript and 176-file curated bundle |

Run evidence is linked from the [campaign handoff](../harness/research/sector-expansion/HANDOFF.md).
The [v2 admission register](../harness/research/sector-expansion/report-publication-editorial.json)
records its verified PDF and manifest. Remote W&B records can require project
access; their existence does not establish public availability. No public
archive, anonymous reviewer package or journal submission is claimed here.
The checked-in portable inputs support the offline commands without that
access. Reconstructing snapshots from raw calls additionally requires the
exact pinned artifacts and, for the inventory, the source task database.

The report bundle may additionally embed
`report/data/peer-review-executed-evidence.tar.gz`, an already validated
projection of the new numerical rerun's episode views and transaction receipts.
Its exact SHA256 must match the execution-evidence entry in the verified
admission register. Packaging copies that one named archive without extracting
it or constructing data from recovery databases. Inclusion depends on the
final artifact size and admission; it must not be inferred from this optional
path alone. Historical parent execution evidence remains available through
its separately permissioned artifact rather than being duplicated here.

New defence generations, repaired-objection runs or expanded judge ablations
require Cloudflare credentials, cloud compute, the harness environment and
separately recorded campaign configuration and spend. They cannot be obtained
by rerendering these snapshots. Independent human adjudication is also a
separate evidence-collection step; it cannot be inferred from passing tests.

## Data terms and release boundary

The repository's [source notices](../tasks/source_notices/ATTRIBUTION.md) and
[catalog](../tasks/catalog.json) retain source-specific terms: FinQA and
TAT-QA data are recorded as CC-BY-4.0, ContractNLI as CC-BY-4.0, and SciFact
claims/annotations as CC-BY-4.0 with ODC-By-1.0 abstracts. MathDial has a
recorded discrepancy between repository CC-BY-SA-4.0 and a Hugging Face
CC-BY-4.0 tag; the catalog retains the more restrictive share-alike notice.
These are retained provenance notices, not a new legal clearance. Check the
pinned upstream release and embedded source-document terms before public
redistribution. Dataset licenses do not automatically cover every source
document or model-service response.

Reviewer packaging should include only explicitly selected source, portable
inputs, generated assets, notices and manifests. Credentials, `.env`, hidden
reasoning, raw unfiltered call logs, recovery databases and spending ledgers
remain outside a report bundle. Visible quoted outputs and projected usage
receipts are distinct from private SDK reasoning. The presence of an item in
a local working tree is not release authorization.

## Preparing a local report archive

`report/analysis/archive_peer_review_report.py` prepares and verifies a curated
report bundle. It performs no upload, submission or public release. Supply a
JSON metadata file with `parents` (fully qualified, versioned artifact names
mapped to their recorded digests) and `main_pages` from the final rendered
review. Total pages are read from the PDF with `pdfinfo`; no page count is
hardcoded.

The five parent pairs must exactly match the frozen v128 study, archived
report v2, new numerical collection, numerical execution evidence and new
judge collection. The helper reads `peer-review/admission.json`, requires
its verified status, and checks its byte hash and artifact mapping against
the portable result's provenance. Supplied metadata cannot substitute a
different artifact or digest. The result snapshot's SHA256 is recorded when
the report bundle is built; it is not written into the input admission
register, which avoids a circular hash dependency.

```sh
.harness/report-venv/bin/python report/analysis/archive_peer_review_report.py --destination .harness/peer-review-report-admission --metadata .harness/peer-review-report-metadata.json
.harness/report-venv/bin/python report/analysis/archive_peer_review_report.py --destination .harness/peer-review-report-admission --verify
```

Preparation refuses an existing destination and records each file's SHA256
and byte count in `manifest.json`, with a separate `manifest.sha256`. For
subsequent remote admission, retain that manifest hash outside the bundle and
pass it through `--expected-manifest-sha256` during verification. Verification
checks the exact file set and rejects symlinks or altered files.

The inclusion policy covers active report sources/assets, portable inputs,
analysis code, source notices and peer-review protocol records. Only the exact
stage-1 `sources.json` and blank `source-reviews.csv` are eligible; unexpected
files in that directory abort preparation. Operator
keys and stage-2 model responses remain outside this bundle. This report
archive contains task references and is therefore a research reproduction
bundle, not a blinded adjudication distribution. The stage-1 packet must be
distributed separately according to `ADJUDICATION.md`.
