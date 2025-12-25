import random

import pygame

import gamebox
from bomb import Bomb
from controlconfig import ControlConfig
from kombattant import Kombattant
from loadout import Loadout
from snowball import Snowball
from spriteconfig import SpriteConfig


pygame.mixer.init()
# this will only play the first time through, in the title screen
pygame.mixer.music.load("sounds/dark-tension.mp3")
pygame.mixer.music.play()  # non-blocking

camera = gamebox.Camera(1000, 800)
weapons: set[Bomb] = set()
snowballs: set[Snowball] = set()
# TODO: Make number of players variable
# TODO: Make player and krampus stats variable?
player_speed = 15
krampus_speed = 25
snowball_speed = 10
snowball_interval = 300
krampus = Kombattant(
    0,
    weapons,
    ControlConfig(
        pygame.K_RIGHT, pygame.K_LEFT, pygame.K_UP, pygame.K_DOWN, pygame.K_RSHIFT, pygame.K_LSHIFT
    ),
    Loadout(
        .4,
        SpriteConfig("images/krampus_idle_sprites.png", 2, 4, 8),
        SpriteConfig("images/krampus_attack_sprites.png", 1, 4, 3),
    ),
    krampus_speed,
    500,
    50,
)
player_1 = Kombattant(
    1,
    weapons,
    ControlConfig(
        pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_q, pygame.K_e
    ),
    Loadout(
        .15,
        SpriteConfig("images/egg.png", 1, 1, 1),
        SpriteConfig("images/egg.png", 1, 1, 1),
    ),
    player_speed,
    100,
    700,
)
player_2 = Kombattant(
    2, 
    weapons,
    ControlConfig(
        pygame.K_k, pygame.K_h, pygame.K_u, pygame.K_j, pygame.K_y, pygame.K_i
    ),
    Loadout(
        .15,
        SpriteConfig("images/egg_green.png", 1, 1, 1),
        SpriteConfig("images/egg_green.png", 1, 1, 1),
    ),
    player_speed,
    900,
    700,
)
players = [krampus, player_1, player_2]
stars = []
counter = 0
game_on = False
stage = 1

blocks: list[gamebox.SpriteBox] = []

game_age = 0 # frames
game_end_point = None

def restart_game():
    global blocks, players, weapons, game_on, game_age, game_end_point, snowballs, snowball_speed, snowball_interval
    for player in players:
        player.reset()
    weapons.clear()
    snowballs.clear()
    game_on = True
    game_end_point = None
    game_age = 0
    snowball_speed = 10
    snowball_interval = 300
    blocks = []
    for x in [150, 325, 500, 675, 850]:
        for y in [100, 250, 400, 550, 700]:
            new_block = gamebox.from_image(x, y, "images/box.png")
            new_block.width = 40
            new_block.height = 40
            blocks.append(new_block)

    pygame.mixer.music.load("sounds/combat-epic.mp3")
    pygame.mixer.music.play()


