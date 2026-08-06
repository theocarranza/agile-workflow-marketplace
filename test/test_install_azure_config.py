import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.install import (
    AZURE_MCP_PACKAGE,
    azure_mcp_launch,
    ensure_azure_mcp_installed,
    parse_args,
    write_cursor_azure_wrapper,
    write_project_config,
)


class TestAzureMcpLaunch(unittest.TestCase):
    """How the Azure DevOps MCP server gets started."""

    def test_pinned_entrypoint_is_preferred(self):
        """A pinned node invocation avoids npx resolution and PATH breakage."""
        command, args = azure_mcp_launch(
            azure_org="my-org",
            node_path="/usr/local/bin/node",
            npx_path="/usr/local/bin/npx",
            entrypoint=Path("/home/u/.local/share/azure-devops-mcp/dist/index.js"),
        )
        self.assertEqual(command, "/usr/local/bin/node")
        self.assertEqual(args[-1], "my-org")
        self.assertTrue(args[0].endswith("index.js"))

    def test_falls_back_to_npx_without_entrypoint(self):
        """No pinned install means npx, which still works."""
        command, args = azure_mcp_launch(
            azure_org="my-org", node_path="/usr/local/bin/node", npx_path="/usr/bin/npx", entrypoint=None
        )
        self.assertEqual(command, "/usr/bin/npx")
        self.assertEqual(args, ["-y", AZURE_MCP_PACKAGE, "my-org"])

    def test_falls_back_to_npx_without_node(self):
        """A pinned entrypoint is useless without a node to run it."""
        command, _ = azure_mcp_launch(
            azure_org="o", node_path=None, npx_path="/usr/bin/npx", entrypoint=Path("/x/index.js")
        )
        self.assertEqual(command, "/usr/bin/npx")

    def test_org_is_always_the_trailing_argument(self):
        """Both forms put the org last, which is what the config reader relies on."""
        for entrypoint in (None, Path("/x/index.js")):
            _, args = azure_mcp_launch(
                azure_org="trailing", node_path="/n", npx_path="/npx", entrypoint=entrypoint
            )
            self.assertEqual(args[-1], "trailing")

    def test_install_is_skipped_when_npm_is_absent(self):
        """Without npm there is nothing to install, and that is not an error."""
        with patch("scripts.install.azure_mcp_entrypoint", return_value=None):
            self.assertIsNone(ensure_azure_mcp_installed(npm_path=None))

    def test_existing_install_is_reused_without_running_npm(self):
        """A pinned install already present must not trigger a network call."""
        marker = Path("/already/installed/index.js")
        with patch("scripts.install.azure_mcp_entrypoint", return_value=marker):
            with patch("scripts.install.subprocess.run") as run:
                self.assertEqual(ensure_azure_mcp_installed(npm_path="/usr/bin/npm"), marker)
                run.assert_not_called()

    def test_install_failure_degrades_to_none(self):
        """A failed npm install falls back to npx rather than aborting the installer."""
        with patch("scripts.install.azure_mcp_entrypoint", return_value=None):
            with patch("scripts.install.subprocess.run", side_effect=OSError("boom")):
                self.assertIsNone(ensure_azure_mcp_installed(npm_path="/usr/bin/npm", quiet=True))


