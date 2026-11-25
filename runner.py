import re, sys, os
os.environ["PYGAME_HIDE_SUPPORT_PROMPT"] = "1"
import pygame, time
from pygame.locals import *
import library_handler as lh
import el_compiler as elc
import runtime

print("FractalScript, An ExtremeRay Project, 2025-2026")
print("For more info, please refer to https://ezcode.unaux.com")
print()

colors = {
    0: (0, 0, 0), 1: (220, 20, 20), 2: (245, 160, 0), 3: (255, 230, 0),
    4: (128, 255, 0), 5: (0, 180, 0), 6: (0, 100, 0), 7: (100, 180, 255),
    8: (0, 230, 230), 9: (0, 60, 220), 10: (0, 0, 160), 11: (220, 0, 220),
    12: (140, 40, 220), 13: (220, 50, 120), 14: (255, 150, 180),
    15: (255, 200, 210), 16: (80, 80, 80), 17: (240, 240, 240)
}

grid = []
cell_size = 40
screen = None
loop_blocks = {}
variables = {}
key_hold_times = {}
repeat_delay = 0.50
repeat_interval = 0.01

runtime.init(sys.modules[__name__])

def make_grid(w, h):
    global grid, screen
    grid = [[0 for _ in range(w)] for _ in range(h)]
    pygame.init()
    screen = pygame.display.set_mode((w * cell_size, h * cell_size))

def _default_draw_grid():
    screen.fill((0, 0, 0))
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            x, y = c * cell_size, r * cell_size
            if isinstance(val, tuple):
                pygame.draw.rect(screen, val, (x, y, cell_size, cell_size))
            elif isinstance(val, int):
                pygame.draw.rect(screen, colors.get(val, (255, 255, 255)),
                                 (x, y, cell_size, cell_size))
            elif isinstance(val, pygame.Surface):
                screen.blit(val, (x, y))
            else:
                pygame.draw.rect(screen, (0, 0, 0), (x, y, cell_size, cell_size))
    pygame.display.flip()

def draw_grid():
    fn = runtime.get_override("draw_grid")
    if fn is not None:
        fn()
    else:
        _default_draw_grid()

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

