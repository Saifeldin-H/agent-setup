import json
import os
import shutil
import subprocess
import tempfile
from pathlib import Path

TEST_DIR = Path(__file__).resolve().parent
SCRIPTS = TEST_DIR.parents[1] / "skills" / "babysit-pr" / "scripts"
HEAD = "a" * 40
READY_COMMAND = [SCRIPTS / "ready-check", "example/demo", "7", HEAD]
WATCH_COMMAND = [SCRIPTS / "pr-wait", "7", "--repo", "example/demo", "--until", "green", "--interval", "5"]
FIELDS = {
    "class", "head", "state", "merged", "auto_merge", "checks", "merge_state",
    "unresolved_threads", "changes_requested", "bot_review",
}


def run(command, case, env, timeout=12):
    return subprocess.run(
        command,
        env={**env, "PR_FIXTURE": case},
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def assert_watch(env):
    try:
        proc = run(WATCH_COMMAND, "pending", env, timeout=2)
    except subprocess.TimeoutExpired:
        state = Path(env["HOME"]) / ".local/state/pr-wait/example__demo__7.json"
        assert state.is_file(), "pending watcher timed out before completing its first poll"
        print("PASS pr-wait pending (short timeout terminated a watcher with a saved baseline)")
    else:
        raise AssertionError(f"pending watcher exited early: {proc!r}")
    for case, code, event in [
        ("green", 0, "green on aaaaaaa"),
        ("failed", 1, "required check failed: build"),
        ("closed", 1, "closed without merging"),
        ("merged", 0, "merged: https://"),
    ]:
        proc = run(WATCH_COMMAND, case, env)
        assert proc.returncode == code and event in proc.stdout, (case, proc)
        print(f"PASS pr-wait {case} (exit {code})")


def assert_ready(env):
    for case, code, classification, fields in [
        ("green", 0, "READY", {
            "head": HEAD, "state": "OPEN", "merged": False, "auto_merge": None,
            "checks": {"build (app 10)": "green", "lint": "green"}, "merge_state": "CLEAN",
            "unresolved_threads": 0, "changes_requested": [],
            "bot_review": {"copilot-pull-request-reviewer[bot]": "CHANGES_REQUESTED"},
        }),
        ("neutral", 0, "READY", {}),
        ("no-required", 0, "READY", {"checks": {"build": "green", "lint": "green", "test": "green"}}),
        ("no-required-empty", 1, "CHECK_PENDING", {"checks": {}}),
        ("no-required-failed-run", 1, "CHECK_FAILED", {"checks": {"build": "green", "lint": "green", "test": "failed"}}),
        ("no-required-failed-status", 1, "CHECK_FAILED", {"checks": {"build": "green", "lint": "failed", "test": "green"}}),
        ("no-required-pending-status", 1, "CHECK_PENDING", {"checks": {"build": "green", "lint": "pending", "test": "green"}}),
        ("pending", 1, "CHECK_PENDING", {}),
        ("missing", 1, "CHECK_PENDING", {}),
        ("failed", 1, "CHECK_FAILED", {"checks": {"build (app 10)": "failed", "lint": "green"}}),
        ("status-failed", 1, "CHECK_FAILED", {"checks": {"build (app 10)": "green", "lint": "failed"}}),
        ("merged", 1, "MERGED", {"merged": True, "state": "MERGED"}),
        ("closed", 1, "CLOSED", {"merged": False, "state": "CLOSED"}),
        ("head", 1, "HEAD_CHANGED", {"head": "b" * 40}),
        ("race", 1, "HEAD_CHANGED", {"head": "b" * 40, "checks": None}),
        ("auto", 1, "AUTO_MERGE_ON", {"auto_merge": {"merge_method": "squash"}}),
        ("graph-auto", 1, "AUTO_MERGE_ON", {"auto_merge": {"enabledAt": "2026-11-19T09:00:00Z"}}),
        ("queue-flag", 1, "IN_MERGE_QUEUE", {"auto_merge": None}),
        ("queue-entry", 1, "IN_MERGE_QUEUE", {"auto_merge": None}),
        ("draft", 1, "DRAFT", {"state": "OPEN"}),
        ("behind", 1, "BEHIND", {"merge_state": "BEHIND"}),
        ("conflict", 1, "CONFLICT", {"merge_state": "DIRTY"}),
        ("thread", 1, "UNRESOLVED_THREADS", {"unresolved_threads": 1}),
        ("changes", 1, "CHANGES_REQUESTED", {"changes_requested": ["reviewer"]}),
        ("old-changes", 1, "CHANGES_REQUESTED", {"changes_requested": ["reviewer"]}),
        ("approved-later", 0, "READY", {"changes_requested": []}),
        ("commented-later", 1, "CHANGES_REQUESTED", {"changes_requested": ["reviewer"]}),
        ("more-threads", 1, "API_ERROR", {"unresolved_threads": None}),
        ("unknown", 1, "API_ERROR", {"merge_state": "UNKNOWN"}),
        ("error", 1, "API_ERROR", {}),
        ("rest-error", 1, "API_ERROR", {}),
    ]:
        proc = run(READY_COMMAND, case, env)
        assert proc.returncode == code, (case, proc)
        assert len(proc.stdout.splitlines()) == 1, (case, proc)
        result = json.loads(proc.stdout)
        assert result.keys() == FIELDS, (case, result)
        assert result["class"] == classification, (case, result)
        for field, value in fields.items():
            assert result[field] == value, (case, field, result)
        print(f"PASS ready-check {case} (exit {code}, {classification})")

    for case, code, classification in [
        ("green", 0, "OPEN"), ("auto", 0, "OPEN"), ("closed", 1, "CLOSED"),
        ("merged", 1, "MERGED"), ("head", 1, "HEAD_CHANGED"),
    ]:
        proc = run([*READY_COMMAND, "--preflight"], case, env)
        assert proc.returncode == code and json.loads(proc.stdout)["class"] == classification, proc
        print(f"PASS ready-check --preflight {case} (exit {code}, {classification})")
    proc = run([*READY_COMMAND[:-1], "bad-sha"], "green", env)
    assert proc.returncode == 2 and json.loads(proc.stdout)["class"] == "BAD_INPUT", proc
    print("PASS ready-check bad input (exit 2)")


def main():
    with tempfile.TemporaryDirectory(prefix=".offline-", dir=TEST_DIR) as directory:
        scratch = Path(directory)
        bin_dir = scratch / "bin"
        bin_dir.mkdir()
        shutil.copy(TEST_DIR / "gh", bin_dir / "gh").chmod(0o755)
        # A private PATH prevents any fallback to a real gh. The tested scripts
        # and fake gh all use /usr/bin/env python3.
        python = shutil.which("python3")
        assert python is not None
        (bin_dir / "python3").symlink_to(python)
        env = {
            "HOME": directory,
            "PATH": str(bin_dir),
            "PYTHONUNBUFFERED": "1",
        }
        assert_ready(env)
        assert_watch(env)


if __name__ == "__main__":
    main()
