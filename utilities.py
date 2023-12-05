import pyautogui
import config
import tkinter as tk
from time import time, sleep
import pynput
import numpy as np
import renderer as rnd
from detectors import present_detection, find_gilded


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
        self.only_autoclicker = False
        self.start_stop_button = tk.Button(self.root, text="Start/Stop", command=lambda: self.start_stop(),
                                           height=2, width=15)
        self.re_center_button = tk.Button(self.root, text="Re-center cursor",
                                          command=lambda: pyautogui.moveTo(config.AC_POINT),
                                          height=2, width=15)
        self.stop_button = tk.Button(self.root, text="QUIT", command=lambda: self.stop(),
                                     height=2, width=15, fg="red")
        self.autoclicker_button = tk.Button(self.root, text="Only autoclicker", command=lambda: self.autoclicker(),
                                            height=2, width=15)
        self.start_stop_button.place(x=3, y=10)
        self.re_center_button.place(x=3, y=50)
        self.autoclicker_button.place(x=3, y=90)
        self.stop_button.place(x=3, y=150)
        self.change_position()

    @staticmethod
    def start_stop():
        pyautogui.press("space")
        pyautogui.moveTo(config.AC_POINT)

    def autoclicker(self):
        self.only_autoclicker ^= True
        if self.only_autoclicker:
            pyautogui.moveTo(config.AC_POINT)
        print("Only Autoclicker:", self.only_autoclicker)

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
        self.name_pos = (-1, -1)

    def level_up(self):
        x, y = self.name_pos
        click_on_point(config.LEVEL_UP_X, y + 45)
        self.level += 1
        if self.level == self.level_ceiling:
            if self.unique_ups:
                if self.level_ceiling not in config.SKILL_UNLOCKS["Unique"][self.name]:
                    self.raise_level_ceiling()
            else:
                if self.level_ceiling not in config.SKILL_UNLOCKS["Normal"]:
                    self.raise_level_ceiling()

    def level_skill(self):
        if self.level == self.level_ceiling:
            self.raise_level_ceiling()
        x, y = self.name_pos
        click_on_point(config.SKILL_X_COORDINATE + (config.SKILL_OFFSET * self.skill_level), y + 45)
        self.skill_level += 1
        print(f"{self.name} Skill level: {self.skill_level}/{self.max_skill_level}")

    def reset(self):
        self.level = 0
        self.skill_level = 0
        self.level_ceiling = config.LEVEL_GUIDE[0]
        self.name_pos = (-1, -1)

    def skill_unlocked(self):
        if self.skill_level < self.max_skill_level:
            if self.unique_ups:
                level_req = config.SKILL_UNLOCKS["Unique"][self.name][self.skill_level]
            else:
                level_req = config.SKILL_UNLOCKS["Normal"][self.skill_level]
            return self.level >= level_req
        return False

    def raise_level_ceiling(self):
        if self.level_ceiling < max(config.LEVEL_GUIDE):
            if self.level_ceiling not in config.LEVEL_GUIDE:
                self.level_ceiling = config.LEVEL_GUIDE[0]
            else:
                idx = config.LEVEL_GUIDE.index(self.level_ceiling) + 1
                self.level_ceiling = config.LEVEL_GUIDE[idx]
        else:
            self.level_ceiling += config.LEVEL_OVER_STEP

    def gild(self):
        self.gilded = True


class Power(object):
    """
    Class for Powers and their attribute
    """

    def __init__(self, name, cooldown, key, state, hero, skill):
        self.name = name
        self.unlocked = state
        self.cooldown = cooldown
        self.cd_timer = 0
        self.key = key
        self.hero = hero
        self.skill = skill

    def unlock(self):
        self.unlocked = True
        print(self.name, "Unlocked")
        if self.name == "The Dark Ritual":
            self.activate()

    def activate(self):
        pyautogui.press(self.key)
        self.cd_timer = time()
        print(self.name, "Active")

    def reset(self):
        self.unlocked = False
        self.cd_timer = 0

    def on_cooldown(self):
        if (time() - self.cd_timer) > self.cooldown:
            return False

        return True


