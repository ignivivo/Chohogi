from __future__ import annotations

import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
TOOL = ROOT / "tooling/verify-runtime-entrypoint.py"
T = "assets/agents/trunk_orchestration/"
FILES = ["hooks/hooks.json", "assets/runtime_entrypoint/AGENTS.md", T + "conductor.md", T + "branches_workflows/delivery.md",
         T + "branches_workflows/debugging.md", T + "task-loop.md", "skills/homeostasis/SKILL.md"]


def copy_tree(target: Path) -> None:
    for rel in FILES:
        (target / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / rel, target / rel)
    (target / "assets/agents").mkdir(parents=True, exist_ok=True)


def verify(root: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run([sys.executable, str(TOOL), "--root", str(root)], text=True, capture_output=True, check=False)


class RuntimeEntrypointTests(unittest.TestCase):
    def test_repository_passes(self) -> None:
        result = verify(ROOT)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_broken_hook_guidance_path_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_tree(root)
            hook = root / "hooks/hooks.json"
            hook.write_text(hook.read_text().replace("runtime_entrypoint/AGENTS.md", "runtime_entrypoint/AGENT.md"))
            result = verify(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("AGENT.md", result.stdout)

    def test_guidance_over_the_size_cap_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_tree(root)
            guidance = root / "assets/runtime_entrypoint/AGENTS.md"
            text = guidance.read_text()
            guidance.write_text(text.replace("<!-- chohogi:global-guidance:end -->", "가" * 4001 + "\n<!-- chohogi:global-guidance:end -->"))
            result = verify(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("size cap", result.stdout)

    def test_orchestration_documents_over_the_line_budget_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_tree(root)
            (root / "assets/agents/trunk_orchestration/new-policy.md").write_text("rule\n" * 3000, encoding="utf-8")
            result = verify(root)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("line budget", result.stdout)

    def test_retired_and_linked_skill_documents_do_not_count(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            copy_tree(root)
            retired = root / "assets/agents/genome_inheritance/retired_assets"
            retired.mkdir(parents=True)
            (retired / "old.md").write_text("rule\n" * 3000, encoding="utf-8")
            result = verify(root)
        self.assertEqual(result.returncode, 0, result.stdout)

    def test_each_removed_core_rule_anchor_fails(self) -> None:
        cases = [("assets/runtime_entrypoint/AGENTS.md", "실패하는 테스트를 먼저"),
                 ("assets/runtime_entrypoint/AGENTS.md", "완료 주장은 처리 방식과 무관하다"),
                 ("assets/runtime_entrypoint/AGENTS.md", "| 생각 | 실제 |"),
                 ("assets/runtime_entrypoint/AGENTS.md", "~/.agents/chohogi/trunk_orchestration/conductor.md"),
                 (T + "conductor.md", '"진입한다"는 해당 skill'),
                 (T + "branches_workflows/delivery.md", "실패하는 테스트를 먼저"),
                 (T + "branches_workflows/debugging.md", "네 번째 수정을 시도하지 않는다"),
                 (T + "task-loop.md", "## 최종 검토"),
                 ("skills/homeostasis/SKILL.md", "execution-record.py --project"),
                 ("skills/homeostasis/SKILL.md", "decide the smallest prevention first")]
        for rel, anchor in cases:
            with self.subTest(rel=rel, anchor=anchor), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                copy_tree(root)
                path = root / rel
                path.write_text(path.read_text().replace(anchor, "removed"))
                result = verify(root)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(rel, result.stdout)


if __name__ == "__main__":
    unittest.main()
