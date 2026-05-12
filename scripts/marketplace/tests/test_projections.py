import unittest

from marketplace.model import MarketplaceModel, Plugin, PluginPin, Workflow
from marketplace.projections import (
    render_athena_marketplace_entry,
    render_claude_marketplace_entry,
    render_codex_marketplace_entry,
    render_plugin_claude_manifest,
    render_plugin_codex_manifest,
)


def make_plugin(**overrides):
    base = dict(
        name="example",
        version="1.2.3",
        description="An example plugin",
        category="testing",
        author={"name": "Athenaflow"},
        keywords=["a", "b"],
        repository=None,
        license=None,
        homepage=None,
        contributors=None,
        marketplace_description=None,
        skills_path="./skills/",
        mcp_servers=None,
        interface={"displayName": "Example", "shortDescription": "Short", "developerName": "Athenaflow", "category": "Testing"},
    )
    base.update(overrides)
    return Plugin(**base)


def make_workflow(**overrides):
    base = dict(name="ex", version="0.0.1", description="A workflow", marketplace_description=None, raw={"name": "ex", "version": "0.0.1"}, pins=[])
    base.update(overrides)
    return Workflow(**base)


class TestPluginManifestProjections(unittest.TestCase):
    def test_claude_manifest_minimal(self):
        out = render_plugin_claude_manifest(make_plugin())
        self.assertEqual(out["name"], "example")
        self.assertEqual(out["description"], "An example plugin")
        self.assertEqual(out["version"], "1.2.3")
        self.assertEqual(out["category"], "testing")
        self.assertEqual(out["keywords"], ["a", "b"])
        self.assertNotIn("repository", out)
        self.assertNotIn("license", out)

    def test_claude_manifest_with_optional_fields(self):
        out = render_plugin_claude_manifest(
            make_plugin(repository="https://example.com", license="MIT", homepage="https://example.com/home")
        )
        self.assertEqual(out["repository"], "https://example.com")
        self.assertEqual(out["license"], "MIT")
        self.assertEqual(out["homepage"], "https://example.com/home")

    def test_codex_manifest_includes_skills_and_interface(self):
        out = render_plugin_codex_manifest(make_plugin())
        self.assertEqual(out["skills"], "./skills/")
        self.assertIn("interface", out)
        self.assertEqual(out["interface"]["displayName"], "Example")

    def test_codex_manifest_with_mcp_servers(self):
        out = render_plugin_codex_manifest(make_plugin(mcp_servers={"foo": {"cmd": "bar"}}))
        self.assertEqual(out["mcpServers"], {"foo": {"cmd": "bar"}})


class TestMarketplaceProjections(unittest.TestCase):
    def test_claude_marketplace_entry_uses_plugin_path_for_source(self):
        out = render_claude_marketplace_entry(make_plugin(name="foo-bar"))
        self.assertEqual(out["source"], "./plugins/foo-bar")

    def test_claude_marketplace_entry_omits_self_repository(self):
        out = render_claude_marketplace_entry(
            make_plugin(repository="https://github.com/AthenaFlow/workflow-marketplace")
        )
        self.assertNotIn("repository", out)

    def test_claude_marketplace_entry_forwards_external_repository(self):
        out = render_claude_marketplace_entry(make_plugin(repository="https://github.com/example/plugin"))
        self.assertEqual(out["repository"], "https://github.com/example/plugin")

    def test_claude_marketplace_entry_omits_athenaflow_author(self):
        out = render_claude_marketplace_entry(make_plugin(author={"name": "Athenaflow"}))
        self.assertNotIn("author", out)

    def test_claude_marketplace_entry_includes_third_party_author(self):
        out = render_claude_marketplace_entry(make_plugin(author={"name": "Jesse Vincent", "email": "jesse@fsck.com"}))
        self.assertEqual(out["author"]["name"], "Jesse Vincent")

    def test_marketplace_description_overrides_canonical(self):
        plugin = make_plugin(description="canonical text", marketplace_description="catalog text")
        claude_out = render_claude_marketplace_entry(plugin)
        codex_out = render_codex_marketplace_entry(plugin)
        self.assertEqual(claude_out["description"], "catalog text")
        self.assertEqual(codex_out["description"], "catalog text")

    def test_codex_marketplace_entry_has_required_policy(self):
        out = render_codex_marketplace_entry(make_plugin())
        self.assertEqual(out["policy"], {"installation": "AVAILABLE", "authentication": "ON_INSTALL"})
        self.assertEqual(out["source"], {"source": "local", "path": "./plugins/example"})

    def test_athena_marketplace_entry_uses_workflow_json_source_path(self):
        out = render_athena_marketplace_entry(make_workflow(name="my-flow"))
        self.assertEqual(out["source"], "./workflows/my-flow/workflow.json")

    def test_athena_marketplace_entry_uses_marketplace_description_when_set(self):
        out = render_athena_marketplace_entry(
            make_workflow(description="long agent-facing", marketplace_description="short catalog")
        )
        self.assertEqual(out["description"], "short catalog")


if __name__ == "__main__":
    unittest.main()
