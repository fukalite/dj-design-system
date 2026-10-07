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


def test_load_tracks_reads_spec_and_plan(conductor_dir):
    tracks = conductor_project.load_tracks(conductor_dir=conductor_dir)
    alpha = get_track(tracks=tracks, track_id="alpha_20260101")
    gamma = get_track(tracks=tracks, track_id="gamma_20260103")

    assert alpha.spec == "# Specification: Alpha\n"
    assert alpha.plan.startswith("# Implementation Plan\n\n## Phase 1: Setup")
    assert gamma.spec == ""


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


def make_track(**overrides):
    values = {
        "id": "alpha_20260101",
        "title": "Alpha Feature",
        "type": "feature",
        "status": "new",
        "initiative": None,
        "depends_on": (),
        "phases": (
            conductor_project.Phase(name="Phase 1: Setup", is_complete=True),
            conductor_project.Phase(name="Phase 2: Build", is_complete=False),
        ),
        "spec": "# Specification: Alpha\n\nBuild the alpha.\n",
        "plan": "# Implementation Plan\n\n## Phase 2: Build\n- [ ] Task: Build it\n",
    }
    values.update(overrides)
    return conductor_project.Track(**values)


def make_field(name, options=()):
    return conductor_project.ProjectField(
        id=f"field-{name}",
        name=name,
        options={option: f"option-{option}" for option in options},
    )


def make_schema():
    fields = [
        make_field(name="Track ID"),
        make_field(name="Current phase"),
        make_field(
            name="Status",
            options=("Backlog", "Ready", "In progress", "In review", "Done"),
        ),
        make_field(
            name="Track type", options=("feature", "bugfix", "chore", "project")
        ),
        make_field(name="Initiative", options=("gallery_rebuild",)),
    ]
    return conductor_project.ProjectSchema(
        project_id="project-1", fields={field.name: field for field in fields}
    )


def make_synced_issue(track, **overrides):
    field_values = conductor_project.build_field_values(
        track=track, current_status=None, pull_requests=()
    )
    values = {
        "issue_id": f"issue-{track.id}",
        "track_id": track.id,
        "title": track.title,
        "body": conductor_project.build_issue_body(track=track),
        "is_closed": track.status == "completed",
        "blocked_by_ids": frozenset(),
        "item_id": f"item-{track.id}",
        "field_values": {
            name: value for name, value in field_values.items() if value is not None
        },
    }
    values.update(overrides)
    return conductor_project.MirroredIssue(**values)


def test_build_issue_body_holds_marker_spec_and_plan():
    body = conductor_project.build_issue_body(track=make_track())

    assert body.startswith("<!-- conductor-track: alpha_20260101 -->\n")
    assert "conductor/tracks/alpha_20260101" in body
    assert body.index("# Specification: Alpha") < body.index("# Implementation Plan")
    assert "- [ ] Task: Build it" in body


def test_build_issue_body_omits_missing_documents():
    body = conductor_project.build_issue_body(track=make_track(spec="", plan=""))

    assert "---" not in body


def test_build_issue_body_rejects_bodies_over_the_issue_limit():
    with pytest.raises(conductor_project.TrackParseError, match="alpha_20260101"):
        conductor_project.build_issue_body(track=make_track(spec="x" * 70_000))


def test_parse_track_marker_reads_marker():
    body = conductor_project.build_issue_body(track=make_track())

    assert conductor_project.parse_track_marker(body=body) == "alpha_20260101"


def test_parse_track_marker_returns_none_without_marker():
    assert conductor_project.parse_track_marker(body="Just an issue") is None


def test_build_field_values_maps_metadata():
    values = conductor_project.build_field_values(
        track=make_track(initiative="gallery_rebuild"),
        current_status=None,
        pull_requests=(),
    )

    assert values == {
        "Track ID": "alpha_20260101",
        "Track type": "feature",
        "Initiative": "gallery_rebuild",
        "Current phase": "Phase 2: Build",
        "Status": "Backlog",
    }


def test_build_field_values_clears_empty_values():
    values = conductor_project.build_field_values(
        track=make_track(phases=()), current_status=None, pull_requests=()
    )

    assert values["Initiative"] is None
    assert values["Current phase"] is None


