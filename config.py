"""
Configuration file containing global constants
"""

""" SYSTEM VARIABLES """
GAME_NAME = 'Clicker Heroes'
IMG_PATH = 'images/'
SAVE_PATH = 'saves/'
WINDOW_WIDTH = 1050  # DO NOT CHANGE!
WINDOW_HEIGHT = 600  # DO NOT CHANGE!
DEBUG = True

""" HERO LEVELING VARIABLES """
# Levels at heroes unlock new skill/upgrade
SKILL_UNLOCKS = {"Normal": [10, 25, 50, 75, 100, 125, 150],
                 "Unique": {"Referi Jerator, Ice Wizard": [10, 25, 50, 75, 125],
                            "Athena, Goddess of War": [10, 25, 50, 100],
                            "Aphrodite, Goddess of Love": [10, 25, 50, 100, 125],
                            "Dread Knight": [10, 25, 50, 100],
                            "Atlas": [10, 25, 50, 100],
                            "Terra": [10, 25, 50, 100],
                            "Phthalo": [10, 25, 50, 100],
                            "Orntchya Gladeye, Didensy Banana": [10, 25, 50, 100],
                            "Lilin": [10, 25, 50, 100],
                            "Cadmia": [10, 25, 50, 100],
                            "Alabaster": [10, 25, 50, 100],
                            "Astraea": [10, 25, 50, 100],
                            "Chiron": [10, 25, 50, 100],
                            "Moloch": [10, 25, 50, 100],
                            "Bomber Max": [10, 25, 50, 100],
                            "Gog": [10, 25, 50, 100],
                            "Wepwawet": [25, 100, 1500, 2000],
                            "Tsuchi": [1000, 2000, 4000, 8000]
                            }
                 }
# Hero leveling guide logic for the program to follow [NOTE: MUST GO OVER LEVEL 150!]
LEVEL_GUIDE = [1, 10, 25, 50, 75, 100, 125, 150, 175, 200]
# Level step for leveling heroes after the level guide
LEVEL_OVER_STEP = 100
# Seconds waiting for gold to accumulate for hero level up
HERO_WAIT_TIME = 30

""" GAME STATE VARIABLES """
# Unused?
ASCENSION_STEP = 43
# Number of in game auto clickers
NUMBER_OF_CLICKERS = 2
# Seconds grinding current level to until retrying to beat next boss
GRIND_TIME = 300
# Default wait time in seconds. Used mainly in between clicks
CLICK_WAIT = 1 / 2000
# Default time for a boss level in seconds
BOSS_TIME = 30

""" PIXEL POINTS """
# Autoclicker point. AC is toggled on only at this point.
AC_POINT = (775, 365)
# Points of various object. Used to navigate through menus
PREV_GAME_LEVEL_POINT = (728, 65)
NEXT_GAME_LEVEL_POINT = (822, 65)
NEXT_GAME_LEVEL_TEST_POINT = (812, 47)
OPEN_PRESENT_POINT = (1000, 500)
START_CHEST_POINT = (510, 300)
OPEN_CHEST_POINT = (523, 324)
EXIT_CHEST_POINT = (800, 130)
ASCEND_POINT = (997, 229)
DEL_RELICS_POINT = (485, 370)
CONFIRM_ASCEND_POINT = (485, 420)
OUTSIDERS_MENU_POINT = (465, 145)
TRANSCEND_POINT = (265, 270)
CONFIRM_TRANS_POINT = (410, 450)
GAME_CLICKERS_POINT = (990, 338)
SCROLL_TOP_POINT = (488, 250)
SCROLL_BOTTOM_POINT = (478, 570)
SCROLLING_POINT = (465, 407)
# Center point of the level up button (needs to be added to hero name Y-coordinate)
LVL_BTN_CENTER = (117, 30)
# Center point of the skills button (needs to be added to hero name Y-coordinate)
SKILLS_BTN_CENTER = (182, 56)
# X-coordinate of level up button. Used for reading pixel value
LVL_BTN_X = 157
# X-coordinate of the first skill under heroes
SKILLS_BTN_X = 182
# Pixel distance between hero name and different buttons. In Y-coordinates.
NAME_DIST = {"LVL_BTN": 15,
             "SKILLS_BTN": 41}
# Pixel distance between skill icons. In X-coordinates
SKILLS_BTN_GAP = 29
# Pixel distance between level up buttons. In Y-coordinates
LVL_BTN_GAP = 100

""" PIXEL VALUES """
# Pixel values [RGB] for new game level at (x, y) == (812,47)
NEW_GAME_LEVEL_COLOR = [171, 205, 195]
# Pixel values [RGB] for present icon at (x, y) == (1000,500)
PRESENT_COLOR = [245, 128, 128]
# Pixel values [RGB] for button at (x, y) == (485,370)
DEL_RELICS_BTN_COLOR = [68, 215, 35]
# Pixel contrast values
COLOR = {"LOW": 50,
         "128": 128,
         "MEDIUM": 150,
         "190": 190,
         "HIGH": 200,
         "VERY_HIGH": 250}

""" DETECTOR VARIABLES """
# Threshold for template matching detection
CONFIDENCE_THRESHOLD = 0.7
