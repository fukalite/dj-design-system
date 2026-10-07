"""Mirror Conductor track state into the fukalite GitHub Project.

Trial tooling for conductor/tracks/github_project_trial_20261007. The files
under conductor/ stay the source of truth; this script reads them and
mirrors track state into the Project.
"""

import argparse
import dataclasses
import json
import re
import subprocess
import sys
from collections.abc import Iterable, Sequence
from pathlib import Path
from typing import Any, Protocol


CONDUCTOR_DIR = Path(__file__).resolve().parent.parent.parent / "conductor"
REGISTRY_FILE = "tracks.md"
METADATA_FILE = "metadata.json"
PLAN_FILE = "plan.md"
SPEC_FILE = "spec.md"
ISSUE_BODY_LIMIT = 65_536

OWNER = "fukalite"
REPOSITORY = "dj-design-system"
ISSUE_REPOSITORY = "dj-design-system-conductor"
PROJECT_NUMBER = 2
TRACK_LABEL = "track"
REPOSITORY_URL = f"https://github.com/{OWNER}/{REPOSITORY}"

TRACK_ID_FIELD = "Track ID"
TRACK_TYPE_FIELD = "Track type"
INITIATIVE_FIELD = "Initiative"
CURRENT_PHASE_FIELD = "Current phase"
STATUS_FIELD = "Status"
STATUS_COLUMNS = {
    "new": ("Backlog", "Ready"),
    "in_progress": ("In progress", "In review"),
    "completed": ("Done",),
}
COMPLETED_STATUS = "completed"
IN_PROGRESS_COLUMN = "In progress"
IN_REVIEW_COLUMN = "In review"

TRACK_MARKER_PATTERN = re.compile(r"<!-- conductor-track: (?P<id>\S+) -->")

REGISTRY_ENTRY_PATTERN = re.compile(
    r"\*\*Track: (?P<title>.+?)\*\*\s*\n\s*\*Link: \[[^\]]*\]\((?:conductor/)?tracks/(?P<id>[^/]+)/"
)
PHASE_HEADING_PATTERN = re.compile(
    r"^## (?P<name>Phase .+?)(?:\s*\[checkpoint: [^\]]*\])?\s*$"
)
OPEN_TASK_PATTERN = re.compile(r"^\s*- \[[ ~]\]")


class TrackParseError(Exception):
    """A track's files cannot be read into a Track."""


class ProjectSchemaError(Exception):
    """The Project is missing a field, option or label the mirror needs."""


class GitHubError(Exception):
    """A GitHub API call made through gh failed."""


@dataclasses.dataclass(frozen=True)
class Phase:
    """A phase heading in a track's plan.md."""

    name: str
    is_complete: bool


@dataclasses.dataclass(frozen=True)
class Track:
    """The state of one Conductor track, as recorded in its files."""

    id: str
    title: str
    type: str
    status: str
    initiative: str | None
    depends_on: tuple[str, ...]
    phases: tuple[Phase, ...]
    spec: str
    plan: str

    @property
    def current_phase(self) -> str | None:
        """The name of the first incomplete phase, or None when there is none."""
        return next(
            (phase.name for phase in self.phases if not phase.is_complete), None
        )


@dataclasses.dataclass(frozen=True)
class ProjectField:
    """A Project field. Single-select fields map option names to option ids."""

    id: str
    name: str
    options: dict[str, str]


@dataclasses.dataclass(frozen=True)
class ProjectSchema:
    """The Project's id and fields, keyed by field name."""

    project_id: str
    fields: dict[str, ProjectField]


@dataclasses.dataclass(frozen=True)
class MirroredIssue:
    """An issue that mirrors a track, with its Project item's field values."""

    issue_id: str
    track_id: str
    title: str
    body: str
    is_closed: bool
    blocked_by_ids: frozenset[str]
    item_id: str | None
    field_values: dict[str, str]


@dataclasses.dataclass(frozen=True)
class PullRequest:
    """An open pull request in the code repository."""

    number: int
    is_draft: bool
    body: str


