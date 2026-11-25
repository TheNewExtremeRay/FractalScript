"""
library_handler.py — FractalScript Library System

Discovers Python (.py) and EzLibrary (.el) files in the libraries/ folder.
  - .py files: standard Python modules (callable via call(Lib[...] {...}))
  - .el files: command-definition files (adds new syntax to FractalScript)
"""

import os
import sys
import importlib
import inspect

LIBRARIES_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "libraries")

_py_loaded = {}
_el_loaded = {}

# Global registry of .el commands
# Format: [{"syntax":..., "func":..., "name":..., "params":[...], "lib":...}, ...]
REGISTERED_COMMANDS = []

if os.path.isdir(LIBRARIES_DIR) and LIBRARIES_DIR not in sys.path:
    sys.path.insert(0, LIBRARIES_DIR)


def discover() -> list:
    """Return list of available library names (without extension)."""
    if not os.path.isdir(LIBRARIES_DIR):
        return []
    libs = []
    for f in sorted(os.listdir(LIBRARIES_DIR)):
        if f == "__init__.py":
            continue
        if f.endswith(".py"):
            libs.append(f[:-3])
        elif f.endswith(".el"):
            libs.append(f[:-3])
    return libs


def _find_file(name):
    py_path = os.path.join(LIBRARIES_DIR, name + ".py")
    if os.path.exists(py_path):
        return py_path, "py"
    el_path = os.path.join(LIBRARIES_DIR, name + ".el")
    if os.path.exists(el_path):
        return el_path, "el"
    return None, None


def load(name: str):
    """Load a library by name. Returns module for .py or data dict for .el."""
    if name in _py_loaded:
        return _py_loaded[name]
    if name in _el_loaded:
        return _el_loaded[name]

    filepath, lib_type = _find_file(name)
    if filepath is None:
        print(f"[LIB] Library '{name}' not found (checked .py and .el)")
        return None

    if lib_type == "py":
        try:
            mod = importlib.import_module(name)
            _py_loaded[name] = mod
            print(f"[LIB] Loaded Python library: {name}")
            return mod
        except Exception as e:
            print(f"[LIB ERROR] Could not load Python library '{name}': {e}")
            return None
    else:
        try:
            import el_compiler as elc
            data = elc.load_el_file(filepath)
            if not data["commands"]:
                print(f"[LIB] .el file '{name}' has no commands (empty or wrong format)")
                _el_loaded[name] = data
                return data
            count = 0
            for cmd in data["commands"]:
                cmd["lib"] = name
                REGISTERED_COMMANDS.append(cmd)
                count += 1
            _el_loaded[name] = data
            print(f"[LIB] Loaded .el library: {name} ({count} commands registered)")
            return data
        except Exception as e:
            print(f"[LIB ERROR] Could not load .el library '{name}': {e}")
            import traceback
            traceback.print_exc()
            return None


def call(lib_name, func_name, *args):
    """Call a function from a .py library. Passes runner as keyword arg if accepted."""
    mod = _py_loaded.get(lib_name) or load(lib_name)
    if mod is None:
        print(f"[LIB] Library '{lib_name}' not loaded")
        return None
    if isinstance(mod, dict):
        print(f"[LIB] '{lib_name}' is a .el command library — use commands directly")
        return None
    func = getattr(mod, func_name, None)
    if func is None:
        print(f"[LIB] Function '{func_name}' not found in '{lib_name}'")
        avail = [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith("_")]
        print(f"  Available: {', '.join(avail)}")
        return None
    try:
        import runtime
        rt = runtime.get()
        sig = inspect.signature(func)
        if "runner" in sig.parameters:
            return func(*args, runner=rt)
        return func(*args)
    except Exception as e:
        print(f"[LIB ERROR] '{lib_name}.{func_name}({args})': {e}")
        return None


def list_functions(lib_name):
    """List functions/commands in a library."""
    if lib_name in _py_loaded:
        mod = _py_loaded[lib_name]
        return [n for n in dir(mod) if callable(getattr(mod, n)) and not n.startswith("_")]
    if lib_name in _el_loaded:
        return [c["name"] + "(" + ", ".join(c["params"]) + ")" for c in _el_loaded[lib_name]["commands"]]
    return []


if __name__ == "__main__":
    print("FractalScript Library Handler")
    print(f"  Directory: {LIBRARIES_DIR}")
    found = discover()
    if found:
        print(f"  Libraries: {', '.join(found)}")
        for lib in found:
            funcs = list_functions(lib)
            if funcs:
                print(f"    {lib}: {', '.join(funcs)}")
    else:
        print("  No libraries found.")
    if REGISTERED_COMMANDS:
        print(f"  Registered commands: {len(REGISTERED_COMMANDS)}")
        for c in REGISTERED_COMMANDS:
            print(f"    {c['name']} (from {c['lib']})")
