#!/usr/bin/env node
import fs from 'node:fs';
import path from 'node:path';

const repoRoot = path.resolve(new URL('..', import.meta.url).pathname);
const failures = [];

function read(relPath) {
  return fs.readFileSync(path.join(repoRoot, relPath), 'utf8');
}

function readJson(relPath) {
  return JSON.parse(read(relPath));
}

function assert(condition, message) {
  if (!condition) failures.push(message);
}

function assertIncludes(haystack, needle, message) {
  assert(haystack.includes(needle), message);
}

function assertNotIncludes(haystack, needle, message) {
  assert(!haystack.includes(needle), message);
}

function main() {
  const agentsMarketplace = readJson('.agents/plugins/marketplace.json');
  const claudeMarketplace = readJson('.claude-plugin/marketplace.json');
  const workflowMarketplace = readJson('.athena-workflow/marketplace.json');
  const readme = read('README.md');
  const planDoc = read('docs/architecture/plugin-suite-plan.md');
  const immediateDoc = read('docs/architecture/plugin-suite-immediate-split.md');
  const futureDoc = read('docs/architecture/plugin-suite-future-suite.md');

  const expectedPluginNames = [
    'exploratory-testing',
    'smoke-testing',
    'regression-testing',
  ];
  const expectedWorkflowNames = [
    'exploratory-testing',
    'smoke-testing',
    'regression-testing',
  ];

  const agentPlugins = new Set(agentsMarketplace.plugins.map((plugin) => plugin.name));
  const claudePlugins = new Set(claudeMarketplace.plugins.map((plugin) => plugin.name));
  const workflowNames = new Set(workflowMarketplace.workflows.map((workflow) => workflow.name));

  for (const pluginName of expectedPluginNames) {
    assert(agentPlugins.has(pluginName), `.agents/plugins/marketplace.json must register ${pluginName}`);
    assert(claudePlugins.has(pluginName), `.claude-plugin/marketplace.json must register ${pluginName}`);
  }

  for (const workflowName of expectedWorkflowNames) {
    assert(workflowNames.has(workflowName), `.athena-workflow/marketplace.json must register ${workflowName}`);
  }

  const exploratoryWorkflow = readJson('workflows/exploratory-testing/workflow.json');
  const smokeWorkflow = readJson('workflows/smoke-testing/workflow.json');
  const regressionWorkflow = readJson('workflows/regression-testing/workflow.json');
  const exploratoryWorkflowMd = read('workflows/exploratory-testing/workflow.md');
  const smokeWorkflowMd = read('workflows/smoke-testing/workflow.md');
  const regressionWorkflowMd = read('workflows/regression-testing/workflow.md');
  const exploratorySkill = read('plugins/exploratory-testing/skills/exploratory-test-writer/SKILL.md');
  const smokeSkill = read('plugins/smoke-testing/skills/define-smoke-scope/SKILL.md');
  const regressionSkill = read('plugins/regression-testing/skills/define-regression-scope/SKILL.md');
  const exploratoryClaudePlugin = readJson('plugins/exploratory-testing/.claude-plugin/plugin.json');
  const exploratoryCodexPlugin = readJson('plugins/exploratory-testing/.codex-plugin/plugin.json');
  const smokeClaudePlugin = readJson('plugins/smoke-testing/.claude-plugin/plugin.json');
  const smokeCodexPlugin = readJson('plugins/smoke-testing/.codex-plugin/plugin.json');
  const regressionClaudePlugin = readJson('plugins/regression-testing/.claude-plugin/plugin.json');
  const regressionCodexPlugin = readJson('plugins/regression-testing/.codex-plugin/plugin.json');
  const exploratoryOpenAi = read('plugins/exploratory-testing/skills/exploratory-test-writer/agents/openai.yaml');
  const exploratoryClaudeAgent = read('plugins/exploratory-testing/skills/exploratory-test-writer/agents/claude.yaml');
  const smokeOpenAi = read('plugins/smoke-testing/skills/define-smoke-scope/agents/openai.yaml');
  const smokeClaudeAgent = read('plugins/smoke-testing/skills/define-smoke-scope/agents/claude.yaml');
  const regressionOpenAi = read('plugins/regression-testing/skills/define-regression-scope/agents/openai.yaml');
  const regressionClaudeAgent = read('plugins/regression-testing/skills/define-regression-scope/agents/claude.yaml');

  const expectedExploratoryRefs = [
    'agent-web-interface@lespaceman/athena-workflow-marketplace',
    'app-exploration@lespaceman/athena-workflow-marketplace',
    'test-analysis@lespaceman/athena-workflow-marketplace',
    'exploratory-testing@lespaceman/athena-workflow-marketplace',
  ];
  const expectedSmokeRefs = [
    'agent-web-interface@lespaceman/athena-workflow-marketplace',
    'app-exploration@lespaceman/athena-workflow-marketplace',
    'test-analysis@lespaceman/athena-workflow-marketplace',
    'smoke-testing@lespaceman/athena-workflow-marketplace',
  ];
  const expectedRegressionRefs = [
    'agent-web-interface@lespaceman/athena-workflow-marketplace',
    'app-exploration@lespaceman/athena-workflow-marketplace',
    'test-analysis@lespaceman/athena-workflow-marketplace',
    'regression-testing@lespaceman/athena-workflow-marketplace',
  ];

  assert(
    JSON.stringify(exploratoryWorkflow.plugins.map((plugin) => plugin.ref)) === JSON.stringify(expectedExploratoryRefs),
    'workflows/exploratory-testing/workflow.json must depend on the layered exploratory suite',
  );
  assert(
    JSON.stringify(smokeWorkflow.plugins.map((plugin) => plugin.ref)) === JSON.stringify(expectedSmokeRefs),
    'workflows/smoke-testing/workflow.json must depend on the layered smoke suite',
  );
  assert(
    JSON.stringify(regressionWorkflow.plugins.map((plugin) => plugin.ref)) === JSON.stringify(expectedRegressionRefs),
    'workflows/regression-testing/workflow.json must depend on the layered regression suite',
  );
  assertIncludes(
    exploratoryWorkflow.description,
    'recommend the appropriate execution workflow',
    'workflows/exploratory-testing/workflow.json must describe execution as a recommendation handoff',
  );
  assertIncludes(
    smokeWorkflow.description,
    'recommend the appropriate execution workflow',
    'workflows/smoke-testing/workflow.json must describe execution as a recommendation handoff',
  );
  assertIncludes(
    regressionWorkflow.description,
    'recommend the appropriate execution workflow',
    'workflows/regression-testing/workflow.json must describe execution as a recommendation handoff',
  );
  assertIncludes(
    exploratoryWorkflowMd,
    'stop with an\nexplicit recommendation',
    'workflows/exploratory-testing/workflow.md must require an explicit execution handoff instead of same-session execution',
  );
  assertIncludes(
    exploratoryWorkflowMd,
    'appropriate execution workflow:',
    'workflows/exploratory-testing/workflow.md must list the execution handoff targets',
  );
  assertIncludes(
    exploratoryWorkflowMd,
    'does not load execution-layer plugins itself',
    'workflows/exploratory-testing/workflow.md must explain why execution remains a handoff',
  );
  assertNotIncludes(
    exploratoryWorkflowMd,
    'continue with the',
    'workflows/exploratory-testing/workflow.md must not imply same-session execution-layer continuation',
  );
  assertIncludes(
    smokeWorkflowMd,
    'stop with an explicit',
    'workflows/smoke-testing/workflow.md must require an explicit execution handoff instead of same-session execution',
  );
  assertIncludes(
    regressionWorkflowMd,
    'appropriate execution workflow:',
    'workflows/regression-testing/workflow.md must require an explicit execution handoff instead of same-session execution',
  );
  assertIncludes(
    smokeWorkflowMd,
    'does not load execution-layer plugins itself',
    'workflows/smoke-testing/workflow.md must explain why execution remains a handoff',
  );
  assertIncludes(
    regressionWorkflowMd,
    'does not load execution-layer plugins itself',
    'workflows/regression-testing/workflow.md must explain why execution remains a handoff',
  );
  assertNotIncludes(
    smokeWorkflowMd,
    'continue with the',
    'workflows/smoke-testing/workflow.md must not imply same-session execution-layer continuation',
  );
  assertNotIncludes(
    regressionWorkflowMd,
    'continue with the',
    'workflows/regression-testing/workflow.md must not imply same-session execution-layer continuation',
  );

  assertIncludes(readme, 'node scripts/validate-intent-suite.mjs', 'README must document the intent suite validator');
  assertIncludes(readme, '`exploratory-testing` | Frame risk hypotheses and investigation focus via exploratory charters', 'README must describe exploratory-testing as charter-focused');
  assertIncludes(readme, '`smoke-testing` | Define the minimum critical-path confidence scope before runnable automation is selected', 'README must describe smoke-testing as an intent-layer plugin');
  assertIncludes(readme, '`regression-testing` | Define rerunnable regression scope across changed and high-risk areas before runnable automation is selected', 'README must describe regression-testing as an intent-layer plugin');
  assertNotIncludes(readme, 'exploratory-testing` is currently available as a plugin without a dedicated workflow family', 'README must not claim exploratory-testing lacks a workflow family');

  for (const [label, content] of [
    ['plugin-suite-plan.md', planDoc],
    ['plugin-suite-immediate-split.md', immediateDoc],
    ['plugin-suite-future-suite.md', futureDoc],
  ]) {
    assertIncludes(content, 'exploratory-testing', `${label} must mention exploratory-testing`);
    assertIncludes(content, 'smoke-testing', `${label} must mention smoke-testing`);
    assertIncludes(content, 'regression-testing', `${label} must mention regression-testing`);
  }

  for (const [label, content] of [
    ['exploratory-test-writer', exploratorySkill],
    ['define-smoke-scope', smokeSkill],
    ['define-regression-scope', regressionSkill],
  ]) {
    assertNotIncludes(content, 'produces `e2e-plan/coverage-plan.md`', `${label} must not claim ownership of coverage-plan.md`);
    assertNotIncludes(content, 'produces `test-cases/<feature>.md`', `${label} must not claim ownership of test-cases/<feature>.md`);
  }

  assertIncludes(exploratorySkill, 'e2e-plan/exploratory-charter.md', 'exploratory-test-writer must reference exploratory-charter.md');
  assertIncludes(smokeSkill, 'e2e-plan/smoke-charter.md', 'define-smoke-scope must reference smoke-charter.md');
  assertIncludes(regressionSkill, 'e2e-plan/regression-charter.md', 'define-regression-scope must reference regression-charter.md');

  assertIncludes(exploratorySkill, 'optional artifact owned by this plugin', 'exploratory-test-writer must mark exploratory-charter.md as optional');
  assertIncludes(smokeSkill, 'not part of the core', 'define-smoke-scope must mark smoke-charter.md as optional');
  assertIncludes(regressionSkill, 'not part of the core', 'define-regression-scope must mark regression-charter.md as optional');

  assertIncludes(
    exploratoryClaudePlugin.description,
    'Exploratory testing charters',
    'exploratory-testing Claude manifest must stay aligned to charter-only ownership',
  );
  assertIncludes(
    exploratoryCodexPlugin.description,
    'Exploratory testing charters',
    'exploratory-testing Codex manifest must stay aligned to charter-only ownership',
  );
  assertIncludes(
    smokeClaudePlugin.description,
    'Smoke testing scopes',
    'smoke-testing Claude manifest must describe smoke intent only',
  );
  assertIncludes(
    smokeCodexPlugin.description,
    'Smoke testing scopes',
    'smoke-testing Codex manifest must describe smoke intent only',
  );
  assertIncludes(
    regressionClaudePlugin.description,
    'Regression testing scopes',
    'regression-testing Claude manifest must describe regression intent only',
  );
  assertIncludes(
    regressionCodexPlugin.description,
    'Regression testing scopes',
    'regression-testing Codex manifest must describe regression intent only',
  );

  assertIncludes(exploratoryOpenAi, 'Define Exploratory Charter', 'exploratory-testing OpenAI agent metadata must use charter framing');
  assertIncludes(exploratoryOpenAi, 'risk hypotheses', 'exploratory-testing OpenAI agent metadata must keep charter-focused scope');
  assertIncludes(exploratoryClaudeAgent, 'user-invocable: true', 'exploratory-testing Claude agent metadata must remain user invocable');
  assertIncludes(smokeOpenAi, 'Define Smoke Scope', 'smoke-testing OpenAI agent metadata must use smoke-scope framing');
  assertIncludes(smokeOpenAi, 'critical-path confidence scope', 'smoke-testing OpenAI agent metadata must keep smoke-only scope');
  assertIncludes(smokeClaudeAgent, 'user-invocable: true', 'smoke-testing Claude agent metadata must remain user invocable');
  assertIncludes(regressionOpenAi, 'Define Regression Scope', 'regression-testing OpenAI agent metadata must use regression-scope framing');
  assertIncludes(regressionOpenAi, 'rerunnable regression scope', 'regression-testing OpenAI agent metadata must keep regression-only scope');
  assertIncludes(regressionClaudeAgent, 'user-invocable: true', 'regression-testing Claude agent metadata must remain user invocable');

  if (failures.length > 0) {
    console.error('intent suite validation failed:\n');
    for (const failure of failures) {
      console.error(`- ${failure}`);
    }
    process.exit(1);
  }

  console.log('intent suite validation passed');
}

main();
