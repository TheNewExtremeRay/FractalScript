"""
el_compiler.py — EzLibrary (.el) Command Compiler

Parses .el files — a dead-simple format for adding NEW COMMANDS to FractalScript.

Each .el file defines one or more commands that become available directly
in .ez scripts after importing.

Syntax:
  // comment

  Def {
    Library.name: "MyLibrary"
    Library.version: v1.0
    Package.identifier: "project.maker.mylib"
  }

  Cmd {
    Syntax: 'CommandName(param1) SubCommand(param2)'
    Func: 'print("param1 = " + param1)'
  }

Parameters in the Syntax template use {name} — they match quoted strings
or unquoted text from the command line. Quotes around a {param} in the
template are automatically stripped for matching.
"""

import os
import re


class ELError(Exception):
    pass


# ── Global overrides bridge ───────────────────────────────────
# Allows .el Func code to set runner globals via set_global().
# Runner reads and applies these each frame.

GLOBAL_OVERRIDES = []


# ── Parsing helpers ───────────────────────────────────────────

def _strip_comment(line):
    """Remove // comments from a line, preserving strings."""
    in_str = False
    ch = None
    for i, c in enumerate(line):
        if in_str:
            if c == ch:
                in_str = False
        elif c in ('"', "'"):
            in_str = True
            ch = c
        elif c == "/" and i + 1 < len(line) and line[i + 1] == "/":
            return line[:i].rstrip()
    return line


def _read_block_lines(lines, start):
    """Read lines from 'start' until matching close-brace. Returns (body_lines, end_index)."""
    depth = 1
    body = []
    i = start
    while i < len(lines) and depth > 0:
        raw = lines[i]
        opens = raw.count("{")
        closes = raw.count("}")
        depth += opens - closes
        if depth > 0:
            body.append(raw)
        i += 1
    if depth != 0:
        raise ELError("Unmatched braces")
    return body, i


def _parse_block_body(body_lines):
    """
    Parse key:value lines from a block body.
    Supports multi-line quoted values — if a value starts with ' or ",
    lines are consumed until the matching closing quote is found.
    Returns dict of {key: value}.
    """
    result = {}
    current_key = None
    current_val = []
    in_multiline = False
    multiline_quote = None

    for line in body_lines:
        if in_multiline:
            current_val.append(line)
            stripped = line.strip()
            if stripped.endswith(multiline_quote) or stripped.endswith(multiline_quote + ")"):
                in_multiline = False
            continue

        # Check if this line starts a new key: value
        m = re.match(r"\s*(\w[\w.]*)\s*:\s*(.*)", line)
        if m:
            # Save previous key if any
            if current_key is not None:
                result[current_key] = "\n".join(current_val).strip()

            current_key = m.group(1)
            val = m.group(2).strip()
            current_val = [val]

            # Check if value starts with a quote (multi-line)
            if val.startswith("'") or val.startswith('"'):
                multiline_quote = val[0]
                rest = val[1:]
                if multiline_quote not in rest:
                    in_multiline = True
        else:
            # Continuation of previous value
            if current_key is not None:
                current_val.append(line)

    # Save last key
    if current_key is not None:
        result[current_key] = "\n".join(current_val).strip()

    # Strip surrounding quotes from values
    for k in result:
        v = result[k]
        if (v.startswith('"') and v.endswith('"')) or \
           (v.startswith("'") and v.endswith("'")):
            v = v[1:-1]
        # Strip blank lines from multi-line Func code
        if k == "Func" and "\n" in v:
            lines = [l for l in v.split("\n") if l.strip()]
            v = "\n".join(lines)
        result[k] = v

    return result


# ── Main parser ───────────────────────────────────────────────

