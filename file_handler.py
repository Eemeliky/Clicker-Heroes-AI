import json
from config import SKILL_UNLOCKS, SAVE_PATH


def load_from_file():
    """
    Loads the gamestate from save.json or creates one from setup.json
    :return:
    """
    h_data, g_data, p_data = ([] for _ in range(3))
    save_file = False
    try:
        with open(SAVE_PATH + "save.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            h_data = data["Heroes"]
            SKILL_UNLOCKS["Unique"] = data["Unique skills"]
            p_data = data["Powers"]
            g_data = data["Gamestate"]
            save_file = True
    except IOError:
        pass

    if not save_file:
        try:
            with open("setup.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                h_data = data["Heroes"]
                SKILL_UNLOCKS["Unique"] = data["Unique skills"]
                p_data = data["Powers"]
                g_data = data["Gamestate"]
        except IOError:
            print("'setup.json' NOT FOUND!")
            return h_data, g_data, p_data

    return h_data, g_data, p_data


def save_data(game):
    pass
