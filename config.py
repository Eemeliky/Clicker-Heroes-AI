# Levels for skill unlocks
SKILL_UNLOCKS = {"Normal": [10, 25, 50, 75, 100, 125, 150],
                 "Unique": {"Referi Jerator, Ice Wizard": [10, 25, 50, 75, 125, 150],
                            "Athena, Goddess of War": [10, 25, 50, 100, 125, 150],
                            "Dread Knight": [10, 25, 50, 100, 125, 150],
                            "Aphrodite, Goddess of Love": [10, 25, 50, 100, 125, 150],
                            "Atlas": [10, 25, 50, 100, 125, 150],
                            "Terra": [10, 25, 50, 100, 125, 150],
                            "Phthalo": [10, 25, 50, 100, 125, 150],
                            "Orntchya Gladeye, Didensy Banana": [10, 25, 50, 100, 125, 150],
                            "Lilin": [10, 25, 50, 100, 125, 150],
                            "Cadmia": [10, 25, 50, 100, 125, 150],
                            "Alabaster": [10, 25, 50, 100, 125, 150],
                            "Astraea": [10, 25, 50, 100, 125, 150],
                            "Chiron": [10, 25, 50, 100, 125, 150],
                            "Moloch": [10, 25, 50, 100, 125, 150],
                            "Bomber Max": [10, 25, 50, 100, 125, 150],
                            "Gog": [10, 25, 50, 100, 125, 150]
                            }
                 }

# Hero leveling guide logic for the program to follow
LEVEL_GUIDE = [1, 5, 10, 15, 25, 50, 75, 85, 95, 105, 115, 125, 135, 145, 155, 165, 175, 185, 195, 205, 215, 225]
LEVEL_OVER_STEP = 25  # Step for leveling heroes over the guide
GAME_NAME = 'Clicker Heroes'
AC_POINT = (775, 365)  # Only point where autoclicker works
NEW_GAME_LEVEL = [72, 122, 198]  # pixel values for new game level
LEVEL_UP_X = 149  # Level up button x-coordinate
SKILL_X_COORDINATE = 197  # Level up skill x-coordinate
SKILL_OFFSET = 32  # Pixels between skill icons
IMG_PATH = 'images/'
SAVE_PATH = 'saves/'
CONFIDENCE_THRESHOLD = 0.7  # Threshold for the detection of heroes
WINDOW_WIDTH = 1050  # Game window width
WINDOW_HEIGHT = 600  # Game window height
GRIND_TIME = 300  # Time in seconds
WAIT_TIME = 15
DEBUG = True