def tick(keys):
    global counter, game_on, players, stage, game_age, game_end_point, weapons, snowballs, snowball_speed, snowball_interval
    if not game_on:
        counter += 1

        if counter % 5 == 0:
            num_stars = random.randint(0, 7)
            for i in range(num_stars):
                stars.append(gamebox.from_color(random.randint(5, 995), 0, "white", 3, 3))

        camera.clear("black")
        title = gamebox.from_text(500, 200, "KRAMPUS KOMBAT", "Arial", 100, "yellow", True, True)
        krampus_instructions = gamebox.from_text(500, 400, "Krampus: Use the arrow keys to move and right shift to attack", "Arial", 30, "green")
        player_1_instructions = gamebox.from_text(500, 500, "Player 2: Use W,A,S,D to move and Q or E to attack", "Arial", 30, "green")
        player_2_instructions = gamebox.from_text(500, 600, "Player 3: Use U,H,J,K to move and Y or I to attack", "Arial", 30, "green")
        start = gamebox.from_text(500, 700, "Press B to begin", "Arial", 40, "green", True)
        if pygame.K_b in keys:
            restart_game()
        for star in stars:
            # move the star
            star.y += 6
            if star.y > 800:
                stars.remove(star)
            # draw the star
            camera.draw(star)
            camera.draw(title)
            camera.draw(krampus_instructions)
            camera.draw(player_1_instructions)
            camera.draw(player_2_instructions)
            camera.draw(start)
    elif game_on and (not game_end_point or game_age < game_end_point):
        game_age += 1

        camera.clear("gray")
        floor = gamebox.from_color(500, 800, "black", 1200, 30)
        ceiling = gamebox.from_color(500, 0, "black", 1200, 30)
        left_wall = gamebox.from_color(0, 400, "black", 30, 1200)
        right_wall = gamebox.from_color(1000, 400, "black", 30, 1200)
        platforms = [floor, ceiling, left_wall, right_wall]
        platforms.extend(blocks)
        presents_stolen = game_age // 10
        clock_text = gamebox.from_text(850, 50, f"Presents stolen: {presents_stolen}", "Arial", 24, "Black")
        camera.draw(clock_text)

        for platform in platforms:
            camera.draw(platform)

        # Generate snowballs once things go on long enough
        if game_age >= 300:
            if game_age % snowball_interval == 0:
                y_pos = random.randint(10, 790)
                snowballs.add(Snowball(1000, y_pos, -snowball_speed, 0))
            if game_age % 5000 == 0:
                snowball_speed += 3
                snowball_interval = int(snowball_interval * .8)

        # ALL STAGES
        # advance frames of every object
        for player in players:
            player.next_frame()

            # first assume we are not moving
            player.sprite_box.xspeed = 0
            player.sprite_box.yspeed = 0

            # accept controls
            for key in keys:
                player.read_key(key)

            player.sprite_box.y += player.sprite_box.yspeed
            player.sprite_box.x += player.sprite_box.xspeed

        dead_snowballs = set()
        for snowball in snowballs:
            snowball.next_frame()
            # TODO: The players and snowballs should handle this themselves in next_frame()
            snowball.sprite_box.x += snowball.sprite_box.xspeed
            snowball.sprite_box.y += snowball.sprite_box.yspeed

            # draw snowballs first
            camera.draw(snowball.sprite_box)

            # things that can destroy the snowball
            if snowball.sprite_box.x <= 0:
                dead_snowballs.add(snowball)

            # TODO: We loop through every group of items multiple times
            # it would be better to loop through ALL sprites, and just have custom touches impls
            # which known what to do to each of the items based on what types they are
            # TODO TODO TODO this is a big one
            if snowball in dead_snowballs:
                continue

            for block in blocks:
                if snowball.sprite_box.touches(block):
                    dead_snowballs.add(snowball)
                    break

            if snowball in dead_snowballs:
                continue

            for weapon in weapons:
                if snowball.sprite_box.touches(weapon.sprite_box):
                    dead_snowballs.add(snowball)
                    break

            if snowball in dead_snowballs:
                continue

            for player in players:
                if snowball.sprite_box.touches(player.sprite_box):
                    dead_snowballs.add(snowball)
                    break

        for weapon in weapons:
            weapon.next_frame()
            # draw weapons before players, if one gets triggered early that will happen on the next frame
            camera.draw(weapon.sprite_box)

        # If one bomb hits another, the second should explode immediately
        # NOTE: This could be made more efficient if performance becomes an issue
        for weapon1 in weapons:
            for weapon2 in weapons:
                if weapon1 == weapon2 or not (weapon1.is_activated or weapon2.is_activated) or (weapon1.is_activated and weapon2.is_activated):
                    continue
                # exactly 1 of the weapons is activated
                if weapon1.explosion_is_touching(weapon2.sprite_box):
                    weapon2.trigger_early()
                elif weapon2.explosion_is_touching(weapon1.sprite_box):
                    weapon1.trigger_early()

            # blocks can be destroyed by explosions
            if weapon1.is_activated:
                blocks_to_destroy = []
                for block in blocks:
                    if weapon1.explosion_is_touching(block):
                        blocks_to_destroy.append(block)
                for block in blocks_to_destroy:
                    blocks.remove(block)
                    platforms.remove(block)
                continue

            # snowballs also set off bombs
            for snowball in snowballs:
                if weapon1.sprite_box.touches(snowball.sprite_box):
                    weapon1.trigger_early()

        # move player back if it's overlapping with something
        # kill players touching active weapons or snowballs
        # randomize player order so that they can't push each other around
        random.shuffle(players)
        for player in players:
            # Players should not be able to run through each other
            for other_player in players:
                if other_player != player and other_player.sprite_box.touches(player.sprite_box):
                    player.sprite_box.move_to_stop_overlapping(other_player.sprite_box)

            # NOTE: This has to come after player-player interactions to prioritize not being pushed off the map
            for platform in platforms:
                if player.sprite_box.touches(platform):
                    player.sprite_box.move_to_stop_overlapping(platform)
                if player.sprite_box.bottom_touches(platform):
                    player.sprite_box.move_to_stop_overlapping(platform)

            # interact with weapons
            # TODO: Maybe players shouldn't be able to run through idle bombs... but what about when they are first laid?
            for weapon in weapons:
                if weapon.explosion_is_touching(player.sprite_box):
                    player.die()
            
            for snowball in snowballs:
                if snowball.sprite_box.touches(player.sprite_box):
                    player.die()

            camera.draw(player.sprite_box)

        #### cleanup ####
        for snowball in dead_snowballs:
            snowballs.remove(snowball)

        # Check if the game_end_point should be scheduled
        if not game_end_point:
            non_krampus_alive = False
            krampus_alive = False
            for player in players:
                if player.is_krampus and not player.is_dead:
                    krampus_alive = True
                elif not player.is_krampus and not player.is_dead:
                    non_krampus_alive = True
            if not non_krampus_alive or not krampus_alive:
                game_end_point = game_age + 50
                if non_krampus_alive:
                    # NOTE: if a non-Krampus player kills themselves at the last second (after Krampus already died),
                    # they will lose, but this song will still play
                    pygame.mixer.music.load("sounds/funny-dancing-kids.mp3")
                else:
                    pygame.mixer.music.load("sounds/valhalla-awaits.mp3")  # krampus
                pygame.mixer.music.play()  # non-blocking

    # TODO: what if everyone dies at the same time? Right now Krampus would win
    else:  # game_age >= game_end_point
        # check who won, ties go to Krampus
        # TODO: Put this in a fn, it's repeated code
        non_krampus_alive = False
        krampus_alive = False
        for player in players:
            if player.is_krampus and not player.is_dead:
                krampus_alive = True
            elif not player.is_krampus and not player.is_dead:
                non_krampus_alive = True
        presents_stolen = game_age // 10
        if not non_krampus_alive:
            text_color = "red"
            camera.clear("black")
            win_text = gamebox.from_text(
                500, 400, "KRAMPUS WINS", "Arial", 80, text_color, True, True
            )
            score_string = f"Krampus already stole {presents_stolen} presents, and soon they'll all be his!"
        else:
            text_color = "blue"
            camera.clear("white")
            win_string = "You killed Krampus! Christmas is saved!"
            win_text = gamebox.from_text(
                500, 400, win_string, "Arial", 50, text_color, True, True
            )
            score_string = f"But he did steal {presents_stolen} presents..."

        score_text = gamebox.from_text(
            500, 500, score_string, "Arial", 25, text_color, True
        )
        camera.draw(win_text)
        camera.draw(score_text)
        restart = gamebox.from_text(500, 600, "Press B to play again", "Arial", 40, text_color, True)
        camera.draw(restart)
        if pygame.K_b in keys:
            restart_game()

    camera.display()

ticks_per_second = 30

# keep this line the last one in your program
gamebox.timer_loop(ticks_per_second, tick)