def parse_el_file(path):
    """
    Parse a .el file and return:
      def_info: dict with name, version, package
      cmds: list of dicts, each with 'syntax' and 'func' strings
    """
    if not os.path.exists(path):
        raise ELError(f"File not found: {path}")

    with open(path, "r", encoding="utf-8") as f:
        raw_lines = f.readlines()

    # Strip comments & blank lines, keep braces
    # Track multi-line quoted values so // inside Func code isn't stripped
    cleaned = []
    in_func_block = False
    func_quote = None
    for line in raw_lines:
        stripped_for_check = line.strip()

        # Track if we're inside a multi-line Func: '...' block
        if not in_func_block:
            # Check if this line starts a key with a quoted value
            km = re.match(r"\s*(\w[\w.]*)\s*:\s*(['\"])", line)
            if km:
                func_quote = km.group(2)
                val_start = line[km.end(2):]
                # If closing quote not on same line, we're in multi-line
                if func_quote not in val_start:
                    in_func_block = True
            line = _strip_comment(line)
        else:
            # Inside multi-line quoted value — don't strip comments
            # Check if this line ends the quoted value
            if stripped_for_check.endswith(func_quote) or stripped_for_check.endswith(func_quote + ")"):
                in_func_block = False
                func_quote = None

        if line.strip():
            cleaned.append(line)

    def_info = {"name": "", "version": "", "package": ""}
    cmds = []
    i = 0

    while i < len(cleaned):
        line = cleaned[i].strip()

        if line in ("Def {", "Def{"):
            body, i = _read_block_lines(cleaned, i + 1)
            parsed = _parse_block_body(body)
            def_info = {
                "name": parsed.get("Library.name", ""),
                "version": parsed.get("Library.version", ""),
                "package": parsed.get("Package.identifier", ""),
                "bypass": parsed.get("Library.bypass", "").lower() == "true",
            }
            continue

        if line in ("Cmd {", "Cmd{"):
            body, i = _read_block_lines(cleaned, i + 1)
            parsed = _parse_block_body(body)
            syntax = parsed.get("Syntax", "")
            func = parsed.get("Func", "")
            if syntax:
                cmds.append({"syntax": syntax, "func": func})
            continue

        i += 1

    return def_info, cmds


# ── Syntax matcher ────────────────────────────────────────────

def extract_params(syntax_template, command_line):
    """
    Match a command line against a syntax template and extract parameters.

    Template:   Fetch({url}) InDIR({path})
    Command:    Fetch("https://example.com/file.txt") InDIR("./downloads/")

    Returns dict of {param_name: value} or None if no match.

    Handles templates with or without quotes around {param}.
    """
    # Normalize: strip quotes immediately around {param} in the template
    # e.g. 'Fetch("{url}") InDIR("{path}")' -> 'Fetch({url}) InDIR({path})'
    normalized = re.sub(r'"\{(\w+)\}"', r'{\1}', syntax_template)
    normalized = re.sub(r"'\{(\w+)\}'", r'{\1}', normalized)

    # Build regex from normalized template
    regex_str = ""
    param_names = []
    i = 0
    while i < len(normalized):
        if normalized[i] == "{":
            end = normalized.find("}", i)
            if end != -1:
                name = normalized[i + 1:end]
                if name:
                    param_names.append(name)
                    # Match: "quoted" or 'quoted' or unquoted text (no spaces/parens)
                    regex_str += r'(?:' + r'"([^"]*)"' + r"|" + r"'([^']*)'" + r"|" + r"([^\s()]+)" + r')'
                    i = end + 1
                    continue
        regex_str += re.escape(normalized[i])
        i += 1

    # Ensure full match
    regex_str += "$"

    m = re.match(regex_str, command_line)
    if not m:
        return None

    # Extract captured groups
    result = {}
    group_idx = 1
    for name in param_names:
        for g in range(group_idx, group_idx + 3):
            if g <= m.lastindex and m.group(g) is not None:
                result[name] = m.group(g)
                break
        group_idx += 3

    return result if result is not None else None


# ── Command executor ──────────────────────────────────────────

def _make_set_global():
    """Create a set_global function that appends to GLOBAL_OVERRIDES."""
    def set_global(key, value):
        GLOBAL_OVERRIDES.append({"key": key, "value": value})
    return set_global


