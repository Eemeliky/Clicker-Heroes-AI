import cv2
from typing import Tuple, List
from config import IMG_PATH, CONFIDENCE_THRESHOLD, DEBUG
from renderer import get_screenshot, render
import numpy as np


def template_matching(needle_img: np.ndarray, base_img: np.ndarray, BITWISE=False) -> Tuple[float, Tuple[int, int]]:
    """
    Function for template matching
    :param needle_img: Needle image. Image we are looking for
    :param base_img: Base image, Image where to look for the needle image
    :param BITWISE: flag for performing inversion of each pixel in the base img (sometimes helps with detection)
    :return: confidence and location of the best match.
    """
    if BITWISE:
        base_img: np.ndarray = cv2.bitwise_not(base_img)
    results_img: np.ndarray = cv2.matchTemplate(base_img, needle_img, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(results_img)
    return max_val, max_loc


def find_hero(hero_name: str, gilded: bool) -> Tuple[int, int]:
    """
    :param hero_name: Name of the hero
    :param gilded: True for gilded, False for not gilded.
    :return: Position of hero's name on the screenshot as (x,y).
    """

    img: np.ndarray = get_screenshot()
    img_g: np.ndarray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name: str = IMG_PATH + 'heroes/' + hero_name + '.png'
    needle_img: np.ndarray = cv2.imread(image_name, 0)

    if not gilded:
        needle_img = cv2.bitwise_not(needle_img)

    confidence, (x, y) = template_matching(needle_img, img_g, BITWISE=True)
    found: bool = (confidence > CONFIDENCE_THRESHOLD) & ((y + 75) < 600)
    if found:
        width: int = needle_img.shape[1]
        height: int = needle_img.shape[0]
        starting_point: Tuple[int, int] = (int(x), int(y))
        ending_point: Tuple[int, int] = (int(x + width), int(y + height))
        cv2.rectangle(img, starting_point, ending_point, color=(255, 0, 0), thickness=2)
        render(img)
        return x, y
    return 0, 0


def present_detection(game_level: int) -> bool:
    """
    Gets pixel value from the postion where the present appears every 10th level after level 100.
    :param game_level: Level of the game
    :return: True if present is there
    """
    img: np.ndarray = get_screenshot()
    if game_level > 100:
        return (img[517, 999, :] == np.array([245, 128, 128])).all()  # RGB
    return False


def get_chest_name_img() -> np.ndarray:
    """
    Gets cropped image of the screen after chest where gilding happens.
    :return: Cropped image as negative
    """
    img: np.ndarray = get_screenshot(BGR=True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_crop: np.ndarray = img[220:430, 255:810]
    return cv2.bitwise_not(img_crop)


def gilding_matching(base_img: np.ndarray, hero_name: str) -> float:
    """
    :param base_img: Image of game screen that is used to find match.
    :param hero_name: Name of the hero
    :return: Confidence that name of the hero is on the base_img
    """
    img_name: str = IMG_PATH + 'heroes/' + hero_name + '.png'
    needle_img: np.ndarray = cv2.imread(img_name, 0)
    needle_img = cv2.bitwise_not(needle_img)
    confidence, _ = template_matching(needle_img, base_img, BITWISE=True)
    return confidence


def find_bee() -> Tuple[int, int]:
    """
    Finds the bee that appears at the top of the screen.
    :return: Position of the bee on the screenshot as (x,y)
    """
    img: np.ndarray = get_screenshot(BGR=True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    name: str = IMG_PATH + 'Bee.png'
    needle_img: np.ndarray = cv2.imread(name, 0)
    img = img[50:150, 590:960]
    confidence, (x, _) = template_matching(needle_img, img)
    if confidence > 0.9:
        if DEBUG:
            print('Bee found with confidence:', round(confidence, 4))
        y: int = 100
        return x + 590, y
    return -1, -1


def read_hero_level(hero_name_y: int) -> int:
    """
    Function to read hero level from the screenshot of the game window. Helps to error correct unregistered clicks.
    :param hero_name_y: y-coordinate of name of the hero
    :return: level of the current hero read form the game screen
    """
    numbers: str = ""
    img: np.ndarray = get_screenshot(True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name: str = IMG_PATH + 'numbers/' + 'lvl.png'
    needle_img: np.ndarray = cv2.imread(image_name, 0)
    width: int = needle_img.shape[1]
    img_crop: np.ndarray = img[hero_name_y + 12: hero_name_y + 32, 200:400]
    confidence, (x, y) = template_matching(needle_img, img_crop)
    img_crop = img_crop[:, x+width:]
    if confidence > CONFIDENCE_THRESHOLD:
        for _ in range(25):
            best_guess: List[int] = [200, -1]
            best_confidence: float = 0.0
            tmp_max_conf: float = 0.0
            step: int = 12
            for num in range(10):
                image_name = IMG_PATH + 'numbers/' + 'num_' + str(num) + '.png'
                needle_img = cv2.imread(image_name, 0)
                width = needle_img.shape[1]
                results: np.ndarray = cv2.matchTemplate(img_crop, needle_img, cv2.TM_CCOEFF_NORMED)
                _, max_conf, _, _ = cv2.minMaxLoc(results)
                if max_conf > tmp_max_conf:
                    tmp_max_conf = max_conf
                locations = np.where(results > CONFIDENCE_THRESHOLD)
                for point in zip(*locations[::-1]):
                    if point[0] < best_guess[0] or (point[0] == best_guess[0] and max_conf > best_confidence):
                        best_guess[0] = point[0]
                        best_guess[1] = num
                        step = width
                        best_confidence = max_conf
            if tmp_max_conf < 0.5 or img_crop.shape[1] < 11:
                break
            numbers += str((best_guess[1]))
            img_crop = img_crop[:, best_guess[0] + step:]
        if len(numbers) > 0:
            return int(numbers)
    return 0


def read_game_level(level_string: str) -> int:
    """
    Function to read game level from the screenshot of the game window. Helps to error correct unregistered clicks.
    :param level_string: current saved game level as string
    :return: current game level read form the game screen
    """
    numbers: str = ""
    img: np.ndarray = get_screenshot(True)
    img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    image_name: str = IMG_PATH + 'numbers/' + 'lvl_game.png'
    needle_img: np.ndarray = cv2.imread(image_name, 0)
    width: int = needle_img.shape[1]
    img_crop: np.ndarray = img[100: 117, 675:895]
    confidence, (x, y) = template_matching(needle_img, img_crop)
    img_crop = img_crop[:, x+width:]
    if confidence > 0.5:
        for mag in range(len(level_string) + 1):
            best_guess: List[int] = [200, -1]
            best_confidence: float = 0.0
            ties: List[str] = []
            step: int = 12
            for num in range(10):
                image_name = IMG_PATH + 'numbers/' + 'gnum_' + str(num) + '.png'
                needle_img = cv2.imread(image_name, cv2.IMREAD_GRAYSCALE)
                width = needle_img.shape[1]
                if img_crop.shape[1] < width:
                    break
                results: np.ndarray = cv2.matchTemplate(img_crop, needle_img, cv2.TM_CCOEFF_NORMED)
                _, max_conf, _, _ = cv2.minMaxLoc(results)
                locations: np.ndarray = np.where(results > 0.67)
                for point in zip(*locations[::-1]):
                    if point[0] < best_guess[0] or (point[0] == best_guess[0] and max_conf > best_confidence):
                        best_guess[0] = point[0]
                        best_guess[1] = num
                        step = width
                        best_confidence = max_conf
                    elif point[0] == best_guess[0] and max_conf - best_confidence < 0.1 and best_guess[1] != num:
                        ties.append(str(num))
            if best_confidence < 0.6:
                if len(numbers) > 0:
                    return int(numbers)
            else:
                match: bool = False
                if ties:
                    for tie in ties:
                        if tie == level_string[mag]:
                            numbers += str(tie)
                            match = True
                    if not match:
                        numbers += str((best_guess[1]))
                else:
                    numbers += str((best_guess[1]))
            img_crop = img_crop[:, best_guess[0] + step:]
        return 0
