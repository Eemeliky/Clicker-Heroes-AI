import cv2
import core
import file_handler as fh
import renderer as rnd
import utilities as util
import detectors as dts
from pynput import keyboard
from threading import Thread
from config import DEBUG
import time

LOGIC_RUNNING = False


def on_release(key):
    global LOGIC_RUNNING
    if key == keyboard.Key.ctrl and DEBUG:
        x, y = util.get_position()
        value = util.get_pixel_val()
        print(f"({x},{y}) [{value}]")
    elif key == keyboard.Key.space:
        LOGIC_RUNNING ^= True
        print("Logic:", LOGIC_RUNNING)


def game_functions(game):
    game.check_level()
    core.power_use_logic(game)
    util.auto_click()
    if dts.detect_hero(game):
        core.hero_leveling_logic(game)
    else:
        util.scroll_down(game)


def game_loop(game):
    print("SETUP DONE!")
    global LOGIC_RUNNING
    while game.control_window.running:
        game.control_window.root.update()
        game.control_window.logic = LOGIC_RUNNING
        if not rnd.find_game_win():
            break
        else:
            if LOGIC_RUNNING and not game.control_window.only_autoclicker:
                game_functions(game)
            elif game.control_window.only_autoclicker:
                util.auto_click()
                time.sleep(1/20)
                if DEBUG:
                    img = rnd.get_screenshot()
                    rnd.render(img)

    fh.save_data(game)
    if game.control_window.running:
        game.control_window.stop()


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
