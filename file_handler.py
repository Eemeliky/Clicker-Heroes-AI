import json
from config import SAVE_PATH


def load_from_file():
    """
    Loads the gamestate from save.json or creates one from setup.json
    :return:
    """
    h_dict, g_dict, p_dict = ([] for _ in range(3))
    save_file = False
    try:
        with open(SAVE_PATH + "save.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            h_dict = data["Heroes"]
            p_dict = data["Powers"]
            g_dict = data["Gamestate"]
            save_file = True
    except IOError:
        pass

    if not save_file:
        try:
            with open("setup.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                h_dict = data["Heroes"]
                p_dict = data["Powers"]
                g_dict = data["Gamestate"]
        except IOError:
            print("'setup.json' NOT FOUND!")
            return h_dict, g_dict, p_dict

    return h_dict, g_dict, p_dict


def save_data(game):  # Not implemented yet
    pass