class ProjectClient(Protocol):
    """Reads and writes the issues and Project items that mirror tracks."""

    def fetch_schema(self) -> ProjectSchema: ...

    def fetch_open_pull_requests(self) -> list[PullRequest]: ...

    def fetch_mirrored_issues(self) -> list[MirroredIssue]: ...

    def create_issue(self, title: str, body: str) -> str: ...

    def update_issue(self, issue_id: str, title: str, body: str) -> None: ...

    def set_issue_closed(self, issue_id: str, is_closed: bool) -> None: ...

    def add_to_project(self, issue_id: str) -> str: ...

    def set_field_value(
        self, item_id: str, field: ProjectField, value: str
    ) -> None: ...

    def clear_field_value(self, item_id: str, field: ProjectField) -> None: ...

    def add_blocked_by(self, issue_id: str, blocking_issue_id: str) -> None: ...

    def remove_blocked_by(self, issue_id: str, blocking_issue_id: str) -> None: ...

    def fetch_item_order(self) -> list[str]: ...

    def move_item_after(self, item_id: str, after_id: str | None) -> None: ...


def load_tracks(conductor_dir: Path) -> list[Track]:
    """Read every non-archived track under a conductor directory.

    Args:
        conductor_dir: The conductor/ directory.

    Returns:
        The tracks, sorted by id.

    Raises:
        TrackParseError: A track's metadata is missing its id or names another track.
    """
    titles = parse_registry_titles(text=(conductor_dir / REGISTRY_FILE).read_text())
    track_dirs = sorted(
        path.parent for path in (conductor_dir / "tracks").glob(f"*/{METADATA_FILE}")
    )
    return [load_track(track_dir=track_dir, titles=titles) for track_dir in track_dirs]


def load_track(track_dir: Path, titles: dict[str, str]) -> Track:
    """Read one track directory.

    Args:
        track_dir: The track's directory.
        titles: Track titles from the registry, keyed by track id.

    Returns:
        The track.

    Raises:
        TrackParseError: The metadata is missing its id or names another track.
    """
    metadata = json.loads((track_dir / METADATA_FILE).read_text())
    track_id = metadata.get("id")
    if track_id is None:
        raise TrackParseError(f"{track_dir.name}: {METADATA_FILE} has no id")
    if track_id != track_dir.name:
        raise TrackParseError(f"{track_dir.name}: {METADATA_FILE} id is {track_id}")
    plan_text = read_optional_file(path=track_dir / PLAN_FILE)
    return Track(
        id=track_id,
        title=titles.get(track_id, track_id),
        type=metadata["type"],
        status=metadata["status"],
        initiative=metadata.get("initiative"),
        depends_on=tuple(metadata.get("depends_on", ())),
        phases=parse_phases(text=plan_text),
        spec=read_optional_file(path=track_dir / SPEC_FILE),
        plan=plan_text,
    )


def read_optional_file(path: Path) -> str:
    """Read a file, or return an empty string when it does not exist."""
    return path.read_text() if path.exists() else ""


def parse_registry_titles(text: str) -> dict[str, str]:
    """Read track titles from tracks.md.

    Args:
        text: The contents of tracks.md.

    Returns:
        Track titles keyed by track id.
    """
    return {
        match["id"]: match["title"] for match in REGISTRY_ENTRY_PATTERN.finditer(text)
    }


def parse_phases(text: str) -> tuple[Phase, ...]:
    """Read the phases from a plan.md.

    A phase is complete when it has no open (`[ ]`) or in-progress (`[~]`)
    tasks or sub-tasks.

    Args:
        text: The contents of plan.md.

    Returns:
        The phases in plan order.
    """
    phases: list[Phase] = []
    for line in text.splitlines():
        heading = PHASE_HEADING_PATTERN.match(line)
        if heading:
            phases.append(Phase(name=heading["name"], is_complete=True))
        elif phases and OPEN_TASK_PATTERN.match(line):
            phases[-1] = dataclasses.replace(phases[-1], is_complete=False)
    return tuple(phases)


def build_issue_body(track: Track) -> str:
    """Build the body of the issue that mirrors a track.

    Args:
        track: The track.

    The body holds the track's spec and plan verbatim, after a hidden track
    marker and a note naming the source files.

    Returns:
        The issue body.

    Raises:
        TrackParseError: The body is over GitHub's issue body limit.
    """
    track_url = f"{REPOSITORY_URL}/tree/main/conductor/tracks/{track.id}"
    sections = [
        f"<!-- conductor-track: {track.id} -->\n"
        f"Mirrored from [`conductor/tracks/{track.id}`]({track_url}). The files "
        "are the source of truth; edits made here are overwritten.\n",
    ]
    sections.extend(document for document in (track.spec, track.plan) if document)
    body = "\n---\n\n".join(section.rstrip("\n") + "\n" for section in sections)
    if len(body) > ISSUE_BODY_LIMIT:
        raise TrackParseError(
            f"{track.id}: issue body is {len(body)} characters, "
            f"over GitHub's {ISSUE_BODY_LIMIT}"
        )
    return body


