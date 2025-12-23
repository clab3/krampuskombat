import os
import random

import pygame

import gamebox
from bomb import Bomb
from controlconfig import ControlConfig
from kombattant import Kombattant
from snowball import Snowball


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

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
    krampus_speed
)
player_1 = Kombattant(
    1,
    weapons,
    ControlConfig(
        pygame.K_d, pygame.K_a, pygame.K_w, pygame.K_s, pygame.K_q, pygame.K_e
    ),
    player_speed
)
player_2 = Kombattant(
    2, 
    weapons,
    ControlConfig(
        pygame.K_k, pygame.K_h, pygame.K_u, pygame.K_j, pygame.K_y, pygame.K_i
    ),
    player_speed
)
players = [krampus, player_1, player_2]
stars = []
counter = 0
game_on = False
stage = 1

moving1 = gamebox.from_color(200, 700, "black", 200, 15)
moving2 = gamebox.from_color(700, 600, "black", 200, 15)
moving3 = gamebox.from_color(400, 500, "black", 200, 15)
moving4 = gamebox.from_color(100, 400, "black", 200, 15)
moving5 = gamebox.from_color(900, 300, "black", 200, 15)
moving6 = gamebox.from_color(600, 200, "black", 200, 15)
moving7 = gamebox.from_color(800, 100, "black", 200, 15)
moving_platforms = [moving1, moving2, moving3, moving4, moving5, moving6, moving7]

game_age = 0 # frames
game_end_point = None

def reset_game():
    global players, weapons, game_on, game_age, game_end_point, snowballs, snowball_speed, snowball_interval
    for player in players:
        player.reset()
    weapons.clear()
    snowballs.clear()
    game_on = True
    game_end_point = None
    game_age = 0
    snowball_speed = 10
    snowball_interval = 300


def tick(keys):
    global counter, game_on, players, stage, game_age, game_end_point, weapons, snowballs, snowball_speed, snowball_interval
    if not game_on:
        counter += 1

        if counter % 5 == 0:
            numstars = random.randint(0, 7)
            for i in range(numstars):
                stars.append(gamebox.from_color(random.randint(5, 995), 0, "white", 3, 3))

        camera.clear("black")
        title = gamebox.from_text(500, 200, "KRAMPUS KOMBAT", "Arial", 100, "yellow", True, True)
        krampus_instructions = gamebox.from_text(500, 400, "Krampus: Use the arrow keys to move and right shift to attack", "Arial", 30, "green")
        player_1_instructions = gamebox.from_text(500, 500, "Player 2: Use W,A,S,D to move and Q or E to attack", "Arial", 30, "green")
        player_2_instructions = gamebox.from_text(500, 600, "Player 3: Use U,H,J,K to move and Y or I to attack", "Arial", 30, "green")
        start = gamebox.from_text(500, 700, "Press B to begin", "Arial", 40, "green", True)
        if pygame.K_b in keys:
            game_on = True
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

        camera.clear("cyan")
        floor = gamebox.from_color(500, 800, "black", 1200, 30)
        ceiling = gamebox.from_color(500, 0, "black", 1200, 30)
        left_wall = gamebox.from_color(0, 400, "black", 30, 1200)
        right_wall = gamebox.from_color(1000, 400, "black", 30, 1200)
        platforms = [floor, ceiling, left_wall, right_wall]
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
            player.display.xspeed = 0
            player.display.yspeed = 0

            # accept controls
            for key in keys:
                player.read_key(key)

            player.display.y += player.display.yspeed
            player.display.x += player.display.xspeed

        dead_snowballs = set()
        for snowball in snowballs:
            snowball.next_frame()
            # TODO: The players and snowballs should handle this themselves in next_frame()
            snowball.display.x += snowball.display.xspeed
            snowball.display.y += snowball.display.yspeed
            # snowballs aren't affected by anything, so we can draw them immediately
            camera.draw(snowball.display)

            if snowball.display.x <= 0:
                dead_snowballs.add(snowball)

        # this feels stupid but I can't change the size of snowballs during iteration
        for snowball in dead_snowballs:
            snowballs.remove(snowball)

        for weapon in weapons:
            weapon.next_frame()
            # draw weapons before players, if one gets triggered early that will happen on the next frame
            camera.draw(weapon.display)

        # If one bomb hits another, the second should explode immediately
        # NOTE: This could be made more efficient if performance becomes an issue
        for weapon1 in weapons:
            for weapon2 in weapons:
                if weapon1 == weapon2 or not (weapon1.is_activated or weapon2.is_activated) or (weapon1.is_activated and weapon2.is_activated):
                    continue
                # exactly 1 of the weapons is activated
                if weapon1.explosion_is_touching(weapon2.display):
                    weapon2.trigger_early()
                elif weapon2.explosion_is_touching(weapon1.display):
                    weapon1.trigger_early()

            if weapon1.is_activated:
                continue
            # snowballs also set off bombs
            for snowball in snowballs:
                if weapon1.display.touches(snowball.display):
                    weapon1.trigger_early()

        # move player back if it's overlapping with something
        # kill players touching active weapons or snowballs
        # randomize player order so that they can't push each other around
        random.shuffle(players)
        for player in players:
            # Players should not be able to run through each other
            for other_player in players:
                if other_player != player and other_player.display.touches(player.display):
                    player.display.move_to_stop_overlapping(other_player.display)

            # NOTE: This has to come after player-player interactions to prioritize not being pushed off the map
            for platform in platforms:
                if player.display.touches(platform):
                    player.display.move_to_stop_overlapping(platform)
                if player.display.bottom_touches(platform):
                    player.display.move_to_stop_overlapping(platform)

            # interact with weapons
            # TODO: Maybe players shouldn't be able to run through idle bombs... but what about when they are first laid?
            for weapon in weapons:
                if weapon.explosion_is_touching(player.display):
                    player.die()
            
            for snowball in snowballs:
                if snowball.display.touches(player.display):
                    player.die()

            camera.draw(player.display)

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
        if not non_krampus_alive:
            text_color = "red"
            camera.clear("black")
            wintext = gamebox.from_text(500, 400, "KRAMPUS WINS", "Arial", 80, text_color, True, True)
        else:
            text_color = "blue"
            camera.clear("white")
            wintext = gamebox.from_text(500, 400, "You killed Krampus! Christmas is saved!", "Arial", 50, text_color, True, True)
        camera.draw(wintext)
        restart = gamebox.from_text(500, 700, "Press B to play again", "Arial", 40, text_color, True)
        camera.draw(restart)
        if pygame.K_b in keys:
            reset_game()

    camera.display()

ticks_per_second = 30

# keep this line the last one in your program
gamebox.timer_loop(ticks_per_second, tick)
