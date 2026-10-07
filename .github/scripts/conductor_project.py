"""Mirror Conductor track state into the fukalite GitHub Project.

Trial tooling for conductor/tracks/github_project_trial_20261007. The files
under conductor/ stay the source of truth; this script reads them and
mirrors track state into the Project.
"""

import dataclasses
import json
import re
from pathlib import Path


CONDUCTOR_DIR = Path(__file__).resolve().parent.parent.parent / "conductor"
REGISTRY_FILE = "tracks.md"
METADATA_FILE = "metadata.json"
PLAN_FILE = "plan.md"

REGISTRY_ENTRY_PATTERN = re.compile(
    r"\*\*Track: (?P<title>.+?)\*\*\s*\n\s*\*Link: \[[^\]]*\]\((?:conductor/)?tracks/(?P<id>[^/]+)/"
)
PHASE_HEADING_PATTERN = re.compile(
    r"^## (?P<name>Phase .+?)(?:\s*\[checkpoint: [^\]]*\])?\s*$"
)
OPEN_TASK_PATTERN = re.compile(r"^\s*- \[[ ~]\]")


class TrackParseError(Exception):
    """A track's files cannot be read into a Track."""


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

    @property
    def current_phase(self) -> str | None:
        """The name of the first incomplete phase, or None when there is none."""
        return next(
            (phase.name for phase in self.phases if not phase.is_complete), None
        )


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
    plan_path = track_dir / PLAN_FILE
    plan_text = plan_path.read_text() if plan_path.exists() else ""
    return Track(
        id=track_id,
        title=titles.get(track_id, track_id),
        type=metadata["type"],
        status=metadata["status"],
        initiative=metadata.get("initiative"),
        depends_on=tuple(metadata.get("depends_on", ())),
        phases=parse_phases(text=plan_text),
    )


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
