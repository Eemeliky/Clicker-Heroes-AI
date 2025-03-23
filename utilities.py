import pyautogui
from typing import List, Tuple, Dict, Any
import tkinter as tk
from time import time
import pynput
import numpy as np

from config import *
import detectors as dts
import renderer as rnd


class ControlWindow:
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
                                          command=lambda: pyautogui.moveTo(AC_POINT),
                                          height=2, width=15)
        self.stop_button = tk.Button(self.root, text="QUIT", command=lambda: self.stop(),
                                     height=2, width=15, fg="red")
        self.autoclicker_button = tk.Button(self.root, text="Only autoclicker", command=lambda: self.autoclicker(),
                                            height=2, width=15)
        self.start_stop_button.place(x=3, y=10)
        self.re_center_button.place(x=3, y=50)
        self.autoclicker_button.place(x=3, y=90)
        self.stop_button.place(x=3, y=150)
        self.root.geometry('+{}+{}'.format(WINDOW_WIDTH, round(WINDOW_HEIGHT - 260)))

    @staticmethod
    def start_stop():
        pyautogui.press("space")
        pyautogui.moveTo(AC_POINT)

    def autoclicker(self):
        self.only_autoclicker ^= True
        if self.only_autoclicker:
            pyautogui.moveTo(AC_POINT)
        print("Only Autoclicker:", self.only_autoclicker)

    def stop(self):
        self.running = False
        self.root.destroy()

    def run(self):
        self.root.mainloop()


class Hero:
    """
    Class for Heroes and their attributes
    """

    def __init__(self, name: str, level: int, level_ceiling: int, skill_level: int, max_skill_level: int,
                 gilded: bool, unique_ups: bool):
        self.name = name
        self.level = level
        self.skill_level = skill_level  # Current skill level
        self.max_skill_level = max_skill_level  # Max skill level for the hero
        self.level_ceiling = level_ceiling  # Target level for upgrading the hero
        self.gilded = gilded
        self.unique_ups = unique_ups
        self.name_pos = (-1, -1)
        self.lvl_off_sync = False

    def level_up(self, ctrl=False):
        x = LVL_BTN_CENTER[0]
        y = LVL_BTN_CENTER[1] + self.name_pos[1]
        click_on_point(x, y, ctrl=ctrl)
        self.level += 100 if ctrl else 1

        if self.level >= self.level_ceiling and not self.skill_unlocked():
            self.raise_level_ceiling()

    def level_skill(self) -> None:
        x = SKILLS_BTN_CENTER[0] + (SKILLS_BTN_GAP * self.skill_level)
        y = SKILLS_BTN_CENTER[1] + self.name_pos[1]
        click_on_point(x, y)
        self.skill_level += 1
        if self.level == self.level_ceiling:
            self.raise_level_ceiling()
        print(f"{self.name} Skill level: {self.skill_level}/{self.max_skill_level}")

    def reset(self, full_reset=False) -> None:
        self.level = 0
        self.skill_level = 0
        self.name_pos = (-1, -1)
        if full_reset:
            self.gilded = False
        if self.unique_ups:
            self.level_ceiling = SKILL_UNLOCKS["Unique"][self.name][0]
            return
        self.level_ceiling = SKILL_UNLOCKS["Normal"][0]

    def skill_unlocked(self):
        if self.skill_level < self.max_skill_level:
            if self.unique_ups:
                level_req = SKILL_UNLOCKS["Unique"][self.name][self.skill_level]
            else:
                level_req = SKILL_UNLOCKS["Normal"][self.skill_level]
            return self.level >= level_req
        return False

    def raise_level_ceiling(self):
        if self.level_ceiling < max(LEVEL_GUIDE) and (self.skill_level < self.max_skill_level):
            if self.level_ceiling not in LEVEL_GUIDE:
                self.level_ceiling += LEVEL_OVER_STEP
            else:
                idx = LEVEL_GUIDE.index(self.level_ceiling) + 1
                self.level_ceiling = LEVEL_GUIDE[idx]
        else:
            self.level_ceiling += LEVEL_OVER_STEP

    def gild(self):
        self.gilded = True
        print(f"{self.name} gilded!")

    def found(self) -> bool:
        (x, y) = dts.find_hero(self.name, self.gilded)
        if x > 0:
            self.name_pos = (x, y)
            return True
        return False

    def print_level(self):
        print(self.name, "lvl", self.level)


