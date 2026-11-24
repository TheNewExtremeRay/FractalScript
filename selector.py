import sys, os, subprocess

ez_file = sys.argv[1]
folder = os.path.dirname(os.path.abspath(__file__))  # selector.py folder

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
    print("Detected Graphical script. Launching run_ez.bat ...")
    subprocess.run([os.path.join(folder, "run_ez.bat"), ez_file])
elif script_type == "text":
    print("Detected Text script. Launching run_ez_text.bat ...")
    subprocess.run([os.path.join(folder, "run_ez_text.bat"), ez_file])
else:
    print("Unknown script type.")
