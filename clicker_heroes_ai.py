import cv2
import pyautogui

import config
import core
import file_handler as fh
import renderer as rnd
import utilities as util
import detectors as dts
from pynput import keyboard
from threading import Thread
import time


logic_running = False


def on_release(key):
    global logic_running
    if key == keyboard.Key.space:
        logic_running ^= True
        print("Logic:", logic_running)


def game_loop(game):
    print("SETUP DONE!")
    global logic_running
    while game.control_window.running:
        game.control_window.root.update()
        if logic_running:
            game.change_level()
            if dts.detect_hero(game):
                core.hero_leveling_logic(game)
            else:
                util.scroll_down(game)
            util.auto_click()
        else:
            img = rnd.get_screenshot()
            rnd.render(img)


def setup():
    heroes, game_data, powers = fh.load_from_file()
    game = util.create_game_data(heroes, game_data, powers)
    hwnd = rnd.find_game_win()
    if heroes and hwnd:
        rnd.move_game_win(hwnd)
        time.sleep(1)
        game.create_control_win()
        game_thread = Thread(target=game_loop, args=(game, ))
        listener = keyboard.Listener(on_release=on_release)
        listener.start()
        game_thread.start()
        game.control_window.run()
        game_thread.join()
        listener.stop()
        listener.join()


def main():
    setup()
    cv2.destroyAllWindows()
    print("Program terminated")


if __name__ == '__main__':
    main()
