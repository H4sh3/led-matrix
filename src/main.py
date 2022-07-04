#!/usr/bin/env python
# Display a runtext with double-buffering.
import time

from matrixController import CENTER_MODE, RAIN_MODE, SPIRAL_MODE, SPLASH_MODE, MatrixController

# Twitch API
import twitch

# add secrets.py file with oauth chat token
from secrets import oauth_chat_token

# Main function
if __name__ == "__main__":
    # Start listening for chat messages and add them to our internal representation

    matrixController = MatrixController()

    def subsFunc(message):
        if "toggleLights" in message.text:
            matrixController.headlights = not matrixController.headlights
            return

        if "!color" == message.text:
            matrixController.change_color()
            return

        if "!splash" == message.text:
            matrixController.activate_mode(SPLASH_MODE)
            return

        if "!center" == message.text:
            matrixController.activate_mode(CENTER_MODE)
            return

        if "!spiral" == message.text:
            matrixController.activate_mode(SPIRAL_MODE)
            return

        if "!rain" == message.text:
            matrixController.activate_mode(RAIN_MODE)
            return

        # not a command -> write as message to the matrix

        matrixController.add_message(f'{message.sender}: {message.text}')

    print(f'run_text.headlights {matrixController.headlights}')
    twitch.Chat(channel='#joeybaracuda', nickname='joeybaracuda',
                oauth=oauth_chat_token).subscribe(subsFunc)
    
    # one second to connect to chat
    time.sleep(1)

    # start matrix runner after we initialzed the chat
    matrixController.process()
