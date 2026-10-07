# GitHub Project Mirror

Every track is mirrored to [GitHub Project #2](https://github.com/orgs/fukalite/projects/2) as one issue in `fukalite/dj-design-system-conductor`. While the trial (`github_project_trial_20261007`) runs, the files are the source of truth.

## Rules
- Mirror every change to a track's files to the Project in the same step. Never change the Project without changing the files.
- Never edit a track issue's body by hand. Rebuild it from the files.
- Find a track's issue by its **Track ID** field, never by title.
- If a `gh` call fails, report it and carry on with the file workflow. Never block track work on the Project.

## Mapping
| Track | Project |
| --- | --- |
| `tracks.md` title | Issue title |
| `spec.md` + `plan.md` | Issue body (see [Build the body](#build-the-body)) |
| `id` | **Track ID** |
| `type` | **Track type** |
| `initiative` | **Initiative** (cleared when `null`) |
| First phase in `plan.md` with a `[ ]` or `[~]` task | **Current phase** (cleared when none) |
| `status: new` | **Status** Backlog (or Ready) |
| `status: in_progress` | **Status** In progress; In review once the track's PR is ready for review |
| `status: completed` | **Status** Done, and the issue is closed as completed |
| `depends_on` | "Blocked by" links to the blocking tracks' issues |
| `depends_on` | Board order: a track sits below every track that blocks it |

A new `type` or `initiative` value needs a new option on the Project first. Ask the user to add it.

## Identifiers
| Name | Id | Options |
| --- | --- | --- |
| Project | `PVT_kwDOEGdWms4BmH3q` | |
| Status | `PVTSSF_lADOEGdWms4BmH3qzhkyHQk` | Backlog `f75ad846`, Ready `61e4505c`, In progress `47fc9ee4`, In review `df73e18b`, Done `98236657` |
| Track ID | `PVTF_lADOEGdWms4BmH3qzhkyJ4A` | |
| Current phase | `PVTF_lADOEGdWms4BmH3qzhkyJ4E` | |
| Track type | `PVTSSF_lADOEGdWms4BmH3qzhkyJ5Y` | feature `ff542278`, bugfix `64e6ce8b`, chore `4cf72960`, project `c4f44df2` |
| Initiative | `PVTSSF_lADOEGdWms4BmH3qzhkyJ5c` | gallery_rebuild `cc84bd0b` |

If an id is rejected, re-read them with `gh project field-list 2 --owner fukalite --format json`.

## Operations

### Read the board
```sh
gh project item-list 2 --owner fukalite --format json --limit 200 \
  --jq '.items[] | select(.labels | index("track")) | {item: .id, number: .content.number, url: .content.url, track: ."track ID", status, phase: ."current phase"}'
```

### Build the body
Write the body to a temporary file. The format must match exactly, so the mirror stays comparable.
```sh
id=<track_id>; dir=conductor/tracks/$id; body=$(mktemp)
{
  printf '<!-- conductor-track: %s -->\n' "$id"
  printf 'Mirrored from [`%s`](https://github.com/fukalite/dj-design-system/tree/main/%s). The files are the source of truth; edits made here are overwritten.\n' "$dir" "$dir"
  for doc in spec.md plan.md; do
    [ -s "$dir/$doc" ] && printf '\n---\n\n%s\n' "$(cat "$dir/$doc")"
  done
} > "$body"
```

### Create a track's issue and item
```sh
url=$(gh issue create --repo fukalite/dj-design-system-conductor --label track --title "<title>" --body-file "$body")
item=$(gh project item-add 2 --owner fukalite --url "$url" --format json --jq .id)
```
Then set every field, add the "blocked by" links and place the item.

### Update a track's issue
```sh
gh issue edit <number> --repo fukalite/dj-design-system-conductor --title "<title>" --body-file "$body"
gh issue close <number> --repo fukalite/dj-design-system-conductor --reason completed
gh issue reopen <number> --repo fukalite/dj-design-system-conductor
```

### Set or clear a field
```sh
gh project item-edit --project-id PVT_kwDOEGdWms4BmH3q --id <item> --field-id <field> --text "<value>"
gh project item-edit --project-id PVT_kwDOEGdWms4BmH3q --id <item> --field-id <field> --single-select-option-id <option>
gh project item-edit --project-id PVT_kwDOEGdWms4BmH3q --id <item> --field-id <field> --clear
```

### Add or remove a "blocked by" link
```sh
issue=$(gh issue view <number> --repo fukalite/dj-design-system-conductor --json id --jq .id)
blocker=$(gh issue view <blocker_number> --repo fukalite/dj-design-system-conductor --json id --jq .id)
gh api graphql -f query='mutation($i: ID!, $b: ID!) { addBlockedBy(input: {issueId: $i, blockingIssueId: $b}) { issue { id } } }' -f i="$issue" -f b="$blocker"
```
Use `removeBlockedBy` with the same arguments to remove one.

### Place an item below its blockers
Move the item directly after the lowest-placed blocker's item. Leave items without blockers where they are.
```sh
gh api graphql -f query='mutation($p: ID!, $i: ID!, $a: ID) { updateProjectV2ItemPosition(input: {projectId: $p, itemId: $i, afterId: $a}) { clientMutationId } }' -f p=PVT_kwDOEGdWms4BmH3q -f i=<item> -f a=<blocker_item>
```
