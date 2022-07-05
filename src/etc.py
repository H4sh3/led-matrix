import math
import random
from config import COLORS


def get_random_color(oldColor):
    # return [random.randint(0,255) for _ in range(3)]
    indx = random.randint(0, len(COLORS)-2)
    f = [c for c in COLORS if c[0] != oldColor[0] or c[1] != oldColor[1] or c[2] != oldColor[2]]
    return [c for c in f[indx]]



def rotate(point,origin , angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

