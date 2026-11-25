# FractalScript Library Making Guide

Create libraries for FractalScript in two ways:

- **Python (`.py`)** — full Python power, called via `call(Lib[...] {...})`
- **EzLibrary (`.el`)** — define new *commands* that become part of the FractalScript language

---

## EzLibrary (`.el`) — Add New Commands

`.el` files let you **add new commands** to FractalScript. After importing, those commands can be used directly in `.ez` scripts as if they were built-in.

### The Format

```el
// Comment

Def {
  Library.name: "YourLib"
  Library.version: v1.0
  Package.identifier: "yourname.project.yourlib"
}

Cmd {
  Syntax: 'CommandName("{param1}") SubCommand("{param2}")'
  Func: 'print("param1 = " + param1)'
}
```

- **`Def { }`** — library metadata (required, one per file)
- **`Cmd { }`** — a command definition (as many as you want)
- **`Syntax:`** — how the command looks in `.ez` scripts, with `{param}` placeholders
- **`Func:`** — Python code that runs when the command matches

### Real Example: `gitfetch.el`

```el
Def {
  Library.name: "GitFetch"
  Library.version: v1.0
  Package.identifier: "project1.fractalscript.gitfetch"
}

Cmd {
  Syntax: 'Fetch("{url}") InDIR("{path}")'
  Func: '
import os, urllib.request
filename = url.split("/")[-1]
os.makedirs(path, exist_ok=True)
save_path = os.path.join(path, filename)
print("Downloading: " + url)
urllib.request.urlretrieve(url, save_path)
print("Saved to: " + save_path)
'
}
```

### Using It in FractalScript

```
import gitfetch.el

loop-MyLoop
  Fetch("https://github.com/user/repo/readme.md") InDIR("./downloads/")
loop-MyLoop-end
```

That's it. The `{url}` and `{path}` placeholders from the `Syntax` template automatically extract the values from the command line and make them available as Python variables in your `Func` code.

### How It Works

1. You write `import gitfetch.el` in your `.ez` script
2. The `.el` file is parsed: `Def { }` gives metadata, `Cmd { }` defines the command syntax
3. The command `Fetch("{url}") InDIR("{path}")` is registered with the engine
4. When the parser sees `Fetch("...") InDIR("...")`, it matches the syntax template
5. It extracts `url` and `path` from the quoted strings
6. It executes the `Func` Python code with those variables set

### Syntax Rules

| Rule | Example |
|------|---------|
| Parameters in `{ }` | `Fetch("{url}")` |
| Quoted strings match parameters | `Fetch("https://..."` -> `url` = `"https://..."` |
| Multiple parts in one command | `Fetch(url) InDIR(path)` |
| Python code in `Func:` | Multi-line or single-line, indentation matters |
| `print()` in Func | Use `print()` — output appears in terminal |

### Built-in Helpers in Func code

Your `Func:` Python code automatically has access to:

- **The extracted parameters** as named variables (e.g. `url`, `path`)
- **`print()`** — prints to terminal
- **`fetch(url)`** — simple HTTP GET helper
- **`set_global(key, value)`** — set runner globals (for bypass mode)
- **All Python builtins** — `str()`, `int()`, `open()`, `import`, etc.
- **Any Python module** — `import os`, `import urllib.request`, etc.

### Bypass Mode

If your library needs to override the rendering loop (e.g. custom draw functions), add `Library.bypass: true` to the `Def` block:

```el
Def {
  Library.name: "MyOverlay"
  Library.version: v1.0
  Package.identifier: "my.overlay.lib"
  Library.bypass: true
}
```

In bypass mode, `Func` code runs in the runtime module namespace. Use `runtime.set_override("draw_grid", my_func)` to override rendering.

---

## Python Libraries (`.py`)

For complex logic, write a standard Python file.

### Minimal Example

```python
# libraries/my_tools.py
def flash_grid():
    print("[my_tools] Grid flash!")
```

### Calling from FractalScript

```
call(Lib[my_tools] {flash_grid})
```

### Rules

| Rule | Why |
|------|-----|
| File goes in `libraries/` | Handler only scans this folder |
| Function runs every frame it's called | Inside a loop — keep it fast |
| Use `print()` for output | Return values not yet captured |
| Import any Python library | Everything is available |

---

## Testing Your Library

```bash
# List all libraries
python library_handler.py

# Test .el self-test
python el_compiler.py
```

---

## Troubleshooting

| Problem | Fix |
|---------|-----|
| Command not found | Check `Syntax:` template matches your command exactly |
| Parameters empty | Make sure `{name}` in Syntax matches variable name in `Func:` |
| `import` fails | Check the file exists in `libraries/` folder |
| Python error in Func | Check the terminal for traceback |
