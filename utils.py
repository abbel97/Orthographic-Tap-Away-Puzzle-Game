import math

def identity():
    return [
        1.0, 0.0, 0.0, 0.0,
        0.0, 1.0, 0.0, 0.0,
        0.0, 0.0, 1.0, 0.0,
        0.0, 0.0, 0.0, 1.0,
    ]


def translation_matrix(tx, ty, tz):
    m = identity()
    m[12] = tx
    m[13] = ty
    m[14] = tz
    return m


def rotation_x(degrees):
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    m = identity()
    m[5] = c
    m[6] = s
    m[9] = -s
    m[10] = c
    return m


def rotation_y(degrees):
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    m = identity()
    m[0] = c
    m[2] = -s
    m[8] = s
    m[10] = c
    return m


def rotation_z(degrees):
    r = math.radians(degrees)
    c, s = math.cos(r), math.sin(r)
    m = identity()
    m[0] = c
    m[1] = s
    m[4] = -s
    m[5] = c
    return m


def multiply(a, b):
    result = [0.0] * 16
    
    for col in range(4):
        for row in range(4):
            total = 0.0
            for k in range(4):
                total += a[k * 4 + row] * b[col * 4 + k]
            result[col * 4 + row] = total
    return result


def multiply_many(*matrices):
    result = identity()

    for m in matrices:
        result = multiply(result, m)
    return result


def transform_point(m, point):
    x, y, z = point
    out = [0.0, 0.0, 0.0]

    for row in range(3):
        out[row] = (
            m[0 * 4 + row] * x
            + m[1 * 4 + row] * y
            + m[2 * 4 + row] * z
            + m[3 * 4 + row] * 1.0
        )
    return tuple(out)