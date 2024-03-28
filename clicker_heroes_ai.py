import cv2
import core
import file_handler as fh
import utilities as util
from pynput import keyboard
import threading
from config import DEBUG
import time

LOGIC_RUNNING = False


def on_release(key):
    global LOGIC_RUNNING
    if key == keyboard.Key.ctrl_r and DEBUG:
        x, y = util.get_position()
        value = util.get_pixel_val()
        print(f"(x,y) = ({x},{y}) {value} RGB")
    elif key == keyboard.Key.space:
        LOGIC_RUNNING ^= True
        print("Logic:", LOGIC_RUNNING)


def game_functions(game):
    game.detections()
    game.level_checks()
    core.power_use_logic(game)
    util.auto_click()
    if game.hero.found():
        core.hero_leveling_logic(game)
    else:
        util.scroll_down(game)


def game_loop(game):
    util.game_auto_clicker()
    global LOGIC_RUNNING
    print("SETUP DONE!")
    while game.control_window.running:
        game.control_window.root.update()
        game.control_window.logic = LOGIC_RUNNING
        if not util.rnd.find_game_win():
            break
        else:
            if LOGIC_RUNNING and not game.control_window.only_autoclicker:
                game_functions(game)
            elif game.control_window.only_autoclicker:
                util.auto_click()
                time.sleep(1/2000)
                if DEBUG:
                    util.rnd.render()
    fh.save_data(game)


def setup():
    heroes, game_data, powers = fh.load_from_file()
    game: util.GameData = util.create_game_data(heroes, game_data, powers)
    hwnd = util.rnd.find_game_win()
    if heroes and hwnd:
        util.rnd.move_game_win(hwnd)
        time.sleep(1)
        game.create_control_win()
        game_thread = threading.Thread(target=game_loop, args=(game, ), daemon=True)
        listener = keyboard.Listener(on_release=on_release)
        listener.start()
        game_thread.start()
        game.control_window.run()
        listener.stop()
        game_thread.join()


def main():
    setup()
    cv2.destroyAllWindows()
    print("Program terminated")


if __name__ == '__main__':
    main()
