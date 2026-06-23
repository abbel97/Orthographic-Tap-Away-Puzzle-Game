
DIRECTIONS = {
    "+x": (1, 0, 0),
    "-x": (-1, 0, 0),
    "+y": (0, 1, 0),
    "-y": (0, -1, 0),
    "+z": (0, 0, 1),
    "-z": (0, 0, -1),
}

DEFAULT_EXIT_SPEED = 6.0
DEFAULT_EXIT_DISTANCE = 12.0
BLOCKED_FLASH_DURATION = 0.3


def blocks(direction_key, from_pos, other_pos):
    if other_pos == from_pos:
        return False
    
    dx, dy, dz = DIRECTIONS[direction_key]
    x, y, z = from_pos
    ox, oy, oz = other_pos

    if dx:
        return oy == y and oz == z and (ox - x) * dx > 0
    if dy:
        return ox == x and oz == z and (oy - y) * dy > 0
    if dz:
        return ox == x and oy == y and (oz - z) * dz > 0
    return False

class Cube:
    def __init__(self, cube_id, grid_pos, direction_key, color=(0.75, 0.75, 0.78)):
        self.id = cube_id
        self.grid_pos = tuple(grid_pos)
        self.direction_key = direction_key
        self.direction = DIRECTIONS[direction_key]
        self.color = color

        self.exiting = False
        self.removed = False

        self.anim_distance = 0.0  
        self.blocked_flash_timer = 0.0

    @property
    def anim_offset(self):
        dx, dy, dz = self.direction
        return (dx * self.anim_distance, dy * self.anim_distance, dz * self.anim_distance)

    def start_exit(self):
        if not self.exiting and not self.removed:
            self.exiting = True

    def trigger_blocked_flash(self, duration=BLOCKED_FLASH_DURATION):
        self.blocked_flash_timer = duration

    def update(self, dt, speed=DEFAULT_EXIT_SPEED, exit_distance=DEFAULT_EXIT_DISTANCE):
        if self.blocked_flash_timer > 0.0:
            self.blocked_flash_timer = max(0.0, self.blocked_flash_timer - dt)

        if not self.exiting or self.removed:
            return
        
        self.anim_distance += speed * dt
        if self.anim_distance >= exit_distance:
            self.anim_distance = exit_distance
            self.removed = True

    def is_active(self):
        return not self.exiting and not self.removed

    def __repr__(self):
        return f"Cube(id={self.id}, pos={self.grid_pos}, dir={self.direction_key})"