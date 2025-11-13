"""Tests for the mycli console entry."""


def test_main_sets_selected_project(monkeypatch):
    # Import target module
    import app

    # Prevent actual registry IO
    monkeypatch.setattr(app, "load_all_projects", lambda: None)

    # Ensure clean state
    import state as st
    st.projects.clear()
    st.selected_project = None

    # Mock project registration to succeed
    monkeypatch.setattr(
        app,
        "add_project_from_path",
        lambda path, name: {"success": True, "key": "tmp_project"},
    )

    # Mock discovery to be a no-op
    import backend.catalog as catalog
    monkeypatch.setattr(
        catalog, "refresh_catalog", lambda key: {"success": True, "count": 0}
    )

    # Skip launching the TUI
    monkeypatch.setenv("MYCLI_NO_UI", "1")

    # Run entrypoint
    app.main()

    # Verify selection was set
    assert st.selected_project == "tmp_project"
