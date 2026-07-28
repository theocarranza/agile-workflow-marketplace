import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install import (
    _MCP_JSON_HOSTS,
    detect_hosts,
    link_cli_skills,
    merge_json_mcp,
    parse_targets,
    read_azure_org_from_mcp,
    register_antigravity_plugin,
    resolve_tool_paths,
    validate_azure_org,
    wire_project_mcp,
)

ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = ROOT / "install.sh"


class TestInstallHelpers(unittest.TestCase):
    def test_link_cli_skills_links_only_missing_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "skills"
            source.mkdir(parents=True)
            (source / "alpha").mkdir()
            (source / "beta").mkdir()
            destination = root / "destination"
            self.assertTrue(link_cli_skills(source.parent, destination))
            self.assertEqual((destination / "alpha").resolve(), (source / "alpha").resolve())
            (destination / "beta").unlink()
            (destination / "beta").mkdir()
            self.assertTrue(link_cli_skills(source.parent, destination))
            self.assertTrue((destination / "beta").is_dir())

    @patch("scripts.install.Path.home")
    def test_register_antigravity_wires_cli_plugin_and_skills(self, mock_home) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_home.return_value = root / "home"
            install = root / "install"
            plugin = install / "agile-workflow"
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".codex-plugin" / "plugin.json").write_text(
                json.dumps({"name": "agile-workflow", "version": "0.9.0", "description": "test"}),
                encoding="utf-8",
            )
            (plugin / "skills" / "amend-workitems").mkdir(parents=True)
            (plugin / "skills" / "amend-workitems" / "SKILL.md").write_text("---\nname: amend-workitems\n---\n", encoding="utf-8")
            self.assertTrue(register_antigravity_plugin(install))
            cli_plugin = root / "home" / ".gemini" / "antigravity-cli" / "plugins" / "agile-workflow"
            self.assertEqual(json.loads((cli_plugin / "plugin.json").read_text())["name"], "agile-workflow")
            self.assertTrue((cli_plugin / "skills" / "amend-workitems" / "SKILL.md").is_file())
            self.assertEqual(
                (root / "home" / ".gemini" / "antigravity-cli" / "skills" / "amend-workitems").resolve(),
                (plugin / "skills" / "amend-workitems").resolve(),
            )

    def test_read_azure_org_from_mcp(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".mcp.json"
            path.write_text(
                json.dumps(
                    {
                        "mcpServers": {
                            "azure-devops": {
                                "command": "npx",
                                "args": ["-y", "@azure-devops/mcp", "my-org"],
                            }
                        }
                    }
                ),
                encoding="utf-8",
            )
            self.assertEqual(read_azure_org_from_mcp(path), "my-org")

    def test_merge_json_mcp_preserves_existing(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / ".mcp.json"
            path.write_text(
                json.dumps({"mcpServers": {"other": {"command": "echo"}}}),
                encoding="utf-8",
            )
            merge_json_mcp(path, {"azure-devops": {"command": "npx", "args": []}})
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertIn("other", data["mcpServers"])
            self.assertIn("azure-devops", data["mcpServers"])


    def test_validate_azure_org_rejects_spaces(self) -> None:
        with self.assertRaises(ValueError):
            validate_azure_org("bad org")

    def test_parse_targets_explicit(self) -> None:
        self.assertEqual(parse_targets("cursor,codex", non_interactive=True), ["cursor", "codex"])

    def test_parse_targets_unknown_raises(self) -> None:
        with self.assertRaises(ValueError):
            parse_targets("foo", non_interactive=True)

    @patch("scripts.install.Path.home")
    def test_detect_hosts(self, mock_home) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            (home / ".claude").mkdir()
            (home / ".cursor").mkdir()
            mock_home.return_value = home
            hosts = detect_hosts()
            self.assertIn("claude", hosts)
            self.assertIn("cursor", hosts)

    @patch("scripts.install.shutil.which")
    def test_resolve_tool_paths(self, mock_which) -> None:
        mock_which.side_effect = lambda name: {
            "python3": "/usr/bin/python3",
            "npx": "/usr/local/bin/npx",
        }.get(name)
        paths = resolve_tool_paths("python3", "npx")
        self.assertEqual(paths["python3"], "/usr/bin/python3")
        self.assertEqual(paths["npx"], "/usr/local/bin/npx")

    @patch("scripts.install.shutil.which")
    def test_resolve_tool_paths_missing_raises(self, mock_which) -> None:
        mock_which.return_value = None
        with self.assertRaises(ValueError):
            resolve_tool_paths("npx")

    @patch("scripts.install.resolve_tool_paths")
    def test_wire_project_mcp_cursor_only_skips_mcp_json(self, mock_resolve) -> None:
        mock_resolve.return_value = {"python3": "/usr/bin/python3", "npx": "/usr/local/bin/npx"}
        with tempfile.TemporaryDirectory() as tmp:
            project = Path(tmp) / "app"
            project.mkdir()
            install = Path(tmp) / "install"
            (install / "agile-workflow" / "orchestrator_core").mkdir(parents=True)
            wire_project_mcp(
                project,
                install_dir=install,
                azure_org="my-org",
                targets=["cursor"],
            )
            self.assertFalse((project / ".mcp.json").exists())
            self.assertTrue((project / ".cursor" / "mcp.json").exists())
            cursor_mcp = json.loads((project / ".cursor" / "mcp.json").read_text(encoding="utf-8"))
            azure = cursor_mcp["mcpServers"]["azure-devops"]
            self.assertTrue(azure["command"].endswith("azure-devops-mcp.sh"))
            self.assertEqual(azure["args"], [])
            orch = cursor_mcp["mcpServers"]["agile-workflow-orchestrator"]
            self.assertEqual(orch["command"], "/usr/bin/python3")

    @patch("scripts.install.resolve_tool_paths")
    def test_wire_project_mcp_does_not_touch_global_cursor(self, mock_resolve) -> None:
        mock_resolve.return_value = {"python3": "/usr/bin/python3", "npx": "/usr/local/bin/npx"}
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            project = Path(tmp) / "app"
            project.mkdir()
            install = Path(tmp) / "install"
            (install / "agile-workflow" / "orchestrator_core").mkdir(parents=True)
            global_mcp = home / ".cursor" / "mcp.json"
            global_mcp.parent.mkdir(parents=True)
            global_mcp.write_text(
                json.dumps({"mcpServers": {"dart": {"command": "/bin/dart", "args": []}}}),
                encoding="utf-8",
            )
            with patch("scripts.install.Path.home", return_value=home):
                wire_project_mcp(
                    project,
                    install_dir=install,
                    azure_org="my-org",
                        targets=["cursor"],
                )
            self.assertEqual(
                json.loads(global_mcp.read_text(encoding="utf-8")),
                {"mcpServers": {"dart": {"command": "/bin/dart", "args": []}}},
            )

    def test_mcp_json_hosts_excludes_cursor(self) -> None:
        self.assertNotIn("cursor", _MCP_JSON_HOSTS)


class TestInstallShBootstrap(unittest.TestCase):
    def test_local_checkout_reaches_python_installer(self) -> None:
        proc = subprocess.run(
            ["bash", str(INSTALL_SH), "--help"],
            capture_output=True,
            text=True,
            check=False,
        )
        self.assertEqual(proc.returncode, 0, proc.stderr)
        combined = (proc.stdout + proc.stderr).lower()
        self.assertIn("azure-org", combined)
        self.assertNotIn("bootstrapping", combined)

    def test_piped_install_bootstraps_instead_of_cwd_install_py(self) -> None:
        env = {
            **os.environ,
            "AGILE_WORKFLOW_REPO": "file:///nonexistent-agile-workflow-marketplace",
            "AGILE_WORKFLOW_REF": "main",
        }
        proc = subprocess.run(
            ["bash", "-s", "--", "-y", "--azure-org", "demo", "--project-dir", "/tmp"],
            input=INSTALL_SH.read_text(encoding="utf-8"),
            capture_output=True,
            text=True,
            env=env,
            check=False,
        )
        combined = proc.stdout + proc.stderr
        self.assertIn("Bootstrapping", combined)
        self.assertNotIn("can't open file", combined)
        self.assertNotEqual(proc.returncode, 0)


if __name__ == "__main__":
    unittest.main()
