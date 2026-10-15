from pathlib import Path
from streamlit.testing.v1 import AppTest


def test_dashboard_controls_and_selection():
    app = AppTest.from_file(str(Path(__file__).resolve().parents[1] / "app/dashboard.py")).run(timeout=30)
    assert not app.exception
    app.button(key="artist_1").click().run()
    assert not app.exception
    app.button(key="toggle_genres").click().run()
    assert not app.exception
    app.text_area(key="rec_request").set_value("rainy night").run()
    assert not app.exception
    add = next(button for button in app.button if (button.key or "").startswith("add_"))
    add.click().run()
    assert not app.exception
    assert len(app.session_state["my_selection"]) == 1
    assert any(item.value == "Similar to your selection" for item in app.subheader)
    app.button(key="clear_selection").click().run()
    assert not app.exception
    assert app.session_state["my_selection"] == []
    app.button(key="manual_add_toggle").click().run()
    app.text_input(key="manual_search").set_value("[").run()
    assert not app.exception

