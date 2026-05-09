"""Shared helpers for suite validators."""
from __future__ import annotations

import sys
from dataclasses import dataclass, field
from pathlib import Path

# Make sibling packages importable.
_SCRIPTS = Path(__file__).resolve().parent.parent
if str(_SCRIPTS) not in sys.path:
    sys.path.insert(0, str(_SCRIPTS))

from marketplace import MarketplaceModel, load  # noqa: E402


SHARED_LAYER_PLUGIN_REFS = (
    "agent-web-interface",
    "app-exploration",
    "test-analysis",
)


@dataclass
class SuiteContext:
    repo_root: Path
    model: MarketplaceModel
    failures: list[str] = field(default_factory=list)

    def assert_(self, condition: bool, message: str) -> None:
        if not condition:
            self.failures.append(message)

    def read(self, rel_path: str) -> str:
        return (self.repo_root / rel_path).read_text()

    def exists(self, rel_path: str) -> bool:
        return (self.repo_root / rel_path).exists()

    def assert_workflow_pin_versions_match_model(self, workflow_name: str) -> None:
        """Cheap structural check that replaces hardcoded `expectedRefs` arrays.

        Asserts every Plugin Pin in the Workflow references a real Plugin and the pinned
        version equals that Plugin's current version in the canonical model. This is the
        invariant the old arrays were trying (and failing) to enforce.
        """
        workflow = self.model.workflow(workflow_name)
        plugin_names = {p.name for p in self.model.plugins}
        for pin in workflow.pins:
            self.assert_(
                pin.plugin_name in plugin_names,
                f"workflow {workflow_name}: Plugin Pin {pin.plugin_name!r} references unknown plugin",
            )
            if pin.plugin_name in plugin_names:
                expected = self.model.plugin(pin.plugin_name).version
                self.assert_(
                    pin.version == expected,
                    f"workflow {workflow_name}: Plugin Pin {pin.plugin_name!r} pinned at {pin.version}, current is {expected}",
                )

    def assert_workflow_includes_shared_layer(self, workflow_name: str) -> None:
        """Assert the layered execution suite (agent-web-interface + app-exploration + test-analysis) is pinned."""
        workflow = self.model.workflow(workflow_name)
        pinned = {pin.plugin_name for pin in workflow.pins}
        for shared in SHARED_LAYER_PLUGIN_REFS:
            self.assert_(
                shared in pinned,
                f"workflow {workflow_name}: must pin shared layer plugin {shared!r}",
            )


def run_assertions(suite_name: str, validator) -> int:
    repo_root = Path(__file__).resolve().parent.parent.parent
    model = load(repo_root)
    ctx = SuiteContext(repo_root=repo_root, model=model)
    validator(ctx)
    if ctx.failures:
        print(f"{suite_name} suite validation failed:\n")
        for f in ctx.failures:
            print(f"- {f}")
        return 1
    print(f"{suite_name} suite validation passed")
    return 0