def parse_track_marker(body: str) -> str | None:
    """Read the track id from an issue body's hidden marker.

    Args:
        body: The issue body.

    Returns:
        The track id, or None when the body has no marker.
    """
    match = TRACK_MARKER_PATTERN.search(body)
    return match["id"] if match else None


def build_field_values(
    track: Track,
    current_status: str | None,
    pull_requests: Sequence[PullRequest],
) -> dict[str, str | None]:
    """Build the Project field values that mirror a track.

    Args:
        track: The track.
        current_status: The item's current Status column, if any.
        pull_requests: Open pull requests linked to the track.

    Returns:
        Field values keyed by field name. None means the field is cleared.

    Raises:
        TrackParseError: The track's status has no Status columns.
    """
    columns = STATUS_COLUMNS.get(track.status)
    if columns is None:
        raise TrackParseError(f"{track.id}: unknown status {track.status}")
    return {
        TRACK_ID_FIELD: track.id,
        TRACK_TYPE_FIELD: track.type,
        INITIATIVE_FIELD: track.initiative,
        CURRENT_PHASE_FIELD: track.current_phase,
        STATUS_FIELD: build_status(
            track=track,
            columns=columns,
            current_status=current_status,
            pull_requests=pull_requests,
        ),
    }


def build_status(
    track: Track,
    columns: tuple[str, ...],
    current_status: str | None,
    pull_requests: Sequence[PullRequest],
) -> str:
    """Pick a track's Status column.

    A completed track is always Done. Otherwise, open pull requests decide:
    In review when every one is ready for review, else In progress. Without
    pull requests, the current column is kept when it is one of the track
    status's columns.
    """
    if track.status != COMPLETED_STATUS and pull_requests:
        if all(not pull_request.is_draft for pull_request in pull_requests):
            return IN_REVIEW_COLUMN
        return IN_PROGRESS_COLUMN
    return current_status if current_status in columns else columns[0]


def find_linked_pull_requests(
    track_id: str, pull_requests: Iterable[PullRequest]
) -> tuple[PullRequest, ...]:
    """Find the pull requests whose body names a track's id.

    Args:
        track_id: The track id.
        pull_requests: Open pull requests.

    Returns:
        The pull requests linked to the track.
    """
    pattern = re.compile(rf"(?<![\w]){re.escape(track_id)}(?![\w])")
    return tuple(
        pull_request
        for pull_request in pull_requests
        if pattern.search(pull_request.body)
    )


def validate_schema(schema: ProjectSchema, tracks: Iterable[Track]) -> None:
    """Check the Project has every field and option the tracks need.

    Args:
        schema: The Project schema.
        tracks: The tracks to mirror.

    Raises:
        ProjectSchemaError: A field or single-select option is missing.
    """
    required_options = {
        STATUS_FIELD: {
            column for columns in STATUS_COLUMNS.values() for column in columns
        },
        TRACK_TYPE_FIELD: {track.type for track in tracks},
        INITIATIVE_FIELD: {track.initiative for track in tracks if track.initiative},
    }
    problems = [
        f"missing field {name}"
        for name in (TRACK_ID_FIELD, CURRENT_PHASE_FIELD, *required_options)
        if name not in schema.fields
    ]
    for name, options in required_options.items():
        field = schema.fields.get(name)
        if field is not None:
            problems.extend(
                f"missing {name} option {option}"
                for option in sorted(options - field.options.keys())
            )
    if problems:
        raise ProjectSchemaError("; ".join(problems))


