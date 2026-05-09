#!/usr/bin/env node
// Thin Node shim. Real logic lives in scripts/suite_validators/playwright.py — it imports
// MarketplaceModel so workflow Plugin Pin checks come from the canonical model rather than a
// hardcoded array.
import { spawnSync } from 'node:child_process';
import path from 'node:path';

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname);
const result = spawnSync(
  'python3',
  ['-m', 'suite_validators', 'playwright'],
  {
    cwd: repoRoot,
    env: { ...process.env, PYTHONPATH: `${repoRoot}/scripts${process.env.PYTHONPATH ? ':' + process.env.PYTHONPATH : ''}` },
    stdio: 'inherit',
  },
);
process.exit(result.status ?? 1);
