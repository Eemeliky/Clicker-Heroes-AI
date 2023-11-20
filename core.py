import config as cf
import utilities as util
import renderer as rnd
import time
import pyautogui


def upgrade_first_levels(game):
    """
    Upgrades first 2 levels when template matching doesn't work, because achievements block the hero name.
    :param game: GameData class object
    """
    hero = game.hero
    img = rnd.get_screenshot()

    if (hero.level == 3) & hero.level_ceiling == (cf.LEVEL_GUIDE[0]):
        hero.level_up()
    elif (hero.name == 'Cid, the Helpful Adventurer') & (hero.level < 3):
        if img[235, cf.LEVEL_UP_X, 2] == 255:
            util.click_on_point(cf.LEVEL_UP_X, 235)
            hero.level_up()


def improve_hero(game):
    """
    Levels up hero if it's available or buys new skill if it's unlocked
    :param game: GameData class object
    """
    if game.level < 5:
        upgrade_first_levels(game)
    else:
        hero = game.hero
        img = rnd.get_screenshot()
        x, y = game.hero_name_xy
        if hero.skill_unlocked():
            y = y + 45  # 45px is offset from the top of the hero name to the upgrade button
            pixel_val = [img[y, 197 + (cf.SKILL_OFFSET * hero.skill_level), i] for i in range(3)]
            if min(pixel_val) > 50:
                util.click_on_point(cf.SKILL_X_COORDINATE + (cf.SKILL_OFFSET * hero.skill_level), y)
                hero.level_skill()
        elif img[y, cf.LEVEL_UP_X, 2] > 200:
            util.click_on_point(cf.LEVEL_UP_X, game.hero_y)
            hero.level_up()


def hero_level_up_logic(game):
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

        elif (hero.name == 'Cid, the Helpful Adventurer') & (hero.level > 99):
            # If Cid is lvl 100 skip Cid, because leveling him beyond this is not useful due low increases to he's dps
            game.next_hero()

        else:
            lvl_clg = hero.level_ceiling
            improve_hero(game)

            if lvl_clg != hero.level_ceiling:
                if game.hero_index > 24 and hero.level < 425:
                    # after 'Frostleaf' the price for new hero raises considerably
                    # -> that we have to wait for current best hero to be lvl +400 to buy new hero
                    game.reset_hero_queue()
                else:
                    game.next_hero()


# TODO: ALL FUNCTIONS UNDER
def power_unlocker(game, hero, powers):
    if game.unlocked_powers >= (len(powers) - 1):
        return
    if hero.name in POWER_UNLOCK:
        if (hero.level == POWER_UNLOCK[hero.name][0]) & (hero.skill_level == POWER_UNLOCK[hero.name][1]):
            power = powers[POWER_UNLOCK[hero.name][2]]
            if not power.unlocked:
                power.unlock()
                game.unlock_power()


def power_usage(game, powers):
    if game.unlocked_powers > 0:
        if not game.grind_mode:
            for power in powers:
                if power.unlocked:
                    if (time.time() - power.cd_timer) > power.cooldown:
                        power.activate()


def ascend_logic(game, heroes, powers):
    if game.asc_available:
        if (game.level > 1000) & (game.ascensions < 1):
            print("ASCEND AT", game.level)
            print()
            print()
            game.ascend()
            for hero in heroes:
                hero.reset()
            for power in powers:
                power.reset()
            pyautogui.moveTo(cf.AC_POINT)




