# Orthographic Tap way 3D Puzzle Game

A 3-D block-clearing puzzle rendered in **parallel (orthographic) projection** using PyOpenGL and pygame.
---

## Gameplay

You are presented with a compact cluster of small cubes. Every cube carries a **directional arrow** showing the only path it can travel.  Click a cube and it flies out along its arrow, but only if the entire path ahead of it is **unobstructed**.

Clear every cube to solve the puzzle.

---

## Controls

| Input | Action |
|---|---|
| **Left-drag** | Rotate the block in 3-D to inspect it from any angle |
| **Left-click** | Tap a cube, it exits if free, flashes orange if blocked |
| **R** | Restart the current puzzle (same seed) |
| **N** | Generate a brand-new random puzzle |
| **+  /  =** | Increase grid size (harder, more cubes) |
| **−** | Decrease grid size (easier, fewer cubes) |
| **ESC** | Quit |

---

## Technical highlights

| Concept | Where used |
|---|---|
| **Orthographic projection** (`glOrtho`) | `renderer.py → setup_projection` |
| **3-D affine transformations** | `utils.py` - flat-list 4×4 matrices, column-major for OpenGL |
| **Global rotation via mouse drag** | `game.py → apply_drag_rotation` |
| **Color-buffer picking** | `picker.py` - each cube rendered as a unique flat colour; `glReadPixels` decodes the click |
| **Obstruction check** | `cube.py → blocks()` - integer axis-aligned ray test |
| **Exit animation** | `cube.py → update()` - increments `anim_distance` along the direction vector each frame |
| **Blocked flash** | `renderer.py → _display_color()` - lerp to orange while `blocked_flash_timer > 0` |
| **Hard puzzle generation** | `puzzle.py → generate_hard_level()` - random-restart search maximising dependency-chain depth |

---

## Puzzle generation, how difficulty works

The generator scores a layout by simulating a **greedy wave solve**:

- **Wave 0** - cubes that are free from the start.
- **Wave k** - cubes that only become free after all wave-0 … wave-(k-1) cubes are removed.

**Depth score = Σ (wave\_index × cubes freed in that wave).**

A high score means many cubes are buried deep in dependency chains and require careful ordering to remove.  The generator tries up to ~40 random layouts (for a 4×4×4 grid) and keeps the highest-scoring solvable one, falling back to a hill-climbing improvement of the onion-peel baseline if needed.

---

## Setup

```bash
pip install -r requirements.txt
python main.py
```