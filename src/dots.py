
import math
import random
from config import CENTER, CENTER_P, WIDTH
from etc import rotate

SPIRAL_MODE = 0
CENTER_MODE = 1
RAIN_MODE = 2
SPLASH_MODE = 3

MODES = [SPIRAL_MODE,CENTER_MODE,SPLASH_MODE,RAIN_MODE]


class DotInterface():
    def __init__(self,mode,color):
        self.mode = mode
        self.color = color

    def update(self):
        ...

    def isDone(self):
        ...

class CenterDot(DotInterface):
    def __init__(self,*args, **kwargs):
        super(CenterDot, self).__init__(*args, **kwargs)

        sides = ["l","r","t","b"]
        side = sides[random.randint(0,len(sides)-1)]
        if side == "l":
            self.x = 0
            self.y = random.randint(0,WIDTH)
        elif side =="r":
            self.x = WIDTH
            self.y = random.randint(0,WIDTH)
        elif side =="t":
            self.x = random.randint(0,WIDTH)
            self.y = 0
        elif side =="b":
            self.x = random.randint(0,WIDTH)
            self.y = WIDTH
    
    def update(self):
        self.y += -1 if self.y > CENTER else 1
        self.x += -1 if self.x > CENTER else 1
    
    def is_done(self):
        return abs(self.x - CENTER) <= 2 and abs(self.y - CENTER) <= 2


class SplashDot(DotInterface):
    def __init__(self,*args, **kwargs):
        super(SplashDot, self).__init__(*args, **kwargs)

        self.x = CENTER+random.randint(-5,5)
        self.y = CENTER+random.randint(-5,5)

    def update(self):
        self.x += 1 if self.x >= CENTER else -1
        self.y += 1 if self.y >= CENTER else -1

    def is_done(self):
        return self.x <= 0 or self.x >= WIDTH or self.y >= WIDTH or self.y <= 0


class SpiralDot(DotInterface):
    def __init__(self,*args, **kwargs):
        super(SpiralDot, self).__init__(*args, **kwargs)
        sides = ["l","r","t","b"]
        side = sides[random.randint(0,len(sides)-1)]
        if side == "l":
            self.x = 0
            self.y = WIDTH//2
        elif side =="r":
            self.x = WIDTH
            self.y = WIDTH//2
        elif side =="t":
            self.x = WIDTH//2
            self.y = 0
        elif side =="b":
            self.x = WIDTH//2
            self.y = WIDTH

        #self.y = 0 if random.random() > 0.5 else CENTER
        #self.x = 0 if random.random() > 0.5 else CENTER
        r = 1
        self.y += random.randint(-r,r)
        self.x += random.randint(-r,r)

    def update(self):
        x,y = rotate((self.x,self.y),CENTER_P,math.radians(9))
        self.x = x
        self.y = y

        # move to center
        step = 0.15
        self.x += step if self.x <= CENTER else -step
        self.y += step if self.y <= CENTER else -step

    def is_done(self):
        return abs(self.x - CENTER) <= 1 and abs(self.y - CENTER) <= 1


class RainDot(DotInterface):
    def __init__(self,*args, **kwargs):
        super(RainDot, self).__init__(*args, **kwargs)

        self.x = random.randint(0,63)
        self.y = 0

    def update(self):
        self.y+=1

    def is_done(self):
        return self.y >= 63

def get_dot(mode,color):
    color = [i for i in color]
    if mode == SPIRAL_MODE:
        return SpiralDot(mode,color)
    
    if mode == CENTER_MODE:
        return CenterDot(mode,color)
    
    if mode == RAIN_MODE:
        return RainDot(mode,color)
    
    if mode == SPLASH_MODE:
        return SplashDot(mode,color)
            