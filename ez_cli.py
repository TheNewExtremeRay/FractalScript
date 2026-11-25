"""
ez_cli.py — FractalScript Terminal & Library Manager

Usage:
    ez              Open interactive terminal (in a new cmd window)
    ez lib <url>    Download and install a .el library
    ez run <file>   Run an .ez script
    ez libs         List installed libraries
    ez help         Show available commands
"""

import os
import sys
import urllib.request

FRACTALSCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
LIBRARIES_DIR = os.path.join(FRACTALSCRIPT_DIR, "libraries")


def _normalize_github_url(url):
    url = url.strip().strip("'\"")
    if "github.com" in url and "/blob/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/blob/", "/")
    if "github.com" in url and "/tree/" in url:
        url = url.replace("github.com", "raw.githubusercontent.com").replace("/tree/", "/")
    return url


def install_library(url):
    url = _normalize_github_url(url)
    filename = url.split("/")[-1]
    if not filename.endswith(".el"):
        print(f"  Error: URL must point to a .el file (got '{filename}')")
        return False
    save_path = os.path.join(LIBRARIES_DIR, filename)
    if os.path.exists(save_path):
        print(f"  '{filename}' already installed. Overwriting...")
    print(f"  Downloading: {url}")
    try:
        urllib.request.urlretrieve(url, save_path)
    except Exception as e:
        print(f"  Download failed: {e}")
        return False
    try:
        import el_compiler as elc
        data = elc.load_el_file(save_path)
        name = data["info"]["name"] or filename
        count = len(data["commands"])
        print(f"  Installed: {name} ({count} commands) -> {filename}")
        return True
    except Exception as e:
        print(f"  Warning: Installed but failed to validate: {e}")
        return True


def list_libraries():
    if not os.path.isdir(LIBRARIES_DIR):
        print("  No libraries directory found.")
        return
    libs = []
    for f in sorted(os.listdir(LIBRARIES_DIR)):
        if f == "__init__.py" or f.startswith("_"):
            continue
        if f.endswith(".py") or f.endswith(".el"):
            libs.append(f)
    if not libs:
        print("  No libraries installed.")
        return
    print("  Installed libraries:")
    for lib in libs:
        name = os.path.splitext(lib)[0]
        ext = os.path.splitext(lib)[1]
        print(f"    {name} ({ext[1:]})")


def run_script(filename):
    selector = os.path.join(FRACTALSCRIPT_DIR, "selector.py")
    if not os.path.exists(filename):
        print(f"  File not found: {filename}")
        return
    os.system(f'python "{selector}" "{filename}"')


def show_help():
    print("  Commands:")
    print("    lib <url>     Install a .el library from URL")
    print("    run <file>    Run a FractalScript script")
    print("    libs          List installed libraries")
    print("    clear         Clear the terminal")
    print("    help          Show this help message")
    print("    exit          Close the terminal")


def repl():
    print()
    print("  FractalScript Terminal")
    print("  Type 'help' for commands.")
    print()
    while True:
        try:
            raw = input("ez> ")
        except (EOFError, KeyboardInterrupt):
            print("\n  Bye!")
            break

        cmd = raw.strip()
        if not cmd:
            continue

        parts = cmd.split(None, 1)
        verb = parts[0].lower()
        arg = parts[1] if len(parts) > 1 else ""

        if verb in ("exit", "quit"):
            print("  Bye!")
            break
        elif verb == "help":
            show_help()
        elif verb == "libs":
            list_libraries()
        elif verb == "lib":
            if not arg:
                print("  Usage: lib <url>")
            else:
                install_library(arg)
        elif verb == "run":
            if not arg:
                print("  Usage: run <file.ez>")
            else:
                run_script(arg)
        elif verb == "clear":
            os.system("cls" if os.name == "nt" else "clear")
        else:
            print(f"  Unknown command: '{verb}'. Type 'help' for commands.")


def main():
    args = sys.argv[1:]

    if not args:
        repl()
        return

    command = args[0].lower()

    if command == "lib":
        if len(args) < 2:
            print("Usage: ez lib <url>")
            sys.exit(1)
        success = install_library(args[1])
        sys.exit(0 if success else 1)

    elif command == "run":
        if len(args) < 2:
            print("Usage: ez run <file.ez>")
            sys.exit(1)
        run_script(args[1])

    elif command == "libs":
        list_libraries()

    elif command == "help":
        print("Usage: ez [command]")
        print()
        print("Commands:")
        print("  (no args)           Open interactive terminal")
        print("  lib <url>           Install a .el library from URL")
        print("  run <file.ez>       Run a FractalScript script")
        print("  libs                List installed libraries")
        print("  help                Show this help")

    else:
        print(f"Unknown command: '{command}'. Type 'ez help' for usage.")
        sys.exit(1)


if __name__ == "__main__":
    main()
