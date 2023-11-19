import cv2
import win32gui
from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_NAME
from numpy import array
from PIL import ImageGrab


def find_game_win():
    """
    Finds the game window and returns it if it's found
    :return: Game window object
    """
    hwnd = win32gui.FindWindow(None, GAME_NAME)
    if not hwnd:
        print(f"Game window '{GAME_NAME}' not found!")
    return hwnd


def move_game_win(hwnd):
    """
    Moves game window to the front so that it's visible
    :param hwnd: Game window object
    """
    win32gui.SetForegroundWindow(hwnd)
    win32gui.MoveWindow(hwnd, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, True)


def get_screenshot(BGR=False):
    """
    Takes screenshot from the game window
    :param BGR: boolean, returns the screenshot as BRG
    :return: screenshot of the game as a numpy array (RGB)
    """
    hwnd = win32gui.FindWindow(None, GAME_NAME)
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    bbox = [left, top, right, bot]
    img = array(ImageGrab.grab(bbox))  # noqa
    if BGR:
        img_bgr = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
        return img_bgr
    else:
        return img


def render(img):
    """
    Resizes the image and renders it in a Render window next to the game window.
    :param img: Image to render as a numpy array (BGR)
    """
    small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imshow("Render", small)
    hwnd = win32gui.FindWindow(None, 'Render')
    win32gui.MoveWindow(hwnd, WINDOW_WIDTH, 0, round((WINDOW_WIDTH + 35) / 2), round((WINDOW_HEIGHT + 80) / 2),
                        True)
    cv2.waitKey(1)
