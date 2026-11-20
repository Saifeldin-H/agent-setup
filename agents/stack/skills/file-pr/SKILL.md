---
name: file-pr
description: "File an authorized pull request. Use for an explicit request to open a PR, a spec with PR: file, or the filing stage of ship-pr."
---

# File PR

The user's `/ship-pr` invocation or direct request to open the PR authorizes opening it. The coordinator records `AUTHORIZED BY: user, <date>, /ship-pr <what>` in its own notes and copies it into the PR owner's spec if a worker is assigned. For a direct request, record the requested action in `<what>`. Use the recorded authorization without asking again. A worker filing the PR verifies that its spec records the user's authorization. Stop and report if authorization is missing.

1. Check whether the branch already has a PR. Inspect its target and state before reusing it. If GraphQL is exhausted, use the REST pulls list filtered by `head=owner:branch`.
2. Review the local diff against the intended base. Use the repo's branch naming, title, and PR template rules. Follow the repo's ticket and exemption rules.
3. Before drafting any GitHub text, read the target repo's `CLAUDE.md`, `AGENTS.md`, and `.claude/rules/*.md` that exist. This applies to PR titles and bodies, comments, review replies, and commit messages. Lead the PR description with the user's problem. Explain the change and report the verification in the template's sections. Write a concise title that describes the outcome.
4. Omit AI attribution and all AI or model mentions by default. Add attribution or a **Cross-vendor review** block only if the repo rules explicitly allow it and the user or spec asks for it. If the block is authorized, give the author and reviewer vendor and model, the rounds, and the verdict.
5. Check the title, body, quotes, and attachments for secrets and private details. File a regular PR by default. Use a draft if the spec or repo rules require one.

If `gh pr create` reports GraphQL rate exhaustion, recheck for an existing PR via REST before retrying. Create via REST using the same title, body, base, head, and draft choice. For a cross-repo branch, use `owner:branch` for the head.

```sh
gh api "repos/$repo/pulls" --method POST \
  -f "title=$title" -f "head=$head" -f "base=$base" \
  -F "body=@$body_file" -F "draft=$draft"
```

Verify the returned URL and target branch. Use `leaving-pr-comments` at `~/.agents/stack/skills/leaving-pr-comments/SKILL.md` if an authorized follow-up comment is needed. Hand monitoring to the designated owner via `babysit-pr` at `~/.agents/stack/skills/babysit-pr/SKILL.md`.

Never use `gh pr merge`, `--auto`, or `--admin`, even where the repo documents them for people.
