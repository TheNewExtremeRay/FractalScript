"""Quick parser test for app_compiler.py (no Pygame needed)."""
import sys, os, unittest.mock as mock

# Mock customtkinter so we can test parsing without a display
sys.modules['customtkinter'] = mock.MagicMock()

# Now import the compiler
import app_compiler as ac


def reset_state():
    """Reset all global state between tests."""
    ac.elements = []
    ac.app_initial_state = []
    ac.loop_actions = []
    ac.element_id_counter = [0]
    ac.active_events = set()
    ac.ever_active_events = set()
    ac.background_text = []
    ac.widget_map = {}
    ac.console_label = None
    ac.loop_after_id = None
    ac.app = None


def test_parse_user_app_file():
    """Parse the exact syntax from the user's App example4EzCode.ez file."""
    reset_state()
    ac.parse_app_file("Example4EzCode/App example4EzCode.ez")

    print(f"\n=== USER APP FILE TEST ===")
    print(f"Window size: {ac.window_w} x {ac.window_h}")
    print(f"Elements: {len(ac.elements)}")
    for e in ac.elements:
        print(f"  - {e.type} at ({e.x1},{e.y1})->({e.x2},{e.y2})  text='{e.text}' func='{e.function}' trigger='{e.trigger}'")
    print(f"Loop actions: {len(ac.loop_actions)}")
    for act in ac.loop_actions:
        print(f"  - {act['type']} event='{act.get('event','')}'")
        for k in ('actions', 'else_actions'):
            if k in act:
                for a in act[k]:
                    print(f"      {k}: {a['type']}")

    # Check initial UI element (the button)
    assert len(ac.elements) >= 1, "Should have at least 1 element (the button)"
    btn = ac.elements[0]
    assert btn.type == "Border", f"Expected Border element, got {btn.type}"
    assert btn.function == "Button", f"Expected Button function, got {btn.function}"
    assert btn.trigger == "Hello-Button-Press", f"Expected Hello-Button-Press trigger, got {btn.trigger}"

    # Check loop-action parsing
    assert len(ac.loop_actions) >= 1, "Should have at least 1 loop action"
    assert ac.loop_actions[0]['type'] == 'if_event', "Expected if_event action"
    assert ac.loop_actions[0]['event'] == 'Hello-Button-Press', "Expected Hello-Button-Press event"

    # Check if-block actions (say + set Text)
    if_actions = ac.loop_actions[0]['actions']
    assert len(if_actions) >= 2, f"Expected >=2 if-actions, got {len(if_actions)}"
    assert if_actions[0]['type'] == 'say', f"Expected say as first action, got {if_actions[0]['type']}"
    assert if_actions[0]['text'] == 'Hello World!'
    assert if_actions[1]['type'] == 'set_element', f"Expected set_element as second action, got {if_actions[1]['type']}"
    assert if_actions[1]['elem_type'] == 'Text'
    assert if_actions[1]['x'] == 300
    assert if_actions[1]['y'] == 80
    assert if_actions[1]['content'] == 'Hello, World!'

    # Check else-block actions (reset)
    else_actions = ac.loop_actions[0].get('else_actions', [])
    assert len(else_actions) >= 1, "Should have at least 1 else action (RESET)"
    assert else_actions[0]['type'] == 'reset', f"Expected reset in else, got {else_actions[0]['type']}"

    print("=== USER APP FILE TEST PASSED ===")


def test_parse_example_app():
    """Parse the reference example.app file and verify structure."""
    reset_state()
    ac.parse_app_file("Example4EzCode/example.app")

    print(f"\n=== EXAMPLE APP TEST ===")
    print(f"Window size: {ac.window_w} x {ac.window_h}")
    print(f"Elements: {len(ac.elements)}")
    for e in ac.elements:
        print(f"  - {e.type} at ({e.x1},{e.y1})->({e.x2},{e.y2})  text='{e.text}' func='{e.function}' trigger='{e.trigger}'")
    print(f"Loop actions: {len(ac.loop_actions)}")
    for act in ac.loop_actions:
        print(f"  - {act['type']} event='{act.get('event','')}'")
        for k in ('actions', 'else_actions'):
            if k in act and act[k]:
                for a in act[k]:
                    print(f"      {k}: {a['type']}")

    # example.app has: a button + a status bar = 2 elements
    assert len(ac.elements) >= 2, f"Expected >=2 elements, got {len(ac.elements)}"

    # Should have 1 loop action (if_event with no else)
    assert len(ac.loop_actions) >= 1, "Expected at least 1 loop action"
    assert ac.loop_actions[0]['type'] == 'if_event', "Expected if_event action"
    assert ac.loop_actions[0]['event'] == 'Hello-Button-Press'

    # Check if-actions: say + 2x set_text + set_border
    if_actions = ac.loop_actions[0]['actions']
    assert len(if_actions) >= 2, f"Expected >=2 if-actions, got {len(if_actions)}"
    assert if_actions[0]['type'] == 'say', f"Expected say, got {if_actions[0]['type']}"

    # example.app has no else
    else_actions = ac.loop_actions[0].get('else_actions', [])
    assert len(else_actions) == 0, f"Expected no else actions, got {len(else_actions)}"

    print("=== EXAMPLE APP TEST PASSED ===")


def test_event_persistence():
    """Test that ever_active_events prevents else from running after event fires."""
    reset_state()
    ac.parse_app_file("Example4EzCode/App example4EzCode.ez")

    # Simulate button click → event fires
    ac._on_trigger_event("Hello-Button-Press")
    assert "Hello-Button-Press" in ac.active_events

    # One tick: should execute if-branch, consume event, add to ever_active
    ac._process_tick()
    assert "Hello-Button-Press" not in ac.active_events  # consumed
    assert "Hello-Button-Press" in ac.ever_active_events  # marked

    # The Text element should now be in elements
    texts = [e for e in ac.elements if e.type == "Text"]
    assert len(texts) >= 1, f"Expected at least 1 Text element after event, got {len(texts)}"
    assert texts[0].text == "Hello, World!"
    assert texts[0].x1 == 300
    assert texts[0].y1 == 80

    # Next tick: event not active, but IS in ever_active → else NOT executed
    ac._process_tick()
    texts_after = [e for e in ac.elements if e.type == "Text"]
    assert len(texts_after) >= 1, "Text should persist after 2nd tick (else should not reset)"

    print("=== EVENT PERSISTENCE TEST PASSED ===")


def test_reset_clears_ever_active():
    """Test that reset_app() clears ever_active_events for clean restart."""
    reset_state()
    ac.parse_app_file("Example4EzCode/App example4EzCode.ez")

    # Fire event and process a tick
    ac._on_trigger_event("Hello-Button-Press")
    ac._process_tick()
    assert "Hello-Button-Press" in ac.ever_active_events

    # Reset the app
    ac.reset_app()
    assert "Hello-Button-Press" not in ac.ever_active_events  # cleared
    assert len(ac.background_text) == 0  # cleared

    print("=== RESET CLEARS EVER_ACTIVE TEST PASSED ===")


if __name__ == "__main__":
    test_parse_user_app_file()
    test_parse_example_app()
    test_event_persistence()
    test_reset_clears_ever_active()
    print("\n=== ALL TESTS PASSED ===")
