import random

import utils
import puzzle
import cube as cube_module
from cube import Cube

DEFAULT_GRID_SIZE = 4
MIN_GRID_SIZE = 2
MAX_GRID_SIZE = 6


class GameState:
    def __init__(self, grid_size=DEFAULT_GRID_SIZE, seed=None):
        self.grid_size = grid_size
        self.seed = seed if seed is not None else random.randrange(1 << 30)
        self.cubes = []
        self.rotation_matrix = utils.identity()
        self.moves = 0
        self.center = (0.0, 0.0, 0.0)
        self._build()

    def _build(self):
        self.moves = 0
        self.rotation_matrix = utils.identity()

        layout = puzzle.generate_hard_level(self.grid_size, seed=self.seed)
        self.cubes = [
            Cube(cube_id=i, grid_pos=pos, direction_key=direction, color=color)
            for i, (pos, direction, color) in enumerate(layout)
        ]
        self.center = self._compute_center()

    def restart(self):
        self._build()

    def new_puzzle(self, grid_size=None):
        if grid_size is not None:
            self.grid_size = grid_size
        self.seed = random.randrange(1 << 30)
        self._build()

    def resize(self, delta):
        new_size = max(MIN_GRID_SIZE, min(MAX_GRID_SIZE, self.grid_size + delta))
        if new_size != self.grid_size:
            self.new_puzzle(grid_size=new_size)

    def _compute_center(self):
        if not self.cubes:
            return (0.0, 0.0, 0.0)
        
        xs = [c.grid_pos[0] for c in self.cubes]
        ys = [c.grid_pos[1] for c in self.cubes]
        zs = [c.grid_pos[2] for c in self.cubes]

        return (
            (min(xs) + max(xs)) / 2.0,
            (min(ys) + max(ys)) / 2.0,
            (min(zs) + max(zs)) / 2.0,
        )

    def apply_drag_rotation(self, dx_pixels, dy_pixels, sensitivity=0.4):
        delta = utils.multiply(
            utils.rotation_x(dy_pixels * sensitivity),
            utils.rotation_y(dx_pixels * sensitivity),
        )
        self.rotation_matrix = utils.multiply(delta, self.rotation_matrix)

    def get_cube(self, cube_id):
        for c in self.cubes:
            if c.id == cube_id:
                return c
        return None

    def is_path_clear(self, cube):
        for other in self.cubes:
            if other is cube or other.removed:
                continue
            if cube_module.blocks(cube.direction_key, cube.grid_pos, other.grid_pos):
                return False
        return True

    def try_remove(self, cube_id):
        cube = self.get_cube(cube_id)

        if cube is None or not cube.is_active():
            return False
        
        if self.is_path_clear(cube):
            cube.start_exit()
            self.moves += 1
            return True
        
        cube.trigger_blocked_flash()
        return False

    def is_won(self):
        return all(c.removed for c in self.cubes)

    def remaining_count(self):
        return sum(1 for c in self.cubes if not c.removed)

    def update(self, dt):
        for c in self.cubes:
            c.update(dt)