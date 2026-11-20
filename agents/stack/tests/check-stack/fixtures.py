"""Run the validator against one valid stack and isolated regressions."""

import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path


SKILLS = ["file-pr", "leaving-pr-comments", "babysit-pr", "ship-pr", "blast-radius", "ste"]
REQUIRES = {
    "roles/planner.md": ["principles.md", "## Plan", "ste"],
    "roles/architect.md": ["principles.md", "## Plan", "## Review", "blast-radius"],
    "roles/plan-checker.md": ["principles.md", "## Plan"],
    "roles/implementer.md": ["principles.md", "## Build", "babysit-pr", "file-pr"],
    "roles/adversarial-reviewer.md": ["principles.md", "## Review", "blast-radius"],
    "~/.claude/CLAUDE.md": ["/ship-pr", "file-pr", "babysit-pr"],
    "~/.claude/skills/pr-review-master/SKILL.md": ["ste", "leaving-pr-comments"],
    "stack/skills/ship-pr/SKILL.md": ["file-pr", "babysit-pr", "leaving-pr-comments"],
    "stack/skills/babysit-pr/SKILL.md": ["leaving-pr-comments", "scripts/pr-wait", "scripts/ready-check"],
    "stack/skills/file-pr/SKILL.md": ["leaving-pr-comments"],
    "stack/skills/blast-radius/SKILL.md": ["ste"],
}
PRINCIPLES = """## Plan
principle-foundational-thinking
principle-sequence-verifiable-units
principle-subtract-before-you-add
principle-laziness-protocol
principle-migrate-callers-then-delete-legacy-apis
principle-make-operations-idempotent
principle-separate-before-serializing-shared-state
## Build
principle-prove-it-works
principle-fix-root-causes
principle-test-behavior-not-implementation
principle-boundary-discipline
principle-type-system-discipline
tdd
## Review
principle-attack-the-premise
principle-minimize-reader-load
principle-explain-the-number
principle-test-behavior-not-implementation
"""
MERGE_COMMAND = " ".join(("gh", "pr", "merge"))
FORBIDDEN_SENTENCE = f"If the status changes, {MERGE_COMMAND}.\n"
PROHIBITIONS = {
    "bold prohibition": f"- **Never** run {MERGE_COMMAND}",
    "quoted prohibition": "> Never use --admin",
    "nested prohibition": f"> 2. _Do not_ use {MERGE_COMMAND}",
}
FORBIDDEN_LINES = {
    "negative preface before command": f"Do not stop: if checks pass, {MERGE_COMMAND} --squash --auto",
    "semicolon after prohibition": f"Never stop; use {MERGE_COMMAND}",
    "conditional prohibition": f"Do not stop if checks pass, use {MERGE_COMMAND}",
    "REST merge path": "Use the endpoint /repos/o/r/pulls/N/merge",
    "GraphQL enable auto-merge": "Use enablePullRequestAutoMerge",
    "GraphQL enqueue": "Use enqueuePullRequest",
    "GraphQL merge": "Use mergePullRequest",
}
NEGATIVES = {
    "missing reference": "missing required reference ste",
    "nonexistent skill token": "nonexistent skill token unknown-skill",
    "missing principle entry": "Plan must contain exactly",
    "principle citation only": "has no guidance",
    "wrong vendor flag": "manifest vendor flags",
    "forbidden sentence": "forbidden token outside a prohibition",
    "malformed frontmatter": "malformed YAML frontmatter",
    "pr-wait byte change": "pr-wait differs",
    "missing vendor link": "ste is not installed for codex",
    "disabled vendor link": "DISABLED-LINK",
    **{name: "forbidden token outside a prohibition" for name in FORBIDDEN_LINES},
}


def document(home, name):
    return home / (name[2:] if name.startswith("~/") else ".agents/" + name)


def write(path, text):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)


