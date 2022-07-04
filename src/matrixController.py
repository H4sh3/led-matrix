import math
import random
from samplebase import SampleBase
from rgbmatrix import graphics
from etc import get_random_color
from config import *
import time

SPIRAL_MODE = 0
CENTER_MODE = 1
RAIN_MODE = 2
SPLASH_MODE = 3

MODES = [SPIRAL_MODE,CENTER_MODE,SPLASH_MODE,RAIN_MODE]

font = graphics.Font()
font.LoadFont(f"../../../fonts/{FONT_NAME}")

class Message():
    def __init__(self, message, init_pos):
        self.message = message
        self.init_pos = init_pos
        self.curr_pos = init_pos
        self.completed = 0

        color = get_random_color()
        self.text_color = graphics.Color(color[0],color[1],color[2])

    def step(self, len):
        self.curr_pos -= 1
        if (self.curr_pos + len < 0):
            self.curr_pos = self.init_pos
            self.completed += 1

    def finished(self) -> bool:
        return self.completed >= 2

def rotate(point,origin , angle):
    ox, oy = origin
    px, py = point

    qx = ox + math.cos(angle) * (px - ox) - math.sin(angle) * (py - oy)
    qy = oy + math.sin(angle) * (px - ox) + math.cos(angle) * (py - oy)
    return qx, qy

class Dot():
    def __init__(self,mode,color):
        self.mode = mode
        self.color = color

        if self.mode == SPIRAL_MODE:
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
            self.y += random.randint(-2,2)
            self.x += random.randint(-2,2)
        elif self.mode == CENTER_MODE:
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
        elif self.mode == SPLASH_MODE:
                self.x = CENTER+random.randint(-5,5)
                self.y = CENTER+random.randint(-5,5)
        elif self.mode == RAIN_MODE:
            self.x = random.randint(0,63)
            self.y = 0

    def update(self):
        if self.mode == CENTER_MODE:
            self.y += -1 if self.y > CENTER else 1
            self.x += -1 if self.x > CENTER else 1
            return

        if self.mode == SPLASH_MODE:
            self.x += 1 if self.x >= CENTER else -1
            self.y += 1 if self.y >= CENTER else -1
            return

        if self.mode == SPIRAL_MODE:
            # rotate
            x,y = rotate((self.x,self.y),CENTER_P,math.radians(5))
            self.x = x
            self.y = y

            # move to center
            step = 0.55
            self.x += step if self.x <= CENTER else -step
            self.y += step if self.y <= CENTER else -step
            return
        
        if self.mode == RAIN_MODE:
            self.y+=1

    def isDone(self):
        if self.mode == CENTER_MODE:
            return abs(self.x - CENTER) <= 2 and abs(self.y - CENTER) <= 2

        if self.mode == SPLASH_MODE:
            return self.x <= 0 or self.x >= WIDTH or self.y >= WIDTH or self.y <= 0

        if self.mode == SPIRAL_MODE:
            return abs(self.x - CENTER) <= 1 and abs(self.y - CENTER) <= 1
        
        if self.mode == RAIN_MODE:
            return self.y >= 63


class MatrixController(SampleBase):
    def __init__(self, *args, **kwargs):
        super(MatrixController, self).__init__(*args, **kwargs)
        self.parser.add_argument(
            "-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.y_offsets = [0 for _ in range(7)]
        self.active_gap = False

        self.active_mode = RAIN_MODE

        self.matrixColor = get_random_color()

        self.dots = []
        for _ in range(50):
            self.dots.append(Dot(self.active_mode,self.matrixColor))


        self.respawn_dot_cooldown = 0

        self.headlights = False

        self.cnt = 0

    def add_message(self,message):
        self.messages.append(Message(message, WIDTH))

    def change_color(self):
        self.matrixColor = [random.randint(0,255) for _ in range(3)]
        return

        old_color = self.matrixColor

        new_color = get_random_color()
        while old_color[0] == new_color[0] and old_color[1] == new_color[1] and old_color[2] == new_color[2]:
            new_color = get_random_color()

        self.matrixColor = get_random_color()



    def activate_mode(self,new_mode):
        self.active_mode = new_mode

        print(f'new mode {self.active_mode}')
        # update existing dots
        for dot in self.dots:
            dot.mode=new_mode

    def update_dots(self):
        # remove dots that reached the bottom
        self.dots = [dot for dot in self.dots if not dot.isDone()]

        for dot in self.dots:
            self.canvas.SetPixel(dot.x, dot.y, dot.color[0], dot.color[1], dot.color[2])

        for dot in self.dots:
            dot.update()


        # return early if splash cd is not yet 0
        if self.respawn_dot_cooldown >= 0:
            self.respawn_dot_cooldown-=1

            if self.respawn_dot_cooldown == 1:
                self.matrixColor = get_random_color()
            return

        if len(self.messages) == 0:
            for _ in range(3):
                self.dots.append(Dot(self.active_mode,self.matrixColor))
                self.dots.append(Dot(self.active_mode,self.matrixColor))

    def update_messages(self):
        # render messages
        for i, m in enumerate(self.messages):
            if i >= MESSAGE_ROWS:
                break
            length = graphics.DrawText(
                self.canvas, font, m.curr_pos, 3+CHAR_HEIGHT+(i*6)+(i*CHAR_HEIGHT)+self.y_offsets[i], m.text_color, m.message)
            m.step(length)


        # Remove messages that have been shown n-times)
        for i, message in enumerate(self.messages):
            if message.finished():  # and not self.active_gap:
                for j in range(i, MESSAGE_ROWS+1):
                    if self.y_offsets[j] != 0:
                        continue
                    self.y_offsets[j] = CHAR_HEIGHT

                self.messages.remove(message)

        # Update message offset to fill gaps smoothly
        for i, offset in enumerate(self.y_offsets):
            if offset <= 0:
                continue
            self.y_offsets[i] -= 1

    def run(self):
        #self.matrix.brightness = 75
        print(f'brightness: {self.matrix.brightness}')

        self.canvas = self.matrix.CreateFrameCanvas()

        self.messages = []

        while True:

            if self.headlights:
                for x in range(0, 64):
                    self.canvas.SetPixel(x, 0, 255, 255, 255)
                    self.canvas.SetPixel(x, 63, 255, 255, 255)


            self.canvas.Clear()

            self.update_dots()
            self.update_messages()

            time.sleep(SLEEP_DURATION)

            self.canvas = self.matrix.SwapOnVSync(self.canvas)




            self.cnt+=1
            # new mode every n-steps
            if self.cnt % 50 == 0:
                self.change_color()

            if self.cnt >= 150:
                print(f'num dots {len(self.dots)}')
                #new_mode = (self.active_mode+1)%len(MODES)
                # new_mode = MODES[random.randint(0,len(MODES)-1)]
                # while new_mode == self.active_mode:
                #   new_mode = MODES[random.randint(0,len(MODES)-1)]
                #self.activate_mode(new_mode)
                self.cnt = 0