@pytest.mark.parametrize(
    ("status", "current_status", "expected"),
    [
        ("new", "Ready", "Ready"),
        ("new", "Done", "Backlog"),
        ("in_progress", "In review", "In review"),
        ("in_progress", "Backlog", "In progress"),
        ("completed", "In review", "Done"),
    ],
)
def test_build_field_values_keeps_status_within_its_columns(
    status, current_status, expected
):
    values = conductor_project.build_field_values(
        track=make_track(status=status), current_status=current_status, pull_requests=()
    )

    assert values["Status"] == expected


def test_build_field_values_rejects_unknown_status():
    with pytest.raises(conductor_project.TrackParseError, match="paused"):
        conductor_project.build_field_values(
            track=make_track(status="paused"), current_status=None, pull_requests=()
        )


def make_pull_request(is_draft, body="Implements alpha_20260101."):
    return conductor_project.PullRequest(number=1, is_draft=is_draft, body=body)


@pytest.mark.parametrize(
    ("status", "draft_states", "expected"),
    [
        ("new", (True,), "In progress"),
        ("new", (False,), "In review"),
        ("in_progress", (False, False), "In review"),
        ("in_progress", (False, True), "In progress"),
        ("completed", (True,), "Done"),
    ],
)
def test_build_field_values_follows_open_pull_requests(status, draft_states, expected):
    values = conductor_project.build_field_values(
        track=make_track(status=status),
        current_status="Ready",
        pull_requests=tuple(
            make_pull_request(is_draft=is_draft) for is_draft in draft_states
        ),
    )

    assert values["Status"] == expected


def test_find_linked_pull_requests_matches_track_id_in_body():
    linked = make_pull_request(is_draft=True)
    other = make_pull_request(is_draft=True, body="Implements beta_20260102.")
    prefixed = make_pull_request(is_draft=True, body="See xalpha_20260101.")

    assert conductor_project.find_linked_pull_requests(
        track_id="alpha_20260101", pull_requests=[linked, other, prefixed]
    ) == (linked,)


def test_backfill_moves_status_for_an_open_pull_request(make_fake_project_client):
    track = make_track()
    client = make_fake_project_client(
        schema=make_schema(),
        issues=[make_synced_issue(track=track)],
        pull_requests=[make_pull_request(is_draft=False)],
    )

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == [
        ("set_field_value", "item-alpha_20260101", "Status", "In review")
    ]


def test_backfill_creates_and_fills_a_missing_issue(make_fake_project_client):
    client = make_fake_project_client(schema=make_schema(), issues=[])

    conductor_project.backfill(client=client, tracks=[make_track()])

    assert client.calls == [
        ("create_issue", "Alpha Feature"),
        ("add_to_project", "issue-1"),
        ("set_field_value", "item-issue-1", "Track ID", "alpha_20260101"),
        ("set_field_value", "item-issue-1", "Track type", "feature"),
        ("set_field_value", "item-issue-1", "Current phase", "Phase 2: Build"),
        ("set_field_value", "item-issue-1", "Status", "Backlog"),
    ]


def test_backfill_leaves_a_synced_issue_alone(make_fake_project_client):
    track = make_track()
    client = make_fake_project_client(
        schema=make_schema(), issues=[make_synced_issue(track=track)]
    )

    actions = conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == []
    assert actions == []


def test_backfill_keeps_status_moved_within_its_columns(make_fake_project_client):
    track = make_track()
    issue = make_synced_issue(track=track)
    issue.field_values["Status"] = "Ready"
    client = make_fake_project_client(schema=make_schema(), issues=[issue])

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == []


def test_backfill_updates_changed_title_and_fields(make_fake_project_client):
    track = make_track()
    issue = make_synced_issue(track=track, title="Old title")
    issue.field_values["Current phase"] = "Phase 1: Setup"
    client = make_fake_project_client(schema=make_schema(), issues=[issue])

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == [
        ("update_issue", "issue-alpha_20260101"),
        ("set_field_value", "item-alpha_20260101", "Current phase", "Phase 2: Build"),
    ]


def test_backfill_clears_a_field_with_no_value(make_fake_project_client):
    track = make_track()
    issue = make_synced_issue(track=track)
    issue.field_values["Initiative"] = "gallery_rebuild"
    client = make_fake_project_client(schema=make_schema(), issues=[issue])

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == [("clear_field_value", "item-alpha_20260101", "Initiative")]


def test_backfill_adds_an_existing_issue_to_the_project(make_fake_project_client):
    track = make_track()
    issue = make_synced_issue(track=track, item_id=None, field_values={})
    client = make_fake_project_client(schema=make_schema(), issues=[issue])

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls[0] == ("add_to_project", "issue-alpha_20260101")