class Power:
    """
    Class for Powers and their attribute
    """

    def __init__(self, name: str, cooldown: int, key: str, state: bool, hero: str, skill: int):
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
        if self.name == "The Dark Ritual" or "Metal Detector":
            self.activate()

    def activate(self):
        pyautogui.press(self.key)
        self.cd_timer = time()
        print(self.name, "Active")

    def reset(self):
        self.unlocked = False
        self.cd_timer = 0

    def ready(self):
        return (time() - self.cd_timer) > self.cooldown


class GameData:
    """
    Class for game variables
    """

    def __init__(self, level: int, heroes: List[Hero], hero_idx: int,
                 powers: List[Power], powers_num: int, ascension: int, transcend: int,
                 global_skill_num: int, best_hero_idx: int):
        self.heroes = heroes
        self.hero_index = hero_idx
        self.hero = self.heroes[self.hero_index]
        self.powers = powers
        self.unlocked_powers = powers_num
        self.level = level
        self.control_window = ControlWindow()
        self.ascensions = ascension
        self.transcends = transcend
        self.boss_timer = 0.0
        self.grind_timer = 0.0
        self.level_up_timer = 0.0
        self.clickers_set = False  # Set to true if you have game's own auto clickers
        self.global_skill_num = global_skill_num
        self.best_hero_index = best_hero_idx

    def reset_hero_queue(self) -> None:
        self.hero_index = 0
        self.hero = self.heroes[self.hero_index]
        self.update_hero_timer()

    def next_hero(self) -> None:
        self.hero.print_level()
        self.hero_index += 1
        if self.hero_index == len(self.heroes):
            self.hero_index = 0
        self.hero = self.heroes[self.hero_index]
        self.update_hero_timer()

    def update_hero_timer(self) -> None:
        self.level_up_timer = time()

    def next_hero_available(self) -> bool:
        img: np.ndarray = rnd.get_screenshot()
        x = LVL_BTN_X
        y = self.hero.name_pos[1] + LVL_BTN_GAP
        pixel_val = [int(img[y, x, i]) for i in range(3)]
        return max(pixel_val) > COLOR["128"]

    def get_hero_timer(self) -> float:
        return time() - self.level_up_timer

    def reset_checks(self) -> bool:
        if self.level > 300 and self.transcends == 0:
            self.transcend()
            return True

        if self.grind_timer:
            amenhotep: Hero = self.heroes[19]
            if self.ascensions > 9:
                self.transcend()
                return True

            if amenhotep.level >= 150 and self.level > 130:
                if self.global_skill_num == 0 or self.best_hero_index > 38:
                    self.ascend()
                    return True
        return False

    def boss_level_checks(self) -> None:
        img: np.ndarray = rnd.get_screenshot()
        if new_level_available(img):
            print("  BOSS DEFEATED IN {:.2f}s".format(time() - self.boss_timer))
            self.boss_timer = 0.0
            self.move_up_level()

        elif (time() - self.boss_timer) > BOSS_TIME:
            self.level -= 1
            self.boss_timer = 0.0
            self.grind_timer = time()
            click_on_point(PREV_GAME_LEVEL_POINT)
            self.update_hero_timer()
            print(f"  GRINDING TIME! ({GRIND_TIME}s)")

    def level_checks(self) -> None:
        if self.reset_checks():
            return

        if self.level % 5 == 0:
            self.boss_level_checks()
            return

        if self.grind_timer and (time() - self.grind_timer) > GRIND_TIME:
            self.grind_timer = 0.0
            self.move_up_level()
            print("  GRIND ENDED!")
            return

        img = rnd.get_screenshot()
        if not self.grind_timer and new_level_available(img):
            self.move_up_level()

    def move_up_level(self) -> None:
        self.level += 1
        click_on_point(NEXT_GAME_LEVEL_POINT)
        # Tries to verify game level from the screen
        if self.level % 33 == 0 and self.level % 10 != 0:
            read_level = dts.read_game_level(str(self.level))
            if read_level > 0 and read_level != self.level:
                self.level = read_level
                print(f"Sync'd game level to {self.level}")
        if self.level % 5 == 0:
            print(f"  Game level: {self.level} (BOSS)")
            self.boss_timer = time()
        else:
            print(f"  Game level: {self.level}")

    def detections(self) -> None:
        if self.level > 50:
            x, y = dts.find_bee()
            while x > 0:
                move_to(x, y)
                for _ in range(3):
                    auto_click(check=False)
                x, y = dts.find_bee()
            x, y = AC_POINT
            move_to(x, y)

        if dts.present_detection(self.level):
            click_on_point(OPEN_PRESENT_POINT)
            rnd.sleep(0.5)
            # Double click to make sure game registers click
            click_on_point(START_CHEST_POINT)
            rnd.sleep(0.1)
            click_on_point(START_CHEST_POINT)
            rnd.sleep(0.05)
            idx: int = chest_handler(self.heroes)
            if idx > 0:
                self.heroes[idx].gild()
            else:
                print("No suitable hero found! -> Gilding none")
            # Double click to make sure game registers click
            click_on_point(EXIT_CHEST_POINT)
            rnd.sleep(0.1)
            click_on_point(EXIT_CHEST_POINT)
            rnd.sleep(0.05)

    def ascend(self) -> None:
        print("Ascending...")
        self.ascensions += 1
        for hero in self.heroes:
            hero.reset()
        for power in self.powers:
            power.reset()
        self.reset_hero_queue()
        self.level = 1
        self.boss_timer = 0.0
        self.grind_timer = 0.0
        self.unlocked_powers = 0
        self.clickers_set = False
        self.global_skill_num = 0
        self.best_hero_index = 0
        print()
        print()
        print(f"{self.ascensions}. Ascension")
        click_on_point(ASCEND_POINT, center=False)
        rnd.sleep(0.5)
        img = rnd.get_screenshot()
        rnd.sleep(0.5)
        if is_correct_color(img, DEL_RELICS_POINT, color_as_list=DEL_RELICS_BTN_COLOR):
            click_on_point(DEL_RELICS_POINT, center=False)
            rnd.sleep(0.5)
        click_on_point(CONFIRM_ASCEND_POINT)
        rnd.sleep(1)
        set_game_clickers(self)
        rnd.sleep(0.2)

    def transcend(self) -> None:
        print("Transcending...")
        self.transcends += 1
        self.ascensions = 0
        for hero in self.heroes:
            hero.reset(full_reset=True)
        for power in self.powers:
            power.reset()
        self.reset_hero_queue()
        self.level = 1
        self.boss_timer = 0.0
        self.grind_timer = 0.0
        self.unlocked_powers = 0
        print()
        print()
        print(f"  {self.transcends}. Transcend")
        click_on_point(OUTSIDERS_MENU_POINT, center=False)
        rnd.sleep(0.5)
        click_on_point(TRANSCEND_POINT, center=False)
        rnd.sleep(0.125)
        click_on_point(CONFIRM_TRANS_POINT)


