"""Playwright suite validator (replaces validate-playwright-suite.mjs)."""
from __future__ import annotations

from .common import SuiteContext


def validate_playwright(ctx: SuiteContext) -> None:
    ctx.assert_(not ctx.exists("plugins/e2e-test-builder"), "plugins/e2e-test-builder must be removed")

    # Registry membership (was: hand-walk three marketplace files)
    plugin_names = {p.name for p in ctx.model.plugins}
    workflow_names = {w.name for w in ctx.model.workflows}
    ctx.assert_("playwright-automation" in plugin_names, "marketplace registries must register playwright-automation")
    ctx.assert_("playwright-automation" in workflow_names, ".athena-workflow/marketplace.json must retain the playwright-automation workflow entry")

    # Pin invariants (was: hardcoded expectedRefs array)
    ctx.assert_workflow_includes_shared_layer("playwright-automation")
    ctx.assert_workflow_pin_versions_match_model("playwright-automation")

    readme = ctx.read("README.md")
    workflow_md = ctx.read("workflows/playwright-automation/workflow.md")
    analyze = ctx.read("plugins/playwright-automation/skills/analyze-test-codebase/SKILL.md")
    write_code = ctx.read("plugins/playwright-automation/skills/write-test-code/SKILL.md")
    add_tests = ctx.read("plugins/playwright-automation/skills/add-playwright-tests/SKILL.md")
    coverage = ctx.read("plugins/test-analysis/skills/plan-test-coverage/SKILL.md")
    generate = ctx.read("plugins/test-analysis/skills/generate-test-cases/SKILL.md")
    review = ctx.read("plugins/test-analysis/skills/review-test-cases/SKILL.md")

    ctx.assert_("claude plugin install app-exploration@athena-workflow-marketplace" in readme, "README must document app-exploration as a shared prerequisite for the Playwright stack")
    ctx.assert_("claude plugin install test-analysis@athena-workflow-marketplace" in readme, "README must document test-analysis as a shared prerequisite for the Playwright stack")
    ctx.assert_("claude plugin install playwright-automation@athena-workflow-marketplace" in readme, "README must document playwright-automation as the Playwright execution layer install step")
    ctx.assert_(
        "does not install the shared" in readme and "`app-exploration` and `test-analysis` layers" in readme,
        "README must explain that installing an execution plugin alone does not install the shared layers",
    )
    ctx.assert_(
        "The full orchestration surface remains the workflow pair `playwright-automation` and `robot-automation`" in readme,
        "README must preserve the workflow-first orchestration note",
    )
    ctx.assert_("e2e-test-builder@athena-workflow-marketplace" not in readme, "README must not present e2e-test-builder as a manageable plugin surface")
    ctx.assert_("plugins/e2e-test-builder/" not in readme, "README must not list plugins/e2e-test-builder in the active repository structure")

    for label, content in (("workflow.md", workflow_md), ("analyze-test-codebase", analyze), ("write-test-code", write_code), ("add-playwright-tests", add_tests)):
        ctx.assert_("add-e2e-tests" not in content, f"{label} must not reference add-e2e-tests")

    for label, content in (("analyze-test-codebase", analyze), ("write-test-code", write_code)):
        ctx.assert_("agent-web-interface-guide" not in content, f"{label} must not present agent-web-interface-guide as the canonical Playwright exploration path")

    ctx.assert_("capture-feature-evidence" in analyze, "analyze-test-codebase must route live-site exploration through capture-feature-evidence")
    ctx.assert_("capture-feature-evidence" in write_code, "write-test-code must route missing product evidence through capture-feature-evidence")
    ctx.assert_("agent-web-interface-guide" in workflow_md, "workflows/playwright-automation/workflow.md must explicitly list agent-web-interface-guide for browser-backed exploration and triage")

    for label, content in (("plan-test-coverage", coverage), ("generate-test-cases", generate), ("review-test-cases", review)):
        ctx.assert_("e2e-plan/exploration-report.md" in content, f"{label} must reference e2e-plan/exploration-report.md")

    ctx.assert_("e2e-plan/coverage-plan.md" in coverage, "plan-test-coverage must produce e2e-plan/coverage-plan.md")
    ctx.assert_(
        "test-cases/<feature-name>.md" in generate or "test-cases/<feature>.md" in generate,
        "generate-test-cases must target test-cases/<feature>.md-style output",
    )
