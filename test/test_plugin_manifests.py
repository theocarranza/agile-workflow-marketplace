"""Guards the plugin's packaging contract.

The v0.10.0 release shipped with both manifests still reading `0.9.0`, so the install
landed in a cache directory named after a version the code had not been since the
previous release. Nothing failed -- the mismatch is invisible at runtime, which is
exactly why it needs a test rather than a review habit.
"""

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parent.parent
PLUGIN_ROOT = ROOT / "agile-backlog-toolkit"
PLUGIN_MANIFEST = PLUGIN_ROOT / ".claude-plugin" / "plugin.json"
MARKETPLACE_MANIFEST = ROOT / ".claude-plugin" / "marketplace.json"
PLUGIN_MCP = PLUGIN_ROOT / ".mcp.json"

VERSION_IN_PROSE = re.compile(r"v\d+\.\d+\.\d+")


def load(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8"))


class TestManifestVersions(unittest.TestCase):
    def test_plugin_and_marketplace_declare_the_same_version(self) -> None:
        plugin = load(PLUGIN_MANIFEST)
        entries = [
            entry
            for entry in load(MARKETPLACE_MANIFEST)["plugins"]
            if entry["name"] == plugin["name"]
        ]
        self.assertEqual(len(entries), 1, msg="plugin must appear once in the marketplace")
        self.assertEqual(
            plugin["version"],
            entries[0]["version"],
            msg="plugin.json and marketplace.json disagree on the release version",
        )

    def test_descriptions_do_not_hardcode_a_version(self) -> None:
        # A version repeated in prose drifts independently of the one that ships.
        plugin = load(PLUGIN_MANIFEST)
        entry = load(MARKETPLACE_MANIFEST)["plugins"][0]
        for label, description in (
            ("plugin.json", plugin["description"]),
            ("marketplace.json", entry["description"]),
        ):
            with self.subTest(manifest=label):
                self.assertIsNone(
                    VERSION_IN_PROSE.search(description),
                    msg=f"{label} description hardcodes a version; the manifest already has one",
                )


class TestBundledMcpServer(unittest.TestCase):
    def test_plugin_ships_an_mcp_server(self) -> None:
        self.assertTrue(
            PLUGIN_MCP.is_file(),
            msg="the plugin must bundle .mcp.json so a Claude Code install needs no extra wiring",
        )
        servers = load(PLUGIN_MCP)["mcpServers"]
        self.assertIn("orchestrator", servers)

    def test_server_resolves_its_own_path(self) -> None:
        # An absolute path here would only work on the machine that wrote it.
        server = load(PLUGIN_MCP)["mcpServers"]["orchestrator"]
        self.assertEqual(server["env"]["PYTHONPATH"], "${CLAUDE_PLUGIN_ROOT}")
        self.assertEqual(server["args"], ["-m", "orchestrator_core", "mcp"])

    def test_plugin_root_is_importable_as_declared(self) -> None:
        # PYTHONPATH is the plugin root, so orchestrator_core has to live directly under it.
        self.assertTrue((PLUGIN_ROOT / "orchestrator_core" / "__init__.py").is_file())


if __name__ == "__main__":
    unittest.main()