def backfill(client: ProjectClient, tracks: list[Track]) -> list[str]:
    """Bring the Project in line with the tracks, changing only what differs.

    Args:
        client: The Project client.
        tracks: The tracks to mirror.

    Returns:
        A description of each change made or skipped.

    Raises:
        ProjectSchemaError: The Project is missing a field or option.
    """
    schema = client.fetch_schema()
    validate_schema(schema=schema, tracks=tracks)
    issues = {issue.track_id: issue for issue in client.fetch_mirrored_issues()}
    issue_ids = {track_id: issue.issue_id for track_id, issue in issues.items()}
    pull_requests = client.fetch_open_pull_requests()
    actions: list[str] = []
    item_ids: dict[str, str] = {}
    for track in tracks:
        synced = sync_issue(
            client=client,
            schema=schema,
            track=track,
            issue=issues.get(track.id),
            pull_requests=find_linked_pull_requests(
                track_id=track.id, pull_requests=pull_requests
            ),
            actions=actions,
        )
        issue_ids[track.id] = synced.issue_id
        item_ids[track.id] = synced.item_id
    for track in tracks:
        sync_blocked_by(
            client=client,
            track=track,
            issue=issues.get(track.id),
            issue_ids=issue_ids,
            actions=actions,
        )
    sync_item_order(client=client, tracks=tracks, item_ids=item_ids, actions=actions)
    return actions


def order_tracks(tracks: Sequence[Track]) -> list[Track]:
    """Order tracks so every track comes after the tracks it depends on.

    Tracks are sorted by dependency depth (the longest chain of dependencies
    below them), then by id. Dependencies on tracks that are not in the list
    are ignored.

    Args:
        tracks: The tracks.

    Returns:
        The tracks in order.

    Raises:
        TrackParseError: The dependencies form a cycle.
    """
    tracks_by_id = {track.id: track for track in tracks}
    depths: dict[str, int] = {}
    for track in tracks:
        measure_depth(
            track=track, tracks_by_id=tracks_by_id, depths=depths, visiting=set()
        )
    return sorted(tracks, key=lambda track: (depths[track.id], track.id))


def measure_depth(
    track: Track,
    tracks_by_id: dict[str, Track],
    depths: dict[str, int],
    visiting: set[str],
) -> int:
    """Measure a track's dependency depth, caching results in depths.

    Raises:
        TrackParseError: The dependencies form a cycle.
    """
    if track.id in depths:
        return depths[track.id]
    if track.id in visiting:
        raise TrackParseError(f"{track.id}: dependency cycle")
    visiting.add(track.id)
    dependencies = [
        tracks_by_id[dependency]
        for dependency in track.depends_on
        if dependency in tracks_by_id
    ]
    depths[track.id] = 1 + max(
        (
            measure_depth(
                track=dependency,
                tracks_by_id=tracks_by_id,
                depths=depths,
                visiting=visiting,
            )
            for dependency in dependencies
        ),
        default=-1,
    )
    return depths[track.id]


def sync_item_order(
    client: ProjectClient,
    tracks: Sequence[Track],
    item_ids: dict[str, str],
    actions: list[str],
) -> None:
    """Move Project items so each track sits above the tracks it blocks.

    Only items out of place are moved. Items that do not mirror a track keep
    their place relative to their neighbours.

    Args:
        client: The Project client.
        tracks: The tracks.
        item_ids: Project item ids keyed by track id.
        actions: Descriptions of changes made, appended to.
    """
    ordered = order_tracks(tracks=tracks)
    desired = [item_ids[track.id] for track in ordered]
    wanted = set(desired)
    current = [item_id for item_id in client.fetch_item_order() if item_id in wanted]
    for index, (track, item_id) in enumerate(zip(ordered, desired, strict=True)):
        if current[index] == item_id:
            continue
        after_id = desired[index - 1] if index else None
        client.move_item_after(item_id=item_id, after_id=after_id)
        current.remove(item_id)
        current.insert(index, item_id)
        actions.append(f"{track.id}: moved to position {index + 1}")


@dataclasses.dataclass(frozen=True)
class SyncedIssue:
    """The ids of a track's issue and Project item after syncing."""

    issue_id: str
    item_id: str


