import itertools
import random
import cube as cube_module

PALETTE = [
    (0.85, 0.25, 0.25),  #red
    (0.25, 0.55, 0.85),  #blue
    (0.30, 0.75, 0.35),  #green
    (0.90, 0.70, 0.20),  #amber
    (0.65, 0.35, 0.80),  #purple
    (0.95, 0.55, 0.20),  #orange
    (0.30, 0.80, 0.80),  #teal
    (0.80, 0.80, 0.85),  #light gray
    (0.90, 0.45, 0.65),  #rose
    (0.45, 0.85, 0.75),  #mint
]

_ALL_DIR_KEYS = list(cube_module.DIRECTIONS.keys())
_AXES = ((0, "-x", "+x"), 
         (1, "-y", "+y"), 
         (2, "-z", "+z"))


def _depth_score(layout_dict):
    positions = list(layout_dict.keys())

    blocked_by = {pos: set() for pos in positions}
    for p in positions:
        dk = layout_dict[p]
        for other in positions:
            if p != other and cube_module.blocks(dk, p, other):
                blocked_by[p].add(other)

    active = {pos: set(blocked_by[pos]) for pos in positions}
    remaining = set(positions)
    total_score = 0
    wave = 0

    while remaining:
        freeable = {pos for pos in remaining if not active[pos]}

        if not freeable:
            return -1                   
        total_score += wave * len(freeable)
        remaining   -= freeable
        wave        += 1
        for other in remaining:  
            active[other] -= freeable

    return total_score


def _simpler_level(n, all_positions, rng):  #onion_peel method, fallback method for generating a solvable layout
    layout = {}

    for pos in all_positions:
        candidates = []
        for axis, neg_key, pos_key in _AXES:
            coord = pos[axis]
            candidates.append((coord, neg_key))
            candidates.append((n - 1 - coord, pos_key))

        min_dist  = min(d for d, _ in candidates)
        best_keys = [key for d, key in candidates if d == min_dist]
        layout[pos] = rng.choice(best_keys)
    return layout


def generate_hard_level(n, seed=None):
    rng         = random.Random(seed)
    all_positions = list(itertools.product(range(n), repeat=3))
    n_cubes     = n ** 3

    best_layout = None
    best_score  = -1

    attempts = max(40, 1200 // n_cubes)

    for _ in range(attempts):
        layout = {pos: rng.choice(_ALL_DIR_KEYS) for pos in all_positions}
        score  = _depth_score(layout)
        if score > best_score:
            best_score  = score
            best_layout = layout

    if best_score <= 0:
        layout = _simpler_level(n, all_positions, rng)
        score  = _depth_score(layout)

        shuffled = list(all_positions)
        for _ in range(3):              
            rng.shuffle(shuffled)
            for pos in shuffled:
                current_dk = layout[pos]
                for dk in rng.sample(_ALL_DIR_KEYS, 4):
                    if dk == current_dk:
                        continue
                    layout[pos] = dk
                    new_score   = _depth_score(layout)
                    if new_score > score:
                        score      = new_score
                        current_dk = dk       
                    else:
                        layout[pos] = current_dk  

        if score > best_score:
            best_score  = score
            best_layout = layout

    color_pool = (list(PALETTE) * ((n_cubes // len(PALETTE)) + 1))[:n_cubes]
    rng.shuffle(color_pool)

    return [
        (pos, best_layout[pos], color_pool[i])
        for i, pos in enumerate(all_positions)
    ]


def verify_solvable(layout):
    d = {pos: dk for pos, dk, *_ in layout}
    return _depth_score(d) >= 0