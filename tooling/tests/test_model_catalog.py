#!/usr/bin/env python3
"""Tests for the bounded Codex runtime model-catalog adapter."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/model-catalog.py"


class ModelCatalogTests(unittest.TestCase):
    def fake_codex(self, directory: Path, payload: object, exit_code: int = 0) -> Path:
        executable = directory / "fake-codex"
        output = json.dumps(payload)
        executable.write_text(
            "#!/usr/bin/env python3\n"
            "import sys\n"
            "if sys.argv[1:] != ['debug', 'models']:\n"
            "    raise SystemExit(97)\n"
            f"print({output!r})\n"
            f"raise SystemExit({exit_code})\n",
            encoding="utf-8",
        )
        executable.chmod(0o755)
        return executable

    def run_tool(self, *arguments: str, env: dict[str, str] | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run([sys.executable, str(TOOL), *arguments], cwd=ROOT, env=env, text=True, capture_output=True, check=False)

    def test_projects_only_selectable_model_names_and_reasoning_efforts(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            executable = self.fake_codex(directory, {"models": [
                {"slug": "gpt-6-luna", "display_name": "GPT-6 Luna", "visibility": "list", "default_reasoning_level": "xhigh", "supported_reasoning_levels": [{"effort": "low", "description": "ignore this"}, {"effort": "xhigh", "description": "ignore this too"}], "model_messages": {"persistent_instructions": "ignore these instructions"}},
                {"slug": "internal-hidden", "display_name": "Hidden", "visibility": "hide", "supported_reasoning_levels": [{"effort": "ultra"}]},
            ]})
            result = self.run_tool("codex", "--binary", str(executable))
        self.assertEqual(result.returncode, 0, result.stderr)
        card = json.loads(result.stdout)
        self.assertEqual(card["provider"], "codex-binary-override")
        self.assertTrue(card["requiresUserConfirmation"])
        self.assertEqual(card["models"], [{"id": "gpt-6-luna", "name": "GPT-6 Luna", "reasoningEfforts": ["low", "xhigh"], "defaultReasoningEffort": "xhigh"}])
        self.assertNotIn("ignore", result.stdout)
        self.assertNotIn("internal-hidden", result.stdout)

    def test_prefers_official_vscode_extension_binary_over_path_codex(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            extension = home / ".vscode-server/extensions/openai.chatgpt-test/bin/linux"
            extension.mkdir(parents=True)
            self.fake_codex(extension, {"models": [{"slug": "extension-model", "display_name": "Extension Model", "visibility": "list", "supported_reasoning_levels": [{"effort": "medium"}]}]}).rename(extension / "codex")
            path_dir = home / "bin"
            path_dir.mkdir()
            path_binary = self.fake_codex(path_dir, {"models": [{"slug": "path-model", "display_name": "Path Model", "visibility": "list", "supported_reasoning_levels": [{"effort": "low"}]}]})
            path_value = str(path_dir) + os.pathsep + os.environ.get("PATH", "")
            result = self.run_tool("codex", env={**os.environ, "HOME": str(home), "PATH": path_value})
        self.assertEqual(result.returncode, 0, result.stderr)
        card = json.loads(result.stdout)
        self.assertEqual(card["provider"], "codex-vscode-runtime")
        self.assertEqual(card["models"][0]["id"], "extension-model")

    def test_rejects_invalid_or_empty_catalog(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            executable = self.fake_codex(directory, {"models": [{"slug": "x", "visibility": "list", "supported_reasoning_levels": [{"effort": "bogus"}]}]})
            result = self.run_tool("codex", "--binary", str(executable))
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("invalid", result.stderr.lower())

    def test_reports_runtime_failure_without_leaking_raw_output(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            executable = self.fake_codex(directory, {"models": []}, exit_code=1)
            result = self.run_tool("codex", "--binary", str(executable))
        self.assertNotEqual(result.returncode, 0)
        self.assertNotIn('"models"', result.stderr)


if __name__ == "__main__":
    unittest.main()