def sync_issue(
    client: ProjectClient,
    schema: ProjectSchema,
    track: Track,
    issue: MirroredIssue | None,
    pull_requests: Sequence[PullRequest],
    actions: list[str],
) -> SyncedIssue:
    """Create or update a track's issue and Project item.

    Args:
        client: The Project client.
        schema: The Project schema.
        track: The track.
        issue: The track's existing issue, if any.
        pull_requests: Open pull requests linked to the track.
        actions: Descriptions of changes made, appended to.

    Returns:
        The issue and item ids.
    """
    body = build_issue_body(track=track)
    is_closed = track.status == COMPLETED_STATUS
    if issue is None:
        issue_id = client.create_issue(title=track.title, body=body)
        actions.append(f"{track.id}: created issue")
        if is_closed:
            client.set_issue_closed(issue_id=issue_id, is_closed=True)
        item_id = None
        field_values: dict[str, str] = {}
    else:
        issue_id = issue.issue_id
        if issue.title != track.title or issue.body != body:
            client.update_issue(issue_id=issue_id, title=track.title, body=body)
            actions.append(f"{track.id}: updated title and body")
        if issue.is_closed != is_closed:
            client.set_issue_closed(issue_id=issue_id, is_closed=is_closed)
            actions.append(f"{track.id}: {'closed' if is_closed else 'reopened'} issue")
        item_id = issue.item_id
        field_values = issue.field_values
    if item_id is None:
        item_id = client.add_to_project(issue_id=issue_id)
        actions.append(f"{track.id}: added to Project")
    sync_field_values(
        client=client,
        schema=schema,
        track=track,
        item_id=item_id,
        field_values=field_values,
        pull_requests=pull_requests,
        actions=actions,
    )
    return SyncedIssue(issue_id=issue_id, item_id=item_id)


def sync_field_values(
    client: ProjectClient,
    schema: ProjectSchema,
    track: Track,
    item_id: str,
    field_values: dict[str, str],
    pull_requests: Sequence[PullRequest],
    actions: list[str],
) -> None:
    """Set or clear each Project field that differs from the track.

    Args:
        client: The Project client.
        schema: The Project schema.
        track: The track.
        item_id: The track's Project item id.
        field_values: The item's current field values, keyed by field name.
        pull_requests: Open pull requests linked to the track.
        actions: Descriptions of changes made, appended to.
    """
    desired_values = build_field_values(
        track=track,
        current_status=field_values.get(STATUS_FIELD),
        pull_requests=pull_requests,
    )
    for name, value in desired_values.items():
        if field_values.get(name) == value:
            continue
        field = schema.fields[name]
        if value is None:
            client.clear_field_value(item_id=item_id, field=field)
            actions.append(f"{track.id}: cleared {name}")
        else:
            client.set_field_value(item_id=item_id, field=field, value=value)
            actions.append(f"{track.id}: set {name} to {value}")


def sync_blocked_by(
    client: ProjectClient,
    track: Track,
    issue: MirroredIssue | None,
    issue_ids: dict[str, str],
    actions: list[str],
) -> None:
    """Make a track's "blocked by" links match its depends_on.

    Only links to other track issues are removed, so links added by hand to
    non-track issues are kept.

    Args:
        client: The Project client.
        track: The track.
        issue: The track's issue as it was before syncing, if it existed.
        issue_ids: Issue ids keyed by track id, for every mirrored track.
        actions: Descriptions of changes made or skipped, appended to.
    """
    issue_id = issue_ids[track.id]
    current_ids = issue.blocked_by_ids if issue else frozenset()
    desired_ids = set()
    for dependency in track.depends_on:
        if dependency not in issue_ids:
            actions.append(
                f"{track.id}: skipped dependency on {dependency} (no mirrored issue)"
            )
            continue
        desired_ids.add(issue_ids[dependency])
    track_ids = {issue_id: track_id for track_id, issue_id in issue_ids.items()}
    for blocking_id in sorted(desired_ids - current_ids):
        client.add_blocked_by(issue_id=issue_id, blocking_issue_id=blocking_id)
        actions.append(f"{track.id}: added blocked by {track_ids[blocking_id]}")
    for blocking_id in sorted((current_ids - desired_ids) & track_ids.keys()):
        client.remove_blocked_by(issue_id=issue_id, blocking_issue_id=blocking_id)
        actions.append(f"{track.id}: removed blocked by {track_ids[blocking_id]}")


SCHEMA_QUERY = """
query($owner: String!, $repo: String!, $number: Int!, $label: String!) {
  organization(login: $owner) {
    projectV2(number: $number) {
      id
      fields(first: 50) {
        nodes {
          ... on ProjectV2FieldCommon { id name }
          ... on ProjectV2SingleSelectField { options { id name } }
        }
      }
    }
  }
  repository(owner: $owner, name: $repo) {
    id
    label(name: $label) { id }
  }
}
"""

