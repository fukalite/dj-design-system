---
name: complete-work
description: "Orchestrates completing a piece of work: enforces main branch safety, prompts for draft PR preference, commits work, executes /code-review, iterates with local gemini-reviewer, opens a PR, monitors CI, and resolves remote review comments until all green."
---

# Complete Work Skill

You orchestrate the completion, auditing, and delivery of a piece of work into a GitHub Pull Request. You enforce strict branch protection, execute dual-layer code reviews (local refactoring + local auditor), create/update the PR, and iterate on CI and remote review comments until all checks are green.

---

## 1. Main Branch Protection & Base Resolution (CRITICAL)

**Never commit or push directly to `main` at all costs.**

Before staging or committing any files:
1. Inspect the current branch: `git branch --show-current`.
2. **If on `main`**:
   - Check if the user specified a branch to stack/chain onto. If so, branch off that target: `git checkout -b <feature-branch> <target-branch>`.
   - Otherwise, default to branching off the latest `origin/main`:
     ```bash
     git fetch origin main && git checkout -b feat/<descriptive-name> origin/main
     ```
3. **If already on a feature branch / PR**:
   - Confirm you are working into the intended PR branch.
4. **Push Safeguard**:
   - Always push feature branches with explicit refspecs (`git push -u origin <branch>:<branch>`) so that Git's `push.default = upstream` never inadvertently pushes commits to `main`.

---

## 2. Interactive Draft PR Preference Gate

Before launching any review subagents or creating commits, prompt the user for their PR preference using `ask_question`:

- **Question**: "Should the Pull Request be created as a Draft PR?"
- **Options**:
  - `(Recommended) Create as Draft PR`
  - `Create as Ready for Review PR`

Store the user's preference to determine flags for `gh pr create` and whether a manual `/review` comment trigger is required.

---

## 3. Step 1: Initial Commit

1. Run pre-commit quality gates:
   - `export PATH="$HOME/.asdf/shims:$PATH" && just check`
   - `export PATH="$HOME/.asdf/shims:$PATH" && just test`
2. Clean untracked generated build artifacts if present:
   - `git clean -f dj_design_system/components/` (compiled `.js` files)
3. Stage changes and create the initial commit:
   ```bash
   git add <modified-files>
   git commit -m "<type>(<scope>): <concise description of work>"
   ```

---

## 4. Step 2: Code Review Skill Execution (`/code-review`)

Run the `/code-review` workflow to audit code against project styleguides and apply standard refactors:
1. Inspect the touched files against:
   - [layered-architecture.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/layered-architecture.md)
   - [dds-components.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/dds-components.md)
   - [general.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/general.md)
   - [python.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/python.md)
   - [html-css.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/html-css.md)
   - [javascript.md](file:///home/marcel/projects/dj-design-system/conductor/code_styleguides/javascript.md)
2. Apply immediate refactorings to fix compliance issues, dead code, or token tier violations.
3. Verify with `just check` and `just test`.
4. If changes were made, commit them:
   ```bash
   git commit -m "style(review): apply code-review refactors"
   ```

*(Note: Do not run this step more than once per phase/delivery to avoid review duplication).*

---

## 5. Step 3: Local `gemini-reviewer` Subagent Loop

Harness the [gemini-reviewer](file:///home/marcel/projects/dj-design-system/.agents/agents/gemini-reviewer.md) subagent to perform an independent, non-destructive audit mirroring CI:

1. Invoke the subagent:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "gemini-reviewer",
           "Role": "Local Gemini Reviewer",
           "Prompt": "Review the current branch changeset against origin/main following CI review criteria."
       }]
   )
   ```
2. When the subagent reports back:
   - If findings are present (`[CRITICAL]`, `[HIGH]`, or `[MEDIUM]`):
     - Apply the recommended fixes using IDE edit tools (`replace_file_content`).
     - Run `just check` and `just test`.
     - Commit the fixes:
       ```bash
       git commit -m "fix(review): address local gemini-reviewer findings"
       ```
     - Re-invoke `gemini-reviewer` to re-audit.
   - Repeat until `gemini-reviewer` issues an **all clear response** (`APPROVE` verdict with zero blocking issues).

---

## 6. Step 4: Open or Update Pull Request

1. Push the branch to the remote repository:
   ```bash
   git push -u origin <branch>:<branch>
   ```
2. Check if a PR already exists:
   ```bash
   gh pr view --json number,url
   ```
3. If no PR exists, create one matching the user's preference from Step 2:
   - **Draft PR**:
     ```bash
     gh pr create --draft --base main --head <branch> --title "<title>" --body "<body>"
     ```
   - **Ready PR**:
     ```bash
     gh pr create --base main --head <branch> --title "<title>" --body "<body>"
     ```

---

## 7. Step 5: CI Checks & Automated Remote Review

1. Monitor CI checks until all workflows complete:
   ```bash
   gh pr checks --watch
   ```
2. If the PR was created as a Draft, trigger the Gemini CI review:
   ```bash
   gh pr comment <pr_number> --body "/review"
   ```
3. Wait for the automated CI review to post inline findings and summary.

---

## 8. Step 6: Remote Feedback Resolution Loop

1. Inspect unresolved comments:
   ```bash
   just comments <pr_number>
   ```
2. If unresolved comments or failed CI checks exist:
   - Make the required corrections in code and tests.
   - Verify with `just check` and `just test`.
   - Commit the fixes:
     ```bash
     git commit -m "fix(review): address PR review comments"
     ```
   - Push to remote: `git push`.
   - Resolve the addressed review comments on GitHub.
   - Request re-review:
     ```bash
     gh pr comment <pr_number> --body "/review"
     ```
   - Re-check `gh pr checks --watch`.
3. Continue iterating until:
   - All CI checks pass cleanly (`ci-complete` passed).
   - No unresolved comments from Gemini remain.
4. Report completion to the user with the PR URL.
