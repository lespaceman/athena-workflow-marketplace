"""Robot suite validator (replaces validate-robot-suite.mjs)."""
from __future__ import annotations

from .common import SuiteContext


def validate_robot(ctx: SuiteContext) -> None:
    for rel_path in (
        "plugins/robot-automation/skills/plan-test-coverage",
        "plugins/robot-automation/skills/generate-test-cases",
        "plugins/robot-automation/skills/review-test-cases",
    ):
        ctx.assert_(not ctx.exists(rel_path), f"{rel_path} must be removed so shared planning/spec skills live only in test-analysis")

    workflow_names = {w.name for w in ctx.model.workflows}
    ctx.assert_("robot-automation" in workflow_names, ".athena-workflow/marketplace.json must retain the robot-automation workflow entry")

    ctx.assert_workflow_includes_shared_layer("robot-automation")
    ctx.assert_workflow_pin_versions_match_model("robot-automation")

    readme = ctx.read("README.md")
    workflow_md = ctx.read("workflows/robot-automation/workflow.md")
    add_tests = ctx.read("plugins/robot-automation/skills/add-robot-tests/SKILL.md")
    write_code = ctx.read("plugins/robot-automation/skills/write-robot-code/SKILL.md")
    analyze = ctx.read("plugins/robot-automation/skills/analyze-test-codebase/SKILL.md")

    ctx.assert_("node scripts/validate-robot-suite.mjs" in readme, "README must document the Robot suite validator")
    ctx.assert_("claude plugin install app-exploration@athena-workflow-marketplace" in readme, "README must document app-exploration as a shared prerequisite for the Robot stack")
    ctx.assert_("claude plugin install test-analysis@athena-workflow-marketplace" in readme, "README must document test-analysis as a shared prerequisite for the Robot stack")
    ctx.assert_("claude plugin install robot-automation@athena-workflow-marketplace" in readme, "README must document robot-automation as the Robot execution layer install step")
    ctx.assert_(
        "does not install the shared" in readme and "`app-exploration` and `test-analysis` layers" in readme,
        "README must explain that installing an execution plugin alone does not install the shared layers",
    )
    ctx.assert_(
        "The full orchestration surface remains the workflow pair `playwright-automation` and `robot-automation`" in readme,
        "README must preserve the workflow-first orchestration note",
    )
    ctx.assert_(
        "`robot-automation` | Robot execution layer: analyze codebases, write `.robot` suites, review them, and fix flake after the shared layers are ready" in readme,
        "README must describe robot-automation as the Robot execution layer",
    )
    ctx.assert_("agent-web-interface-guide" in workflow_md, "workflows/robot-automation/workflow.md must explicitly list agent-web-interface-guide for browser-backed exploration and triage")

    for label, content in (("add-robot-tests", add_tests), ("write-robot-code", write_code), ("analyze-test-codebase", analyze)):
        ctx.assert_("agent-web-interface-guide" not in content, f"{label} must not present agent-web-interface-guide as the canonical Robot layer entry point")

    for label, content in (("workflows/robot-automation/workflow.md", workflow_md), ("add-robot-tests", add_tests)):
        ctx.assert_("capture-feature-evidence" in content, f"{label} must reference capture-feature-evidence as the shared exploration layer")
        ctx.assert_("plan-test-coverage" in content, f"{label} must reference plan-test-coverage as the shared planning layer")
        ctx.assert_("generate-test-cases" in content, f"{label} must reference generate-test-cases as the shared spec layer")
        ctx.assert_("review-test-cases" in content, f"{label} must reference review-test-cases as the shared spec review layer")

    for label, content in (("add-robot-tests", add_tests), ("write-robot-code", write_code)):
        ctx.assert_("docs/qa/exploration-report.md" in content, f"{label} must reference docs/qa/exploration-report.md")

    ctx.assert_("docs/qa/coverage-plan.md" in add_tests, "add-robot-tests must reference docs/qa/coverage-plan.md")
    ctx.assert_("docs/qa/test-cases/<feature>.md" in add_tests, "add-robot-tests must reference docs/qa/test-cases/<feature>.md")