ISSUES_QUERY = """
query($owner: String!, $repo: String!, $label: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    issues(first: 50, after: $cursor, labels: [$label], states: [OPEN, CLOSED]) {
      pageInfo { hasNextPage endCursor }
      nodes {
        id
        title
        body
        state
        blockedBy(first: 50) { nodes { id } }
        projectItems(first: 20) {
          nodes {
            id
            project { id }
            fieldValues(first: 30) {
              nodes {
                ... on ProjectV2ItemFieldTextValue {
                  text
                  field { ... on ProjectV2FieldCommon { name } }
                }
                ... on ProjectV2ItemFieldSingleSelectValue {
                  name
                  field { ... on ProjectV2FieldCommon { name } }
                }
              }
            }
          }
        }
      }
    }
  }
}
"""

PULL_REQUESTS_QUERY = """
query($owner: String!, $repo: String!, $cursor: String) {
  repository(owner: $owner, name: $repo) {
    pullRequests(first: 50, after: $cursor, states: [OPEN]) {
      pageInfo { hasNextPage endCursor }
      nodes { number isDraft body }
    }
  }
}
"""

CREATE_ISSUE_MUTATION = """
mutation($repositoryId: ID!, $title: String!, $body: String!, $labelId: ID!) {
  createIssue(input: {
    repositoryId: $repositoryId, title: $title, body: $body, labelIds: [$labelId]
  }) { issue { id } }
}
"""

UPDATE_ISSUE_MUTATION = """
mutation($id: ID!, $title: String!, $body: String!) {
  updateIssue(input: {id: $id, title: $title, body: $body}) { issue { id } }
}
"""

CLOSE_ISSUE_MUTATION = """
mutation($issueId: ID!) {
  closeIssue(input: {issueId: $issueId, stateReason: COMPLETED}) { issue { id } }
}
"""

REOPEN_ISSUE_MUTATION = """
mutation($issueId: ID!) {
  reopenIssue(input: {issueId: $issueId}) { issue { id } }
}
"""

ADD_ITEM_MUTATION = """
mutation($projectId: ID!, $contentId: ID!) {
  addProjectV2ItemById(input: {projectId: $projectId, contentId: $contentId}) {
    item { id }
  }
}
"""

SET_FIELD_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!, $value: ProjectV2FieldValue!) {
  updateProjectV2ItemFieldValue(input: {
    projectId: $projectId, itemId: $itemId, fieldId: $fieldId, value: $value
  }) { projectV2Item { id } }
}
"""

CLEAR_FIELD_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $fieldId: ID!) {
  clearProjectV2ItemFieldValue(input: {
    projectId: $projectId, itemId: $itemId, fieldId: $fieldId
  }) { projectV2Item { id } }
}
"""

ITEM_ORDER_QUERY = """
query($projectId: ID!, $cursor: String) {
  node(id: $projectId) {
    ... on ProjectV2 {
      items(first: 100, after: $cursor, orderBy: {field: POSITION, direction: ASC}) {
        pageInfo { hasNextPage endCursor }
        nodes { id }
      }
    }
  }
}
"""

MOVE_ITEM_MUTATION = """
mutation($projectId: ID!, $itemId: ID!, $afterId: ID) {
  updateProjectV2ItemPosition(input: {
    projectId: $projectId, itemId: $itemId, afterId: $afterId
  }) { clientMutationId }
}
"""

ADD_BLOCKED_BY_MUTATION = """
mutation($issueId: ID!, $blockingIssueId: ID!) {
  addBlockedBy(input: {issueId: $issueId, blockingIssueId: $blockingIssueId}) {
    issue { id }
  }
}
"""

REMOVE_BLOCKED_BY_MUTATION = """
mutation($issueId: ID!, $blockingIssueId: ID!) {
  removeBlockedBy(input: {issueId: $issueId, blockingIssueId: $blockingIssueId}) {
    issue { id }
  }
}
"""


