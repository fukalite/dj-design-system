---
name: complete-work
description: "Orchestrates completing a piece of work: enforces main branch safety, detects existing PRs vs new/stacked PRs, prompts for base and draft preferences, commits work, executes /code-review, iterates with local gemini-reviewer, opens/updates PR, monitors CI, and resolves remote review comments until all green."
---

# Complete Work Skill

You orchestrate the completion, auditing, and delivery of a piece of work into a GitHub Pull Request. You support:
- **Phase 2+ of an active track**: Updating an existing track PR with new commits and verifying CI.
- **Phase 1 of a new track (Clean)**: Branching cleanly off `origin/main` into a new standalone PR.
- **Phase 1 of a new track (Stacked / Chained)**: Stacking onto an existing branch or upstream PR with proper `--base` targeting.
- **Stacked phase PRs**: Delivering individual phases as dependent chained PRs.

---

## 1. Branch Strategy & State Detection (CRITICAL)

**Never commit or push directly to `main` at all costs.**

Before staging or committing any files, run discovery:
```bash
git branch --show-current
gh pr view --json number,title,baseRefName,headRefName,isDraft,state 2>/dev/null || true
```

Evaluate the current state against three scenarios:

---

### Scenario A: Working into an Existing PR (e.g. Phase 2+ of a Track)
If `gh pr view` returns an open PR matching the current branch:
1. **Identify Existing PR**: Note PR number, base branch (`baseRefName`), and draft status.
2. **Set Base Reference**: Set `BASE_REF = baseRefName` (usually `main`, or a parent branch if already stacked).
3. **No Duplicate Prompts**: Do **not** ask whether to create a draft PR (the PR already exists).
4. **Proceed Directly**: Move to [Section 3: Initial Commit](#3-step-1-initial-commit). When pushing later in Section 6, you will update this existing PR.

---

### Scenario B: On `main` Branch (New Track or Unbranched Work)
If currently on `main`:
1. **Never commit on `main`**.
2. Determine whether to start a clean branch or chain onto another branch using `ask_question`:
   - **Question**: "How should this new piece of work be branched and targeted for Pull Request?"
   - **Options**:
     - `(Recommended) Clean PR based off origin/main`: Base work on latest `origin/main` (`BASE_REF = "main"`).
     - `Stack / Chain on an existing branch or PR`: Stack work onto an active branch (`BASE_REF = "<chosen-branch>"`).
3. Create and switch to the new feature branch:
   - For clean: `git fetch origin main && git checkout -b feat/<name> origin/main`
   - For stacked: `git fetch origin <target> && git checkout -b feat/<name> origin/<target>`
4. Prompt for Draft PR preference via [Section 2: Draft PR Preference Gate](#2-interactive-draft-pr-preference-gate).

---

### Scenario C: On a Branch Without an Open PR (First Phase or New Stack)
If on a non-main branch that does not have an open PR:
1. Ask the user using `ask_question`:
   - **Question**: "What is the intended base branch for this new Pull Request?"
   - **Options**:
     - `(Recommended) Target main (Standalone PR)`: Sets `BASE_REF = "main"`.
     - `Target parent branch <parent_branch> (Stacked PR)`: Sets `BASE_REF = "<parent_branch>"`.
     - `Rebase / restart cleanly off origin/main`: Switch to fresh branch off `origin/main`.
2. Prompt for Draft PR preference via [Section 2: Draft PR Preference Gate](#2-interactive-draft-pr-preference-gate).

---

## 2. Interactive Draft PR Preference Gate

*(Only executed for new PRs in Scenario B and Scenario C. Skipped for Scenario A).*

Prompt the user using `ask_question`:
- **Question**: "Should the new Pull Request be created as a Draft PR?"
- **Options**:
  - `(Recommended) Create as Draft PR`
  - `Create as Ready for Review PR`

Record `IS_DRAFT = true/false`.

---

## 3. Step 1: Initial Commit

1. Run pre-commit quality gates:
   - `export PATH="$HOME/.asdf/shims:$PATH" && just check`
   - `export PATH="$HOME/.asdf/shims:$PATH" && just test`
2. Clean untracked generated build artefacts if present:
   - `git clean -f dj_design_system/components/` (compiled `.js` files)
3. Stage changes and create the initial commit:
   ```bash
   git add <modified-files>
   git commit -m "<type>(<scope>): <concise description of work>"
   ```

---

## 4. Step 2: Code Review Skill Execution (`/code-review`)

Run the `/code-review` workflow to audit code against project styleguides and apply standard refactorings:
1. Inspect touched files against:
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

1. Invoke the subagent with the resolved `BASE_REF`:
   ```python
   invoke_subagent(
       Subagents=[{
           "TypeName": "gemini-reviewer",
           "Role": "Local Gemini Reviewer",
           "Prompt": f"Review the changeset against origin/{BASE_REF}...HEAD following CI review criteria."
       }]
   )
   ```
   *(Scoping to `origin/{BASE_REF}...HEAD` ensures stacked PRs are only audited for their own commits, ignoring upstream parent commits).*

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

1. **Push Branch**:
   Push with explicit refspecs so `push.default = upstream` never misdirects to `main`:
   ```bash
   git push -u origin <branch>:<branch>
   ```
2. **Check PR Status**:
   ```bash
   gh pr view --json number,url 2>/dev/null || true
   ```
3. **If PR Already Exists (Scenario A)**:
   - The push has automatically updated the PR. Proceed directly to CI monitoring.
4. **If New PR Needed (Scenario B or C)**:
   - Create the PR using the dynamic `--base ${BASE_REF}` and draft preference:
     - **Draft PR**:
       ```bash
       gh pr create --draft --base "${BASE_REF}" --head "<branch>" --title "<title>" --body "<body>"
       ```
     - **Ready PR**:
       ```bash
       gh pr create --base "${BASE_REF}" --head "<branch>" --title "<title>" --body "<body>"
       ```

---

## 7. Step 5: CI Checks & Automated Remote Review

1. Monitor CI checks until all workflows complete:
   ```bash
   gh pr checks --watch
   ```
2. If the PR is a Draft PR, trigger the automated Gemini review:
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