def is_correct_color(img,
                     point: Tuple[int, int],
                     color_as_list: List[int] = None,
                     r=256, g=256, b=256) -> bool:
    if color_as_list:
        r, g, b = color_as_list
    x, y = point
    return img[y, x, 0] == r and img[y, x, 1] == g and img[y, x, 2] == b


def new_level_available(img) -> bool:
    return is_correct_color(img, NEXT_GAME_LEVEL_TEST_POINT, color_as_list=NEW_GAME_LEVEL_COLOR)


def chest_handler(heroes: List[Hero]) -> int:
    """
    Clicks on the chest that appears on the screen after opening present and calls for hero gilding.
    :param heroes: List of heroes
    :return index of the best match for gilding
    """
    click_on_point(OPEN_CHEST_POINT)
    rnd.sleep(2)
    img_n: np.ndarray = dts.get_chest_name_img()
    conf_of_best: float = 0.0
    idx_of_best: int = 0
    for idx, hero in enumerate(heroes):
        tmp_conf: float = dts.gilding_matching(img_n, hero.name)
        # Terminate early if very confident
        if tmp_conf > 0.85:
            return idx
        if tmp_conf > conf_of_best and tmp_conf > 0.65:
            idx_of_best = idx
            conf_of_best = tmp_conf
    return idx_of_best


def click_on_point(point: Tuple[int, int], center=True, ctrl=False) -> None:
    """
    :param point: (x, y) coordinates on the screen
    :param ctrl: flag for control click
    :param center: flag for returning to autoclicker point
    """
    x, y = point
    pyautogui.moveTo(x, y)
    if ctrl:
        keyboard: rnd.Controller = rnd.Controller()
        with keyboard.pressed(rnd.Key.ctrl_l):
            rnd.sleep(0.1)
            pyautogui.click()

    if not ctrl:
        # Extra wait because the game is not fast enough to register inputs
        rnd.sleep(CLICK_WAIT)
        pyautogui.click()

    if center:
        pyautogui.moveTo(AC_POINT)


