---
name: publish-safe-commit
description: Commits local changes with a safety-first workflow and publishes only allowlisted files to a separate public repository. Use when the user asks to commit current files, prepare a repo for GitHub Pages, or push sanitized content to a public mirror like the-cure-public.
disable-model-invocation: true
---

# Publish-Safe Commit

## Purpose

Use this skill to:
- commit work in the current repository without leaking secrets
- publish only safe files to a separate public repo (`the-cure-public`)
- keep private notes, internal logic, and sensitive artifacts out of public history

## Rules

1. Never publish everything by default.
2. Build a publish allowlist first, then copy only those files.
3. Treat markdown docs, scripts, and config files as sensitive until reviewed.
4. Abort publishing if any potential secret is detected.
5. Prefer adding a clean `dist/` or `public/` output to the public repo when available.

## Workflow

Copy this checklist and keep it updated:

```markdown
Task Progress:
- [ ] Step 1: Review repo state
- [ ] Step 2: Scan for secrets and sensitive files
- [ ] Step 3: Build publish allowlist
- [ ] Step 4: Commit private/source repo changes
- [ ] Step 5: Sync allowlisted files to `the-cure-public`
- [ ] Step 6: Verify public repo content and push
```

### Step 1: Review repo state

Run:

```bash
git status --short
git diff --stat
```

Report:
- staged and unstaged changes
- untracked files
- any obvious risky files

### Step 2: Scan for secrets and sensitive files

Run targeted checks before any commit or publish:

```bash
rg -n "(api[_-]?key|secret|token|password|private[_-]?key|BEGIN (RSA|OPENSSH|EC) PRIVATE KEY)" .
rg -n "(internal|confidential|do not share|private note)" "*.md"
```

Also check for files that should remain private:
- `.env*`
- `*.pem`, `*.p12`, `*.key`
- private certificates and credentials JSON
- internal-only planning docs

If anything is found, stop and ask whether to redact, remove, or keep private.

### Step 3: Build publish allowlist

Create an explicit allowlist for what can go public.

Default safe examples:
- static site output (`index.html`, `assets/`, `css/`, `js/`)
- intentionally public docs (`README.md`, selected `player-pack/` files)

Default deny examples:
- private dossiers not intended for release
- host notes, actor notes, internal scripts
- build tooling that reveals private process

Always ask the user to confirm the allowlist before syncing.

### Step 4: Commit private/source repo changes

After safety checks:

```bash
git add <approved-files>
git commit -m "<message>"
```

Use commit messages that explain why the change exists.

### Step 5: Sync allowlisted files to `the-cure-public`

Assume a sibling repo path:

```bash
../the-cure-public
```

If missing, ask the user for the public repo path.

Sync only allowlisted content, then check:

```bash
git -C ../the-cure-public status --short
git -C ../the-cure-public diff --stat
```

Never copy `.git`, `.env*`, credentials, or private notes.

### Step 6: Verify public repo content and push

Run final checks in `the-cure-public`:

```bash
git -C ../the-cure-public add <allowlisted-files>
git -C ../the-cure-public commit -m "<public publish message>"
git -C ../the-cure-public push -u origin HEAD
```

Confirm for the user:
- what was published
- what stayed private
- GitHub Pages readiness (entry file exists, paths valid)

## Output format

When using this skill, report with:

```markdown
## Publish Safety Report
- Private repo commit: <done/pending>
- Public repo sync: <done/pending>
- Secrets scan: <pass/fail>
- Published files: <list>
- Kept private: <list>
- Next step: <one action>
```