class GitHubProjectClient:
    """A ProjectClient that calls the GitHub GraphQL API through gh."""

    def __init__(
        self, owner: str, issue_repo: str, code_repo: str, project_number: int
    ) -> None:
        self.owner = owner
        self.issue_repo = issue_repo
        self.code_repo = code_repo
        self.project_number = project_number
        self.project_id: str | None = None
        self.repository_id: str | None = None
        self.label_id: str | None = None

    def run_graphql(self, query: str, variables: dict[str, Any]) -> dict[str, Any]:
        """Run a GraphQL query or mutation with gh.

        Args:
            query: The GraphQL document.
            variables: The document's variables.

        Returns:
            The response's data.

        Raises:
            GitHubError: gh failed or the response has errors.
        """
        try:
            result = subprocess.run(
                args=["gh", "api", "graphql", "--input", "-"],
                input=json.dumps({"query": query, "variables": variables}),
                capture_output=True,
                text=True,
                check=True,
            )
        except subprocess.CalledProcessError as error:
            raise GitHubError(error.stderr) from error
        response = json.loads(result.stdout)
        if response.get("errors"):
            raise GitHubError(json.dumps(response["errors"]))
        return response["data"]

    def fetch_schema(self) -> ProjectSchema:
        """Read the Project's fields, and the repository and label ids.

        Raises:
            ProjectSchemaError: The track label does not exist.
        """
        data = self.run_graphql(
            query=SCHEMA_QUERY,
            variables={
                "owner": self.owner,
                "repo": self.issue_repo,
                "number": self.project_number,
                "label": TRACK_LABEL,
            },
        )
        project = data["organization"]["projectV2"]
        repository = data["repository"]
        if repository["label"] is None:
            raise ProjectSchemaError(f"missing label {TRACK_LABEL}")
        self.project_id = project["id"]
        self.repository_id = repository["id"]
        self.label_id = repository["label"]["id"]
        fields = [
            ProjectField(
                id=node["id"],
                name=node["name"],
                options={
                    option["name"]: option["id"] for option in node.get("options", [])
                },
            )
            for node in project["fields"]["nodes"]
        ]
        return ProjectSchema(
            project_id=project["id"], fields={field.name: field for field in fields}
        )

    def fetch_mirrored_issues(self) -> list[MirroredIssue]:
        """Read every track-labelled issue that carries a track marker."""
        issues: list[MirroredIssue] = []
        cursor = None
        while True:
            data = self.run_graphql(
                query=ISSUES_QUERY,
                variables={
                    "owner": self.owner,
                    "repo": self.issue_repo,
                    "label": TRACK_LABEL,
                    "cursor": cursor,
                },
            )
            connection = data["repository"]["issues"]
            for node in connection["nodes"]:
                issue = self.build_mirrored_issue(node=node)
                if issue is not None:
                    issues.append(issue)
            if not connection["pageInfo"]["hasNextPage"]:
                return issues
            cursor = connection["pageInfo"]["endCursor"]

    def fetch_open_pull_requests(self) -> list[PullRequest]:
        """Read every open pull request in the code repository."""
        pull_requests: list[PullRequest] = []
        cursor = None
        while True:
            data = self.run_graphql(
                query=PULL_REQUESTS_QUERY,
                variables={
                    "owner": self.owner,
                    "repo": self.code_repo,
                    "cursor": cursor,
                },
            )
            connection = data["repository"]["pullRequests"]
            pull_requests.extend(
                PullRequest(
                    number=node["number"], is_draft=node["isDraft"], body=node["body"]
                )
                for node in connection["nodes"]
            )
            if not connection["pageInfo"]["hasNextPage"]:
                return pull_requests
            cursor = connection["pageInfo"]["endCursor"]

    def build_mirrored_issue(self, node: dict[str, Any]) -> MirroredIssue | None:
        """Build a MirroredIssue from an issue node, or None without a marker."""
        track_id = parse_track_marker(body=node["body"])
        if track_id is None:
            return None
        item = next(
            (
                item
                for item in node["projectItems"]["nodes"]
                if item["project"]["id"] == self.project_id
            ),
            None,
        )
        field_values = {}
        if item is not None:
            for value in item["fieldValues"]["nodes"]:
                if "field" in value:
                    field_values[value["field"]["name"]] = (
                        value.get("text") or value["name"]
                    )
        return MirroredIssue(
            issue_id=node["id"],
            track_id=track_id,
            title=node["title"],
            body=node["body"],
            is_closed=node["state"] == "CLOSED",
            blocked_by_ids=frozenset(
                blocker["id"] for blocker in node["blockedBy"]["nodes"]
            ),
            item_id=item["id"] if item else None,
            field_values=field_values,
        )

    def create_issue(self, title: str, body: str) -> str:
        """Create a track-labelled issue and return its id."""
        data = self.run_graphql(
            query=CREATE_ISSUE_MUTATION,
            variables={
                "repositoryId": self.repository_id,
                "title": title,
                "body": body,
                "labelId": self.label_id,
            },
        )
        return data["createIssue"]["issue"]["id"]

    def update_issue(self, issue_id: str, title: str, body: str) -> None:
        """Replace an issue's title and body."""
        self.run_graphql(
            query=UPDATE_ISSUE_MUTATION,
            variables={"id": issue_id, "title": title, "body": body},
        )

    def set_issue_closed(self, issue_id: str, is_closed: bool) -> None:
        """Close an issue as completed, or reopen it."""
        self.run_graphql(
            query=CLOSE_ISSUE_MUTATION if is_closed else REOPEN_ISSUE_MUTATION,
            variables={"issueId": issue_id},
        )

    def add_to_project(self, issue_id: str) -> str:
        """Add an issue to the Project and return the item id."""
        data = self.run_graphql(
            query=ADD_ITEM_MUTATION,
            variables={"projectId": self.project_id, "contentId": issue_id},
        )
        return data["addProjectV2ItemById"]["item"]["id"]

    def set_field_value(self, item_id: str, field: ProjectField, value: str) -> None:
        """Set a text field, or a single-select field by option name."""
        field_value = (
            {"singleSelectOptionId": field.options[value]}
            if field.options
            else {"text": value}
        )
        self.run_graphql(
            query=SET_FIELD_MUTATION,
            variables={
                "projectId": self.project_id,
                "itemId": item_id,
                "fieldId": field.id,
                "value": field_value,
            },
        )

    def clear_field_value(self, item_id: str, field: ProjectField) -> None:
        """Clear a field's value on an item."""
        self.run_graphql(
            query=CLEAR_FIELD_MUTATION,
            variables={
                "projectId": self.project_id,
                "itemId": item_id,
                "fieldId": field.id,
            },
        )

    def add_blocked_by(self, issue_id: str, blocking_issue_id: str) -> None:
        """Mark an issue as blocked by another."""
        self.run_graphql(
            query=ADD_BLOCKED_BY_MUTATION,
            variables={"issueId": issue_id, "blockingIssueId": blocking_issue_id},
        )

    def remove_blocked_by(self, issue_id: str, blocking_issue_id: str) -> None:
        """Remove a "blocked by" link between two issues."""
        self.run_graphql(
            query=REMOVE_BLOCKED_BY_MUTATION,
            variables={"issueId": issue_id, "blockingIssueId": blocking_issue_id},
        )

    def fetch_item_order(self) -> list[str]:
        """Read every Project item id in manual (position) order."""
        item_ids: list[str] = []
        cursor = None
        while True:
            data = self.run_graphql(
                query=ITEM_ORDER_QUERY,
                variables={"projectId": self.project_id, "cursor": cursor},
            )
            connection = data["node"]["items"]
            item_ids.extend(node["id"] for node in connection["nodes"])
            if not connection["pageInfo"]["hasNextPage"]:
                return item_ids
            cursor = connection["pageInfo"]["endCursor"]

    def move_item_after(self, item_id: str, after_id: str | None) -> None:
        """Move an item after another, or to the top when after_id is None."""
        self.run_graphql(
            query=MOVE_ITEM_MUTATION,
            variables={
                "projectId": self.project_id,
                "itemId": item_id,
                "afterId": after_id,
            },
        )


def main() -> None:
    """Run the command named on the command line."""
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser(
        "backfill", help="Create or update the Project items that mirror tracks."
    )
    parser.parse_args()

    client = GitHubProjectClient(
        owner=OWNER,
        issue_repo=ISSUE_REPOSITORY,
        code_repo=REPOSITORY,
        project_number=PROJECT_NUMBER,
    )
    try:
        actions = backfill(
            client=client, tracks=load_tracks(conductor_dir=CONDUCTOR_DIR)
        )
    except (TrackParseError, ProjectSchemaError, GitHubError) as error:
        print(f"Error: {error}", file=sys.stderr)
        sys.exit(1)
    for action in actions:
        print(action)
    if not actions:
        print("No changes.")


if __name__ == "__main__":
    main()
