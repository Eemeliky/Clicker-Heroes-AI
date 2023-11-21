import pyautogui
import config
import tkinter as tk
from time import time, sleep
import pynput
import numpy as np
import renderer as rnd


class ControlWindow(object):
    """
    Control panel for the program
    """

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("CONTROLS")
        self.root.geometry("100x200")
        self.root.configure(bg='grey')
        self.logic = False
        self.running = True
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
        self.change_position()

    def start_stop(self):
        if not self.logic:
            self.logic = True
            pyautogui.moveTo(config.AC_POINT)
            return
        self.logic = False

    def stop(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()

    def change_position(self):
        self.root.geometry('+{}+{}'.format(config.WINDOW_WIDTH, round(config.WINDOW_HEIGHT - 260)))


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
        self.level_up_button = (-1, -1)

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
                level_req = config.SKILL_UNLOCKS["Unique"][self.name][self.skill_level]
                return self.level >= level_req
            else:
                level_req = config.SKILL_UNLOCKS["Normal"][self.skill_level]
                return self.level >= level_req

    def raise_level_ceiling(self):
        print(self.name, "lvl", self.level)
        if self.level_ceiling < max(config.LEVEL_GUIDE):
            if self.level_ceiling not in config.LEVEL_GUIDE:
                self.level_ceiling = config.LEVEL_GUIDE[0]
            else:
                idx = config.LEVEL_GUIDE.index(self.level_ceiling) + 1
                self.level_ceiling = config.LEVEL_GUIDE[idx]
        else:
            self.level_ceiling += config.LEVEL_OVER_STEP


class Power(object):
    """
    Class for Powers and their attribute
    """

    def __init__(self, name, cooldown, key, state, hero, level, skill):
        self.name = name
        self.unlocked = state
        self.cooldown = cooldown
        self.cd_timer = cooldown + 1
        self.key = key
        self.hero = hero
        self.level = level
        self.skill = skill

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
    Class for game variables
    """

    def __init__(self, level, heroes, h_idx, powers, ascension, transcend):
        self.heroes = heroes
        self.hero_index = h_idx
        self.hero = self.heroes[self.hero_index]
        self.powers = powers
        self.level = level
        self.control_window = None
        self.ascensions = ascension
        self.transcends = transcend
        self.last_power = ""
        self.boss_timer = 0
        self.grind_timer = 0

    def create_control_win(self):
        self.control_window = ControlWindow()

    def reset_hero_queue(self):
        self.hero_index = 0
        self.hero = self.heroes[self.hero_index]

    def next_hero(self):
        self.hero_index += 1
        if self.hero_index == len(self.heroes):
            self.hero_index = 0
        self.hero = self.heroes[self.hero_index]

    def change_level(self):
        img = rnd.get_screenshot()
        if self.level % 5 == 0:
            if not self.boss_timer:
                self.boss_timer = time()
            elif (img[85, 813, :] == np.array(config.NEW_GAME_LEVEL)).all():
                print("BOSS DEFEATED IN {:.2f}s".format(time() - self.boss_timer))
                self.move_up_level()
            elif (time() - self.boss_timer) > 30:
                self.level -= 1
                self.boss_timer = 0
                self.grind_timer = time()
                click_on_point(728, 82)
                print(f"GRINDING TIME! ({config.GRIND_TIME}s)")
        elif self.grind_timer:
            if (time() - self.grind_timer) > config.GRIND_TIME:
                self.grind_timer = 0
                self.move_up_level()
                print("GRIND ENDED!")
        else:
            if (img[85, 813, :] == np.array(config.NEW_GAME_LEVEL)).all():
                self.move_up_level()

    def move_up_level(self):
        self.level += 1
        click_on_point(813, 85)
        print("Game level: {}".format(self.level))

    def ascend(self):  # Add heroes reset!
        self.level = 1
        self.ascensions += 1
        self.boss_timer = 0
        self.grind_timer = 0
        click_on_point(1000, 245, False)
        sleep(1/5)
        click_on_point(460, 450, False)
        sleep(1/5)


def cursor_ready():
    """
    Checks if the cursor on the correct position for autoclicker
    :return:
    """
    x, y = pyautogui.position()
    if (x == config.AC_POINT[0]) & (y == config.AC_POINT[1]):
        return True
    return False


def click_on_point(x, y, _return=True):
    """
    :param x: x-coordinate on screen
    :param y: y-coordinate on screen
    :param _return: flag for returning to autoclicker point
    """
    pyautogui.moveTo(x, y)
    pyautogui.click()
    if _return:
        pyautogui.moveTo(config.AC_POINT)


def get_pixel_val(img):
    """
    :param img: Image array
    :return: Pixel value that the cursor points to
    """
    x, y = pyautogui.position()
    return img[y, x, :]


def create_game_data(h_data, g_data, p_data):
    """
    :param h_data: Dict with heroes data
    :param g_data: Dict with game data
    :param p_data: Dict with powers data
    :return: GameData class object
    """
    h_tmp = []
    p_tmp = []
    h_idx = 0
    for name in h_data:
        new_hero = Hero(name,
                        h_data[name]["Level"],
                        h_data[name]["Level ceiling"],
                        h_data[name]["Skill level"],
                        h_data[name]["Max skill level"],
                        h_data[name]["Gilded"],
                        h_data[name]["Unique skills"]
                        )
        h_tmp.append(new_hero)
        if g_data["Current hero"] == new_hero.name:
            h_idx = len(h_tmp) - 1

    for name in p_data:
        new_power = Power(name,
                          p_data[name]["Cooldown"],
                          p_data[name]["Key"],
                          p_data[name]["Unlocked"],
                          p_data[name]["Unlock hero"],
                          p_data[name]["Unlock level"],
                          p_data[name]["Unlock skill"]
                          )
        p_tmp.append(new_power)

    game = GameData(g_data["Level"],
                    h_tmp,
                    h_idx,
                    p_tmp,
                    g_data["Ascension level"],
                    g_data["Transcend level"]
                    )
    return game


def scroll_down(game):
    """
    Scrolls down on the heroes list in the game window
    :param game: GameData class object
    """
    img = rnd.get_screenshot()
    if img[565, 501, 2] == 255:
        game.next_hero()
        reset_scroll()
    else:
        pyautogui.scroll(-150)


def reset_scroll():
    """
    Returns to the top of the heroes list in the game window
    """
    img = rnd.get_screenshot()
    while not img[210, 513, 2] == 255:
        pyautogui.scroll(1500)
        img = rnd.get_screenshot()


def auto_click():
    """
    *3x ClICKS* on the autoclicker point
    """
    mouse = pynput.mouse.Controller()
    if cursor_ready:
        mouse.click(pynput.mouse.Button.left)
        mouse.click(pynput.mouse.Button.left)
        mouse.click(pynput.mouse.Button.left)