@pytest.mark.parametrize(
    ("status", "is_closed", "expected_closed"),
    [("completed", False, True), ("new", True, False)],
)
def test_backfill_closes_and_reopens_issues(
    make_fake_project_client, status, is_closed, expected_closed
):
    track = make_track(status=status)
    issue = make_synced_issue(track=track, is_closed=is_closed)
    client = make_fake_project_client(schema=make_schema(), issues=[issue])

    conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == [
        ("set_issue_closed", "issue-alpha_20260101", expected_closed)
    ]


def test_backfill_syncs_blocked_by(make_fake_project_client):
    beta = make_track(id="beta_20260102", title="Beta")
    gamma = make_track(id="gamma_20260103", title="Gamma")
    alpha = make_track(depends_on=("beta_20260102",))
    alpha_issue = make_synced_issue(
        track=alpha, blocked_by_ids=frozenset({"issue-gamma_20260103"})
    )
    client = make_fake_project_client(
        schema=make_schema(),
        issues=[
            make_synced_issue(track=beta),
            make_synced_issue(track=gamma),
            alpha_issue,
        ],
    )

    conductor_project.backfill(client=client, tracks=[alpha, beta, gamma])

    assert client.calls == [
        ("add_blocked_by", "issue-alpha_20260101", "issue-beta_20260102"),
        ("remove_blocked_by", "issue-alpha_20260101", "issue-gamma_20260103"),
    ]


def test_order_tracks_puts_blockers_first():
    tracks = [
        make_track(id="c_3", depends_on=("b_2",)),
        make_track(id="d_4"),
        make_track(id="b_2", depends_on=("a_1", "archived_0")),
        make_track(id="a_1"),
    ]

    ordered = conductor_project.order_tracks(tracks=tracks)

    assert [track.id for track in ordered] == ["a_1", "d_4", "b_2", "c_3"]


def test_order_tracks_rejects_dependency_cycles():
    tracks = [
        make_track(id="a_1", depends_on=("b_2",)),
        make_track(id="b_2", depends_on=("a_1",)),
    ]

    with pytest.raises(conductor_project.TrackParseError, match="cycle"):
        conductor_project.order_tracks(tracks=tracks)


def test_backfill_orders_items_so_blockers_come_first(make_fake_project_client):
    beta = make_track(id="beta_20260102", title="Beta")
    gamma = make_track(id="gamma_20260103", title="Gamma")
    alpha = make_track(depends_on=("beta_20260102",))
    client = make_fake_project_client(
        schema=make_schema(),
        issues=[
            make_synced_issue(track=alpha),
            make_synced_issue(track=gamma),
            make_synced_issue(track=beta),
        ],
    )
    client.item_order.insert(0, "untracked-item")

    actions = conductor_project.backfill(client=client, tracks=[alpha, beta, gamma])

    assert client.item_order == [
        "item-beta_20260102",
        "item-gamma_20260103",
        "untracked-item",
        "item-alpha_20260101",
    ]
    assert "beta_20260102: moved to position 1" in actions


def test_backfill_leaves_ordered_items_alone(make_fake_project_client):
    beta = make_track(id="beta_20260102", title="Beta")
    alpha = make_track(depends_on=("beta_20260102",))
    client = make_fake_project_client(
        schema=make_schema(),
        issues=[make_synced_issue(track=beta), make_synced_issue(track=alpha)],
    )

    conductor_project.backfill(client=client, tracks=[alpha, beta])

    assert not [call for call in client.calls if call[0] == "move_item_after"]


def test_backfill_reports_dependencies_on_untracked_tracks(make_fake_project_client):
    track = make_track(depends_on=("archived_20250101",))
    client = make_fake_project_client(
        schema=make_schema(), issues=[make_synced_issue(track=track)]
    )

    actions = conductor_project.backfill(client=client, tracks=[track])

    assert client.calls == []
    assert actions == [
        "alpha_20260101: skipped dependency on archived_20250101 (no mirrored issue)"
    ]


def test_backfill_rejects_values_missing_from_the_project(make_fake_project_client):
    client = make_fake_project_client(schema=make_schema(), issues=[])

    with pytest.raises(conductor_project.ProjectSchemaError, match="new_initiative"):
        conductor_project.backfill(
            client=client, tracks=[make_track(initiative="new_initiative")]
        )

    assert client.calls == []


