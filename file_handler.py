import json
from config import SAVE_PATH


def load_from_file():
    """
    Loads the game state data from save.json or creates one from setup.json
    """
    h_dict, g_dict, p_dict = ([] for _ in range(3))
    save_file = True
    try:
        with open(SAVE_PATH + "save.json", 'r', encoding='utf-8') as file:
            data = json.load(file)
            h_dict = data["Heroes"]
            p_dict = data["Powers"]
            g_dict = data["Gamestate"]
    except OSError:
        save_file = False

    if not save_file:
        try:
            with open("setup.json", 'r', encoding='utf-8') as file:
                data = json.load(file)
                h_dict = data["Heroes"]
                p_dict = data["Powers"]
                g_dict = data["Gamestate"]
        except OSError:
            print("'setup.json' NOT FOUND!")
            return h_dict, g_dict, p_dict

    return h_dict, g_dict, p_dict


def save_data(game):
    """
    Saves current game data to save.json file
    :param game: GameData class object
    """
    print("Saving...")
    save_dict = {'Heroes': {},
                 'Powers': {}}
    for hero in game.heroes:
        save_dict['Heroes'][hero.name] = {'Level': hero.level,
                                          'Level ceiling': hero.level_ceiling,
                                          'Skill level': hero.skill_level,
                                          'Max skill level': hero.max_skill_level,
                                          'Gilded': hero.gilded,
                                          'Unique skills': hero.unique_ups
                                          }
    for power in game.powers:
        save_dict['Powers'][power.name] = {'Cooldown': power.cooldown,
                                           'Key': power.key,
                                           'Unlocked': power.unlocked,
                                           'Unlock hero': power.hero,
                                           'Unlock skill': power.skill
                                           }
    save_dict['Gamestate'] = {'Level': game.level,
                              'Ascension level': game.ascensions,
                              'Transcend level': game.transcends,
                              'Current hero': game.hero.name,
                              }

    with open(SAVE_PATH + 'save.json', 'w+', encoding='utf-8') as file:
        json.dump(save_dict, file, ensure_ascii=False, indent=4)
