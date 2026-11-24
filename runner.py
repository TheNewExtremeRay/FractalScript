import re, sys, os, pygame, time
from pygame.locals import *
import library_handler as lh
import el_compiler as elc

colors = {
    0: (0, 0, 0), 1: (255, 0, 0), 2: (255, 165, 0), 3: (255, 255, 0),
    4: (0, 255, 0), 5: (0, 128, 0), 6: (0, 100, 0), 7: (173, 216, 230),
    8: (0, 255, 255), 9: (0, 0, 255), 10: (0, 0, 139), 11: (255, 0, 255),
    12: (128, 0, 128), 13: (199, 21, 133), 14: (255, 192, 203),
    15: (255, 182, 193), 16: (128, 128, 128), 17: (255, 255, 255)
}

grid = []
cell_size = 40
screen = None
loop_blocks = {}
variables = {}
key_hold_times = {}
repeat_delay = 0.50
repeat_interval = 0.01

def make_grid(w, h):
    global grid, screen
    grid = [[0 for _ in range(w)] for _ in range(h)]
    pygame.init()
    screen = pygame.display.set_mode((w * cell_size, h * cell_size))

def draw_grid():
    screen.fill((0, 0, 0))
    for r, row in enumerate(grid):
        for c, val in enumerate(row):
            if isinstance(val, int):
                pygame.draw.rect(screen, colors.get(val, (255, 255, 255)),
                                 (c*cell_size, r*cell_size, cell_size, cell_size))
            elif isinstance(val, pygame.Surface):
                screen.blit(val, (c*cell_size, r*cell_size))
            else:
                pygame.draw.rect(screen, (0,0,0),
                                 (c*cell_size, r*cell_size, cell_size, cell_size))
    pygame.display.flip()

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
                loop_blocks[current_loop]["actions"].append({
                    "type": "if_chain",
                    "blocks": [{"type": "if_key", "key": key, "actions": []}]
                })
                in_block = "if_chain"
                continue

            match = re.match(r"\} else-if \(\[keyboard\]\s*\{press\}\s*=\s*(\w+)\)\s*\{", line)
            if match:
                key = match.group(1).lower()
                last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                last_chain.append({"type": "elseif_key", "key": key, "actions": []})
                continue

            if line.startswith("} else {"):
                last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                last_chain.append({"type": "else", "actions": []})
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
                if in_block == "if_chain":
                    last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                    last_chain[-1]["actions"].append(var_action)
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
                if in_block == "if_chain":
                    last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                    last_chain[-1]["actions"].append(action)
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
                if in_block == "if_chain":
                    last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                    last_chain[-1]["actions"].append(region_action)
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
                if in_block == "if_chain":
                    last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                    last_chain[-1]["actions"].append(lib_action)
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
                            elc.exec_command(cmd["func"], params, cmd["name"])
                        if in_block == "if_chain":
                            last_chain = loop_blocks[current_loop]["actions"][-1]["blocks"]
                            last_chain[-1]["actions"].append(_el_action)
                        else:
                            loop_blocks[current_loop]["actions"].append({"type": "action", "action": _el_action})
                        _el_matched = True
                        break
            if _el_matched:
                continue

            print(f"Warning: Unknown command: {line}")

def run_loops(ez_filename):
    pygame.display.set_caption(os.path.splitext(os.path.basename(ez_filename))[0])
    clock = pygame.time.Clock()
    running = True
    while running:
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
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
        clock.tick(60)
    pygame.quit()

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
