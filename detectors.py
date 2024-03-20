import cv2
from typing import Tuple, List

import config
from config import IMG_PATH, CONFIDENCE_THRESHOLD, DEBUG
from renderer import render, get_screenshot
import numpy as np


def template_matching(needle_img, base_img, BITWISE=False) -> Tuple[float, Tuple[int, int]]:
    if BITWISE:
        base_img = cv2.bitwise_not(base_img)
    results_img = cv2.matchTemplate(base_img, needle_img, cv2.TM_CCOEFF_NORMED)
    min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(results_img)
    return max_val, max_loc


def detect_hero(game) -> bool:
    """
    :param game: GameData Class object
    :return: True if hero is found, False if not found
    """
    hero = game.hero
    img = get_screenshot()
    img_g = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name = IMG_PATH + 'heroes/' + hero.name + '.png'
    needle_img = cv2.imread(image_name, 0)

    if not hero.gilded:
        needle_img = cv2.bitwise_not(needle_img)

    confidence, (x, y) = template_matching(needle_img, img_g, BITWISE=True)
    found: bool = (confidence > CONFIDENCE_THRESHOLD) & ((y + 75) < 600)
    if found:
        width = needle_img.shape[1]
        height = needle_img.shape[0]
        starting_point = (int(x), int(y))
        ending_point = (int(x + width), int(y + height))
        cv2.rectangle(img, starting_point, ending_point, color=(255, 0, 0), thickness=2)
        hero.name_pos = (x, y)

    if config.DEBUG:
        render(img)
    return found


def present_detection(game) -> bool:
    img = get_screenshot()
    if game.level > 100:
        return (img[517, 999, :] == np.array([245, 128, 128])).all()  # RGB
    return False


def find_gilded(game) -> int:
    img = get_screenshot(BGR=True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_crop = img[220:430, 255:810]
    img_n = cv2.bitwise_not(img_crop)
    best_match = (-1, -1)
    for idx, hero in enumerate(game.heroes):
        img_name = IMG_PATH + 'heroes/' + hero.name + '.png'
        needle_img = cv2.imread(img_name, 0)
        needle_img = cv2.bitwise_not(needle_img)
        confidence, _ = template_matching(needle_img, img_n, BITWISE=True)
        if confidence > 0.9:
            return idx
        elif confidence > best_match[0] and confidence > CONFIDENCE_THRESHOLD:
            best_match = confidence, idx
    return best_match[1]


def find_bee() -> Tuple[int, int]:
    img = get_screenshot(BGR=True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    name = IMG_PATH + 'Bee.png'
    needle_img = cv2.imread(name, 0)
    img = img[50:150, 590:960]
    confidence, (x, _) = template_matching(needle_img, img)
    if confidence > 0.9:
        if DEBUG:
            print('Bee found with confidence:', round(confidence, 4))
        y = 100
        return x + 590, y
    return -1, -1


def read_hero_level(game) -> int:
    """
    Function to read hero level from the screenshot of the game window. Helps to error correct unregistered clicks.
    :param game: GameState object
    :return: level of the current hero read form the game screen
    """
    read_level: int = -1
    numbers: str = ""
    img = get_screenshot(True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name = IMG_PATH + 'numbers/' + 'lvl.png'
    needle_img = cv2.imread(image_name, 0)
    width = needle_img.shape[1]
    _, name_y = game.hero.name_pos
    img_crop = img[name_y + 12: name_y + 32, 200:400]
    confidence, (x, y) = template_matching(needle_img, img_crop)
    img_crop = img_crop[:, x+width:]
    for _ in range(25):
        best_guess: List[int] = [200, -1]
        best_confidence: float = 0.0
        tmp_max_conf: float = 1.0
        step: int = 12
        for num in range(10):
            image_name = IMG_PATH + 'numbers/' + 'num_' + str(num) + '.png'
            needle_img = cv2.imread(image_name, 0)
            width = needle_img.shape[1]
            results = cv2.matchTemplate(img_crop, needle_img, cv2.TM_CCOEFF_NORMED)
            _, max_conf, _, _ = cv2.minMaxLoc(results)
            if max_conf > tmp_max_conf or num == 0:
                tmp_max_conf = max_conf
            locations = np.where(results > CONFIDENCE_THRESHOLD)
            for point in zip(*locations[::-1]):
                if point[0] < best_guess[0] or (point[0] == best_guess[0] and max_conf > best_confidence):
                    best_guess[0] = point[0]
                    best_guess[1] = num
                    step = width
                    best_confidence = max_conf
        if tmp_max_conf < 0.5:
            break
        numbers += str((best_guess[1]))
        img_crop = img_crop[:, best_guess[0] + step:]
    if len(numbers) > 0:
        return int(numbers)
    return 0
