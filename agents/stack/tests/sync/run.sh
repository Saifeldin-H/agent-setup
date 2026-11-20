#!/bin/bash
set -euo pipefail

backup="$HOME/Documents/ai-documents/agent-setup/backups/2026-11-19-agents"
sync="$HOME/.agents/bin/sync-agents"

fixture() (
    export HOME
    HOME=$(mktemp -d)
    trap 'rm -rf "$HOME"' EXIT
    cp -RP "$backup/agents" "$HOME/.agents"
    cp -RP "$backup/claude" "$HOME/.claude"
    cp -RP "$backup/codex" "$HOME/.codex"
    stack="$HOME/.agents/stack"
    claude="$HOME/.claude/skills"
    codex="$HOME/.agents/skills"
    ledger="$stack/.installed.json"
    for skill in alpha beta; do
        mkdir -p "$stack/skills/$skill"
        touch "$stack/skills/$skill/SKILL.md"
    done
    enabled='{"skills":{"alpha":{"claude":true,"codex":true},"beta":{"claude":true,"codex":true}}}'
    claude_only='{"skills":{"alpha":{"claude":true,"codex":false},"beta":{"claude":true,"codex":true}}}'
    disabled='{"skills":{"alpha":{"claude":false,"codex":false},"beta":{"claude":true,"codex":true}}}'
    manifest "$enabled"
    "$@"
    echo "PASS $1"
)

manifest() {
    printf '%s\n' "$1" > "$stack/stack.json"
}

run() {
    local expected=$1 actual=0
    shift
    output=$("$sync" "$@" 2>&1) || actual=$?
    if [[ "$actual" != "$expected" ]]; then
        printf 'Expected exit %s, got %s\n%s\n' "$expected" "$actual" "$output" >&2
        return 1
    fi
}

absent() {
    [[ ! -e "$1" && ! -L "$1" ]]
}

linked() {
    [[ "$(readlink "$1")" == "$stack/skills/$2" ]]
}

ledger_matches() {
    python3 - "$ledger" "$@" <<'PY'
import json
import os
import sys
from datetime import datetime
from pathlib import Path

ledger = Path(sys.argv[1])
expected = set(sys.argv[2:])
entries = json.loads(ledger.read_text())
assert len(entries) == len(expected), entries
for entry in entries:
    assert set(entry) == {"dest", "target", "vendor", "skill", "created_at"}, entry
    vendor, skill = entry["vendor"], entry["skill"]
    assert f"{vendor}/{skill}" in expected, entry
    expected.remove(f"{vendor}/{skill}")
    directory = {"claude": ".claude/skills", "codex": ".agents/skills"}[vendor]
    dest = Path.home() / directory / skill
    target = ledger.parent / "skills" / skill
    assert (entry["dest"], entry["target"]) == (str(dest), str(target)), entry
    assert os.readlink(dest) == str(target), entry
    assert datetime.fromisoformat(entry["created_at"]).tzinfo is not None, entry
PY
}

snapshot() {
    find "$HOME" \( -type f -o -type l -o -type d \) \
        -exec stat -f '%N %i %p %z %m %c' {} + | LC_ALL=C sort
}

fresh_install() {
    rm -rf "$HOME/.claude/agents"
    run 0
    ledger_matches claude/alpha codex/alpha claude/beta codex/beta
    [[ "$(readlink "$HOME/.codex/AGENTS.md")" == "$HOME/.claude/CLAUDE.md" ]]
    diff -r "$backup/claude/agents" "$HOME/.claude/agents"
}

already_correct() {
    run 0
    cp "$ledger" "$HOME/ledger.before"
    local before
    before=$(snapshot)
    run 0
    [[ $(snapshot) == "$before" ]]
    cmp "$HOME/ledger.before" "$ledger"
    run 0 --check
    [[ $(snapshot) == "$before" ]]
}

stale_link() {
    run 0
    rm "$claude/alpha"
    ln -s "$HOME/missing" "$claude/alpha"
    run 1 --check
    [[ "$output" == *"REFUSED alpha"* ]]
    run 1
    [[ "$(readlink "$claude/alpha")" == "$HOME/missing" ]]
}

missing_link() {
    run 0
    rm "$codex/alpha"
    run 1 --check
    [[ "$output" == *"MISSING $codex/alpha"* ]]
    run 0
    ledger_matches claude/alpha codex/alpha claude/beta codex/beta
}

real_directory() {
    mkdir "$claude/alpha"
    run 1
    [[ -d "$claude/alpha" && ! -L "$claude/alpha" ]]
    absent "$codex/alpha"
    ledger_matches claude/beta codex/beta
}

foreign_symlink() {
    ln -s "$stack/skills/beta" "$claude/alpha"
    run 1
    linked "$claude/alpha" beta
    absent "$codex/alpha"
}

digest_owned() {
    mkdir "$HOME/.agents/.orca-skill-digests/alpha"
    run 1
    [[ "$output" == *"Orca owns alpha"* ]]
    absent "$claude/alpha"
    absent "$codex/alpha"
}

second_vendor_collision() {
    touch "$codex/alpha"
    run 1
    absent "$claude/alpha"
    [[ -f "$codex/alpha" && ! -L "$codex/alpha" ]]
    ledger_matches claude/beta codex/beta
}

