import { execFileSync } from 'node:child_process';
import { copyFileSync, mkdirSync, readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';
import { fileURLToPath } from 'node:url';

const workingPaper = new URL('../public/files/confidence-correction-and-consensus.pdf', import.meta.url);
const archivedPaper = new URL('../../report/data/archived-sector-paper.pdf', import.meta.url);
const research = JSON.parse(readFileSync(new URL('../src/data/research.json', import.meta.url), 'utf8'));

const archivedHash = createHash('sha256').update(readFileSync(archivedPaper)).digest('hex');
if (archivedHash !== research.provenance.reportPdfSha256) {
  throw new Error('SHA-256 mismatch for the admitted report archive.');
}

const buildScript = fileURLToPath(new URL('./build-paper.sh', import.meta.url));
execFileSync('bash', [buildScript], { stdio: 'inherit' });

const compiledPaper = new URL('../../report/epistemics/build/main.pdf', import.meta.url);
mkdirSync(new URL('.', workingPaper), { recursive: true });
copyFileSync(compiledPaper, workingPaper);
console.log('Prepared /files/confidence-correction-and-consensus.pdf from LaTeX sources.');
