import json
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install import (
    _MCP_JSON_HOSTS,
    _mcp_server_payloads,
    assemble_host_tree,
    detect_hosts,
    link_cli_skills,
    main,
    managed_state,
    merge_json_mcp,
    parse_targets,
    read_azure_org_from_mcp,
    register_antigravity_plugin,
    resolve_tool_paths,
    remove_managed_state,
    validate_azure_org,
    wire_project_mcp,
)

ROOT = Path(__file__).resolve().parent.parent
INSTALL_SH = ROOT / "install.sh"


class TestInstallHelpers(unittest.TestCase):
    def test_assembled_host_tree_is_a_physical_complete_copy(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            for dirname in ("common", "skills", "references", "orchestrator_core"):
                (source / dirname).mkdir(parents=True)
                (source / dirname / "marker.txt").write_text(dirname, encoding="utf-8")
            (source / ".claude-plugin").mkdir()
            (source / ".claude-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
            (source / ".codex-plugin").mkdir()
            (source / ".codex-plugin" / "plugin.json").write_text("{}", encoding="utf-8")
            (source / ".mcp.json").write_text("{}", encoding="utf-8")

            destination = assemble_host_tree(source, root / "cursor", "cursor")

            self.assertEqual(destination, root / "cursor")
            for dirname in ("common", "skills", "references", "orchestrator_core"):
                self.assertTrue((destination / dirname / "marker.txt").is_file())
                self.assertFalse((destination / dirname).is_symlink())
            self.assertTrue((destination / ".claude-plugin" / "plugin.json").is_file())
            self.assertFalse((destination / ".codex-plugin").exists())

    def test_mcp_matrix_only_includes_selected_provider_servers(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            kwargs = {
                "proot": root / "plugin",
                "project_dir": root / "project",
                "azure_org": "org",
                "tool_paths": {"python3": "/usr/bin/python3", "npx": "/usr/bin/npx"},
            }
            matrix = {
                "local": (False, False, set()),
                "azure": (True, False, {"azure-devops"}),
                "linear": (False, True, {"linear"}),
                "both": (True, True, {"azure-devops", "linear"}),
            }
            for mode, (azure, linear, expected) in matrix.items():
                with self.subTest(mode=mode):
                    claude, cursor = _mcp_server_payloads(
                        **kwargs,
                        enable_azure=azure,
                        enable_linear=linear,
                    )
                    self.assertEqual(
                        set(claude).intersection({"azure-devops", "linear"}),
                        expected,
                    )
                    self.assertEqual(
                        set(cursor).intersection({"azure-devops", "linear"}),
                        expected,
                    )

    def test_every_required_host_gets_an_independent_complete_tree(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source"
            for dirname in ("common", "skills", "references", "orchestrator_core"):
                (source / dirname).mkdir(parents=True)
                (source / dirname / "resource.txt").write_text(dirname, encoding="utf-8")
            for manifest in (".claude-plugin", ".codex-plugin"):
                (source / manifest).mkdir()
                (source / manifest / "plugin.json").write_text("{}", encoding="utf-8")
            (source / ".mcp.json").write_text("{}", encoding="utf-8")

            for host in ("claude", "codex", "cursor"):
                with self.subTest(host=host):
                    tree = assemble_host_tree(source, root / host, host)
                    self.assertTrue((tree / ".mcp.json").is_file())
                    self.assertTrue((tree / "orchestrator_core" / "resource.txt").is_file())
                    self.assertFalse(any(path.is_symlink() for path in tree.rglob("*")))

    @patch("scripts.install.Path.home")
    def test_non_interactive_replacement_aborts_without_mutation(self, mock_home) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            project = root / "project"
            managed = project / ".claude" / "plugins" / "agile-backlog-toolkit"
            managed.mkdir(parents=True)
            sentinel = managed / "keep.txt"
            sentinel.write_text("old", encoding="utf-8")
            mock_home.return_value = home

            status = main(["-y", "--from-source", "--project-dir", str(project), "--target", "claude"])

            self.assertEqual(status, 1)
            self.assertEqual(sentinel.read_text(encoding="utf-8"), "old")

    @patch("scripts.install.Path.home")
    def test_clean_replacement_removes_only_managed_state(self, mock_home) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            project = root / "project"
            managed = project / ".cursor" / "plugins" / "agile-backlog-toolkit"
            user_file = project / "docs" / "keep.md"
            managed.mkdir(parents=True)
            user_file.parent.mkdir(parents=True)
            user_file.write_text("user-owned", encoding="utf-8")
            mock_home.return_value = home

            self.assertTrue(managed_state(project, root / "install", root / "source"))
            remove_managed_state(project, root / "install", root / "source")

            self.assertFalse(managed.exists())
            self.assertEqual(user_file.read_text(encoding="utf-8"), "user-owned")

    @patch("scripts.install.run_install", side_effect=OSError("simulated install failure"))
    @patch("scripts.install.replacement_choice", return_value=True)
    @patch("scripts.install.Path.home")
    def test_failed_fresh_replacement_removes_partial_state_without_restoring_old(
        self, mock_home, _choice, _install
    ) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            home = root / "home"
            project = root / "project"
            managed = project / ".claude" / "plugins" / "agile-backlog-toolkit"
            user_file = project / "notes" / "keep.md"
            managed.mkdir(parents=True)
            user_file.parent.mkdir(parents=True)
            user_file.write_text("user-owned", encoding="utf-8")
            mock_home.return_value = home

            status = main(["--from-source", "--provider", "local", "--project-dir", str(project), "--target", "claude"])

            self.assertEqual(status, 1)
            self.assertFalse(managed.exists())
            self.assertEqual(user_file.read_text(encoding="utf-8"), "user-owned")

    def test_link_cli_skills_links_only_missing_entries(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            source = root / "source" / "skills"
            source.mkdir(parents=True)
            (source / "alpha").mkdir()
            (source / "beta").mkdir()
            destination = root / "destination"
            self.assertTrue(link_cli_skills(source.parent, destination))
            self.assertTrue((destination / "alpha").is_dir())
            self.assertFalse((destination / "alpha").is_symlink())
            (destination / "beta" / "SKILL.md").unlink(missing_ok=True)
            (destination / "beta").rmdir()
            self.assertTrue(link_cli_skills(source.parent, destination))
            self.assertTrue((destination / "beta").is_dir())
            self.assertFalse((destination / "beta").is_symlink())

    @patch("scripts.install.Path.home")
    def test_register_antigravity_wires_cli_plugin_and_skills(self, mock_home) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            mock_home.return_value = root / "home"
            install = root / "install"
            plugin = install / "agile-backlog-toolkit"
            (plugin / ".codex-plugin").mkdir(parents=True)
            (plugin / ".codex-plugin" / "plugin.json").write_text(
                json.dumps({"name": "agile-backlog-toolkit", "version": "0.11.0", "description": "test"}),
                encoding="utf-8",
            )
            (plugin / "skills" / "amend-workitems").mkdir(parents=True)
            (plugin / "skills" / "amend-workitems" / "SKILL.md").write_text("---\nname: amend-workitems\n---\n", encoding="utf-8")
            self.assertTrue(register_antigravity_plugin(install))
            cli_plugin = root / "home" / ".gemini" / "antigravity-cli" / "plugins" / "agile-backlog-toolkit"
            self.assertEqual(json.loads((cli_plugin / "plugin.json").read_text())["name"], "agile-backlog-toolkit")
            self.assertTrue((cli_plugin / "skills" / "amend-workitems" / "SKILL.md").is_file())
            self.assertTrue((root / "home" / ".gemini" / "antigravity-cli" / "skills" / "amend-workitems" / "SKILL.md").is_file())

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
            (install / "agile-backlog-toolkit" / "orchestrator_core").mkdir(parents=True)
            wire_project_mcp(
                project,
                install_dir=install,
                azure_org=None,
                targets=["cursor"],
                enable_azure=False,
            )
            self.assertFalse((project / ".mcp.json").exists())
            cursor = json.loads((project / ".cursor" / "mcp.json").read_text())
            self.assertIn("agile-backlog-toolkit-orchestrator", cursor["mcpServers"])
            self.assertNotIn("azure-devops", cursor["mcpServers"])

    @patch("scripts.install.resolve_tool_paths")
    def test_wire_project_mcp_does_not_touch_global_cursor(self, mock_resolve) -> None:
        mock_resolve.return_value = {"python3": "/usr/bin/python3", "npx": "/usr/local/bin/npx"}
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp) / "home"
            home.mkdir()
            project = Path(tmp) / "app"
            project.mkdir()
            install = Path(tmp) / "install"
            (install / "agile-backlog-toolkit" / "orchestrator_core").mkdir(parents=True)
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
                    enable_azure=True,
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
            "AGILE_BACKLOG_TOOLKIT_REPO": "file:///nonexistent-agile-backlog-toolkit",
            "AGILE_BACKLOG_TOOLKIT_REF": "main",
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
