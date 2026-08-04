# Git Workflow Rules

- **NEVER Force Push**: Do not use `git push -f` or force push under any circumstances. If you need to fix linting or correct a previous commit, create a new commit or ask the user how they would prefer to handle it instead of rewriting history.
- **Always verify before committing**: Always run `just check` and `just test` before creating a commit. Never commit without ensuring linting, formatting, and tests pass successfully.
- **PR Review Resolution**: When addressing PR feedback, complete the implementation, then use MCP tools to reply to/resolve the open comments on GitHub. Afterward, check if CI actions are running and wait for them to finish before checking for new feedback. If there's new feedback, address it if you can without getting user input, and repeat the cycle.
