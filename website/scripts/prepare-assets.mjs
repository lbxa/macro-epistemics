import { readFileSync } from 'node:fs';
import { createHash } from 'node:crypto';

const workingPaper = new URL('../public/files/confidence-correction-and-consensus.pdf', import.meta.url);
const archivedPaper = new URL('../../report/data/archived-sector-paper.pdf', import.meta.url);
const research = JSON.parse(readFileSync(new URL('../src/data/research.json', import.meta.url), 'utf8'));

const workingPaperHash = '3c5b71257746152171ec1d50f2c43d30e314deb4e317b1c09d7173b2c1683938';
for (const [paper, expected, description] of [
  [workingPaper, workingPaperHash, 'working paper'],
  [archivedPaper, research.provenance.reportPdfSha256, 'admitted report archive'],
]) {
  const actual = createHash('sha256').update(readFileSync(paper)).digest('hex');
  if (actual !== expected) {
    throw new Error(`SHA-256 mismatch for the ${description}.`);
  }
}
