import importlib.util
import json
from pathlib import Path

import pytest


script_path = (
    Path(__file__).resolve().parent.parent
    / ".github"
    / "scripts"
    / "conductor_project.py"
)
spec = importlib.util.spec_from_file_location("conductor_project", script_path)
conductor_project = importlib.util.module_from_spec(spec)
spec.loader.exec_module(conductor_project)


def get_track(tracks, track_id):
    return next(track for track in tracks if track.id == track_id)


def test_load_tracks_returns_every_track_sorted_by_id(conductor_dir):
    tracks = conductor_project.load_tracks(conductor_dir=conductor_dir)

    assert [track.id for track in tracks] == [
        "alpha_20260101",
        "beta_20260102",
        "gamma_20260103",
    ]


def test_load_tracks_reads_metadata(conductor_dir):
    alpha = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="alpha_20260101",
    )

    assert alpha.type == "feature"
    assert alpha.status == "in_progress"
    assert alpha.initiative == "big_push"
    assert alpha.depends_on == ("beta_20260102",)


def test_load_tracks_defaults_optional_metadata(conductor_dir):
    gamma = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="gamma_20260103",
    )

    assert gamma.initiative is None
    assert gamma.depends_on == ()


def test_load_tracks_takes_titles_from_registry(conductor_dir):
    tracks = conductor_project.load_tracks(conductor_dir=conductor_dir)

    assert get_track(tracks=tracks, track_id="alpha_20260101").title == "Alpha Feature"
    assert get_track(tracks=tracks, track_id="beta_20260102").title == "Beta Fix"


def test_load_tracks_falls_back_to_id_for_unregistered_title(conductor_dir):
    gamma = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="gamma_20260103",
    )

    assert gamma.title == "gamma_20260103"


def test_load_tracks_reads_phases(conductor_dir):
    alpha = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="alpha_20260101",
    )

    assert alpha.phases == (
        conductor_project.Phase(name="Phase 1: Setup", is_complete=True),
        conductor_project.Phase(name="Phase 2: Build", is_complete=False),
        conductor_project.Phase(name="Phase 3: Ship", is_complete=False),
    )


def test_current_phase_is_first_incomplete_phase(conductor_dir):
    alpha = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="alpha_20260101",
    )

    assert alpha.current_phase == "Phase 2: Build"


def test_current_phase_is_none_when_every_phase_is_complete(conductor_dir):
    beta = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="beta_20260102",
    )

    assert beta.current_phase is None


def test_current_phase_is_none_without_phases(conductor_dir):
    gamma = get_track(
        tracks=conductor_project.load_tracks(conductor_dir=conductor_dir),
        track_id="gamma_20260103",
    )

    assert gamma.phases == ()
    assert gamma.current_phase is None


def test_load_tracks_rejects_metadata_without_id(conductor_dir):
    metadata_path = conductor_dir / "tracks" / "gamma_20260103" / "metadata.json"
    metadata_path.write_text(json.dumps({"type": "chore", "status": "new"}))

    with pytest.raises(conductor_project.TrackParseError, match="gamma_20260103"):
        conductor_project.load_tracks(conductor_dir=conductor_dir)


def test_load_tracks_rejects_id_that_does_not_match_directory(conductor_dir):
    metadata_path = conductor_dir / "tracks" / "gamma_20260103" / "metadata.json"
    metadata_path.write_text(
        json.dumps({"id": "other", "type": "chore", "status": "new"})
    )

    with pytest.raises(conductor_project.TrackParseError, match="other"):
        conductor_project.load_tracks(conductor_dir=conductor_dir)


def test_load_tracks_reads_the_real_conductor_directory():
    conductor_dir = Path(__file__).resolve().parent.parent / "conductor"

    tracks = conductor_project.load_tracks(conductor_dir=conductor_dir)

    assert tracks
    assert all(track.title != track.id for track in tracks)
