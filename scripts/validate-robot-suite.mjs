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
  const workflowMarketplace = JSON.parse(read('.athena-workflow/marketplace.json'));
  const workflowJson = JSON.parse(read('workflows/robot-automation/workflow.json'));
  const workflowMd = read('workflows/robot-automation/workflow.md');
  const readme = read('README.md');
  const addRobotTests = read('plugins/robot-automation/skills/add-robot-tests/SKILL.md');
  const writeRobotCode = read('plugins/robot-automation/skills/write-robot-code/SKILL.md');
  const analyzeRobotCodebase = read('plugins/robot-automation/skills/analyze-test-codebase/SKILL.md');

  for (const relPath of [
    'plugins/robot-automation/skills/plan-test-coverage',
    'plugins/robot-automation/skills/generate-test-cases',
    'plugins/robot-automation/skills/review-test-cases',
  ]) {
    assert(
      !exists(relPath),
      `${relPath} must be removed so shared planning/spec skills live only in test-analysis`,
    );
  }

  const workflowEntry = workflowMarketplace.workflows.find(
    (workflow) => workflow.name === 'robot-automation',
  );
  assert(
    Boolean(workflowEntry),
    '.athena-workflow/marketplace.json must retain the robot-automation workflow entry',
  );

  const expectedRefs = [
    'agent-web-interface@lespaceman/athena-workflow-marketplace',
    'app-exploration@lespaceman/athena-workflow-marketplace',
    'test-analysis@lespaceman/athena-workflow-marketplace',
    'robot-automation@lespaceman/athena-workflow-marketplace',
  ];
  const actualRefs = workflowJson.plugins.map((plugin) => plugin.ref);
  assert(
    JSON.stringify(actualRefs) === JSON.stringify(expectedRefs),
    'workflows/robot-automation/workflow.json must depend on the canonical layered Robot suite',
  );

  assert(
    readme.includes('node scripts/validate-robot-suite.mjs'),
    'README must document the Robot suite validator',
  );
  assert(
    readme.includes('claude plugin install app-exploration@athena-workflow-marketplace'),
    'README must document app-exploration as a shared prerequisite for the Robot stack',
  );
  assert(
    readme.includes('claude plugin install test-analysis@athena-workflow-marketplace'),
    'README must document test-analysis as a shared prerequisite for the Robot stack',
  );
  assert(
    readme.includes('claude plugin install robot-automation@athena-workflow-marketplace'),
    'README must document robot-automation as the Robot execution layer install step',
  );
  assert(
    readme.includes('does not install the shared') &&
      readme.includes('`app-exploration` and `test-analysis` layers'),
    'README must explain that installing an execution plugin alone does not install the shared layers',
  );
  assert(
    readme.includes('The full orchestration surface remains the workflow pair `playwright-automation` and `robot-automation`'),
    'README must preserve the workflow-first orchestration note',
  );
  assert(
    readme.includes('`robot-automation` | Robot execution layer: analyze codebases, write `.robot` suites, review them, and fix flake after the shared layers are ready'),
    'README must describe robot-automation as the Robot execution layer',
  );

  for (const [label, content] of [
    ['workflows/robot-automation/workflow.md', workflowMd],
    ['add-robot-tests', addRobotTests],
    ['write-robot-code', writeRobotCode],
    ['analyze-test-codebase', analyzeRobotCodebase],
  ]) {
    assert(
      !content.includes('agent-web-interface-guide'),
      `${label} must not present agent-web-interface-guide as the canonical Robot layer entry point`,
    );
  }

  for (const [label, content] of [
    ['workflows/robot-automation/workflow.md', workflowMd],
    ['add-robot-tests', addRobotTests],
  ]) {
    assert(
      content.includes('capture-feature-evidence'),
      `${label} must reference capture-feature-evidence as the shared exploration layer`,
    );
    assert(
      content.includes('plan-test-coverage'),
      `${label} must reference plan-test-coverage as the shared planning layer`,
    );
    assert(
      content.includes('generate-test-cases'),
      `${label} must reference generate-test-cases as the shared spec layer`,
    );
    assert(
      content.includes('review-test-cases'),
      `${label} must reference review-test-cases as the shared spec review layer`,
    );
  }

  for (const [label, content] of [
    ['add-robot-tests', addRobotTests],
    ['write-robot-code', writeRobotCode],
  ]) {
    assert(
      content.includes('e2e-plan/exploration-report.md'),
      `${label} must reference e2e-plan/exploration-report.md`,
    );
  }
  assert(
    addRobotTests.includes('e2e-plan/coverage-plan.md'),
    'add-robot-tests must reference e2e-plan/coverage-plan.md',
  );
  assert(
    addRobotTests.includes('test-cases/<feature>.md'),
    'add-robot-tests must reference test-cases/<feature>.md',
  );

  if (failures.length > 0) {
    console.error('robot suite validation failed:\n');
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log('robot suite validation passed');
}

main();
