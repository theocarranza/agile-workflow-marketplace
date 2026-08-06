"""Guards the plugin's packaging contract for the flat Open Plugins layout."""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT
VERSION = (ROOT / "VERSION").read_text(encoding="utf-8").strip()
PLUGIN_MANIFEST = PLUGIN_ROOT / ".plugin" / "plugin.json"
MARKETPLACE_MANIFESTS = (
    ROOT / ".claude-plugin" / "marketplace.json",
    ROOT / ".cursor-plugin" / "marketplace.json",
    ROOT / ".agents" / "plugins" / "marketplace.json",
)
PLUGIN_MCP = PLUGIN_ROOT / ".mcp.json"
VERSION_IN_PROSE = re.compile(r"v\d+\.\d+\.\d+")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestManifestVersions(unittest.TestCase):
    def test_version_file_matches_open_plugins_manifest(self) -> None:
        plugin = load(PLUGIN_MANIFEST)
        self.assertEqual(plugin["name"], "agile-backlog-toolkit")
        self.assertEqual(plugin["version"], VERSION)

    def test_host_manifests_lockstep(self) -> None:
        plugin = load(PLUGIN_MANIFEST)
        for path in (
            ROOT / ".claude-plugin" / "plugin.json",
            ROOT / ".cursor-plugin" / "plugin.json",
        ):
            with self.subTest(path=path.as_posix()):
                host = load(path)
                self.assertEqual(host["name"], plugin["name"])
                self.assertEqual(host["version"], plugin["version"])

    def test_marketplaces_declare_flat_source_and_same_version(self) -> None:
        plugin = load(PLUGIN_MANIFEST)
        for path in MARKETPLACE_MANIFESTS:
            with self.subTest(path=path.as_posix()):
                entries = [
                    entry
                    for entry in load(path)["plugins"]
                    if entry["name"] == plugin["name"]
                ]
                self.assertEqual(len(entries), 1)
                self.assertEqual(entries[0]["version"], plugin["version"])
                self.assertEqual(entries[0]["source"], "./")

    def test_descriptions_do_not_hardcode_a_version(self) -> None:
        plugin = load(PLUGIN_MANIFEST)
        for path in MARKETPLACE_MANIFESTS:
            entry = load(path)["plugins"][0]
            for label, description in (
                ("plugin.json", plugin["description"]),
                (path.as_posix(), entry["description"]),
            ):
                with self.subTest(manifest=label):
                    self.assertIsNone(
                        VERSION_IN_PROSE.search(description),
                        msg=f"{label} description hardcodes a version",
                    )

    def test_codex_plugin_dir_is_absent(self) -> None:
        self.assertFalse((ROOT / ".codex-plugin").exists())


class TestBundledMcpServer(unittest.TestCase):
    def test_plugin_ships_an_mcp_server(self) -> None:
        self.assertTrue(PLUGIN_MCP.is_file())
        servers = load(PLUGIN_MCP)["mcpServers"]
        self.assertIn("orchestrator", servers)

    def test_server_resolves_its_own_path(self) -> None:
        server = load(PLUGIN_MCP)["mcpServers"]["orchestrator"]
        self.assertEqual(server["env"]["PYTHONPATH"], "${PLUGIN_ROOT}")
        self.assertEqual(server["args"], ["-m", "orchestrator_core", "mcp"])

    def test_plugin_root_is_importable_as_declared(self) -> None:
        self.assertTrue((PLUGIN_ROOT / "orchestrator_core" / "__init__.py").is_file())


if __name__ == "__main__":
    unittest.main()
