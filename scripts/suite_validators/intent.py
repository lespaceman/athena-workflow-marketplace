"""Intent suite validator (replaces validate-intent-suite.mjs)."""
from __future__ import annotations

from .common import SuiteContext


def validate_intent(ctx: SuiteContext) -> None:
    plugin_names = {p.name for p in ctx.model.plugins}
    workflow_names = {w.name for w in ctx.model.workflows}

    for name in ("exploratory-testing", "smoke-testing", "regression-testing"):
        ctx.assert_(name in plugin_names, f"marketplace registries must register {name}")
        ctx.assert_(name in workflow_names, f".athena-workflow/marketplace.json must register {name}")

    for workflow_name in ("exploratory-testing", "smoke-testing", "regression-testing"):
        ctx.assert_workflow_includes_shared_layer(workflow_name)
        ctx.assert_workflow_pin_versions_match_model(workflow_name)

    exploratory_workflow = ctx.model.workflow("exploratory-testing")
    smoke_workflow = ctx.model.workflow("smoke-testing")
    regression_workflow = ctx.model.workflow("regression-testing")

    for label, workflow in (("exploratory-testing", exploratory_workflow), ("smoke-testing", smoke_workflow), ("regression-testing", regression_workflow)):
        ctx.assert_(
            "recommend the appropriate execution workflow" in workflow.description,
            f"workflows/{label}/workflow.json must describe execution as a recommendation handoff",
        )

    exploratory_md = ctx.read("workflows/exploratory-testing/workflow.md")
    smoke_md = ctx.read("workflows/smoke-testing/workflow.md")
    regression_md = ctx.read("workflows/regression-testing/workflow.md")

    ctx.assert_("stop with an\nexplicit recommendation" in exploratory_md, "workflows/exploratory-testing/workflow.md must require an explicit execution handoff instead of same-session execution")
    ctx.assert_("appropriate execution workflow:" in exploratory_md, "workflows/exploratory-testing/workflow.md must list the execution handoff targets")
    ctx.assert_("does not load execution-layer plugins itself" in exploratory_md, "workflows/exploratory-testing/workflow.md must explain why execution remains a handoff")
    ctx.assert_("continue with the" not in exploratory_md, "workflows/exploratory-testing/workflow.md must not imply same-session execution-layer continuation")

    ctx.assert_("stop with an explicit" in smoke_md, "workflows/smoke-testing/workflow.md must require an explicit execution handoff instead of same-session execution")
    ctx.assert_("appropriate execution workflow:" in regression_md, "workflows/regression-testing/workflow.md must require an explicit execution handoff instead of same-session execution")
    ctx.assert_("does not load execution-layer plugins itself" in smoke_md, "workflows/smoke-testing/workflow.md must explain why execution remains a handoff")
    ctx.assert_("does not load execution-layer plugins itself" in regression_md, "workflows/regression-testing/workflow.md must explain why execution remains a handoff")
    ctx.assert_("continue with the" not in smoke_md, "workflows/smoke-testing/workflow.md must not imply same-session execution-layer continuation")
    ctx.assert_("continue with the" not in regression_md, "workflows/regression-testing/workflow.md must not imply same-session execution-layer continuation")

    readme = ctx.read("README.md")
    ctx.assert_("node scripts/validate-intent-suite.mjs" in readme, "README must document the intent suite validator")
    ctx.assert_("`exploratory-testing` | Frame risk hypotheses and investigation focus via exploratory charters" in readme, "README must describe exploratory-testing as charter-focused")
    ctx.assert_("`smoke-testing` | Define the minimum critical-path confidence scope before runnable automation is selected" in readme, "README must describe smoke-testing as an intent-layer plugin")
    ctx.assert_("`regression-testing` | Define rerunnable regression scope across changed and high-risk areas before runnable automation is selected" in readme, "README must describe regression-testing as an intent-layer plugin")
    ctx.assert_("exploratory-testing` is currently available as a plugin without a dedicated workflow family" not in readme, "README must not claim exploratory-testing lacks a workflow family")

    plan_doc = ctx.read("docs/architecture/plugin-suite-plan.md")
    immediate_doc = ctx.read("docs/architecture/plugin-suite-immediate-split.md")
    future_doc = ctx.read("docs/architecture/plugin-suite-future-suite.md")
    for label, content in (("plugin-suite-plan.md", plan_doc), ("plugin-suite-immediate-split.md", immediate_doc), ("plugin-suite-future-suite.md", future_doc)):
        for needle in ("exploratory-testing", "smoke-testing", "regression-testing"):
            ctx.assert_(needle in content, f"{label} must mention {needle}")

    exploratory_skill = ctx.read("plugins/exploratory-testing/skills/exploratory-test-writer/SKILL.md")
    smoke_skill = ctx.read("plugins/smoke-testing/skills/define-smoke-scope/SKILL.md")
    regression_skill = ctx.read("plugins/regression-testing/skills/define-regression-scope/SKILL.md")

    for label, content in (("exploratory-test-writer", exploratory_skill), ("define-smoke-scope", smoke_skill), ("define-regression-scope", regression_skill)):
        ctx.assert_("produces `docs/qa/coverage-plan.md`" not in content, f"{label} must not claim ownership of coverage-plan.md")
        ctx.assert_("produces `docs/qa/test-cases/<feature>.md`" not in content, f"{label} must not claim ownership of docs/qa/test-cases/<feature>.md")

    ctx.assert_("docs/qa/exploratory-charter.md" in exploratory_skill, "exploratory-test-writer must reference exploratory-charter.md")
    ctx.assert_("docs/qa/smoke-charter.md" in smoke_skill, "define-smoke-scope must reference smoke-charter.md")
    ctx.assert_("docs/qa/regression-charter.md" in regression_skill, "define-regression-scope must reference regression-charter.md")
    ctx.assert_("optional artifact owned by this plugin" in exploratory_skill, "exploratory-test-writer must mark exploratory-charter.md as optional")
    ctx.assert_("not part of the core" in smoke_skill, "define-smoke-scope must mark smoke-charter.md as optional")
    ctx.assert_("not part of the core" in regression_skill, "define-regression-scope must mark regression-charter.md as optional")

    # Per-plugin manifest description checks (was: read JSON manually)
    for name, expected in (
        ("exploratory-testing", "Exploratory testing charters"),
        ("smoke-testing", "Smoke testing scopes"),
        ("regression-testing", "Regression testing scopes"),
    ):
        plugin = ctx.model.plugin(name)
        ctx.assert_(expected in plugin.description, f"{name} manifest description must stay aligned to intent-only ownership")

    exploratory_openai = ctx.read("plugins/exploratory-testing/skills/exploratory-test-writer/agents/openai.yaml")
    smoke_openai = ctx.read("plugins/smoke-testing/skills/define-smoke-scope/agents/openai.yaml")
    regression_openai = ctx.read("plugins/regression-testing/skills/define-regression-scope/agents/openai.yaml")
    exploratory_claude = ctx.read("plugins/exploratory-testing/skills/exploratory-test-writer/agents/claude.yaml")
    smoke_claude = ctx.read("plugins/smoke-testing/skills/define-smoke-scope/agents/claude.yaml")
    regression_claude = ctx.read("plugins/regression-testing/skills/define-regression-scope/agents/claude.yaml")

    ctx.assert_("Define Exploratory Charter" in exploratory_openai, "exploratory-testing OpenAI agent metadata must use charter framing")
    ctx.assert_("risk hypotheses" in exploratory_openai, "exploratory-testing OpenAI agent metadata must keep charter-focused scope")
    ctx.assert_("user-invocable: true" in exploratory_claude, "exploratory-testing Claude agent metadata must remain user invocable")
    ctx.assert_("Define Smoke Scope" in smoke_openai, "smoke-testing OpenAI agent metadata must use smoke-scope framing")
    ctx.assert_("critical-path confidence scope" in smoke_openai, "smoke-testing OpenAI agent metadata must keep smoke-only scope")
    ctx.assert_("user-invocable: true" in smoke_claude, "smoke-testing Claude agent metadata must remain user invocable")
    ctx.assert_("Define Regression Scope" in regression_openai, "regression-testing OpenAI agent metadata must use regression-scope framing")
    ctx.assert_("rerunnable regression scope" in regression_openai, "regression-testing OpenAI agent metadata must keep regression-only scope")
    ctx.assert_("user-invocable: true" in regression_claude, "regression-testing Claude agent metadata must remain user invocable")
