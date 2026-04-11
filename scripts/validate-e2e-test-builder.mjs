#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname);

const requiredSkills = [
  'add-e2e-tests',
  'analyze-test-codebase',
  'plan-test-coverage',
  'agent-web-interface-guide',
  'generate-test-cases',
  'review-test-cases',
  'write-test-code',
  'review-test-code',
  'fix-flaky-tests',
];

const skillFiles = [
  'plugins/e2e-test-builder/skills/plan-test-coverage/SKILL.md',
  'plugins/e2e-test-builder/skills/generate-test-cases/SKILL.md',
  'plugins/e2e-test-builder/skills/review-test-cases/SKILL.md',
  'plugins/e2e-test-builder/skills/write-test-code/SKILL.md',
  'plugins/e2e-test-builder/skills/review-test-code/SKILL.md',
];

const failures = [];

function read(relPath) {
  return fs.readFileSync(path.join(repoRoot, relPath), 'utf8');
}

function assert(condition, message) {
  if (!condition) failures.push(message);
}

function main() {
  const readme = read('README.md');
  const workflowJson = JSON.parse(
    read('workflows/e2e-test-builder/workflow.json'),
  );
  const fixFlaky = read(
    'plugins/e2e-test-builder/skills/fix-flaky-tests/SKILL.md',
  );
  const fixPatterns = read(
    'plugins/e2e-test-builder/skills/fix-flaky-tests/references/fix-patterns.md',
  );
  const workflowReadmeSection = readme.slice(
    readme.indexOf('### e2e-test-builder'),
    readme.indexOf('### site-knowledge'),
  );

  for (const skill of requiredSkills) {
    assert(
      readme.includes(`\`${skill}\``),
      `README is missing e2e-test-builder skill entry: ${skill}`,
    );
  }

  assert(
    readme.includes('review-test-cases') &&
      readme.includes('review-test-code') &&
      readme.includes('fix-flaky-tests'),
    'README must document all quality-gate and flaky-test skills',
  );

  assert(
    workflowReadmeSection.includes('Athena CLI owns the stateless session protocol'),
    'README should clarify Athena CLI runtime ownership for the workflow loop',
  );

  assert(
    workflowReadmeSection.includes('Browser exploration is required'),
    'README should document the browser-exploration dependency in the workflow rules',
  );

  for (const relPath of skillFiles) {
    const content = read(relPath);
    assert(
      content.includes('TC-<FEATURE>-<NNN>'),
      `${relPath} must use the canonical TC-ID format TC-<FEATURE>-<NNN>`,
    );
    assert(
      !content.includes('TC-FEATURE-A01') && !content.includes('TC-FEATURE-V01'),
      `${relPath} must not use category-specific TC-ID variants`,
    );
  }

  assert(
    !fixFlaky.includes('networkidle or `load` waitUntil would help') &&
      !fixFlaky.includes('`networkidle` or `load` waitUntil would help'),
    'fix-flaky-tests must not recommend generic networkidle/load waitUntil fixes',
  );

  assert(
    !fixPatterns.includes("// GOOD: wait for navigation to complete\nawait page.goto('/page', { waitUntil: 'networkidle' });"),
    'fix-patterns reference must not present networkidle as a generic recommended fix',
  );

  assert(
    typeof workflowJson.description === 'string' &&
      workflowJson.description.includes('Athena CLI runs this authored Playwright E2E workflow') &&
      workflowJson.description.includes('generate and review specs') &&
      workflowJson.description.includes('write and review tests') &&
      workflowJson.description.includes('execute and stabilize'),
    'workflow.json description should describe Athena CLI ownership plus review/execution stages',
  );

  if (failures.length > 0) {
    console.error('e2e-test-builder validation failed:\n');
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log('e2e-test-builder validation passed');
}

main();
