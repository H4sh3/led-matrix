import random
from config import COLORS


def get_random_color():
    return COLORS[random.randint(0, len(COLORS)-1)]