unowned_link() {
    ln -s "$stack/skills/alpha" "$claude/alpha"
    run 0
    [[ "$output" == *"unowned-ok $claude/alpha"* ]]
    ledger_matches codex/alpha claude/beta codex/beta
    manifest "$disabled"
    run 1
    [[ "$output" == *"DISABLED-LINK $claude/alpha"* ]]
    linked "$claude/alpha" alpha
    absent "$codex/alpha"
    ledger_matches claude/beta codex/beta
}

disabled_removal() {
    run 0
    manifest "$disabled"
    run 1 --check
    [[ "$output" == *"DISABLED-LINK $claude/alpha"* ]]
    ledger_matches claude/alpha codex/alpha claude/beta codex/beta
    run 1
    [[ "$output" == *"DISABLED-LINK $claude/alpha"* ]]
    absent "$claude/alpha"
    absent "$codex/alpha"
    ledger_matches claude/beta codex/beta
}

manual_disabled_link() {
    manifest "$claude_only"
    run 0
    ln -s "$stack/skills/alpha" "$codex/alpha"
    local before
    before=$(snapshot)
    run 1 --check
    [[ "$output" == *"DISABLED-LINK $codex/alpha"* ]]
    [[ $(snapshot) == "$before" ]]
    run 1
    [[ "$output" == *"DISABLED-LINK $codex/alpha"* ]]
    linked "$codex/alpha" alpha
    ledger_matches claude/alpha claude/beta codex/beta
}

disabled_directory() {
    manifest "$claude_only"
    mkdir "$codex/alpha"
    run 0
    [[ -d "$codex/alpha" && ! -L "$codex/alpha" ]]
    ledger_matches claude/alpha claude/beta codex/beta
    run 0 --check
}

gone_disabled_link() {
    run 0
    rm "$codex/alpha"
    manifest "$claude_only"
    cp "$ledger" "$HOME/ledger.before"
    run 0 --check
    [[ "$output" == *"gone    $codex/alpha"* ]]
    cmp "$ledger" "$HOME/ledger.before"
    run 0
    [[ "$output" == *"gone    $codex/alpha"* ]]
    ledger_matches claude/alpha claude/beta codex/beta
    run 0 --check
    [[ "$output" != *"gone    $codex/alpha"* ]]
}

replaced_disabled_link() {
    run 0
    rm "$codex/alpha"
    mkdir "$codex/alpha"
    manifest "$claude_only"
    cp "$ledger" "$HOME/ledger.before"
    run 1
    [[ "$output" == *"no longer matches its ledger entry"* ]]
    [[ -d "$codex/alpha" && ! -L "$codex/alpha" ]]
    cmp "$ledger" "$HOME/ledger.before"
}

removed_skill() {
    run 0
    manifest '{"skills":{"beta":{"claude":true,"codex":true}}}'
    run 0
    absent "$claude/alpha"
    absent "$codex/alpha"
    ledger_matches claude/beta codex/beta
}

repointed_disabled_link() {
    run 0
    cp "$ledger" "$HOME/ledger.before"
    rm "$claude/alpha"
    ln -s "../../.agents/stack/skills/alpha" "$claude/alpha"
    manifest "$disabled"
    run 1
    [[ "$(readlink "$claude/alpha")" == "../../.agents/stack/skills/alpha" ]]
    cmp "$HOME/ledger.before" "$ledger"
}

digest_owned_disabled_link() {
    run 0
    mkdir "$HOME/.agents/.orca-skill-digests/alpha"
    manifest "$disabled"
    run 1
    [[ "$output" == *"Orca owns alpha"* ]]
    ledger_matches claude/alpha codex/alpha claude/beta codex/beta
}

partial_failure_and_retry() {
    local actual=0
    output=$(python3 - "$sync" "$ledger" 2>&1 <<'PYTEST'
import errno
import functools
import os
import runpy
import sys

script, ledger = sys.argv[1:]
replace = os.replace
updates = 0

def fail_second_ledger_update(src, dest):
    global updates
    if os.fspath(dest) == ledger:
        updates += 1
        if updates == 2:
            raise OSError(errno.EIO, "fixture ledger update failure")
    return replace(src, dest)

os.replace = functools.partial(fail_second_ledger_update)
sys.argv = [script]
runpy.run_path(script, run_name="__main__")
PYTEST
    ) || actual=$?
    if [[ "$actual" != 1 || "$output" != *"fixture ledger update failure"* ]]; then
        printf 'Expected the second ledger write to fail. Got exit %s\n%s\n' "$actual" "$output" >&2
        return 1
    fi
    absent "$codex/alpha"
    ledger_matches claude/alpha claude/beta codex/beta
    cp "$ledger" "$HOME/ledger.before"
    run 0
    ledger_matches claude/alpha codex/alpha claude/beta codex/beta
    python3 - "$HOME/ledger.before" "$ledger" <<'PYTEST'
import json
import sys

with open(sys.argv[1]) as before, open(sys.argv[2]) as after:
    assert json.load(before) == json.load(after)[:3]
PYTEST
}

check_writes_nothing() {
    rm -rf "$HOME/.claude/agents" "$claude" "$codex"
    local before
    before=$(snapshot)
    run 1 --check
    [[ "$output" == *"MISSING $codex/alpha"* ]]
    [[ $(snapshot) == "$before" ]]
    absent "$ledger"
}

for test in fresh_install already_correct stale_link missing_link real_directory foreign_symlink \
    digest_owned second_vendor_collision manual_disabled_link disabled_directory gone_disabled_link \
    replaced_disabled_link unowned_link disabled_removal removed_skill repointed_disabled_link digest_owned_disabled_link partial_failure_and_retry check_writes_nothing; do
    fixture "$test"
done
