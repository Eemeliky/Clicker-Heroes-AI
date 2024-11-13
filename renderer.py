from typing import List, Any
import cv2
import numpy as np
import win32gui

from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_NAME
from numpy import array, ndarray, dtype
from PIL import ImageGrab
from pynput.keyboard import Key, Controller
from time import sleep


def find_game_win() -> int:
    """
    Finds the game window and returns it if it's found
    :return: Game window number
    """
    hwnd: int = win32gui.FindWindow(None, GAME_NAME)
    if not hwnd:
        print(f"Game window '{GAME_NAME}' not found!")
    return hwnd


def move_game_win(hwnd: int) -> None:
    """
    Moves game window to the front so that it's visible
    :param hwnd: Game window number
    """
    win32gui.SetForegroundWindow(hwnd)
    win32gui.MoveWindow(hwnd, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, True)


def get_screenshot(BGR=False, ctrl=False) -> ndarray:
    """
    Takes screenshot from the game window
    :param ctrl: boolean, takes screenshot with key "ctrl" held down, Default = false
    :param BGR: boolean, returns the screenshot as BRG instead of RGB, Default = false
    :return: screenshot of the game window as a numpy array,
    Default = ndarray(RGB)
    """
    hwnd: int = win32gui.FindWindow(None, GAME_NAME)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    bbox: List[int] = [left, top, right, bot]
    if ctrl:
        keyboard: Controller = Controller()
        with keyboard.pressed(Key.ctrl_l):
            sleep(0.5)
            img_rgb: np.ndarray[Any, dtype] = array(ImageGrab.grab(bbox=bbox))
    else:
        img_rgb: np.ndarray[Any, dtype] = array(ImageGrab.grab(bbox=bbox))
        if BGR:
            return cv2.cvtColor(img_rgb, cv2.COLOR_RGB2BGR)
    return img_rgb


def render(img: np.array = None) -> None:
    """
    Resizes the image and renders it in render window next to the game window.
    :param img: Image to render as a numpy array (BGR)
    """
    if img.shape[0] == 0:
        img = get_screenshot()
    img_rgb: np.ndarray = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
    small: np.ndarray = cv2.resize(img_rgb, (0, 0), fx=0.5, fy=0.5)
    cv2.imshow("Render", small)
    hwnd: int = win32gui.FindWindow(None, 'Render')
    win32gui.MoveWindow(hwnd, WINDOW_WIDTH, 0, round((WINDOW_WIDTH + 35) / 2),
                        round((WINDOW_HEIGHT + 80) / 2), True)
    cv2.waitKey(1)