def exec_command(func_code, params, cmd_name, bypass=False):
    """Execute Func Python code with extracted params as local variables.
    If bypass=True, exec in runtime's namespace — function defs become overrides."""
    try:
        import runtime
        rt = runtime.get()
        if bypass and rt is not None:
            # Bypass mode: exec in runtime module namespace
            ns = vars(rt).copy()
            ns.update(params)
            ns["set_global"] = _make_set_global()
            ns["fetch"] = lambda url: _http_get(url)
            exec(func_code, ns)
            # Copy any new/changed attrs back to runtime module
            for k, v in ns.items():
                if not k.startswith("_") and callable(v):
                    setattr(rt, k, v)
        else:
            # Normal mode: isolated scope
            scope = {}
            scope.update(params)
            import builtins
            scope.update(vars(builtins))
            scope.update({
                "print": lambda *a, **kw: print("[CMD]", *a, **kw),
                "fetch": lambda url: _http_get(url),
                "os": __import__("os"),
                "json": __import__("json"),
                "sys": __import__("sys"),
                "set_global": _make_set_global(),
                "runtime": __import__("runtime"),
            })
            exec(func_code, scope)
    except Exception as e:
        print(f"[CMD ERROR] In command '{cmd_name}': {e}")
        import traceback
        traceback.print_exc()


def _http_get(url):
    """Simple HTTP GET helper."""
    try:
        import urllib.request
        with urllib.request.urlopen(url, timeout=15) as resp:
            return resp.read().decode("utf-8")
    except Exception as e:
        print(f"[CMD ERROR] fetch('{url}') failed: {e}")
        return None


# ── Public API ────────────────────────────────────────────────

def load_el_file(path):
    """
    Parse a .el file and return ready-to-use command data.

    Returns dict:
      {"info": {name, version, package, bypass},
       "commands": [{syntax, func, name, params, bypass}, ...]}
    """
    def_info, cmds = parse_el_file(path)
    lib_bypass = def_info.get("bypass", False)

    processed = []
    for c in cmds:
        name_match = re.match(r"(\w+)", c["syntax"])
        cmd_name = name_match.group(1) if name_match else "unknown"
        param_names = re.findall(r"\{(\w+)\}", c["syntax"])

        processed.append({
            "syntax": c["syntax"],
            "func": c["func"],
            "name": cmd_name,
            "params": param_names,
            "bypass": lib_bypass,
        })

    return {
        "info": def_info,
        "commands": processed,
    }


# ── Self-test ─────────────────────────────────────────────────

if __name__ == "__main__":
    print("=== EzLibrary (.el) Compiler Self-Test ===\n")

    test = """
Def {
  Library.name: "GitFetch"
  Library.version: v1.0
  Package.identifier: "project1.fractalscript.gitfetch"
}

Cmd {
  Syntax: 'Fetch("{url}") InDIR("{path}")'
  Func: 'print("Fetching from: " + url); print("To: " + path)'
}
"""
    import tempfile
    with tempfile.NamedTemporaryFile(mode="w", suffix=".el", delete=False, encoding="utf-8") as f:
        f.write(test)
        tmp = f.name

    data = load_el_file(tmp)
    os.unlink(tmp)

    print(f"Library: {data['info']['name']} v{data['info']['version']}")
    print(f"Package: {data['info']['package']}")
    for cmd in data["commands"]:
        print(f"\nCommand: {cmd['name']}")
        print(f"  Syntax: {cmd['syntax']}")
        print(f"  Params: {cmd['params']}")

    print("\n--- Testing command matching ---")
    test_line = 'Fetch("https://github.com/user/repo/file.txt") InDIR("./downloads/")'
    for cmd in data["commands"]:
        params = extract_params(cmd["syntax"], test_line)
        if params:
            print(f"  MATCHED! url={params['url']}, path={params['path']}")
        else:
            print(f"  NO MATCH for: {test_line}")

    print("\n=== Self-test complete ===")
