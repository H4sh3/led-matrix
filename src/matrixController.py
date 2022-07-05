import random
from samplebase import SampleBase
from rgbmatrix import graphics
from etc import get_random_color
from config import *
import time

import dots as Dots

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

class MatrixController(SampleBase):
    def __init__(self, *args, **kwargs):
        super(MatrixController, self).__init__(*args, **kwargs)
        self.parser.add_argument(
            "-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.y_offsets = [0 for _ in range(7)]
        self.active_gap = False

        self.active_mode = Dots.SPIRAL_MODE

        self.matrixColor = [c for c in COLORS[0]]
        self.targetColor = [c for c in COLORS[1]]

        self.dots = []
        for _ in range(50):
            self.dots.append(Dots.get_dot(self.active_mode,self.matrixColor))

        self.headlights = False

        self.cnt = 0

    def add_message(self,message):
        self.messages.append(Message(message, WIDTH))


    def change_color(self):
        new_color = get_random_color(self.targetColor)
        self.matrixColor = self.targetColor
        self.targetColor = new_color


    def activate_mode(self,new_mode):
        self.active_mode = new_mode

        new_dots = []
        for dot in self.dots:
            new_dot = Dots.get_dot(new_mode,self.matrixColor)
            new_dot.x = dot.x
            new_dot.y = dot.y
            new_dot.color = dot.color
            new_dots.append(new_dot)
        self.dots = new_dots


    def update_dots(self):
        # remove dots that reached the bottom

        for dot in self.dots:
            self.canvas.SetPixel(dot.x, dot.y, dot.color[0], dot.color[1], dot.color[2])

        self.dots = [dot for dot in self.dots if not dot.is_done()]

        for dot in self.dots:
            dot.update()

        if len(self.messages) == 0:
            for _ in range(6):
                self.dots.append(Dots.get_dot(self.active_mode,self.matrixColor))


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



            s = random.randint(1,5)
            for i in range(3):
                self.matrixColor[i] += s if self.matrixColor[i] < self.targetColor[i] else -s

                if self.matrixColor[i] < 0:
                    self.matrixColor[i] = 0
                if self.matrixColor[i] > 255:
                    self.matrixColor[i] = 255

            self.cnt+=1
            # new mode every n-steps


            if self.cnt == 100:
                self.matrixColor = self.targetColor
                self.targetColor = get_random_color(self.matrixColor)

            if self.cnt >= 200:
                print(f'num dots {len(self.dots)}')
                new_mode = (self.active_mode+1)%len(Dots.MODES)
                new_mode = Dots.MODES[random.randint(0,len(Dots.MODES)-1)]
                while new_mode == self.active_mode:
                   new_mode = Dots.MODES[random.randint(0,len(Dots.MODES)-1)]
                #self.activate_mode(new_mode)
                self.cnt = 0