def fixture(home, case):
    stack = home / ".agents/stack"
    for name, tokens in REQUIRES.items():
        write(document(home, name), "\n".join(tokens) + "\n")
    manifest = {
        "skills": {skill: {"claude": True, "codex": skill != "ship-pr"} for skill in SKILLS},
        "requires": {path: tokens.copy() for path, tokens in REQUIRES.items()},
    }

    for skill, flags in manifest["skills"].items():
        target = stack / "skills" / skill
        path = target / "SKILL.md"
        body = path.read_text() if path.exists() else ""
        metadata = f"---\nname: {skill}\ndescription: >-\n  Fixture for {skill}.\n"
        if skill == "ship-pr":
            metadata += "disable-model-invocation: true\n"
        write(path, metadata + "---\n\n" + body)
        for directory, vendor in ((".claude/skills", "claude"), (".agents/skills", "codex")):
            if flags[vendor]:
                dest = home / directory / skill
                dest.parent.mkdir(parents=True, exist_ok=True)
                dest.symlink_to(target)

    principles = "".join(
        f"{line}\n" if line.startswith("## ") else
        f"### {line}\nTest guidance.\nSource `pstack/skills/{line}/SKILL.md`.\n"
        for line in PRINCIPLES.splitlines()
    )
    write(stack / "principles.md", principles)
    for name in ("pr-wait", "ready-check"):
        path = stack / "skills/babysit-pr/scripts" / name
        write(path, "#!/bin/sh\nexit 0\n")
        path.chmod(0o755)
    write(stack / "upstream/tstack/skills/babysit-pr/scripts/pr-wait", "#!/bin/sh\nexit 0\n")
    for scope in ("upstream", "bin", "tests"):
        write(stack / scope / "excluded.md", FORBIDDEN_SENTENCE)
    write(home / ".agents/common.md", f"- Never use `{MERGE_COMMAND}`.\n2. Do not use --admin.\n")

    planner = document(home, "roles/planner.md")
    if case == "missing reference":
        planner.write_text(planner.read_text().replace("ste\n", "next step\n"))
    elif case == "nonexistent skill token":
        planner.write_text(planner.read_text() + "unknown-skill\n")
        manifest["requires"]["roles/planner.md"].append("unknown-skill")
    elif case == "missing principle entry":
        name = "principle-foundational-thinking"
        (stack / "principles.md").write_text(principles.replace(
            f"### {name}\nTest guidance.\nSource `pstack/skills/{name}/SKILL.md`.\n", ""
        ))
    elif case == "principle citation only":
        (stack / "principles.md").write_text(principles.replace("Test guidance.\n", "", 1))
    elif case == "wrong vendor flag":
        manifest["skills"]["ship-pr"]["codex"] = True
    elif case == "forbidden sentence":
        planner.write_text(planner.read_text() + FORBIDDEN_SENTENCE)
    elif case == "malformed frontmatter":
        path = stack / "skills/ste/SKILL.md"
        path.write_text("---\nname: ste\ndescription: [unterminated\n---\n")
    elif case == "pr-wait byte change":
        (stack / "skills/babysit-pr/scripts/pr-wait").write_text("#!/bin/sh\nexit 1\n")
    elif case == "missing vendor link":
        (home / ".agents/skills/ste").unlink()
    elif case == "disabled vendor link":
        (home / ".agents/skills/ship-pr").symlink_to(stack / "skills/ship-pr")
        manifest["requires"]["~/.claude/CLAUDE.md"].remove("/ship-pr")
    elif case in PROHIBITIONS or case in FORBIDDEN_LINES:
        line = (PROHIBITIONS | FORBIDDEN_LINES)[case]
        planner.write_text(planner.read_text() + line + "\n")
    write(stack / "stack.json", json.dumps(manifest))


def main():
    for case in ["passing stack", *PROHIBITIONS, *NEGATIVES]:
        with tempfile.TemporaryDirectory() as directory:
            fixture(Path(directory), case)
            result = subprocess.run(
                [sys.argv[1]], env={**os.environ, "HOME": directory},
                capture_output=True, text=True,
            )
            expected = int(case in NEGATIVES)
            if result.returncode != expected or NEGATIVES.get(case, "") not in result.stderr:
                raise AssertionError(
                    f"{case}: expected exit {expected}, got {result.returncode}\n"
                    f"{result.stdout}{result.stderr}"
                )
            print(f"PASS {case} (exit {result.returncode})")


if __name__ == "__main__":
    main()
