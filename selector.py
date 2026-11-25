import sys, os, subprocess

ez_file = sys.argv[1]
folder = os.path.dirname(os.path.abspath(__file__))

# Read first lines to detect type
script_type = "unknown"
with open(ez_file, "r", encoding="utf-8") as f:
    for i in range(10):
        line = f.readline()
        if not line:
            break
        if "Grid" in line:
            script_type = "graphical"
            break
        elif "loop-" in line or "if " in line:
            script_type = "text"
            break
        elif "Text" in line:
            script_type = "text"
            break

if script_type == "graphical":
    subprocess.Popen(
        f'start "FractalScript" cmd /k "title FractalScript && python "{os.path.join(folder, "runner.py")}" "{ez_file}" && pause"',
        shell=True
    )
elif script_type == "text":
    subprocess.Popen(
        f'start "FractalScript" cmd /k "title FractalScript && python "{os.path.join(folder, "translator.py")}" "{ez_file}" && pause"',
        shell=True
    )
else:
    print("Unknown script type.")
