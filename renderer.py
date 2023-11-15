import cv2
import win32gui
from config import WINDOW_WIDTH, WINDOW_HEIGHT, GAME_NAME
from numpy import array
from PIL import ImageGrab


def find_game_win():
    hwnd = win32gui.FindWindow(None, GAME_NAME)
    if not hwnd:
        print(f"Game window '{GAME_NAME}' not found!")
    return hwnd


def move_game_win(hwnd):
    win32gui.SetForegroundWindow(hwnd)
    win32gui.MoveWindow(hwnd, 0, 0, WINDOW_WIDTH, WINDOW_HEIGHT, True)


def get_screenshot():
    hwnd = win32gui.FindWindow(None, 'Clicker Heroes')
    left, top, right, bot = win32gui.GetWindowRect(hwnd)
    bbox = [left, top, right, bot]
    img = array(ImageGrab.grab(bbox))  # noqa
    screenshot = cv2.cvtColor(img, cv2.COLOR_RGB2BGR)
    return screenshot


def render(img):
    """
    renders game capture
    :param img: img to render
    """
    small = cv2.resize(img, (0, 0), fx=0.5, fy=0.5)
    cv2.imshow("Render", small)
    hwnd = win32gui.FindWindow(None, 'Render')
    win32gui.MoveWindow(hwnd, WINDOW_WIDTH, 0, round((WINDOW_WIDTH + 35) / 2), round((WINDOW_HEIGHT + 80) / 2),
                        True)
    cv2.waitKey(1)
    # else:
    # img = cv2.cvtColor(screenshot, cv2.COLOR_RGB2BGR)
