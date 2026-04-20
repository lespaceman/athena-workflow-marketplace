#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname);
const failures = [];

function read(relPath) {
  return fs.readFileSync(path.join(repoRoot, relPath), 'utf8');
}

function exists(relPath) {
  return fs.existsSync(path.join(repoRoot, relPath));
}

function assert(condition, message) {
  if (!condition) failures.push(message);
}

function main() {
  const agentsMarketplace = JSON.parse(read('.agents/plugins/marketplace.json'));
  const claudeMarketplace = JSON.parse(read('.claude-plugin/marketplace.json'));
  const workflowMarketplace = JSON.parse(read('.athena-workflow/marketplace.json'));
  const workflowJson = JSON.parse(read('workflows/e2e-test-builder/workflow.json'));
  const readme = read('README.md');
  const workflowMd = read('workflows/e2e-test-builder/workflow.md');
  const analyzeTestCodebase = read('plugins/playwright-automation/skills/analyze-test-codebase/SKILL.md');
  const writeTestCode = read('plugins/playwright-automation/skills/write-test-code/SKILL.md');
  const addPlaywrightTests = read('plugins/playwright-automation/skills/add-playwright-tests/SKILL.md');
  const coveragePlan = read('plugins/test-analysis/skills/plan-test-coverage/SKILL.md');
  const generateCases = read('plugins/test-analysis/skills/generate-test-cases/SKILL.md');
  const reviewCases = read('plugins/test-analysis/skills/review-test-cases/SKILL.md');

  assert(
    !exists('plugins/e2e-test-builder'),
    'plugins/e2e-test-builder must be removed',
  );

  const agentPlugins = new Set(agentsMarketplace.plugins.map((plugin) => plugin.name));
  const claudePlugins = new Set(claudeMarketplace.plugins.map((plugin) => plugin.name));
  assert(
    !agentPlugins.has('e2e-test-builder'),
    '.agents/plugins/marketplace.json must not register e2e-test-builder',
  );
  assert(
    !claudePlugins.has('e2e-test-builder'),
    '.claude-plugin/marketplace.json must not register e2e-test-builder',
  );

  const workflowEntry = workflowMarketplace.workflows.find(
    (workflow) => workflow.name === 'e2e-test-builder',
  );
  assert(
    Boolean(workflowEntry),
    '.athena-workflow/marketplace.json must retain the e2e-test-builder workflow entry',
  );

  const expectedRefs = [
    'agent-web-interface@lespaceman/athena-workflow-marketplace',
    'app-exploration@lespaceman/athena-workflow-marketplace',
    'test-analysis@lespaceman/athena-workflow-marketplace',
    'playwright-automation@lespaceman/athena-workflow-marketplace',
  ];
  const actualRefs = workflowJson.plugins.map((plugin) => plugin.ref);
  assert(
    JSON.stringify(actualRefs) === JSON.stringify(expectedRefs),
    'workflows/e2e-test-builder/workflow.json must depend on the canonical layered Playwright suite',
  );

  assert(
    readme.includes('claude plugin install app-exploration@athena-workflow-marketplace'),
    'README must document app-exploration as a shared prerequisite for the Playwright stack',
  );
  assert(
    readme.includes('claude plugin install test-analysis@athena-workflow-marketplace'),
    'README must document test-analysis as a shared prerequisite for the Playwright stack',
  );
  assert(
    readme.includes('claude plugin install playwright-automation@athena-workflow-marketplace'),
    'README must document playwright-automation as the Playwright execution layer install step',
  );
  assert(
    readme.includes('does not install the shared') &&
      readme.includes('`app-exploration` and `test-analysis` layers'),
    'README must explain that installing an execution plugin alone does not install the shared layers',
  );
  assert(
    readme.includes('The full orchestration surface remains the workflow pair `e2e-test-builder` and `robot-automation`'),
    'README must preserve the workflow-first orchestration note',
  );
  assert(
    readme.includes('e2e-test-builder` survives only as a workflow name'),
    'README must clarify that e2e-test-builder survives only as a workflow name',
  );
  assert(
    !readme.includes('e2e-test-builder@athena-workflow-marketplace'),
    'README must not present e2e-test-builder as a manageable plugin surface',
  );
  assert(
    !readme.includes('plugins/e2e-test-builder/'),
    'README must not list plugins/e2e-test-builder in the active repository structure',
  );

  for (const [content, label] of [
    [workflowMd, 'workflow.md'],
    [analyzeTestCodebase, 'analyze-test-codebase'],
    [writeTestCode, 'write-test-code'],
    [addPlaywrightTests, 'add-playwright-tests'],
  ]) {
    assert(
      !content.includes('add-e2e-tests'),
      `${label} must not reference add-e2e-tests`,
    );
  }

  for (const [content, label] of [
    [analyzeTestCodebase, 'analyze-test-codebase'],
    [writeTestCode, 'write-test-code'],
  ]) {
    assert(
      !content.includes('agent-web-interface-guide'),
      `${label} must not present agent-web-interface-guide as the canonical Playwright exploration path`,
    );
  }
  assert(
    analyzeTestCodebase.includes('capture-feature-evidence'),
    'analyze-test-codebase must route live-site exploration through capture-feature-evidence',
  );
  assert(
    writeTestCode.includes('capture-feature-evidence'),
    'write-test-code must route missing product evidence through capture-feature-evidence',
  );

  for (const [label, content] of [
    ['plan-test-coverage', coveragePlan],
    ['generate-test-cases', generateCases],
    ['review-test-cases', reviewCases],
  ]) {
    assert(
      content.includes('e2e-plan/exploration-report.md'),
      `${label} must reference e2e-plan/exploration-report.md`,
    );
  }
  assert(
    coveragePlan.includes('e2e-plan/coverage-plan.md'),
    'plan-test-coverage must produce e2e-plan/coverage-plan.md',
  );
  assert(
    generateCases.includes('test-cases/<feature-name>.md') ||
      generateCases.includes('test-cases/<feature>.md'),
    'generate-test-cases must target test-cases/<feature>.md-style output',
  );

  if (failures.length > 0) {
    console.error('playwright suite validation failed:\n');
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log('playwright suite validation passed');
}

main();
