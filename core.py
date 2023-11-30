import config as cf
import utilities as util
import renderer as rnd
import time
from detectors import find_gilded


def upgrade_first_levels(game):
    """
    Upgrades first 2 levels when template matching doesn't work, because achievements block the hero name.
    :param game: GameData class object
    """
    hero = game.hero
    img = rnd.get_screenshot()
    if img[235, cf.LEVEL_UP_X, 2] > 250:
        hero.name_pos = (149, 190)
        hero.level_up()


def improve_hero(game):
    """
    Levels up hero if it's available or buys new skill if it's unlocked
    :param game: GameData class object
    """
    if game.level < 3:
        upgrade_first_levels(game)
    else:
        hero = game.hero
        img = rnd.get_screenshot()
        x, y = hero.name_pos
        y = y + 45  # 45px is offset from the top of the hero name to the upgrade button
        if hero.skill_unlocked():
            pixel_val = [img[y, 197 + (cf.SKILL_OFFSET * hero.skill_level), i] for i in range(3)]
            if max(pixel_val) > 50:
                hero.level_skill()
        elif img[y, cf.LEVEL_UP_X, 2] > 200:
            hero.level_up()


def hero_leveling_logic(game):
    """
    Decides what action to do with the current hero
    :param game: GameData class object
    :return:
    """
    hero = game.hero
    if not game.boss_timer:
        if hero.level > hero.level_ceiling:
            # Should not be true under normal conditions
            while hero.level > hero.level_ceiling:
                hero.raise_level_ceiling()

        elif (hero.name == 'Cid, the Helpful Adventurer') & (hero.level_ceiling > 110):
            # If Cid is lvl 100 skip Cid, because leveling him beyond this is not useful due low increases to he's dps
            game.next_hero()

        else:
            lvl_clg = hero.level_ceiling
            improve_hero(game)

            if lvl_clg != hero.level_ceiling:
                if lvl_clg == cf.LEVEL_GUIDE[0]:
                    game.reset_hero_queue()
                elif game.hero_index > 24 and hero.level < 425:
                    # after 'Frostleaf' the price for new hero raises considerably
                    # -> that we have to wait for current best hero to be lvl +400 to buy new hero
                    game.reset_hero_queue()
                else:
                    game.next_hero()


def loop_basic_powers(game):
    """
    Loops through 1-7 powers excluding (Energize and Reload). Activates if power is ready.
    :param game: GameData class object
    """
    if game.unlocked_powers < 7:
        for idx in range(game.unlocked_powers):
            power = game.powers[idx]
            if not power.on_cooldown():
                power.activate()
    else:
        for idx in range(7):
            power = game.powers[idx]
            if not power.on_cooldown():
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
            if not energize.on_cooldown() and not lucky_strike.on_cooldown():
                energize.activate()
                lucky_strike.activate()
            else:
                loop_basic_powers(game)
        elif game.unlocked_powers == len(game.powers):
            energize = game.powers[7]
            reload = game.powers[8]
            if not energize.on_cooldown() and not reload.on_cooldown():
                lucky_strike = game.powers[2]
                golden_clicks = game.powers[4]
                if not lucky_strike.on_cooldown() and not golden_clicks.on_cooldown():
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
