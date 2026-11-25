import re, sys, os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame, time
from pygame.locals import *
import library_handler as lh
import el_compiler as elc

print("FractalScript, An ExtremeRay Project, 2025-2026")
print("For more info, please refer to https://ezcode.unaux.com")
print()

def _parse_lib_call_args(args_str):
    parts = [p.strip() for p in args_str.split(",")]
    if not parts:
        return []
    parsed = []
    for p in parts:
        if not p:
            continue
        if (p.startswith('"') and p.endswith('"')) or \
           (p.startswith("'") and p.endswith("'")):
            parsed.append(p[1:-1])
        elif p.lstrip('-').isdigit():
            parsed.append(int(p))
        elif _is_float(p):
            parsed.append(float(p))
        else:
            parsed.append(p)
    return parsed

def _is_float(s):
    try:
        float(s)
        return True
    except ValueError:
        return False

def _do_import(lib_name):
    name = lib_name.lower()
    if name.endswith(".el"):
        name = name[:-3]
    elif name.endswith(".py"):
        name = name[:-3]
    result = lh.load(name)
    if result is not None:
        print(f"[IMPORT] Loaded library: {name}")
    return result

DEBUG = False
CELL_HEIGHT = 30
FONT_SIZE = 24
WINDOW_W, WINDOW_H = 800, 600

variables = {}
loop_blocks = {}
current_loop = "Main"
screen = None
font = None
text_lines = []
key_states = {}

def debug_print(*args):
    if DEBUG:
        print(*args)

def init_screen():
    global screen, font
    pygame.init()
    screen = pygame.display.set_mode((WINDOW_W, WINDOW_H))
    font = pygame.font.SysFont("Consolas", FONT_SIZE)
    pygame.display.set_caption("FractalScript Text Interface")
    draw_text()

def draw_text():
    if screen is None:
        return
    screen.fill((0, 0, 0))
    y = 0
    for line in text_lines[-20:]:
        text_surface = font.render(line, True, (255, 255, 255))
        screen.blit(text_surface, (10, y))
        y += CELL_HEIGHT
    pygame.display.flip()

def append_text(msg):
    def repl(m):
        name = m.group(1)
        return str(variables.get(name, 0))
    msg = re.sub(r'\|\|\[Var\]\s*\{(.+?)\}\|\|', repl, msg)
    text_lines.clear()
    text_lines.append(msg)
    draw_text()

def translate_file(filename):
    global loop_blocks
    if not os.path.exists(filename):
        print("File not found!")
        sys.exit(1)

    raw = []
    with open(filename, "r", encoding="utf-8") as f:
        for raw_line in f:
            s = raw_line.strip()
            if not s:
                continue
            if s.startswith("//"):
                continue
            if s.endswith("."):
                s = s[:-1]
            raw.append(s)

    i = 0
    while i < len(raw):
        line = raw[i]

        # Import
        if line.startswith("import "):
            lib_name = line[7:].strip()
            _do_import(lib_name)
            i += 1
            continue

        if line == "Text":
            debug_print("Text mode detected")
            i += 1
            continue

        if line.startswith("loop-") and not line.endswith("-end"):
            loop_name = line.split("loop-", 1)[1]
            loop_lines = []
            i += 1
            while i < len(raw) and raw[i] != f"loop-{loop_name}-end":
                loop_lines.append(raw[i])
                i += 1
            if i >= len(raw) or raw[i] != f"loop-{loop_name}-end":
                print(f"Error: loop '{loop_name}' missing end marker")
                sys.exit(1)
            loop_blocks[loop_name] = parse_text_loop_body(loop_lines)
            i += 1
            continue

        if line.endswith("-end") and line.startswith("loop-"):
            print(f"Error: unexpected end marker '{line}'")
            sys.exit(1)

        i += 1

