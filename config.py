# Levels for skill unlocks
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

# Hero leveling guide logic for the program to follow (MUST GO OVER LEVEL 150)
LEVEL_GUIDE = [1, 10, 25, 50, 75, 100, 125, 150, 175]
ASCENSION_STEP = 43
LEVEL_OVER_STEP = 25  # Step for leveling heroes over the guide
GAME_NAME = 'Clicker Heroes'
AC_POINT = (775, 365)  # Only point where autoclicker works
NEW_GAME_LEVEL = [171, 205, 195]  # pixel values for new game level at (x, y) == (812,47)
LEVEL_UP_X = 157  # Level up button x-coordinate
SKILL_X = 197  # Level up skill x-coordinate
SKILL_X_OFFSET = 29  # Pixels between skill icons
SKILL_Y_OFFSET = 41
LEVEL_UP_Y_OFFSET = 15
IMG_PATH = 'images/'
SAVE_PATH = 'saves/'
CONFIDENCE_THRESHOLD = 0.7  # Threshold for the detection of heroes
WINDOW_WIDTH = 1050  # Game window width
WINDOW_HEIGHT = 600  # Game window height
GRIND_TIME = 300  # Time in seconds
WAIT_TIME = 30
DEBUG = True


def set_level_guide(ascensions, transcends):
    global LEVEL_GUIDE
    global LEVEL_OVER_STEP
    global ASCENSION_STEP
    LEVEL_GUIDE = [1, 10, 25, 50, 75, 100, 125, 150, 175]
    ASCENSION_STEP = 43
    LEVEL_OVER_STEP = 25
    if ascensions > 2:
        tmp = SKILL_UNLOCKS["Normal"]
        tmp.append(200)
        LEVEL_GUIDE = tmp
        LEVEL_OVER_STEP = 100
    if transcends > 0:
        ASCENSION_STEP = 100 * transcends
