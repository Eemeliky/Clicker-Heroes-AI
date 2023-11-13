import pyautogui
import config
import tkinter as tk
import numpy as np
from time import time, sleep
from pynput.mouse import Controller, Button


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
                                          command=lambda: pyautogui.moveTo(config.AC_POINT),
                                          height=2, width=15)
        self.stop_button = tk.Button(self.root, text="QUIT", command=lambda: self.stop(),
                                     height=2, width=15, fg="red")
        self.start_stop_button.place(x=3, y=40)
        self.re_center_button.place(x=3, y=80)
        self.stop_button.place(x=3, y=120)

    def start_stop(self):
        if not self.logic_running:
            self.logic_running = True
            pyautogui.moveTo(config.AC_POINT)
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

    def __init__(self, name, level, level_ceiling, skill_level, max_skill_level, gilded, unique_ups):
        self.name = name
        self.level = level
        self.skill_level = skill_level  # Current skill level
        self.max_skill_level = max_skill_level  # Max skill level for the hero
        self.level_ceiling = level_ceiling  # Target level for upgrading the hero
        self.gilded = gilded
        self.unique_ups = unique_ups

    def level_up(self):
        self.level += 1
        if self.level in config.LEVEL_GUIDE:
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
            if self.name in config.SKILL_UNLOCKS["Unique"]:
                level_req = config.SKILL_UNLOCKS[self.name][self.skill_level]
                return self.level >= level_req
            else:
                level_req = config.SKILL_UNLOCKS[self.skill_level]
                return self.level >= level_req

    def raise_level_ceiling(self):
        print(self.name, "lvl", self.level)
        if self.level_ceiling < max(config.LEVEL_GUIDE):
            idx = config.LEVEL_GUIDE.index(self.level_ceiling) + 1
            self.level_ceiling = config.LEVEL_GUIDE[idx]
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
        self.cd_timer = time()

    def reset(self):
        self.unlocked = False
        self.cd_timer = 0


class GameData:
    """
    Class for game's attributes and stats
    """

    def __init__(self, level, ascension, transcend, heroes, h_idx, powers):
        self.heroes = heroes
        self.powers = powers
        self.level = level
        self.ascensions = ascension
        self.transcends = transcend
        self.last_power = ""
        self.grind_mode = False
        self.boss_timer = None
        self.grind_timer = None
        self.hero_index = h_idx
        self.hero = self.heroes[self.hero_index]
        self.img = np.array([])

        self.hero_name_xy = (0, 0)
        self.scroll_bot = False
        self.scroll_top = True
        self.hero_on_screen = False

        self.boss = False
        self.first_levels = True

    def change_lvl(self):
        if not self.grind_mode:
            click_on_point(813, 85)
            self.level += 1
        else:
            click_on_point(728, 82)
            self.level -= 1
        self.boss_timer = None
        self.boss = False
        print("Game level: {}".format(self.level))

    def boss_fight(self):
        self.boss = True
        self.boss_timer = time()
        print("BOSS TIME!")

    def grind_start(self):
        self.grind_mode = True
        self.grind_timer = time()
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
        click_on_point(1000, 245, False)
        sleep(0.1)
        click_on_point(460, 450, False)
        sleep(0.2)


def cursor_center():
    x, y = pyautogui.position()
    if (x == config.AC_POINT[0]) & (y == config.AC_POINT[1]):
        return True
    return False


def click_on_point(x, y, _return=True):
    pyautogui.moveTo(x, y)
    pyautogui.click()
    if _return:
        pyautogui.moveTo(config.AC_POINT)


def get_pixel_val(img):
    x, y = pyautogui.position()
    return img[y, x, :]


def class_dump(h_data, g_data, p_data):
    h_temp = []
    for name in h_data:
        new_hero = Hero(name,
                        h_data[name]["Level"],
                        h_data[name]["Level ceiling"],
                        h_data[name]["Skill level"],
                        h_data[name]["Max skill level"],
                        h_data[name]["Gilded"],
                        h_data[name]["Unique skills"]
                        )

        h_temp.append(new_hero)


def level_checker(game):
    if game.level % 5 == 0:
        if not game.boss_timer:
            game.boss_fight()
        elif (game.img[85, 813, :] == np.array([72, 122, 198])).all():
            print("BOSS DEFEATED IN {:.2f}s".format(time() - game.boss_timer))
            game.change_lvl()
        elif (time() - game.boss_timer) > 30:
            game.grind_start()
    elif not game.grind_mode:
        if (game.img[85, 813, :] == np.array([72, 122, 198])).all():  # [72, 122, 198]
            game.change_lvl()
    elif game.grind_timer:
        if (time() - game.grind_timer) > 180:
            game.grind_end()


def auto_click():
    mouse = Controller()
    if cursor_center:
        mouse.click(Button.left)
        mouse.click(Button.left)
        mouse.click(Button.left)
