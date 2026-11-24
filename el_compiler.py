"""
el_compiler.py — EzLibrary (.el) Command Compiler

Parses .el files — a dead-simple format for adding NEW COMMANDS to EzCode.

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
    Supports multi-line values for Func — lines after Func: are included
    until the next key: line or end of block.
    Returns dict of {key: value}.
    """
    result = {}
    current_key = None
    current_val = []

    for line in body_lines:
        # Check if this line starts a new key: value
        m = re.match(r"(\w[\w.]*)\s*:\s*(.*)", line)
        if m:
            # Save previous key if any
            if current_key is not None:
                result[current_key] = "\n".join(current_val).strip()

            current_key = m.group(1)
            current_val = [m.group(2).strip()]
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
            result[k] = v[1:-1]

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
    cleaned = []
    for line in raw_lines:
        line = _strip_comment(line)
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
                    regex_str += r'"([^"]*)"|' + r"'([^']*)'|" + r"([^\s()]+)"
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

def exec_command(func_code, params, cmd_name):
    """Execute Func Python code with extracted params as local variables."""
    try:
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
      {"info": {name, version, package},
       "commands": [{syntax, func, name, params}, ...]}
    """
    def_info, cmds = parse_el_file(path)

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
  Package.identifier: "project1.ezcode.gitfetch"
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