class GameData:
    """
    Class for game variables
    """

    def __init__(self, level, heroes, h_idx, powers, powers_num, ascension, transcend):
        self.heroes = heroes
        self.hero_index = h_idx
        self.hero = self.heroes[self.hero_index]
        self.powers = powers
        self.unlocked_powers = powers_num
        self.level = level
        self.control_window = None
        self.ascensions = ascension
        self.transcends = transcend
        self.boss_timer = 0
        self.grind_timer = 0
        self.level_up_timer = 0

    def create_control_win(self):
        self.control_window = ControlWindow()

    def reset_hero_queue(self):
        self.hero_index = 0
        self.hero = self.heroes[self.hero_index]
        self.update_hero_timer()

    def next_hero(self):
        if self.hero_index == 0 and self.hero.level > 100:
            print("Skipping Cid")
        else:
            print(self.hero.name, "lvl", self.hero.level)
        self.hero_index += 1
        if self.hero_index == len(self.heroes):
            self.hero_index = 0
        self.hero = self.heroes[self.hero_index]
        self.update_hero_timer()

    def update_hero_timer(self):
        self.level_up_timer = time()

    def get_hero_timer(self):
        return time() - self.level_up_timer

    def check_level(self):
        if self.level % 5 == 0:
            img = rnd.get_screenshot()
            if not self.boss_timer:
                self.boss_timer = time()
            elif (img[85, 813, :] == np.array(config.NEW_GAME_LEVEL)).all():
                print("BOSS DEFEATED IN {:.2f}s".format(time() - self.boss_timer))
                self.boss_timer = 0
                self.move_up_level()
            elif (time() - self.boss_timer) > 30:
                self.level -= 1
                self.boss_timer = 0
                self.grind_timer = time()
                click_on_point(728, 82)
                self.update_hero_timer()
                print(f"GRINDING TIME! ({config.GRIND_TIME}s)")
        elif self.grind_timer:
            amenhotep = self.heroes[18]
            if (time() - self.grind_timer) > config.GRIND_TIME:
                self.grind_timer = 0
                self.move_up_level()
                print("GRIND ENDED!")
            elif self.level > (130 + 100 * self.ascensions) and amenhotep.level > 150:
                print("ASCENSION", self.level)
                print()
                print()
                self.ascend()
        else:
            img = rnd.get_screenshot()
            if (img[85, 813, :] == np.array(config.NEW_GAME_LEVEL)).all():
                self.move_up_level()

    def move_up_level(self):
        self.level += 1
        click_on_point(813, 85)
        if self.level % 5 == 0:
            print("Game level: {} (BOSS)".format(self.level))
        else:
            print("Game level: {}".format(self.level))

    def detections(self):
        if present_detection(self):
            click_on_point(953, 506)
            sleep(1/2)
            chest_handler(self)

    def ascend(self):
        for hero in self.heroes:
            hero.reset()
        for power in self.powers:
            power.reset()
        self.reset_hero_queue()
        self.level = 1
        self.ascensions += 1
        self.boss_timer = 0
        self.grind_timer = 0
        self.unlocked_powers = 0
        click_on_point(1000, 245, center=False)
        sleep(1/5)
        img = rnd.get_screenshot()
        if (img[384, 485, :] == np.array([68, 215, 35])).all():
            click_on_point(485, 384, center=False)
            sleep(1/5)
        click_on_point(460, 450)
        sleep(1/5)


def chest_handler(game):
    """
    Clicks on the chest that appears on the screen after opening present and calls for hero gilding.
    :param game: GameData class object
    """
    click_on_point(523, 324, False)
    sleep(2)
    hero_idx = find_gilded(game)
    if not hero_idx:
        print("ERROR, no suitable hero found!")
    else:
        hero = game.heroes[hero_idx]
        if not hero.gilded:
            hero.gild()
    click_on_point(832, 120)
    sleep(1/2)


def click_on_point(x, y, center=True):
    """
    :param x: x-coordinate on screen
    :param y: y-coordinate on screen
    :param center: flag for returning to autoclicker point
    """
    pyautogui.moveTo(x, y)
    pyautogui.click()
    if center:
        pyautogui.moveTo(config.AC_POINT)


def get_pixel_val(x=0, y=0):
    """
    :param x: x-coordinate on screen
    :param y: y-coordinate on screen
    :return: Pixel value of given point or the point that the cursor points to
    """
    img = rnd.get_screenshot()
    if x == 0 and y == 0:
        x, y = pyautogui.position()
    return img[y, x, :]


def get_position():
    x, y = pyautogui.position()
    return x, y


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
    powers_num = 0
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
                          p_data[name]["Unlock skill"],
                          )
        if new_power.unlocked:
            powers_num += 1
        p_tmp.append(new_power)

    game = GameData(g_data["Level"],
                    h_tmp,
                    h_idx,
                    p_tmp,
                    powers_num,
                    g_data["Ascension level"],
                    g_data["Transcend level"],
                    )
    config.set_level_guide(asc=game.ascensions)
    return game


def scroll_down(game):
    """
    Scrolls down on the heroes list in the game window
    :param game: GameData class object
    """
    if not game.boss_timer:
        img = rnd.get_screenshot()
        if img[565, 501, 2] == 255:
            game.reset_hero_queue()
            reset_scroll()
        else:
            scroll_amount = round(-150 - 100/game.level)
            pyautogui.scroll(scroll_amount)
            sleep(1/5)


def reset_scroll():
    """
    Returns to the top of the heroes list in the game window
    """
    img = rnd.get_screenshot()
    while not img[210, 513, 2] > 250:
        pyautogui.scroll(2500)
        img = rnd.get_screenshot()
    sleep(1/2)


def auto_click():
    """
    *3x ClICKS* on the autoclicker point
    """
    mouse = pynput.mouse.Controller()
    x, y = pyautogui.position()
    if (config.AC_POINT[0] - 5 < x < config.AC_POINT[0] + 5) & (config.AC_POINT[1] - 5 < y < config.AC_POINT[1] + 5):
        mouse.click(pynput.mouse.Button.left)
        mouse.click(pynput.mouse.Button.left)
        mouse.click(pynput.mouse.Button.left)
