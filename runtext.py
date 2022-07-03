#!/usr/bin/env python
# Display a runtext with double-buffering.
from posixpath import split
from xml.etree.ElementInclude import include
from samplebase import SampleBase
from rgbmatrix import graphics
import time
import random
import math

# Twitch API
import twitch

# add secrets.py file with oauth chat token
from secrets import oauth_chat_token


# source code for matrix and canvas
# https://github.com/hzeller/rpi-rgb-led-matrix/blob/a93acf26990ad6794184ed8c9487ab2a5c39cd28/bindings/python/rgbmatrix/core.pyx

COLORS = [
    (255, 0, 0),
    (0, 255, 0),
    (0, 0, 255),
    (199, 8, 241),
    (0, 232, 255),
    (255, 221, 7),
    (255, 7, 202),
]

MESSAGE_ROWS = 4

FONT_NAME = "9x15B.bdf"
CHAR_HEIGHT = 10

SLEEP_DURATION = (60/1000)/2
WIDTH = 64
CENTER= (WIDTH//2)-1
CENTER_P = (CENTER,CENTER)
print(f'CenterP: {CENTER_P}')


def get_random_color():
    return COLORS[random.randint(0, len(COLORS)-1)]


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
    def __init__(self,initSpawn=False):
        # todo refactor this in mode that gets set
        self.splash= False
        self.center= False
        self.spiral= True
        self.fall = False

        if self.spiral:
            if random.random() > 0.5:
                self.x = 0+random.randint(0,5)
                self.y = 0
            else:
                self.x = 63-random.randint(0,5)
                self.y = 63
        else:
            self.x = random.randint(0,63)
            self.y = random.randint(0,63) if initSpawn else 0

    def toggleSplash(self):
        self.splash = not self.splash

    def toggleCenter(self):
        self.center = not self.center

    def toggleRotate(self):
        self.spiral = not self.spiral

    def update(self):
        if self.center:
            self.y += -1 if self.y >= WIDTH//2 else 1
            self.x += -1 if self.x >= WIDTH//2 else 1
            return

        if self.splash:
            self.x += 1 if self.x >= WIDTH//2 else -1
            self.y += 1 if self.y >= WIDTH//2 else -1
            return

        if self.spiral:

            # rotate
            x,y = rotate((self.x,self.y),CENTER_P,math.radians(5))
            self.x = x
            self.y = y

            # move to center
            step = 0.4
            self.x += step if self.x <= CENTER else -step
            self.y += step if self.y <= CENTER else -step
            return
        
        if self.fall:
            self.y+=1

    def isDone(self):
        if self.center:
            return abs(self.x - CENTER) <= 2 and abs(self.y - CENTER) <= 2

        if self.splash:
            return self.x <= 0 or self.x >= WIDTH or self.y >= WIDTH or self.y <= 0

        if self.spiral:
            return abs(self.x - CENTER) <= 0.5 and abs(self.y - CENTER) <= 0.5
        
        if self.fall:
            return self.y >= 63


class RunText(SampleBase):
    def __init__(self, *args, **kwargs):
        super(RunText, self).__init__(*args, **kwargs)
        self.parser.add_argument(
            "-t", "--text", help="The text to scroll on the RGB LED panel", default="Hello world!")

        self.y_offsets = [0 for _ in range(7)]
        self.active_gap = False

        self.dots = []
        for _ in range(50):
            self.dots.append(Dot(True))

        self.matrixColor = get_random_color()

        self.respawn_dot_cooldown = 0


    def update_dots(self):
        # render matrix dots if no message is in chat
        for dot in self.dots:
            dot.update()

        for dot in self.dots:
            self.matrix.SetPixel(dot.x, dot.y, self.matrixColor[0], self.matrixColor[1], self.matrixColor[2])

        # remove dots that reached the bottom
        self.dots = [dot for dot in self.dots if not dot.isDone()]

        # return early if splash cd is not yet 0
        if self.respawn_dot_cooldown >= 0:
            self.respawn_dot_cooldown-=1

            if self.respawn_dot_cooldown == 1:
                self.matrixColor = get_random_color()
            return

        if len(self.messages) == 0:
            self.dots.append(Dot())
            self.dots.append(Dot())


    def run(self):
        self.matrix.brightness = 75
        print(f'brightness: {self.matrix.brightness}')

        offscreen_canvas = self.matrix.CreateFrameCanvas()
        width = offscreen_canvas.width

        self.messages = []

        self.headlights = False

        # Start listening for chat messages and add them to our internal representation

        def subsFunc(message):

            if "toggleLights" in message.text:
                self.headlights = not self.headlights
                return

            if "!color" == message.text:
                self.matrixColor = get_random_color()
                return

            if "!splash" == message.text:
                for dot in self.dots:
                    dot.toggleSplash()
                self.respawn_dot_cooldown = 30
                return

            if "!center" == message.text:
                for dot in self.dots:
                    dot.toggleCenter()
                self.respawn_dot_cooldown = 30
                return

            if "!spiral" == message.text:
                for dot in self.dots:
                    dot.toggleRotate()
                self.respawn_dot_cooldown = 120
                return

            self.messages.append(Message(f'{message.sender}: {message.text}', width))

            print(f'self.headlights {self.headlights}')

        twitch.Chat(channel='#joeybaracuda', nickname='joeybaracuda',
                    oauth=oauth_chat_token).subscribe(subsFunc)

        font = graphics.Font()
        font.LoadFont(f"../../../fonts/{FONT_NAME}")

        while True:
            offscreen_canvas.Clear()

            if self.headlights:
                for x in range(0, 64):
                    self.matrix.SetPixel(x, 0, 255, 255, 255)
                    self.matrix.SetPixel(x, 63, 255, 255, 255)


            self.update_dots()

            # render messages
            for i, m in enumerate(self.messages):
                if i >= MESSAGE_ROWS:
                    break
                length = graphics.DrawText(
                    offscreen_canvas, font, m.curr_pos, 3+CHAR_HEIGHT+(i*6)+(i*CHAR_HEIGHT)+self.y_offsets[i], m.text_color, m.message)
                m.step(length)

            time.sleep(SLEEP_DURATION)

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

            offscreen_canvas = self.matrix.SwapOnVSync(offscreen_canvas)


# Main function
if __name__ == "__main__":
    run_text = RunText()
    if (not run_text.process()):
        run_text.print_help()
