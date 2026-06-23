from OpenGL.GL import (
    glReadPixels,
    glReadBuffer,
    glClearColor,
    glClear,
    glDisable,
    glEnable,
    GL_LIGHTING,
    GL_DITHER,
    GL_BLEND,
    GL_COLOR_BUFFER_BIT,
    GL_DEPTH_BUFFER_BIT,
    GL_RGB,
    GL_UNSIGNED_BYTE,
    GL_BACK,
)

ID_STRIDE = 16


def encode_id(cube_id):
    packed = (cube_id + 1) * ID_STRIDE
    r = (packed & 0x0000FF) / 255.0
    g = ((packed & 0x00FF00) >> 8) / 255.0
    b = ((packed & 0xFF0000) >> 16) / 255.0
    return (r, g, b)


def decode_color(r, g, b):
    packed = r | (g << 8) | (b << 16)

    if packed < ID_STRIDE // 2:
        return None
    
    cube_id = round(packed / ID_STRIDE) - 1
    return cube_id if cube_id >= 0 else None


def pick(mouse_x, mouse_y, window_width, window_height, draw_pick_scene):
    glReadBuffer(GL_BACK)
    glDisable(GL_LIGHTING)
    glDisable(GL_DITHER)
    glDisable(GL_BLEND)
    glClearColor(0.0, 0.0, 0.0, 1.0)
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    draw_pick_scene()

    gl_y = window_height - mouse_y - 1
    if mouse_x < 0 or gl_y < 0 or mouse_x >= window_width or gl_y >= window_height:
        glEnable(GL_LIGHTING)
        return None
    
    radius = 1
    votes = {}
    for dy in range(-radius, radius + 1):
        for dx in range(-radius, radius + 1):
            px = mouse_x + dx
            py = gl_y + dy

            if px < 0 or py < 0 or px >= window_width or py >= window_height:
                continue
            pixel = glReadPixels(px, py, 1, 1, GL_RGB, GL_UNSIGNED_BYTE)
            r, g, b = pixel[0], pixel[1], pixel[2]

            if not isinstance(r, int):
                r, g, b = int(r), int(g), int(b)
            decoded = decode_color(r, g, b)

            if decoded is not None:
                votes[decoded] = votes.get(decoded, 0) + 1

    glEnable(GL_LIGHTING)

    if not votes:
        return None
    return max(votes, key=votes.get)