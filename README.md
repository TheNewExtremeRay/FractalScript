# FractalScript

**A simple scripting engine inspired by Python, designed around one principle: simplicity.**

FractalScript (formerly EzCode) is an experimental scripting engine built to make scripting straightforward through a small set of commands and an easy-to-understand structure.

---

## Installation

<badge color="info">Windows only</badge>

### Requirements

- [Python 3.14.6](https://www.python.org/ftp/python/3.14.6/python-3.14.6-amd64.exe) — Required
- [Pygame](https://www.pygame.org/news) — Required

### Setup

**1. Install Python**

Download and install Python from the [official website](https://www.python.org/) or the Microsoft Store.

**2. Install Pygame**

Open PowerShell and run:

```powershell
pip install pygame
```

**3. Download FractalScript**

Download the [latest release](https://github.com/TheNewExtremeRay/EzCode/releases/download/1.0.0/EzCode.zip).

**4. Extract the archive**

Extract the contents directly into your `C:\` drive.

Your directory structure should look like this:

```text
C:\
└── EzCode\
    ├── launcher.bat
    ├── Main Files\
    └── Examples4EzCode\
        └── Secondary Examples\
```

**5. Configure file association**

1. Open `C:\EzCode\Examples4EzCode`.
2. Right-click any `.ez` file.
3. Select **Open with** → **Choose another app**.
4. Select **Choose an app on your PC**.
5. Navigate to `C:\EzCode\`.
6. Select `launcher.bat`.

You can now open `.ez` scripts directly. The launcher opens a Command Prompt window and starts the script execution environment.

**6. Test your installation (optional)**

Download the [FractalScript testing files](https://github.com/TheNewExtremeRay/EzCode/releases/download/EzCodeMainReleases/Test.Set.zip) and run the included examples individually.

---

## Usage

FractalScript was designed around simplicity. Instead of introducing a large collection of commands, its approach revolves around a central command: `set`.

There are two main interface formats.

### 1. Text Interface Format

The Text Interface Format allows scripts to display text through a simple loop-based structure.

Every script using this format must begin with:

```ez
Text
```

This format declaration is required because of an existing engine limitation.

#### Basic syntax

| Command | Description |
|---|---|
| `Text` | Declares the text interface format. |
| `loop-name` | Starts a loop. |
| `loop-name-end` | Ends a loop. |
| `say ("text")` | Displays text. |

Anything written before the loop is considered setup.

#### Example: Hello World

```ez
Text

loop-Hello
    say ("Hello, World!")
loop-Hello-end
```

Although this structure may seem verbose for simple scripts, it provides a consistent foundation for more complex projects.

---

### 2. Graphical Interface Format

The Graphical Interface Format was the original interface format developed for FractalScript.

It uses a grid-based system to create simple graphical output.

#### Initializing a grid

Start your script with:

```ez
Grid(x, y)
```

Where `x` and `y` represent the grid dimensions.

For example:

```ez
Grid(16, 16)
```

As with the Text Interface Format, the grid declaration must appear before the main loop.

#### The `set` command

The `set` command is the core of the graphical interface.

It can be used to assign a color or an image to an individual grid cell.

**Set a cell's color:**

```ez
set (Grid[r1, c1] {5})
```

**Set a cell's image:**

```ez
set (Grid[r1, c1] {"C:\Images\image.png"})
```

The image path must point to an existing image file.

#### Color palette

FractalScript uses a predefined color palette.

| Code | Color |
|---:|---|
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

**Note:** The original documentation contains conflicting assignments for palette codes `15` and `16`. Their exact colors need to be verified against the implementation.

Custom RGB and hexadecimal colors are not currently supported.

#### Filling rectangular areas

You can also fill a rectangular region of the grid using two coordinate pairs:

```ez
set (Grid[r1, c1, r16, c16])
```

This fills the specified rectangular area with a color.

*Note: Area filling currently supports colors, not images.*

#### Complete graphical example

This example demonstrates grid initialization, area filling, image placement, and individual cell coloring.

```ez
Grid(16, 16)

loop-loop

    # Fill the entire grid with green
    set (Grid[r1, c1, r16, c16] {5})

    # Place an image
    set (Grid[r6, c6] {"C:\Users\YourName\Documents\image.png"})

    # Change an individual cell to red
    set (Grid[r5, c6] {1})

loop-loop-end
```

---

## Project Information

FractalScript is an experimental project focused on exploring simple scripting structures and graphical execution.

**Formerly known as:** EzCode

**Platform:** Windows

**Runtime:** Python + Pygame

**File extension:** `.ez`

---

<div align="center">

**FractalScript**

*Simple syntax. Creative possibilities.*

</div>
