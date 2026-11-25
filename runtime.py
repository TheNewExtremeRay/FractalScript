"""
runtime.py — Shared runtime access for FractalScript libraries.

Import this in any .el or .py library to read/write ALL runner internals:
  grid, screen, cell_size, colors, variables, loop_blocks, etc.

Override API for bypass libraries:
  rt = runtime.get()
  runtime.set_override("draw_grid", my_custom_func)
  runtime.clear_override("draw_grid")
  runtime.clear_overrides()
"""

_proxy = None
_overrides = {}


def get():
    """Return the runner module proxy. Initialize with init() first."""
    return _proxy


def init(runner_module):
    """Called by the runner at startup to register itself."""
    global _proxy
    _proxy = runner_module


def set_override(name, func):
    """Register a function override (e.g. set_override('draw_grid', my_func))."""
    _overrides[name] = func


def clear_override(name):
    """Remove a specific override, restoring the default."""
    _overrides.pop(name, None)


def clear_overrides():
    """Remove all overrides, restoring all defaults."""
    _overrides.clear()


def get_override(name):
    """Get an override function by name, or None if not set."""
    return _overrides.get(name)
