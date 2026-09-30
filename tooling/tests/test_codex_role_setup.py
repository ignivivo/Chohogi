import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling" / "codex-role-setup.py"
ROLE_DIR = ROOT / "assets" / "runtime_entrypoint" / "agents"
CANONICAL = {path.stem.replace("-", "_"): path for path in ROLE_DIR.glob("*.toml")}


def run(config: Path, *extra: str) -> subprocess.CompletedProcess:
    return subprocess.run([sys.executable, str(TOOL), "--config", str(config), *extra], text=True, capture_output=True)


class CodexRoleSetupTests(unittest.TestCase):
    def test_apply_is_idempotent_and_registers_all_canonical_roles(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            config.write_text('model = "gpt-5.6-luna"\n')
            self.assertEqual(run(config, "--apply").returncode, 0)
            first = config.read_text()
            self.assertEqual(run(config, "--apply").returncode, 0)
            self.assertEqual(first, config.read_text())
            for role in ("critical_reviewer", "evidence_scout", "implementation_worker", "final_reviewer", "debugger"):
                self.assertIn(f"[agents.{role}]", first)

    def test_registers_every_role_file_in_the_canonical_directory(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            config.write_text("")
            run(config, "--apply")
            text = config.read_text()
            for role, path in CANONICAL.items():
                self.assertIn(f"[agents.{role}]\nconfig_file = \"{path}\"", text)

    def test_reports_a_registration_that_points_away_from_the_canonical_file(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            blocks = [f'[agents.{role}]\nconfig_file = "{path}"\n' for role, path in CANONICAL.items() if role != "debugger"]
            blocks.append('[agents.debugger]\nconfig_file = "/old/place/debugger.toml"\n')
            config.write_text("\n".join(blocks))
            before = config.read_text()
            check = run(config)
            self.assertEqual(check.returncode, 1)
            self.assertIn("WRONG_PATH debugger", check.stdout)
            applied = run(config, "--apply")
            self.assertEqual(applied.returncode, 1, "apply must not silently rewrite a user's existing entry")
            self.assertEqual(config.read_text(), before)

    def test_apply_backs_up_the_config_before_writing(self):
        with tempfile.TemporaryDirectory() as directory:
            config = Path(directory) / "config.toml"
            config.write_text('model = "gpt-5.6-luna"\n')
            run(config, "--apply")
            backups = list(Path(directory).glob("config.toml.chohogi-backup-*"))
            self.assertEqual(len(backups), 1)
            self.assertEqual(backups[0].read_text(), 'model = "gpt-5.6-luna"\n')


if __name__ == "__main__":
    unittest.main()