ISSUES_RESPONSE = {
    "data": {
        "repository": {
            "issues": {
                "pageInfo": {"hasNextPage": False, "endCursor": None},
                "nodes": [
                    {
                        "id": "issue-1",
                        "title": "Alpha Feature",
                        "body": "<!-- conductor-track: alpha_20260101 -->",
                        "state": "CLOSED",
                        "blockedBy": {"nodes": [{"id": "issue-2"}]},
                        "projectItems": {
                            "nodes": [
                                {
                                    "id": "other-item",
                                    "project": {"id": "other-project"},
                                    "fieldValues": {"nodes": []},
                                },
                                {
                                    "id": "item-1",
                                    "project": {"id": "project-1"},
                                    "fieldValues": {
                                        "nodes": [
                                            {},
                                            {
                                                "text": "alpha_20260101",
                                                "field": {"name": "Track ID"},
                                            },
                                            {
                                                "name": "Done",
                                                "field": {"name": "Status"},
                                            },
                                        ]
                                    },
                                },
                            ]
                        },
                    },
                    {
                        "id": "issue-3",
                        "title": "Untracked",
                        "body": "No marker",
                        "state": "OPEN",
                        "blockedBy": {"nodes": []},
                        "projectItems": {"nodes": []},
                    },
                ],
            }
        }
    }
}


def test_fetch_mirrored_issues_reads_issues_and_project_fields(mocker):
    run = mocker.patch.object(
        conductor_project.subprocess,
        "run",
        return_value=mocker.Mock(stdout=json.dumps(ISSUES_RESPONSE)),
    )
    client = conductor_project.GitHubProjectClient(
        owner="fukalite",
        issue_repo="dj-design-system-conductor",
        code_repo="dj-design-system",
        project_number=2,
    )
    client.project_id = "project-1"

    issues = client.fetch_mirrored_issues()

    assert issues == [
        conductor_project.MirroredIssue(
            issue_id="issue-1",
            track_id="alpha_20260101",
            title="Alpha Feature",
            body="<!-- conductor-track: alpha_20260101 -->",
            is_closed=True,
            blocked_by_ids=frozenset({"issue-2"}),
            item_id="item-1",
            field_values={"Track ID": "alpha_20260101", "Status": "Done"},
        )
    ]
    assert run.call_args.kwargs["args"][:3] == ["gh", "api", "graphql"]


def test_fetch_open_pull_requests_reads_the_code_repository(mocker):
    response = {
        "data": {
            "repository": {
                "pullRequests": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [{"number": 7, "isDraft": True, "body": "alpha_20260101"}],
                }
            }
        }
    }
    run = mocker.patch.object(
        conductor_project.subprocess,
        "run",
        return_value=mocker.Mock(stdout=json.dumps(response)),
    )
    client = conductor_project.GitHubProjectClient(
        owner="fukalite",
        issue_repo="dj-design-system-conductor",
        code_repo="dj-design-system",
        project_number=2,
    )

    pull_requests = client.fetch_open_pull_requests()

    assert pull_requests == [
        conductor_project.PullRequest(number=7, is_draft=True, body="alpha_20260101")
    ]
    request = json.loads(run.call_args.kwargs["input"])
    assert request["variables"]["repo"] == "dj-design-system"


def test_fetch_item_order_reads_items_by_position(mocker):
    response = {
        "data": {
            "node": {
                "items": {
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                    "nodes": [{"id": "item-2"}, {"id": "item-1"}],
                }
            }
        }
    }
    mocker.patch.object(
        conductor_project.subprocess,
        "run",
        return_value=mocker.Mock(stdout=json.dumps(response)),
    )
    client = conductor_project.GitHubProjectClient(
        owner="fukalite",
        issue_repo="dj-design-system-conductor",
        code_repo="dj-design-system",
        project_number=2,
    )
    client.project_id = "project-1"

    assert client.fetch_item_order() == ["item-2", "item-1"]


def test_graphql_raises_on_gh_failure(mocker):
    mocker.patch.object(
        conductor_project.subprocess,
        "run",
        side_effect=conductor_project.subprocess.CalledProcessError(
            returncode=1, cmd="gh", stderr="bad scope"
        ),
    )
    client = conductor_project.GitHubProjectClient(
        owner="fukalite",
        issue_repo="dj-design-system-conductor",
        code_repo="dj-design-system",
        project_number=2,
    )
    client.project_id = "project-1"

    with pytest.raises(conductor_project.GitHubError, match="bad scope"):
        client.fetch_mirrored_issues()
