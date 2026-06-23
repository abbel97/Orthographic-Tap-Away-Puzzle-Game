import sys
import pygame
from pygame.locals import (
    DOUBLEBUF,
    OPENGL,
    RESIZABLE,
    QUIT,
    VIDEORESIZE,
    MOUSEBUTTONDOWN,
    MOUSEBUTTONUP,
    MOUSEMOTION,
    KEYDOWN,
    K_ESCAPE,
    K_r,
    K_n,
    K_EQUALS,
    K_KP_PLUS,
    K_MINUS,
    K_KP_MINUS,
)

import renderer
import picker
from game import GameState

WINDOW_SIZE = (900, 700)
FPS = 60
CLICK_DRAG_THRESHOLD = 4


def main():
    pygame.init()
    pygame.display.set_caption("Tap Away")
    screen = pygame.display.set_mode(WINDOW_SIZE, DOUBLEBUF | OPENGL | RESIZABLE)

    renderer.init_gl()

    game_state = GameState()  
    renderer.fit_to_grid(game_state.grid_size)
    renderer.setup_projection(*WINDOW_SIZE)

    clock = pygame.time.Clock()

    dragging = False
    last_mouse_pos = (0, 0)
    drag_distance = 0  

    running = True
    while running:
        dt = clock.tick(FPS) / 1000.0
        width, height = pygame.display.get_surface().get_size()

        for event in pygame.event.get():
            if event.type == QUIT:
                running = False

            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    running = False
                elif event.key == K_r:
                    game_state.restart()
                elif event.key == K_n:
                    game_state.new_puzzle()
                elif event.key in (K_EQUALS, K_KP_PLUS):
                    game_state.resize(+1)
                    renderer.fit_to_grid(game_state.grid_size)
                    renderer.setup_projection(width, height)
                elif event.key in (K_MINUS, K_KP_MINUS):
                    game_state.resize(-1)
                    renderer.fit_to_grid(game_state.grid_size)
                    renderer.setup_projection(width, height)

            elif event.type == VIDEORESIZE:
                renderer.setup_projection(event.w, event.h)

            elif event.type == MOUSEBUTTONDOWN and event.button == 1:
                dragging = True
                drag_distance = 0
                last_mouse_pos = event.pos

            elif event.type == MOUSEBUTTONUP and event.button == 1:
                if dragging and drag_distance < CLICK_DRAG_THRESHOLD:
                    _handle_click(event.pos, game_state)
                dragging = False

            elif event.type == MOUSEMOTION and dragging:
                dx = event.pos[0] - last_mouse_pos[0]
                dy = event.pos[1] - last_mouse_pos[1]
                drag_distance += abs(dx) + abs(dy)
                game_state.apply_drag_rotation(dx, dy)
                last_mouse_pos = event.pos

        game_state.update(dt)

        renderer.draw_scene(game_state, picking=False)
        pygame.display.flip()

        size_label = f"{game_state.grid_size}x{game_state.grid_size}x{game_state.grid_size}"
        if game_state.is_won():
            pygame.display.set_caption(
                f"Tap Away -- {size_label} solved! Press N for a new one, R to replay."
            )
        else:
            pygame.display.set_caption(
                f"Tap Away -- {size_label} ({game_state.remaining_count()} cubes left)"
            )

    pygame.quit()
    sys.exit()


def _handle_click(mouse_pos, game_state):
    width, height = pygame.display.get_surface().get_size()
    cube_id = picker.pick(
        mouse_pos[0],
        mouse_pos[1],
        width,
        height,
        draw_pick_scene=lambda: renderer.draw_scene(game_state, picking=True),
    )

    if cube_id is None:
        return
    cube = game_state.get_cube(cube_id)
    moved = game_state.try_remove(cube_id)
    
    if cube is not None:
        print(f"picked cube id={cube_id} pos={cube.grid_pos} dir={cube.direction_key} -> {'moved' if moved else 'blocked'}")


if __name__ == "__main__":
    main()