 <div align="center">

# FRACTALSCRIPT

### A simple scripting engine built around simplicity.

Formerly known as **EzCode**

[![Release](https://img.shields.io/badge/Release-1.0.0-38BDF8?style=flat-square)](https://github.com/TheNewExtremeRay/EzCode/releases)
[![Python](https://img.shields.io/badge/Python-3.13-3776AB?style=flat-square&logo=python&logoColor=white)](https://www.python.org/)
[![Pygame](https://img.shields.io/badge/Pygame-2.6.1-00A86B?style=flat-square)](https://www.pygame.org/)
[![Platform](https://img.shields.io/badge/Platform-Windows-0078D6?style=flat-square&logo=windows&logoColor=white)](https://www.microsoft.com/windows)

**Less complexity. More creativity.**

</div>

---

## Overview

FractalScript is an experimental scripting engine inspired by Python, designed to make scripting accessible through a simple syntax and a small set of commands.

Its philosophy is straightforward: keep things simple, make commands versatile, and let users focus on what they're building.

The engine features two interface formats:

| Format | Purpose |
|:---|:---|
| **Text Interface** | Display and organize text-based output |
| **Graphical Interface** | Create grid-based graphical output using colors and images |

---

## Installation

<badge color="info">Windows only</badge>

FractalScript's original runtime requires **Python 3.13** and **Pygame 2.6.1**.

### Step 1 — Install Python 3.13

Open PowerShell and paste:

```powershell
$installer = "$env:TEMP\python-3.13-installer.exe"

Invoke-WebRequest `
  "https://www.python.org/ftp/python/3.13.9/python-3.13.9-amd64.exe" `
  -OutFile $installer

Start-Process $installer -ArgumentList "/passive InstallAllUsers=0 PrependPath=1 Include_test=0" -Wait

Remove-Item $installer
```

Close and reopen PowerShell after installation.

### Step 2 — Install Pygame

Paste this into PowerShell:

```powershell
py -3.13 -m pip install pygame==2.6.1
```

### Step 3 — Download FractalScript

Run this command in PowerShell:

```powershell
Invoke-WebRequest `
  "https://github.com/TheNewExtremeRay/EzCode/releases/download/1.0.0/EzCode.zip" `
  -OutFile "$env:USERPROFILE\Downloads\EzCode.zip"
```

Extract `EzCode.zip` directly into your `C:\` drive.

Your installation should look like this:

```text
C:\
└── EzCode\
    ├── launcher.bat
    ├── Main Files\
    └── Examples4EzCode\
```

The original directory names are retained for compatibility with the existing release.

### Step 4 — Configure script launching

1. Navigate to `C:\EzCode\Examples4EzCode`.
2. Right-click any `.ez` file.
3. Select **Open with** → **Choose another app**.
4. Browse for an application on your computer.
5. Navigate to `C:\EzCode\`.
6. Select `launcher.bat`.

The launcher opens a Command Prompt window and starts the script execution environment.

### Step 5 — Test your installation (Optional)

Download the testing files:

[Download FractalScript Test Set](https://github.com/TheNewExtremeRay/EzCode/releases/download/EzCodeMainReleases/Test.Set.zip)

Open the included files individually to verify that your installation works.

---

## Language Guide

### 01. Text Interface Format

The Text Interface Format provides a straightforward way to display text.

Every script using this format must begin with the `Text` declaration. This requirement exists because of an engine limitation.

**Syntax reference**

| Syntax | Description |
|:---|:---|
| `Text` | Declares the text interface |
| `loop-name` | Starts a loop |
| `loop-name-end` | Ends a loop |
| `say ("text")` | Displays text |

Anything written before the main loop is considered setup.

**Example — Hello World**

```text
Text

loop-Hello

say ("Hello, World!")

loop-Hello-end
```

The format uses a loop-based structure to organize script execution. While it may require more lines for simple output, it provides a consistent structure for larger projects.

### 02. Graphical Interface Format

The Graphical Interface Format was the first interface developed for FractalScript.

It uses a customizable grid to create simple graphical output.

**Initializing a grid**

```text
Grid(16, 16)
```

The two parameters define the grid dimensions.

**The `set` command**

The `set` command is the central operation of the graphical interface.

Set an individual cell to a predefined color:

```text
set (Grid[r1, c1] {5})
```

Place an image inside a cell:

```text
set (Grid[r1, c1] {"C:\Images\image.png"})
```

Image paths must point to existing files.

### Color Palette

FractalScript uses a predefined color palette.

| Code | Color |
|:---:|:---|
| `0` | Black |
| `1` | Red |
| `2` | Orange |
| `3` | Yellow |
| `4` | Lime |
| `5` | Green |
| `6` | Dark Green |
| `7` | Light Blue |
| `8` | Cyan |
| `9` | Blue |
| `10` | Dark Blue |
| `11` | Magenta |
| `12` | Purple |
| `13` | Dark Pink |
| `14` | Pink |
| `17` | White |

Custom RGB and hexadecimal colors are not supported in this release.

**Note:** Palette codes `15` and `16` are omitted because their original documentation contains conflicting assignments. Their exact colors need to be verified against the implementation.

### Rectangular Grid Filling

You can fill a rectangular area using two coordinate pairs:

```text
set (Grid[r1, c1, r16, c16] {5})
```

This fills the selected region with the specified color.

**Current limitation:** Rectangular filling supports colors, but not images.

### Complete Graphical Example

```text
Grid(16, 16)

loop-loop

    # Fill the entire grid with green
    set (Grid[r1, c1, r16, c16] {5})

    # Place an image
    set (Grid[r6, c6] {"C:\Users\YourName\Documents\image.png"})

    # Set an individual cell to red
    set (Grid[r5, c6] {1})

loop-loop-end
```

---

## Project Details

<div align="center">

| Property | Information |
|:---|:---|
| Project | FractalScript |
| Former name | EzCode |
| Runtime | Python |
| Graphics library | Pygame |
| Script extension | `.ez` |
| Platform | Windows |
| Release | 1.0.0 |

</div>

---

<div align="center">

### Explore FractalScript

[**Download**](https://github.com/TheNewExtremeRay/EzCode/releases) · [**Source Code**](https://github.com/TheNewExtremeRay/EzCode) · [**FractalLabs**](https://extremeteam.online)

*Built to make scripting simple.*

</div>
