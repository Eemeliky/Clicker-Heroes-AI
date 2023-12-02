import cv2

import config
from config import IMG_PATH, CONFIDENCE_THRESHOLD, DEBUG
from renderer import render, get_screenshot
from time import sleep
import numpy as np


def detect_hero(game):
    """
    :param game: GameData Class object
    :return: True if hero is found, False if not found
    """
    img = get_screenshot()
    hero = game.hero
    image_name = IMG_PATH + 'heroes/' + hero.name + '.png'
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
        hero.name_pos = (x, y)
        if config.DEBUG:
            render(img)
        return True

    game.hero_name_xy = (-1, -1)
    if config.DEBUG:
        render(img)
    return False


def present_detection(game):
    img = get_screenshot()
    if game.level > 100:
        if (img[517, 999, :] == np.array([245, 128, 128])).all():  # RGB
            return True
    return False


def find_gilded(game):
    img = get_screenshot(BGR=True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_crop = img[220:430, 255:810]
    img_n = cv2.bitwise_not(img_crop)
    best_match = (0, 0)
    for idx, hero in enumerate(game.heroes):
        img_name = IMG_PATH + 'heroes/' + hero.name + '.png'
        needle_img = cv2.imread(img_name, 0)
        needle_img = cv2.bitwise_not(needle_img)
        results_img = cv2.matchTemplate(img_n, needle_img, cv2.TM_CCOEFF_NORMED)
        min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
        if max_val > best_match[0] and max_val > 0.6:
            best_match = (max_val, idx)
    g_hero = game.heroes[best_match[1]]
    if DEBUG:
        print(g_hero.name, 'gilded, Confidence:', round(best_match[0], 4))
    if best_match[0] == 0:
        return None
    return best_match[1]


# TODO: REWRITE ALL FUNCTIONS UNDER
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
