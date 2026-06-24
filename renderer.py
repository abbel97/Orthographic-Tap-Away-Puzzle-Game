import math

from OpenGL.GL import (
    glViewport,   glMatrixMode,
    glLoadIdentity, glOrtho,
    glEnable,    glClearColor,
    glShadeModel, glClear,
    glTranslatef, glMultMatrixf,
    glPushMatrix, glPopMatrix,
    glColor3f,   glNormal3f,
    glBegin,     glEnd,
    glVertex3f,  glLightfv, glColorMaterial,
    GL_PROJECTION,  GL_MODELVIEW,
    GL_DEPTH_TEST,  GL_LIGHTING,
    GL_LIGHT0,      GL_POSITION,
    GL_DIFFUSE,    GL_AMBIENT,
    GL_COLOR_MATERIAL, GL_FRONT_AND_BACK,
    GL_AMBIENT_AND_DIFFUSE,  GL_SMOOTH,
    GL_COLOR_BUFFER_BIT, GL_DEPTH_BUFFER_BIT,
    GL_QUADS,     GL_TRIANGLES,
)

import picker
import cube as cube_module


NEAR_PLANE = 0.1
FAR_PLANE = 100.0
CAMERA_DISTANCE = 10.0    

CUBE_HALF_SIZE = 0.485   
SPACING = 1.0                                    

ARROW_COLOR = (0.08, 0.08, 0.10)
BLOCKED_FLASH_COLOR = (1.0, 0.35, 0.05) #bright orange


def _display_color(cube):
    if cube.blocked_flash_timer <= 0.0:
        return cube.color
    
    t = min(1.0, cube.blocked_flash_timer / cube_module.BLOCKED_FLASH_DURATION)
    return tuple(
        BLOCKED_FLASH_COLOR[i] * t + cube.color[i] * (1.0 - t) for i in range(3)
    )

_half_height = 4.0


def init_gl():
    glEnable(GL_DEPTH_TEST)
    glEnable(GL_LIGHTING)
    glEnable(GL_LIGHT0)
    glLightfv(GL_LIGHT0, GL_POSITION, (5.0, 8.0, 10.0, 0.0))
    glLightfv(GL_LIGHT0, GL_DIFFUSE, (1.0, 1.0, 1.0, 1.0))
    glLightfv(GL_LIGHT0, GL_AMBIENT, (0.35, 0.35, 0.38, 1.0))

    glEnable(GL_COLOR_MATERIAL)
    glColorMaterial(GL_FRONT_AND_BACK, GL_AMBIENT_AND_DIFFUSE)

    glShadeModel(GL_SMOOTH)
    glClearColor(0.10, 0.11, 0.14, 1.0)

def fit_to_grid(grid_size, margin=1.2):
    global _half_height
    extent = (grid_size - 1) / 2.0 * SPACING + CUBE_HALF_SIZE
    radius = math.sqrt(3) * extent
    _half_height = radius * margin


def setup_projection(width, height):
    height = max(height, 1)
    glViewport(0, 0, width, height)

    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    aspect = width / float(height)
    half_h = _half_height
    half_w = half_h * aspect
    glOrtho(-half_w, half_w, -half_h, half_h, NEAR_PLANE, FAR_PLANE)

    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()


def draw_scene(game_state, picking=False):
    if not picking:
        glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)

    glLoadIdentity()
    glTranslatef(0.0, 0.0, -CAMERA_DISTANCE)
    glMultMatrixf(game_state.rotation_matrix)

    cx, cy, cz = game_state.center
    for cube in game_state.cubes:
        if cube.removed:
            continue

        ox, oy, oz = cube.anim_offset
        wx = (cube.grid_pos[0] - cx + ox) * SPACING
        wy = (cube.grid_pos[1] - cy + oy) * SPACING
        wz = (cube.grid_pos[2] - cz + oz) * SPACING

        glPushMatrix()
        glTranslatef(wx, wy, wz)

        if picking:
            glColor3f(*picker.encode_id(cube.id))
            _draw_cube_body(CUBE_HALF_SIZE)
        else:
            glColor3f(*_display_color(cube))
            _draw_cube_body(CUBE_HALF_SIZE)
            _draw_arrow(cube.direction, CUBE_HALF_SIZE)
        glPopMatrix()


def _draw_cube_body(s):
    faces = (
        ((0, 0, 1), ((-s, -s, s), (s, -s, s), (s, s, s), (-s, s, s))),       #+Z
        ((0, 0, -1), ((s, -s, -s), (-s, -s, -s), (-s, s, -s), (s, s, -s))),  #-Z
        ((1, 0, 0), ((s, -s, s), (s, -s, -s), (s, s, -s), (s, s, s))),       #+X
        ((-1, 0, 0), ((-s, -s, -s), (-s, -s, s), (-s, s, s), (-s, s, -s))),  #-X
        ((0, 1, 0), ((-s, s, s), (s, s, s), (s, s, -s), (-s, s, -s))),       #+Y
        ((0, -1, 0), ((-s, -s, -s), (s, -s, -s), (s, -s, s), (-s, -s, s))),  #-Y
    )
    
    for normal, verts in faces:
        glNormal3f(*normal)
        glBegin(GL_QUADS)
        for v in verts:
            glVertex3f(*v)
        glEnd()


def _perp_basis(direction):
    dx, dy, dz = direction

    if abs(dx) > 0.5:
        return (0, 1, 0), (0, 0, 1)
    if abs(dy) > 0.5:
        return (1, 0, 0), (0, 0, 1)
    return (1, 0, 0), (0, 1, 0)


def _draw_arrow(direction, half_size, color=ARROW_COLOR):
    s = half_size
    u, v = _perp_basis(direction)
    
    normals = [u, [-x for x in u], v, [-x for x in v]]
    
    glColor3f(*color)
    
    for normal in normals:
        nx, ny, nz = normal
        eps = s * 0.02 
        face_center = (nx * s, ny * s, nz * s)
        
        rx = ny * direction[2] - nz * direction[1]
        ry = nz * direction[0] - nx * direction[2]
        rz = nx * direction[1] - ny * direction[0]
        
        def to_world(right_amt, forward_amt):
            return (
                face_center[0] + eps * nx + right_amt * rx + forward_amt * direction[0],
                face_center[1] + eps * ny + right_amt * ry + forward_amt * direction[1],
                face_center[2] + eps * nz + right_amt * rz + forward_amt * direction[2],
            )

        shaft_half_w = 0.16 * s
        head_half_w = 0.32 * s
        shaft_bottom = -0.40 * s
        shaft_top = 0.05 * s
        head_tip = 0.46 * s

        glNormal3f(*normal)
        glBegin(GL_TRIANGLES)
        
        p1 = to_world(-shaft_half_w, shaft_bottom)
        p2 = to_world(shaft_half_w, shaft_bottom)
        p3 = to_world(shaft_half_w, shaft_top)
        p4 = to_world(-shaft_half_w, shaft_top)
        glVertex3f(*p1)
        glVertex3f(*p2)
        glVertex3f(*p3)
        glVertex3f(*p1)
        glVertex3f(*p3)
        glVertex3f(*p4)
        
        h1 = to_world(-head_half_w, shaft_top)
        h2 = to_world(head_half_w, shaft_top)
        h3 = to_world(0.0, head_tip)
        glVertex3f(*h1)
        glVertex3f(*h2)
        glVertex3f(*h3)
        
        glEnd()