import { copyFileSync, existsSync, lstatSync, mkdirSync, readFileSync, readlinkSync, renameSync, symlinkSync, writeFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { dirname, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

const website = resolve(dirname(fileURLToPath(import.meta.url)), '..');
const repository = resolve(website, '..');
const exports = resolve(repository, 'video/exports');
const currentReport = resolve(website, 'public/files/confidence-correction-and-consensus.pdf');
if (createHash('sha256').update(readFileSync(currentReport)).digest('hex') !==
    '04fe75d345d73b686af306aee2e69554fcf535b2d84854b935635005232d93af') {
  throw new Error('The current paper differs from the approved website PDF.');
}
const research = JSON.parse(readFileSync(resolve(website, 'src/data/research.json'), 'utf8'));
const reportHash = research.provenance.reportPdfSha256;
if (typeof reportHash !== 'string' || !/^[a-f0-9]{64}$/.test(reportHash)) {
  throw new Error('The public research export must pin the admitted report PDF.');
}
const reportDestination = resolve(website, 'public/files/macro-epistemics-paper.pdf');
const existingReportMatches = existsSync(reportDestination)
  && createHash('sha256').update(readFileSync(reportDestination)).digest('hex') === reportHash;
if (!existingReportMatches) {
  const reportBytes = readFileSync(resolve(repository, 'report/epistemics/build/main.pdf'));
  if (createHash('sha256').update(reportBytes).digest('hex') !== reportHash) {
    throw new Error('The local report differs from the admitted archive. Restore the verified PDF or explicitly admit the newer report before preparing assets.');
  }
  mkdirSync(dirname(reportDestination), { recursive: true });
  writeFileSync(reportDestination, reportBytes);
}
console.log(`Retained admitted PDF: ${research.provenance.reportArtifact}`);
const copies = [
  [resolve(exports, 'macro-epistemics-draft-01.vtt'), resolve(website, 'public/media/macro-epistemics-draft-01.vtt')],
  [resolve(exports, 'macro-epistemics-draft-01-poster.png'), resolve(website, 'src/assets/images/macro-epistemics-poster.png')],
];

for (const [source, destination] of copies) {
  if (existsSync(source)) {
    mkdirSync(dirname(destination), { recursive: true });
    copyFileSync(source, destination);
  } else if (!existsSync(destination)) {
    throw new Error(`Required research artifact is missing: ${relative(website, destination)}`);
  }
  console.log(`Available ${relative(website, destination)}`);
}

// Keep the actual production movie in the user-designated ignored video folder.
// Astro/Vite copies the linked file into ignored dist/ for a static deployment.
const movie = resolve(exports, 'macro-epistemics-draft-01.mp4');
const link = resolve(website, 'public/media/macro-epistemics-draft-01.mp4');
const movieHash = '9ed3928994e23df2ecc14bf032cbf88654e44733c9edf10d4fbc400f850fa68d';
const movieUrl = 'https://github.com/lbxa/apart-epistemics-sprint/releases/download/website-assets-v1/macro-epistemics-draft-01.mp4';
let movieBytes;
if (existsSync(movie)) {
  movieBytes = readFileSync(movie);
} else {
  const response = await fetch(movieUrl, { signal: AbortSignal.timeout(60_000) });
  if (!response.ok) throw new Error(`Published film download failed: HTTP ${response.status}`);
  movieBytes = new Uint8Array(await response.arrayBuffer());
}
if (createHash('sha256').update(movieBytes).digest('hex') !== movieHash) {
  throw new Error('The film differs from the pinned website release asset.');
}
if (!existsSync(movie)) {
  mkdirSync(exports, { recursive: true });
  writeFileSync(`${movie}.download`, movieBytes);
  renameSync(`${movie}.download`, movie);
  console.log('Restored the pinned film into ignored video/exports/.');
}
if (existsSync(link)) {
  if (!lstatSync(link).isSymbolicLink() || resolve(dirname(link), readlinkSync(link)) !== movie) {
    throw new Error('Refusing to replace an unrelated movie in public/media.');
  }
} else {
  symlinkSync(relative(dirname(link), movie), link);
}
console.log('Linked local video export; no production asset moved out of video/.');