def parse_text_loop_body(lines):
    blocks = []
    in_if_chain = False
    for line in lines:
        m = re.match(r"if\s*\(\[keyboard\]\s*\{press\}\s*=\s*(\w+)\)\s*\{", line)
        if m:
            key = m.group(1).lower()
            blocks.append({
                "type": "if_chain",
                "blocks": [{"type": "if_key", "key": key, "actions": []}]
            })
            in_if_chain = True
            continue

        m = re.match(r"if\s*\(\[Var\]\s*\{(\\w+)\}\s*=\s*(\-?\d+)\)\s*\{", line)
        if m:
            vname, vval = m.groups()
            vval = int(vval)
            blocks.append({
                "type": "if_chain",
                "blocks": [{"type": "if_var", "var": vname, "value": vval, "actions": []}]
            })
            in_if_chain = True
            continue

        m = re.match(r"\} else-if \(\[keyboard\]\s*\{press\}\s*=\s*(\w+)\)\s*\{", line)
        if m:
            key = m.group(1).lower()
            if not blocks or blocks[-1].get("type") != "if_chain":
                print("Error: else-if without matching if")
                sys.exit(1)
            blocks[-1]["blocks"].append({"type": "elseif_key", "key": key, "actions": []})
            continue

        if line.startswith("} else {"):
            if not blocks or blocks[-1].get("type") != "if_chain":
                print("Error: else without matching if")
                sys.exit(1)
            blocks[-1]["blocks"].append({"type": "else", "actions": []})
            continue

        if line == "}":
            in_if_chain = False
            continue

        m = re.match(r'set\s*\(Var\[(\w+)\]\s*\{(.+?)\}\)', line)
        if m:
            var_name, operation = m.groups()
            def var_action(vn=var_name, op=operation):
                if op == "create":
                    if vn not in variables:
                        variables[vn] = 0
                elif op.startswith("add("):
                    try:
                        n = int(op[4:-1])
                    except:
                        n = 0
                    variables[vn] = variables.get(vn, 0) + n
                elif op.startswith("rem("):
                    try:
                        n = int(op[4:-1])
                    except:
                        n = 0
                    variables[vn] = variables.get(vn, 0) - n
                elif op.startswith("set("):
                    try:
                        variables[vn] = int(op[4:-1])
                    except:
                        pass
            if blocks and blocks[-1].get("type") == "if_chain" and in_if_chain:
                blocks[-1]["blocks"][-1]["actions"].append(var_action)
            else:
                blocks.append({"type": "action", "action": var_action})
            continue

        m = re.match(r'say\s*\("(.+?)"\)', line)
        if m:
            message = m.group(1)
            def say_action(msg=message):
                append_text(msg)
            if blocks and blocks[-1].get("type") == "if_chain" and in_if_chain:
                blocks[-1]["blocks"][-1]["actions"].append(say_action)
            else:
                blocks.append({"type": "action", "action": say_action})
            continue

        m = re.match(r'wait\((\d+)\)', line)
        if m:
            wait_ms = int(m.group(1))
            def wait_action(ms=wait_ms):
                start = time.time()
                while time.time() - start < (ms/1000.0):
                    for evt in pygame.event.get():
                        if evt.type == QUIT:
                            pygame.quit()
                            sys.exit(0)
                    time.sleep(0.01)
            if blocks and blocks[-1].get("type") == "if_chain" and in_if_chain:
                blocks[-1]["blocks"][-1]["actions"].append(wait_action)
            else:
                blocks.append({"type": "action", "action": wait_action})
            continue

        m = re.match(r'call\s*\(\s*Lib\[(\w+)\]\s*\{([^}]+)\}\s*\)', line)
        if m:
            lib_name = m.group(1)
            body = m.group(2).strip()
            parts = _parse_lib_call_args(body)
            if not parts:
                continue
            func_name = parts[0]
            func_args = parts[1:]
            def lib_action(lib=lib_name, fn=func_name, args=func_args):
                lh.call(lib, fn, *args)
            if blocks and blocks[-1].get("type") == "if_chain" and in_if_chain:
                blocks[-1]["blocks"][-1]["actions"].append(lib_action)
            else:
                blocks.append({"type": "action", "action": lib_action})
            continue

        # Try .el registered commands (deferred action)
        _el_matched = False
        if lh.REGISTERED_COMMANDS:
            for _ecmd in lh.REGISTERED_COMMANDS:
                _eparams = elc.extract_params(_ecmd["syntax"], line)
                if _eparams is not None:
                    def _el_action(cmd=_ecmd, params=_eparams):
                        elc.exec_command(cmd["func"], params, cmd["name"], cmd.get("bypass", False))
                    if blocks and blocks[-1].get("type") == "if_chain" and in_if_chain:
                        blocks[-1]["blocks"][-1]["actions"].append(_el_action)
                    else:
                        blocks.append({"type": "action", "action": _el_action})
                    _el_matched = True
                    break
        if _el_matched:
            continue

    return blocks

def run_loops():
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
        keys = pygame.key.get_pressed()
        for loopname, actions in loop_blocks.items():
            for act in actions:
                if act["type"] == "action":
                    act["action"]()
                elif act["type"] == "if_chain":
                    executed = False
                    for block in act["blocks"]:
                        run_block = False
                        btype = block["type"]
                        if btype in ("if_key", "elseif_key"):
                            key = block["key"]
                            keycode = getattr(pygame, f"K_{key}", None)
                            if keycode and keys[keycode]:
                                if not key_states.get(key, False):
                                    run_block = True
                                    key_states[key] = True
                            else:
                                key_states[key] = False
                        elif btype in ("if_var", "elseif_var"):
                            var_name = block["var"]
                            value = block["value"]
                            if variables.get(var_name, 0) == value:
                                run_block = True
                        elif btype == "else":
                            if not executed:
                                run_block = True
                        if run_block:
                            executed = True
                            for a in block["actions"]:
                                a()
                            break
        clock.tick(30)
    pygame.quit()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python translator.py file.ez")
        sys.exit(1)
    ez_file = sys.argv[1]
    init_screen()
    translate_file(ez_file)
    run_loops()
