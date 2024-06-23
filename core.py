from config import LEVEL_UP_X, SKILL_Y_OFFSET, SKILL_X, SKILL_X_OFFSET, LEVEL_UP_Y_OFFSET, LEVEL_OVER_STEP, WAIT_TIME
from detectors import read_hero_level
import renderer as rnd


def upgrade_first_levels(hero):
    """
    Upgrades first 2 levels when template matching doesn't work, because achievements block the hero name.
    :param hero: Current hero from GameData
    """
    img = rnd.get_screenshot()
    if img[275, LEVEL_UP_X, 2] > 250:
        hero.name_pos = (157, 235)
        hero.level_up()


def upgrade_normal(game, img):
    """
    Function that decides hero level ups and skill level ups, depending on the hero information.
    :param game: GameData class object
    :param img: Screenshot of the game window
    :return:
    """
    hero = game.hero
    x, y = hero.name_pos
    if hero.skill_unlocked():
        r_level = read_hero_level(y)
        if r_level == hero.level or r_level == 0:
            pixel_val = []
            for i in range(3):
                pixel_val.append(img[y + SKILL_Y_OFFSET, SKILL_X + (SKILL_X_OFFSET * hero.skill_level), i])
            if max(pixel_val) > 50:
                hero.level_skill()
        else:
            print(f'Adjusting hero level to {r_level}')
            hero.level = r_level

    elif img[y + LEVEL_UP_Y_OFFSET, LEVEL_UP_X, 2] > 200:
        if LEVEL_OVER_STEP > 25 and (hero.level_ceiling - hero.level) > 99:
            if rnd.np.max(img[y + 43, 125:165, 0]) < 255:
                hero.level_up(CTRL=True)
        else:
            hero.level_up()
            if hero.level % 15 == 0:  # PROBLEM WITH LEVEL 35
                r_level = read_hero_level(hero.name_pos[1])
                if 0 < r_level != hero.level:
                    print(f'Adjusting hero level to {r_level}')
                    hero.level = r_level
            game.update_hero_timer()


def upgrade_functions(game):
    """
    Levels up hero if it's available or buys new skill if it's unlocked
    :param game: GameData class object
    """
    if game.level < 3 and game.ascensions == 0 and game.hero_index == 0:
        upgrade_first_levels(game.hero)
    else:
        if game.hero.skill_level < game.hero.max_skill_level or LEVEL_OVER_STEP < 100:
            img = rnd.get_screenshot()
        else:
            img = rnd.get_screenshot(CTRL=True)
        upgrade_normal(game, img)


def hero_leveling_logic(game):
    """
    Decides what action to do with the current hero
    :param game: GameData class object
    :return: None
    """
    if game.level_up_timer == 0:
        game.update_hero_timer()

    if not game.boss_timer:
        hero = game.hero
        if hero.level > hero.level_ceiling:
            # Should not be true under normal conditions
            while hero.level > hero.level_ceiling:
                hero.raise_level_ceiling()

        elif (hero.name == 'Cid, the Helpful Adventurer') & (hero.level_ceiling > 100):
            # If Cid is lvl 100 skip Cid, because leveling him beyond this is not useful due to low increase to dps
            game.next_hero()

        else:
            lvl_clg = hero.level_ceiling
            upgrade_functions(game)
            timer = game.get_hero_timer()
            if lvl_clg != hero.level_ceiling or timer > WAIT_TIME:
                game.next_hero()


def loop_basic_powers(game):
    """
    Loops through 1-7 powers excluding (Energize and Reload). Activates if power is ready.
    :param game: GameData class object
    """
    if game.unlocked_powers < 7:
        for idx in range(game.unlocked_powers):
            power = game.powers[idx]
            if power.ready():
                power.activate()
    else:
        for idx in range(7):
            power = game.powers[idx]
            if power.ready():
                power.activate()


def power_use_logic(game):
    """
    Decides what to do with powers, unlocks them if possible and uses them in correct order in boss zones.
    :param game: GameData class object
    """
    if not game.boss_timer and game.unlocked_powers < len(game.powers):
        power_unlocker(game)

    elif game.boss_timer:
        if 0 < game.unlocked_powers < 8:
            loop_basic_powers(game)

        elif game.unlocked_powers == 8:
            energize = game.powers[7]
            lucky_strike = game.powers[2]

            if energize.ready() and lucky_strike.ready():
                energize.activate()
                lucky_strike.activate()
            else:
                loop_basic_powers(game)

        elif game.unlocked_powers == len(game.powers):
            energize = game.powers[7]
            reload = game.powers[8]
            if energize.ready() and reload.ready():
                lucky_strike = game.powers[2]
                golden_clicks = game.powers[4]
                if lucky_strike.ready() and golden_clicks.ready():
                    lucky_strike.activate()
                    golden_clicks.activate()
                    energize.activate()
                    reload.activate()
                    lucky_strike.activate()
                    golden_clicks.activate()
            else:
                loop_basic_powers(game)


def power_unlocker(game):
    """
    Unlocks the powers
    :param game: GameData class object
    """
    for power in game.powers:
        if not power.unlocked:
            for hero in game.heroes:
                if hero.level < 25:
                    break
                elif power.hero == hero.name and power.skill <= hero.skill_level:
                    power.unlock()
                    game.unlocked_powers += 1