class TestCursorWrapper(unittest.TestCase):
    """The PATH-sanitising wrapper Cursor needs."""

    def test_wrapper_uses_pinned_entrypoint_when_available(self):
        """Cursor gets the same pinned launch as every other host."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script = write_cursor_azure_wrapper(
                Path(tmpdir),
                azure_org="my-org",
                npx_path="/usr/bin/npx",
                node_path="/usr/local/bin/node",
                entrypoint=Path("/x/dist/index.js"),
            )
            body = script.read_text(encoding="utf-8")
            self.assertIn("/usr/local/bin/node", body)
            self.assertIn("/x/dist/index.js", body)
            self.assertIn("my-org", body)

    def test_wrapper_falls_back_to_npx(self):
        """Without a pinned install the wrapper still works via npx."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script = write_cursor_azure_wrapper(
                Path(tmpdir), azure_org="my-org", npx_path="/usr/bin/npx"
            )
            body = script.read_text(encoding="utf-8")
            self.assertIn("/usr/bin/npx", body)
            self.assertIn(AZURE_MCP_PACKAGE, body)

    def test_wrapper_sanitises_the_environment(self):
        """The leaked Electron variable is what breaks stdio servers under Cursor."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script = write_cursor_azure_wrapper(Path(tmpdir), azure_org="o", npx_path="/usr/bin/npx")
            body = script.read_text(encoding="utf-8")
            self.assertTrue("ELECTRON_RUN_AS_NODE" in body or "cursor-mcp-env.sh" in body)

    def test_wrapper_is_executable(self):
        """A wrapper that cannot be executed is no wrapper at all."""
        with tempfile.TemporaryDirectory() as tmpdir:
            script = write_cursor_azure_wrapper(Path(tmpdir), azure_org="o", npx_path="/usr/bin/npx")
            self.assertTrue(script.stat().st_mode & 0o111)


class TestWriteProjectConfig(unittest.TestCase):
    """The runtime config the installer now writes."""

    def test_writes_org_and_artifacts_path(self):
        """The minimum an install can know."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_project_config(
                Path(tmpdir),
                provider_mode="azure",
                azure_org="my-org",
                azure_project=None,
                azure_team=None,
                azure_process=None,
                artifacts_path="docs/backlog",
            )
            data = json.loads(path.read_text(encoding="utf-8"))
            self.assertEqual(data["azure"]["org"], "my-org")
            self.assertEqual(data["artifacts_path"], "docs/backlog")
            self.assertNotIn("project", data["azure"])

    def test_writes_optional_fields_when_supplied(self):
        """Flags supplied at install time are persisted."""
        with tempfile.TemporaryDirectory() as tmpdir:
            path = write_project_config(
                Path(tmpdir),
                provider_mode="azure",
                azure_org="o",
                azure_project="p",
                azure_team="t",
                azure_process="scrum",
                artifacts_path="docs",
            )
            azure = json.loads(path.read_text(encoding="utf-8"))["azure"]
            self.assertEqual((azure["project"], azure["team"], azure["process"]), ("p", "t", "scrum"))

    def test_reinstall_preserves_lazily_filled_values(self):
        """Re-running the installer must not wipe a team discovered later."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_project_config(
                root, provider_mode="azure", azure_org="o", azure_project="p", azure_team="t",
                azure_process=None, artifacts_path="docs",
            )
            write_project_config(
                root, provider_mode="azure", azure_org="o", azure_project=None, azure_team=None,
                azure_process=None, artifacts_path="docs",
            )
            azure = json.loads((root / ".agile-backlog-toolkit" / "config.json").read_text(encoding="utf-8"))["azure"]
            self.assertEqual(azure["project"], "p")
            self.assertEqual(azure["team"], "t")

    def test_malformed_existing_file_is_replaced_not_fatal(self):
        """A corrupt config must not stop an install."""
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            path = root / ".agile-backlog-toolkit" / "config.json"
            path.parent.mkdir(parents=True)
            path.write_text("{broken", encoding="utf-8")
            written = write_project_config(
                root, provider_mode="azure", azure_org="o", azure_project=None, azure_team=None,
                azure_process=None, artifacts_path="docs",
            )
            self.assertEqual(json.loads(written.read_text(encoding="utf-8"))["azure"]["org"], "o")

    def test_output_matches_what_the_resolver_reads(self):
        """The installer and the runtime must agree on the schema."""
        from orchestrator_core.project_config import load_project_config

        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir)
            write_project_config(
                root, provider_mode="azure", azure_org="o", azure_project="p", azure_team="t",
                azure_process="agile", artifacts_path="docs",
            )
            config = load_project_config(root)
            self.assertEqual(config.artifacts_path, "docs")
            self.assertEqual(config.azure.org, "o")
            self.assertEqual(config.azure.team, "t")
            self.assertTrue(config.azure_ready)


class TestInstallerArgs(unittest.TestCase):
    """New command-line flags."""

    def test_azure_flags_are_accepted(self):
        """All four Azure values can be supplied non-interactively."""
        args = parse_args(
            [
                "--azure-org", "o",
                "--azure-project", "p",
                "--azure-team", "t",
                "--azure-process", "scrum",
            ]
        )
        self.assertEqual(args.azure_project, "p")
        self.assertEqual(args.azure_team, "t")
        self.assertEqual(args.azure_process, "scrum")

    def test_optional_azure_flags_default_to_none(self):
        """Omitting them leaves them for lazy fill."""
        args = parse_args(["--azure-org", "o"])
        self.assertIsNone(args.azure_project)
        self.assertIsNone(args.azure_team)

    def test_process_choices_are_constrained(self):
        """An invalid process is rejected at parse time."""
        with self.assertRaises(SystemExit):
            parse_args(["--azure-process", "kanban"])


if __name__ == "__main__":
    unittest.main()
