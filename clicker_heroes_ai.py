import cv2
import pyautogui
import time
from pynput.mouse import Controller, Button
from PIL import ImageGrab
import win32gui
import numpy as np
import tkinter as tk
import json

import customtkinter  # noqa

# Normal skill unlocks
SKILL_UNLOCKS = {"Normal": [10, 25, 50, 75, 100, 125, 150]}
# Hero upgrade guide logic for the program to follow
LEVEL_GUIDE = [1, 5, 10, 15, 25, 50, 75, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185, 195, 205, 215, 225]

IMG_PATH = 'images/'
SAVE_PATH = 'saves/'
WINDOW_WIDTH = 1050
WINDOW_HEIGHT = 600
CONFIDENCE_THRESHOLD = 0.7
UPGRADE_X_COORDINATE = 149
SKILL_X_COORDINATE = 197
SKILL_OFFSET = 32
AUTOCLICKER_POINT = (775, 365)


class ControlWindow(object):
    """
    Control panel for the program
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CONTROLS")
        self.root.geometry("100x200")
        self.root.configure(bg='grey')
        self.logic_running = False
        self.program_running = True
        self.start_stop_button = tk.Button(self.root, text="Start/Stop", command=lambda: self.start_stop(),
                                           height=2, width=15)
        self.re_center_button = tk.Button(self.root, text="Re-center cursor",
                                          command=lambda: pyautogui.moveTo(AUTOCLICKER_POINT), height=2, width=15)
        self.stop_button = tk.Button(self.root, text="QUIT", command=lambda: self.stop(),
                                     height=2, width=15, fg="red")
        self.start_stop_button.place(x=3, y=40)
        self.re_center_button.place(x=3, y=80)
        self.stop_button.place(x=3, y=120)

    def start_stop(self):
        if not self.logic_running:
            self.logic_running = True
            pyautogui.moveTo(AUTOCLICKER_POINT)
            return
        self.logic_running = False

    def stop(self):
        self.program_running = False
        self.root.destroy()

    def mainloop(self):
        self.root.mainloop()

    def change_position(self, x, y):
        self.root.geometry('+{}+{}'.format(x, y))


class Hero(object):
    """
    Class for Heroes and their attributes
    """

    def __init__(self, name, level, level_ceiling, skill_level, max_skill_level, gilded):
        self.name = name
        self.level = level
        self.skill_level = skill_level  # Current skill level
        self.max_skill_level = max_skill_level  # Max skill level for the hero
        self.level_ceiling = level_ceiling  # Target level for upgrading the hero
        self.gilded = gilded

    def level_up(self):
        self.level += 1
        if self.level in LEVEL_GUIDE:
            self.raise_level_ceiling()

    def level_skill(self):
        self.skill_level += 1
        print(self.name, "Skill", self.skill_level, "Purchased")

    def reset(self):
        self.level = 0
        self.skill_level = 0
        self.level_ceiling = 1

    def skill_unlocked(self):
        if self.skill_level < self.max_skill_level:
            if self.name in SKILL_UNLOCKS["Unique"]:
                level_req = SKILL_UNLOCKS[self.name][self.skill_level]
                return self.level >= level_req
            else:
                level_req = SKILL_UNLOCKS[self.skill_level]
                return self.level >= level_req

    def raise_level_ceiling(self):
        print(self.name, "lvl", self.level)
        if self.level_ceiling < max(LEVEL_GUIDE):
            idx = LEVEL_GUIDE.index(self.level_ceiling) + 1
            self.level_ceiling = LEVEL_GUIDE[idx]
        else:
            self.level_ceiling += 25


class Power(object):

    def __init__(self, name, cooldown, key, state):
        self.name = name
        self.unlocked = state
        self.cooldown = cooldown
        self.cd_timer = 0
        self.key = key

    def unlock(self):
        self.unlocked = True
        print(self.name, "Unlocked")

    def activate(self):
        pyautogui.press(self.key)
        self.cd_timer = time.time()

    def reset(self):
        self.unlocked = False
        self.cd_timer = 0


class GameState:
    """
    Class for game's attributes and stats
    """

    def __init__(self, level, ascension, transcend, h_idx):
        self.level = level
        self.ascensions = ascension
        self.transcends = transcend
        self.last_power = ""
        self.grind_mode = False
        self.boss_timer = None
        self.grind_timer = None
        self.hero_name = ""
        self.hero_index = h_idx

        self.y = 0
        self.scroll_bot = False
        self.scroll_top = True
        self.hero_on_screen = False

        self.boss = False
        self.first_levels = True

    def change_lvl(self):
        if not self.grind_mode:
            pyautogui.moveTo(813, 85)
            pyautogui.click()
            pyautogui.moveTo(AUTOCLICKER_POINT)
            self.level += 1
        else:
            pyautogui.moveTo(728, 82)
            pyautogui.click()
            pyautogui.moveTo(AUTOCLICKER_POINT)
            self.level -= 1
        self.boss_timer = None
        self.boss = False
        print("Game level: {}".format(self.level))

    def boss_fight(self):
        self.boss = True
        self.boss_timer = time.time()
        print("BOSS TIME!")

    def grind_start(self):
        self.grind_mode = True
        self.grind_timer = time.time()
        self.change_lvl()
        print("GRINDING TIME!")

    def grind_end(self):
        self.grind_mode = False
        self.grind_timer = None
        self.change_lvl()
        print("GRINDING ENDED!")

    def next_hero(self):
        self.hero_index += 1

    def ascend(self):
        self.level = 1
        self.ascensions += 1
        self.grind_mode = False
        self.boss_timer = None
        self.grind_timer = None
        self.scroll_bot = False
        self.scroll_top = True
        self.hero_on_screen = False
        self.boss = False
        self.first_levels = True
        pyautogui.moveTo(1000, 245)
        pyautogui.click()
        time.sleep(0.1)
        pyautogui.moveTo(460, 450)
        pyautogui.click()
        time.sleep(0.2)


def get_screenshot():
    hwnd = win32gui.FindWindow(None, 'Clicker Heroes')
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    bbox = [left, top, right, bot]
    img = np.array(ImageGrab.grab(bbox))  # noqa
    screenshot = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return screenshot


def get_pixel_val(img):
    x, y = pyautogui.position()
    return img[y, x, :]


def render(img):
    """
    renders game capture
    :param img: img to render
    """
    if img:
        small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
        cv2.imshow("Render", small)
        hwnd = win32gui.FindWindow(None, 'Render')
        win32gui.MoveWindow(hwnd, WINDOW_WIDTH, 0, round((WINDOW_WIDTH + 35) / 2), round((WINDOW_HEIGHT + 80) / 2),
                            True)
        cv2.waitKey(1)
    # else:
    # img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)


def chest_detection(img, heroes, game_win):
    img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name = IMG_PATH + 'Chest.png'
    needle_img = cv2.imread(image_name, 0)
    results_img = cv2.matchTemplate(img_g, needle_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
    x, y = max_loc
    if max_val > CONFIDENCE_THRESHOLD:
        click_x = round((needle_img.shape[1] / 2)) + x
        click_y = round((needle_img.shape[0] / 2)) + y
        pyautogui.click(click_x, click_y)
        time.sleep(3)
        img = game_win.update_screen()
        img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        image_name = IMG_PATH + 'Relic_Ooze.png'
        needle_img = cv2.imread(image_name, 0)
        results_img = cv2.matchTemplate(img_g, needle_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
        if max_val > CONFIDENCE_THRESHOLD:
            pyautogui.click(832, 120)
            time.sleep(0.5)
            pyautogui.moveTo(AUTOCLICKER_POINT)
        else:
            img_n = cv2.bitwise_not(img_g)
            img_n = img_n[125:500, 222:834]
            for hero in heroes:
                img_name = IMG_PATH + 'heroes/gilded/' + hero.name + '.png'
                needle_img = cv2.imread(img_name, 0)
                needle_img = cv2.bitwise_not(needle_img)
                results_img = cv2.matchTemplate(img_n, needle_img, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
                if max_val > 0.5:
                    hero.gilded = True
                    print(hero.name, 'Gilded!')
                    pyautogui.click(832, 120)
                    time.sleep(1)
                    pyautogui.moveTo(AUTOCLICKER_POINT)
                    break
            pyautogui.click(832, 120)
            time.sleep(0.5)
            pyautogui.moveTo(AUTOCLICKER_POINT)


def draw_detection(game, hero):
    img = get_screenshot()
    if game.hero_name:
        image_name = IMG_PATH + 'heroes/regular/' + game.hero_name + '.png'
        needle_img = cv2.imread(image_name, 0)
        if not hero.gilded:
            needle_img = cv2.bitwise_not(needle_img)
        img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_n = cv2.bitwise_not(img_g)
        results_img = cv2.matchTemplate(img_n, needle_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
        x, y = max_loc
        if (max_val > CONFIDENCE_THRESHOLD) & ((y + 75) < 600):
            width = needle_img.shape[1]
            height = needle_img.shape[0]
            starting_point = (int(x), int(y))
            ending_point = (int(x + width), int(y + height))
            cv2.rectangle(img, starting_point, ending_point, color=(255, 0, 0), thickness=2)
            game.hero_on_screen = True
        else:
            game.hero_on_screen = False
        render(img)


def upgrade_first_levels(img, hero, game):  # Upgrades first 2 levels when template matching doesn't work
    if game.level < 5:
        if (hero.level == 3) & hero.target_level == (LEVEL_GUIDE[0]):
            game.first_levels = False
            hero.upgrade_target_lvl()
        elif (game.hero_name == 'Cid, the Helpful Adventurer') & (hero.level < 3):
            if img[235, UPGRADE_X_COORDINATE, 2] == 255:
                pyautogui.moveTo(UPGRADE_X_COORDINATE, 235)
                pyautogui.click()
                pyautogui.moveTo(AUTOCLICKER_POINT)
                hero.level_up()
    else:
        game.first_levels = False


def upgrade_hero(img, hero, game):
    if hero.skill_unlocked():
        y = game.y + 45  # 45px is offset from the top of the hero name to the upgrade button
        if (img[y, 197 + (SKILL_OFFSET * hero.skill_level), 0] > 50) \
                | (img[y, 197 + (SKILL_OFFSET * hero.skill_level), 1] > 50) \
                | (img[y, 197 + (SKILL_OFFSET * hero.skill_level), 2] > 50):
            pyautogui.moveTo(SKILL_X_COORDINATE + (SKILL_OFFSET * hero.skill_level), game.hero_y)
            pyautogui.click()
            pyautogui.moveTo(AUTOCLICKER_POINT)
            hero.level_skill()
    elif img[game.hero_y, UPGRADE_X_COORDINATE, 2] > 200:
        pyautogui.moveTo(UPGRADE_X_COORDINATE, game.hero_y)
        pyautogui.click()
        pyautogui.moveTo(AUTOCLICKER_POINT)
        hero.level_up()


def hero_upgrade_logic(img, game, hero, num_heroes):
    if hero.level > 0:
        if hero.level > hero.target_level:
            hero.upgrade_target_lvl()

        elif (hero.level == LEVEL_GUIDE[0]) & (hero.target_level == LEVEL_GUIDE[0]):
            # If current hero is the lowest level hero reset cycle
            hero.upgrade_target_lvl()
            game.reset_hero()

        elif (game.hero_name == 'Cid, the Helpful Adventurer') & (hero.level > 100):  # If Cid is lvl 100 skip Cid
            game.next_hero()
        # If current hero is the last hero reset cycle

        elif (hero.level == hero.target_level) & (game.hero_idx == num_heroes):
            hero.upgrade_target_lvl()
            game.reset_hero()

        elif hero.level == hero.target_level:
            if hero.skill_unlocked():
                upgrade_hero(img, hero, game)
            else:
                if game.hero_idx > 24:
                    if hero.level < 425:
                        hero.upgrade_target_lvl()
                        game.reset_hero()
                    else:
                        hero.upgrade_target_lvl()
                        game.next_hero()
                else:
                    if (game.hero_idx == 21) & (hero.level > 149):
                        print("Ascension Available!")
                        game.asc_available = True
                    hero.upgrade_target_lvl()
                    game.next_hero()
        elif hero.level < hero.target_level:
            upgrade_hero(img, hero, game)
    else:
        upgrade_hero(img, hero, game)


def power_unlocker(game, hero, powers):
    if game.unlocked_powers >= (len(powers) - 1):
        return
    if hero.name in POWER_UNLOCK:
        if (hero.level == POWER_UNLOCK[hero.name][0]) & (hero.skill_level == POWER_UNLOCK[hero.name][1]):
            power = powers[POWER_UNLOCK[hero.name][2]]
            if not power.unlocked:
                power.unlock()
                game.unlock_power()


def power_usage(game, powers):
    if game.unlocked_powers > 0:
        if not game.grind_mode:
            for power in powers:
                if power.unlocked:
                    if (time.time() - power.cd_timer) > power.cooldown:
                        power.activate()


def level_checker(game, img):
    if game.level % 5 == 0:
        if not game.boss_timer:
            game.boss_fight()
        elif (img[85, 813, :] == np.array([72, 122, 198])).all():
            print("BOSS DEFEATED IN {:.2f}s".format(time.time() - game.boss_timer))
            game.change_lvl()
        elif (time.time() - game.boss_timer) > 30:
            game.grind_start()
    elif not game.grind_mode:
        if (img[85, 813, :] == np.array([72, 122, 198])).all():  # [72, 122, 198]
            game.change_lvl()
    elif game.grind_timer:
        if (time.time() - game.grind_timer) > 180:
            game.grind_end()


def click(mouse, button):
    if cursor_center:
        mouse.click(button)
        mouse.click(button)
        mouse.click(button)


def scroll_down(game, game_win, heroes):
    if (game.hero_name == 'Cid, the Helpful Adventurer') & game.scroll_top:
        hero = heroes[0]
        if hero.level > 100:
            game.next_hero()
        else:
            time.sleep(1)
    else:
        game.scroll_top = False
        while not game.hero_on_screen:
            pyautogui.scroll(-150)
            img = game_win.update_screen()
            draw_detection(img, game, heroes, game_win)
            time.sleep(1 / 20)
            if img[565, 501, 2] == 255:
                game.scroll_bot = True
                break


def scroll_up(img, game, game_win, heroes):
    while not img[210, 513, 2] == 255:
        pyautogui.scroll(1500)
        img = game_win.update_screen()
        draw_detection(img, game, heroes, game_win)
    game.scroll_bot = False
    game.scroll_top = True
    game.reset_hero()
    time.sleep(1 / 2)


def cursor_center():
    x, y = pyautogui.position()
    if (x == AUTOCLICKER_POINT[0]) & (y == AUTOCLICKER_POINT[1]):
        return True
    return False


def present_detection(img, game):
    if game.level > 100:
        if (img[517, 999, :] == np.array([245, 128, 128])).all():  # BGR
            pyautogui.moveTo(953, 506)
            pyautogui.click()
            pyautogui.moveTo(AUTOCLICKER_POINT)
            time.sleep(0.5)


def bee_detection(img, game, game_win, mouse, button):
    if game.level > 50:
        img = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        image_name = IMG_PATH + 'bee2.png'
        needle_img = cv2.imread(image_name, 0)
        needle_img = cv2.bitwise_not(needle_img)
        img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        img_n = cv2.bitwise_not(img_g)
        img_n = img_n[100:150, 590:960]
        results_img = cv2.matchTemplate(img_n, needle_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
        x, y = max_loc
        if max_val > 0.6:
            width = needle_img.shape[1]
            height = needle_img.shape[0]
            starting_point = (int(x), int(y))
            ending_point = (int(x + width), int(y + height))
            cv2.rectangle(img, starting_point, ending_point, color=(0, 0, 255), thickness=2)
        if max_val > CONFIDENCE_THRESHOLD:
            print("BEE FOUND!!!")
            height = needle_img.shape[0]
            for _ in range(1, 20):
                pyautogui.moveTo(x, (y + round(height / 2)))
                mouse.click(button)
                mouse.click(button)
                mouse.click(button)
            pyautogui.moveTo(AUTOCLICKER_POINT)
        game_win.render(True, img)


def ascend_logic(game, heroes, powers):
    if game.asc_available:
        if (game.level > 1000) & (game.ascensions < 1):
            print("ASCEND AT", game.level)
            print()
            print()
            game.ascend()
            for hero in heroes:
                hero.reset()
            for power in powers:
                power.reset()
            pyautogui.moveTo(AUTOCLICKER_POINT)


def game_loop(game_win, heroes, game, powers):
    mouse = Controller()
    button = Button.left
    pyautogui.moveTo(AUTOCLICKER_POINT)
    controls_win = ControlWindow()
    controls_win.change_position(WINDOW_WIDTH, round(WINDOW_HEIGHT - 260))
    while controls_win.program_running:
        controls_win.root.update()
        img = update_screen()
        if controls_win.logic_running & cursor_center():
            hero = heroes[game.hero_idx]
            game.hero_name = hero.name
            img = game_win.update_screen()
            chest_detection(img, heroes, game_win)
            bee_detection(img, game, game_win, mouse, button)
            # ascend_logic(game, heroes, powers)
            draw_detection(img, game, heroes, game_win)
            level_checker(game, img)
            upgrade_first_levels(img, hero, game)
            if not game.first_levels:
                if not game.boss:
                    if game.hero_on_screen:
                        hero_upgrade_logic(img, game, hero, (len(heroes) - 1))
                    else:
                        if not game.scroll_bot:
                            scroll_down(game, game_win, heroes)
                        else:
                            scroll_up(img, game, game_win, heroes)
            power_unlocker(game, hero, powers)
            power_usage(game, powers)
            click(mouse, button)
            present_detection(img, game)
        else:
            game.hero_name = None
            img = game_win.update_screen()
            draw_detection(img, game, heroes, game_win)
    save_data(game, heroes, powers)


def save_data(game, heroes, powers):
    pass


def load_from_file():
    """
    Loads the gamestate from save.json or creates one from setup.json
    :return:
    """
    save_file = False
    try:
        with open(SAVE_PATH + "save.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            heroes = data["Heroes"]
            SKILL_UNLOCKS["Unique"] = data["Unique skills"]
            powers = data["Powers"]
            game_data = data["Gamestate"]
            save_file = True
    except IOError:
        pass

    if not save_file:
        try:
            with open("setup.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                heroes = data["Heroes"]
                SKILL_UNLOCKS["Unique"] = data["Unique skills"]
                powers = data["Powers"]
                game_data = data["Gamestate"]
        except IOError:
            print("'setup.json' NOT FOUND!")
            return [], [], []

    return heroes, game_data, powers


def setup():
    hwnd = win32gui.FindWindow(None, 'Clicker Heroes')
    win32gui.SetForegroundWindow(hwnd)
    heroes, game_data, powers = load_from_file()
    if heroes:
        win32gui.MoveWindow(hwnd, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, True)
        print("SETUP DONE!")
        game_loop(heroes, game_data, powers)


def main():
    setup()
    cv2.destroyAllWindows()
    print("Program terminated")


if __name__ == '__main__':
    main()
