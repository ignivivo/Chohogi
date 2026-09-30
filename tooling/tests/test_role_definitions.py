from __future__ import annotations

import json
import re
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[2]
TOML_DIR = ROOT / "assets/runtime_entrypoint/agents"
CLAUDE_DIR = ROOT / "agents"
RECOMMENDATIONS = ROOT / "assets/agents/trunk_orchestration/model-recommendations.json"
CARD_ROLES = ("scout", "implementer", "task-reviewer", "final-reviewer", "debugger")
EFFORTS = {"low", "medium", "high", "xhigh", "max"}


def normalized(text: str) -> str:
    return " ".join(text.split())


def toml_role(path: Path) -> dict[str, str]:
    text = path.read_text(encoding="utf-8")
    fields = dict(re.findall(r'^(\w+) = "([^"\n]*)"$', text, re.M))
    body = re.search(r'developer_instructions = """(.*?)"""', text, re.S)
    fields["developer_instructions"] = body.group(1) if body else ""
    return fields


def claude_role(path: Path) -> tuple[dict[str, str], str]:
    _, front, body = path.read_text(encoding="utf-8").split("---", 2)
    fields = dict(line.split(": ", 1) for line in front.strip().splitlines())
    return fields, body


class RoleDefinitionTests(unittest.TestCase):
    def test_every_codex_role_has_a_matching_claude_mirror(self) -> None:
        tomls = sorted(TOML_DIR.glob("*.toml"))
        self.assertTrue(tomls)
        for path in tomls:
            mirror = CLAUDE_DIR / (path.stem + ".md")
            self.assertTrue(mirror.is_file(), f"{mirror} mirrors {path}")
            source = toml_role(path)
            fields, body = claude_role(mirror)
            self.assertEqual(fields["name"], path.stem)
            self.assertTrue(fields["description"].startswith(source["description"]), path.stem)
            self.assertEqual(normalized(body), normalized(source["developer_instructions"]), path.stem)
        self.assertEqual({p.stem for p in CLAUDE_DIR.glob("*.md")}, {p.stem for p in tomls})

    def test_claude_roles_cover_every_profile_role(self) -> None:
        role_agent = json.loads(RECOMMENDATIONS.read_text(encoding="utf-8"))["hosts"]["claude"]["roleAgent"]
        self.assertEqual(set(role_agent), set(CARD_ROLES))
        for role, agent in role_agent.items():
            self.assertTrue((CLAUDE_DIR / f"{agent}.md").is_file(), role)

    def test_claude_role_frontmatter_is_deliverable(self) -> None:
        aliases = json.loads(RECOMMENDATIONS.read_text(encoding="utf-8"))["hosts"]["claude"]["deliveryAlias"]
        for path in sorted(CLAUDE_DIR.glob("*.md")):
            fields, body = claude_role(path)
            self.assertIn(fields.get("model"), aliases, f"{path.stem}: model must be an exact, known id")
            effort = fields.get("effort")
            if fields["model"].startswith("claude-haiku-"):
                self.assertIsNone(effort, f"{path.stem}: Haiku does not take effort")
            else:
                self.assertIn(effort, EFFORTS, path.stem)
            self.assertNotIn("does not impose one", body, f"{path.stem}: body must not deny the frontmatter placement")


if __name__ == "__main__":
    unittest.main()