def set_game_clickers(game: GameData) -> None:
    """
    Setups the game's own autoclicker if it's bought
    """

    if NUMBER_OF_CLICKERS == 0 or game.clickers_set:
        return

    elif not game.clickers_set:
        for _ in range(NUMBER_OF_CLICKERS):
            click_on_point(GAME_CLICKERS_POINT)
        game.clickers_set = True


def get_pixel_val(x: int = 0, y: int = 0) -> np.ndarray:
    """
    Debug function for getting image pixel values
    :param x: x-coordinate on screen
    :param y: y-coordinate on screen
    :return: Pixel value of given point(x,y). Else pixel value of the point of the cursor.
    """
    img: np.ndarray = rnd.get_screenshot()
    if x == 0 and y == 0:
        x, y = pyautogui.position()
    return img[y, x, :]


def get_position() -> Tuple[int, int]:
    """
    Debug function for getting mouse position
    """
    x, y = pyautogui.position()
    return x, y


def create_game_data(h_data: Dict[str, Dict], g_data: Dict[str, Any], p_data: Dict[str, Dict]) -> GameData:
    """
    Parses save data and creates the GameState object.
    :param h_data: Dict with heroes data
    :param g_data: Dict with game data
    :param p_data: Dict with powers data
    :return: GameData class object
    """
    h_tmp: List[Hero] = []
    p_tmp: List[Power] = []
    h_idx: int = 0
    powers_num: int = 0
    for name in h_data:
        new_hero: Hero = Hero(name,
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
        new_power: Power = Power(name,
                                 p_data[name]["Cooldown"],
                                 p_data[name]["Key"],
                                 p_data[name]["Unlocked"],
                                 p_data[name]["Unlock hero"],
                                 p_data[name]["Unlock skill"],
                                 )
        if new_power.unlocked:
            powers_num += 1
        p_tmp.append(new_power)

    game: GameData = GameData(g_data["Level"],
                              h_tmp,
                              h_idx,
                              p_tmp,
                              powers_num,
                              g_data["Ascension level"],
                              g_data["Transcend level"],
                              g_data["Global skill num"],
                              g_data["Best hero index"]
                              )
    return game


def scroll_down(game: GameData) -> None:
    """
    Scrolls down on the heroes list in the game window
    :param game: GameData class object
    """
    if not game.boss_timer:
        img: np.ndarray = rnd.get_screenshot()
        # Check if scroll bar is at bottom
        x, y = SCROLL_BOTTOM_POINT
        if img[y, x, 2] > COLOR["190"]:
            game.reset_hero_queue()
            reset_scroll()
        else:
            x, y = SCROLLING_POINT
            move_to(x, y)
            # TODO: scroll amount weird?
            scroll_amount: int = round(-150 - 100 / game.level)
            pyautogui.scroll(scroll_amount)
            x, y = AC_POINT
            move_to(x, y)
            rnd.sleep(CLICK_WAIT)


def reset_scroll() -> None:
    """
    Returns to the top of the heroes list in the game window
    """
    img: np.ndarray = rnd.get_screenshot()
    x, y = SCROLLING_POINT
    move_to(x, y)
    i, j = SCROLL_TOP_POINT
    while not img[j, i, 2] > COLOR["VERY_HIGH"]:
        pyautogui.scroll(5000)
        img = rnd.get_screenshot()
    x, y = AC_POINT
    move_to(x, y)
    rnd.sleep(CLICK_WAIT)


def auto_click(wait=CLICK_WAIT, check=True, r=5) -> None:
    """
    *CLICKS* clicks r amount of times on the current point
    :param r: Number of clicks
    :param check: Flag for checking if cursor is in autoclick point area
    :param wait: Wait time in seconds (s)
    """
    mouse: pynput.mouse.Controller = pynput.mouse.Controller()
    x, y = pyautogui.position()
    if check:
        if (not (AC_POINT[0] - 5 < x < AC_POINT[0] + 5)
                or not (AC_POINT[1] - 5 < y < AC_POINT[1] + 5)):
            return

    for c_num in range(r):
        mouse.click(pynput.mouse.Button.left)
        if c_num + 1 != r:
            rnd.sleep(wait)


def move_to(x: int, y: int) -> None:
    pyautogui.moveTo(x, y)
