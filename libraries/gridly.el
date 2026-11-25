// ============================================================
//  gridly.el — Grid Tools for FractalScript (Bypass Mode)
//
//  A comprehensive grid manipulation library with bypass mode.
//  Resize cells, draw shapes, fill patterns, toggle grid overlay.
//
//  Usage in .ez scripts:
//    import gridly.el
//    GridResize(20)
//    SetCell(3, 5, 1)
//    FillRegion(0, 0, 15, 15, 5)
//    GridOverlayOn
//    GridOverlayOff
// ============================================================

Def {
  Library.name: "Gridly"
  Library.version: v1.0
  Package.identifier: "fractalscript.lib.gridly"
  Library.bypass: true
}

// ── GridResize ───────────────────────────────────────────────
// Set the pixel size of each grid cell. Window resizes automatically.
// Usage: GridResize({size})

Cmd {
  Syntax: 'GridResize({size})'
  Func: '
try:
    px = int(size)
    if px < 5: px = 5
    if px > 200: px = 200
    set_global("cell_size", px)
    print("Grid cell size: " + str(px) + "px")
except Exception as e:
    print("GridResize error: " + str(e))
'
}

// ── SetCell ──────────────────────────────────────────────────
// Set a single cell to a color.
// Usage: SetCell({row}, {col}, {color})

Cmd {
  Syntax: 'SetCell({row}, {col}, {color})'
  Func: '
try:
    set_global("set_cell", [int(row)-1, int(col)-1, int(color)])
except Exception as e:
    print("SetCell error: " + str(e))
'
}

// ── FillRegion ───────────────────────────────────────────────
// Fill a rectangular area with a color.
// Usage: FillRegion({r1}, {c1}, {r2}, {c2}, {color})
//   r1,c1 = top-left, r2,c2 = bottom-right (1-indexed)

Cmd {
  Syntax: 'FillRegion({r1}, {c1}, {r2}, {c2}, {color})'
  Func: '
try:
    set_global("fill_region", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(color)])
except Exception as e:
    print("FillRegion error: " + str(e))
'
}

// ── ClearGrid ────────────────────────────────────────────────
// Fill the entire grid with one color (default: black).
// Usage: ClearGrid({color})

Cmd {
  Syntax: 'ClearGrid({color})'
  Func: '
try:
    set_global("clear_grid", [int(color)])
except Exception as e:
    print("ClearGrid error: " + str(e))
'
}

// ── DrawOutline ──────────────────────────────────────────────
// Draw a rectangle outline (1px thin).
// Usage: DrawOutline({r1}, {c1}, {r2}, {c2}, {color})

Cmd {
  Syntax: 'DrawOutline({r1}, {c1}, {r2}, {c2}, {color})'
  Func: '
try:
    set_global("outline", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(color)])
except Exception as e:
    print("DrawOutline error: " + str(e))
'
}

// ── Checkerboard ─────────────────────────────────────────────
// Fill a region with a checkerboard pattern of two colors.
// Usage: Checkerboard({r1}, {c1}, {r2}, {c2}, {color1}, {color2})

Cmd {
  Syntax: 'Checkerboard({r1}, {c1}, {r2}, {c2}, {color1}, {color2})'
  Func: '
try:
    set_global("checkerboard", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(color1), int(color2)])
except Exception as e:
    print("Checkerboard error: " + str(e))
'
}

// ── DrawBorder ───────────────────────────────────────────────
// Draw a thick border around a rectangle.
// Usage: DrawBorder({r1}, {c1}, {r2}, {c2}, {color}, {thickness})

Cmd {
  Syntax: 'DrawBorder({r1}, {c1}, {r2}, {c2}, {color}, {thickness})'
  Func: '
try:
    set_global("border", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(color), int(thickness)])
except Exception as e:
    print("DrawBorder error: " + str(e))
'
}

// ── FillCircle ───────────────────────────────────────────────
// Fill a circle with a color.
// Usage: FillCircle({centerRow}, {centerCol}, {radius}, {color})

Cmd {
  Syntax: 'FillCircle({centerRow}, {centerCol}, {radius}, {color})'
  Func: '
try:
    set_global("fill_circle", [int(centerRow)-1, int(centerCol)-1, int(radius), int(color)])
except Exception as e:
    print("FillCircle error: " + str(e))
'
}

// ── DrawLine ─────────────────────────────────────────────────
// Draw a line between two points.
// Usage: DrawLine({r1}, {c1}, {r2}, {c2}, {color})

Cmd {
  Syntax: 'DrawLine({r1}, {c1}, {r2}, {c2}, {color})'
  Func: '
try:
    set_global("fill_line", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(color)])
except Exception as e:
    print("DrawLine error: " + str(e))
'
}

// ── FillGradient ─────────────────────────────────────────────
// Fill a region with a vertical gradient between two colors.
// Usage: FillGradient({r1}, {c1}, {r2}, {c2}, {colorStart}, {colorEnd})

Cmd {
  Syntax: 'FillGradient({r1}, {c1}, {r2}, {c2}, {colorStart}, {colorEnd})'
  Func: '
try:
    set_global("fill_gradient", [int(r1)-1, int(c1)-1, int(r2)-1, int(c2)-1, int(colorStart), int(colorEnd)])
except Exception as e:
    print("FillGradient error: " + str(e))
'
}

// ── GridOverlayOn ────────────────────────────────────────────
// Enables a pixel-grid overlay on all rendered cells.

Cmd {
  Syntax: 'GridOverlayOn'
  Func: '
import pygame, runtime

def _grid_overlay():
    rt = runtime.get()
    screen = rt.screen
    grid = rt.grid
    cell_size = rt.cell_size
    colors = rt.colors
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
            pygame.draw.rect(screen, (50, 50, 50), (x, y, cell_size, cell_size), 1)
    pygame.display.flip()

runtime.set_override("draw_grid", _grid_overlay)
print("[Gridly] Grid overlay ON")
'
}

// ── GridOverlayOff ───────────────────────────────────────────
// Disables the grid overlay, restores default rendering.

Cmd {
  Syntax: 'GridOverlayOff'
  Func: '
import runtime
runtime.clear_override("draw_grid")
print("[Gridly] Grid overlay OFF")
'
}