def translate_file(filename):
    current_loop = None
    in_block = None
    current_chain = None

    with open(filename, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("//"):
                continue
            if line.endswith("."):
                line = line[:-1]

            # Import
            if line.startswith("import "):
                lib_name = line[7:].strip()
                _do_import(lib_name)
                continue

            # Grid
            match = re.match(r"Grid\((\d+),\s*(\d+)\)", line)
            if match:
                x, y = map(int, match.groups())
                make_grid(x, y)
                continue

            # Loop start
            if line.startswith("loop-") and not line.endswith("-end"):
                name = line[5:]
                if name in loop_blocks and loop_blocks[name]["open"]:
                    print(f"Error: loop-{name} already open!")
                    sys.exit()
                loop_blocks[name] = {"actions": [], "open": True}
                current_loop = name
                continue

            if line.startswith("loop-") and line.endswith("-end"):
                name = line[5:-4]
                if name not in loop_blocks or not loop_blocks[name]["open"]:
                    print(f"Error: loop-{name}-end without matching start!")
                    sys.exit()
                loop_blocks[name]["open"] = False
                current_loop = None
                continue

            if current_loop is None:
                print(f"Error: code outside of loop: {line}")
                sys.exit()

            match = re.match(r"if\s*\(\[keyboard\]\s*\{press\}\s*=\s*(\w+)\)\s*\{", line)
            if match:
                key = match.group(1).lower()
                chain = {
                    "type": "if_chain",
                    "blocks": [{"type": "if_key", "key": key, "actions": []}]
                }
                loop_blocks[current_loop]["actions"].append(chain)
                current_chain = chain
                in_block = "if_chain"
                continue

            match = re.match(r"\}?\s*else-if \(\[keyboard\]\s*\{press\}\s*=\s*(\w+)\)\s*\{", line)
            if match:
                key = match.group(1).lower()
                if current_chain is not None:
                    current_chain["blocks"].append({"type": "elseif_key", "key": key, "actions": []})
                in_block = "if_chain"
                continue

            if re.match(r"\}?\s*else\s*\{", line):
                if current_chain is not None:
                    current_chain["blocks"].append({"type": "else", "actions": []})
                in_block = "if_chain"
                continue

            if line == "}":
                in_block = None
                continue

            match = re.match(r'set\s*\(Var\[(\w+)\]\s*\{(.+?)\}\)', line)
            if match:
                var_name, operation = match.groups()
                def var_action(vn=var_name, op=operation):
                    if op == "create":
                        if vn not in variables:
                            variables[vn] = 0
                    elif op.startswith("add("):
                        variables[vn] = variables.get(vn, 0) + int(op[4:-1])
                    elif op.startswith("rem("):
                        variables[vn] = variables.get(vn, 0) - int(op[4:-1])
                    elif op.startswith("set("):
                        variables[vn] = int(op[4:-1])
                if in_block == "if_chain" and current_chain is not None:
                    current_chain["blocks"][-1]["actions"].append(var_action)
                else:
                    loop_blocks[current_loop]["actions"].append({"type": "action", "action": var_action})
                continue

            match = re.match(r'set\s*\(Grid\[r(\d+),\s*c(\d+)\]\s*\{(.+?)\}\)', line)
            if match:
                r, c, val = match.groups()
                r, c = int(r)-1, int(c)-1
                try:
                    val_int = int(val)
                    action = lambda rr=r, cc=c, vv=val_int: (
                        grid.__setitem__(rr, [*grid[rr][:cc], vv, *grid[rr][cc+1:]]), draw_grid()
                    )
                except ValueError:
                    img_path = val.strip('"').replace("(E:)", "E:").replace("\\", "\\\\")
                    try:
                        image = pygame.image.load(img_path)
                        image = pygame.transform.scale(image, (cell_size, cell_size))
                        action = lambda rr=r, cc=c, img=image: (
                            grid.__setitem__(rr, [*grid[rr][:cc], img, *grid[rr][cc+1:]]), draw_grid()
                        )
                    except:
                        continue
                if in_block == "if_chain" and current_chain is not None:
                    current_chain["blocks"][-1]["actions"].append(action)
                else:
                    loop_blocks[current_loop]["actions"].append({"type": "action", "action": action})
                continue

            match = re.match(r'set\s*\(Grid\[r(\d+),\s*c(\d+),\s*r(\d+),\s*c(\d+)\]\s*\{(\d+)\}\)', line)
            if match:
                r1, c1, r2, c2, val = map(int, match.groups())
                def region_action(r1=r1, c1=c1, r2=r2, c2=c2, vv=val):
                    for rr in range(r1-1, r2):
                        for cc in range(c1-1, c2):
                            if isinstance(grid[rr][cc], int):
                                grid[rr][cc] = vv
                    draw_grid()
                if in_block == "if_chain" and current_chain is not None:
                    current_chain["blocks"][-1]["actions"].append(region_action)
                else:
                    loop_blocks[current_loop]["actions"].append({"type": "action", "action": region_action})
                continue

            match = re.match(r'call\s*\(\s*Lib\[(\w+)\]\s*\{([^}]+)\}\s*\)', line)
            if match:
                lib_name = match.group(1)
                body = match.group(2).strip()
                parts = _parse_lib_call_args(body)
                if not parts:
                    continue
                func_name = parts[0]
                func_args = parts[1:]
                def lib_action(lib=lib_name, fn=func_name, args=func_args):
                    lh.call(lib, fn, *args)
                if in_block == "if_chain" and current_chain is not None:
                    current_chain["blocks"][-1]["actions"].append(lib_action)
                else:
                    loop_blocks[current_loop]["actions"].append({"type": "action", "action": lib_action})
                continue

            # Try .el registered commands (deferred action)
            _el_matched = False
            if lh.REGISTERED_COMMANDS:
                for _ecmd in lh.REGISTERED_COMMANDS:
                    _eparams = elc.extract_params(_ecmd["syntax"], line)
                    if _eparams is not None:
                        def _el_action(cmd=_ecmd, params=_eparams):
                            elc.exec_command(cmd["func"], params, cmd["name"], cmd.get("bypass", False))
                        if in_block == "if_chain" and current_chain is not None:
                            current_chain["blocks"][-1]["actions"].append(_el_action)
                        else:
                            loop_blocks[current_loop]["actions"].append({"type": "action", "action": _el_action})
                        _el_matched = True
                        break
            if _el_matched:
                continue

            print(f"Warning: Unknown command: {line}")


def _apply_overrides():
    """Read GLOBAL_OVERRIDES from el_compiler and apply grid operations."""
    global cell_size, screen
    if not elc.GLOBAL_OVERRIDES:
        return
    ops = list(elc.GLOBAL_OVERRIDES)
    elc.GLOBAL_OVERRIDES.clear()
    resized = False
    for op in ops:
        key = op["key"]
        val = op["value"]
        if key == "cell_size":
            cell_size = int(val)
            resized = True
        elif key == "set_cell":
            r, c, color = int(val[0]), int(val[1]), int(val[2])
            if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                grid[r][c] = color
        elif key == "fill_region":
            r1, c1, r2, c2, color = int(val[0]), int(val[1]), int(val[2]), int(val[3]), int(val[4])
            for rr in range(max(0, r1), min(len(grid), r2 + 1)):
                for cc in range(max(0, c1), min(len(grid[0]), c2 + 1)):
                    grid[rr][cc] = color
        elif key == "clear_grid":
            color = int(val[0]) if val else 0
            for r in range(len(grid)):
                for c in range(len(grid[0])):
                    grid[r][c] = color
        elif key == "outline":
            r1, c1, r2, c2, color = int(val[0]), int(val[1]), int(val[2]), int(val[3]), int(val[4])
            for rr in range(max(0, r1), min(len(grid), r2 + 1)):
                for cc in range(max(0, c1), min(len(grid[0]), c2 + 1)):
                    if rr == r1 or rr == r2 or cc == c1 or cc == c2:
                        grid[rr][cc] = color
        elif key == "checkerboard":
            r1, c1, r2, c2, c1_color, c2_color = (int(val[0]), int(val[1]), int(val[2]),
                                                     int(val[3]), int(val[4]), int(val[5]))
            for rr in range(max(0, r1), min(len(grid), r2 + 1)):
                for cc in range(max(0, c1), min(len(grid[0]), c2 + 1)):
                    grid[rr][cc] = c1_color if (rr + cc) % 2 == 0 else c2_color
        elif key == "border":
            r1, c1, r2, c2, color, thickness = (int(val[0]), int(val[1]), int(val[2]),
                                                  int(val[3]), int(val[4]), int(val[5]))
            for rr in range(max(0, r1), min(len(grid), r2 + 1)):
                for cc in range(max(0, c1), min(len(grid[0]), c2 + 1)):
                    edge = (rr - r1 < thickness or r2 - rr < thickness or
                            cc - c1 < thickness or c2 - cc < thickness)
                    if edge:
                        grid[rr][cc] = color
        elif key == "fill_circle":
            cr, cc, radius, color = int(val[0]), int(val[1]), int(val[2]), int(val[3])
            for r in range(max(0, cr - radius), min(len(grid), cr + radius + 1)):
                for c in range(max(0, cc - radius), min(len(grid[0]), cc + radius + 1)):
                    if (r - cr) ** 2 + (c - cc) ** 2 <= radius ** 2:
                        grid[r][c] = color
        elif key == "fill_line":
            r1, c1, r2, c2, color = int(val[0]), int(val[1]), int(val[2]), int(val[3]), int(val[4])
            steps = max(abs(r2 - r1), abs(c2 - c1), 1)
            for i in range(steps + 1):
                t = i / steps
                r = int(r1 + (r2 - r1) * t)
                c = int(c1 + (c2 - c1) * t)
                if 0 <= r < len(grid) and 0 <= c < len(grid[0]):
                    grid[r][c] = color
        elif key == "fill_gradient":
            r1, c1, r2, c2, color_start, color_end = (int(val[0]), int(val[1]), int(val[2]),
                                                        int(val[3]), int(val[4]), int(val[5]))
            cs = colors.get(color_start, (0, 0, 0))
            ce = colors.get(color_end, (255, 255, 255))
            rows = max(1, r2 - r1)
            for rr in range(max(0, r1), min(len(grid), r2 + 1)):
                t = (rr - r1) / rows
                r_c = int(cs[0] + (ce[0] - cs[0]) * t)
                g_c = int(cs[1] + (ce[1] - cs[1]) * t)
                b_c = int(cs[2] + (ce[2] - cs[2]) * t)
                for cc in range(max(0, c1), min(len(grid[0]), c2 + 1)):
                    grid[rr][cc] = (r_c, g_c, b_c)
    if resized and grid:
        cols = len(grid[0])
        rows = len(grid)
        screen = pygame.display.set_mode((cols * cell_size, rows * cell_size))
    draw_grid()

def _default_run_loops(ez_filename):
    global cell_size, screen
    pygame.display.set_caption(os.path.splitext(os.path.basename(ez_filename))[0])
    clock = pygame.time.Clock()
    running = True
    rt = runtime.get()
    while running:
        _apply_overrides()
        # Reset mouse state each frame
        if rt is not None:
            rt.mouse_clicked = False
            rt.mouse_cell = None
            rt.mouse_button = None
            rt._button_clicked = None
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == MOUSEBUTTONDOWN and rt is not None:
                mx, my = event.pos
                col = mx // cell_size
                row = my // cell_size
                if 0 <= row < len(grid) and 0 <= col < len(grid[0]):
                    rt.mouse_clicked = True
                    rt.mouse_cell = (row, col)
                    rt.mouse_button = event.button
        # Detect button clicks before loop actions run
        if rt is not None and rt.mouse_clicked and rt.mouse_cell is not None:
            mr, mc = rt.mouse_cell
            for bid, btn in getattr(rt, "_buttons", {}).items():
                if btn["r1"] <= mr <= btn["r2"] and btn["c1"] <= mc <= btn["c2"]:
                    rt._button_clicked = bid
                    break
        keys = pygame.key.get_pressed()
        current_time = time.time()
        for loopname, loop_data in loop_blocks.items():
            for act in loop_data["actions"]:
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
                            if keycode:
                                pressed = keys[keycode]
                                initial, last = key_hold_times.get(key, (0,0))
                                if pressed:
                                    if initial == 0:
                                        run_block = True
                                        key_hold_times[key] = (current_time, current_time)
                                    elif current_time - initial >= repeat_delay:
                                        if current_time - last >= repeat_interval:
                                            run_block = True
                                            key_hold_times[key] = (initial, current_time)
                                else:
                                    key_hold_times[key] = (0, 0)
                        elif btype == "else":
                            if not executed:
                                run_block = True
                        if run_block:
                            executed = True
                            for a in block["actions"]:
                                a()
                            break
        draw_grid()
        clock.tick(60)
    pygame.quit()

_orig_run_loops = _default_run_loops

def run_loops(ez_filename):
    fn = runtime.get_override("run_loops")
    if fn is not None:
        fn(ez_filename)
    else:
        _default_run_loops(ez_filename)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python runner.py file.ez")
    else:
        ez_file = sys.argv[1]
        translate_file(ez_file)
        for name, data in loop_blocks.items():
            if data["open"]:
                print(f"Error: loop-{name} missing loop-{name}-end!")
                sys.exit()
        run_loops(ez_file)
