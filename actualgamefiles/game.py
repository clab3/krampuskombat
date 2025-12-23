import logging
import os

import pygame
import gamebox
import random


CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))


def load_images_from_directory(directory: str) -> list[str]:
    """Returns a list of image file paths."""
    images = []
    for filename in sorted(os.listdir(directory)):
        if filename.endswith(".png"):
            full_path = os.path.join(directory, filename)
            images.append(full_path)
    return images


class Snowball:
    def __init__(self, x_pos: int, y_pos: int, xspeed: int, yspeed: int):
        sprites_dir = os.path.join(CURRENT_DIR, "snowball_sprites")
        self.sprites = load_images_from_directory(sprites_dir)
        self.frame = 0
        self.display = gamebox.from_image(x_pos, y_pos, self.sprites[self.frame])
        self.display.scale_by(2)
        self.display.xspeed = xspeed
        self.display.yspeed = yspeed

    def next_frame(self) -> None:
        self.frame += 1
        if self.frame >= 12:
            self.frame = 0
        self.display.image = self.sprites[self.frame]
        

class Bomb:
    def __init__(self, x_pos: int, y_pos: int, lifetime: int):
        self.exploding = False
        explode_sprites_file = os.path.join(CURRENT_DIR, "red_explosion_big.png")
        self.explode_sprites = gamebox.load_sprite_sheet(explode_sprites_file, 1, 1)
        # NOTE: This will not quite make sense if I animate the explosion
        explosion_surface = pygame.image.load(explode_sprites_file).convert_alpha()
        self.explosion_scale = 24
        explosion_surface = pygame.transform.scale_by(explosion_surface, self.explosion_scale)
        self.explosion_mask = pygame.mask.from_surface(explosion_surface)

        idle_sprites_file = os.path.join(CURRENT_DIR, "bomb_sprites.png")
        self.idle_sprites = gamebox.load_sprite_sheet(idle_sprites_file, 1, 18)
        self.frame = 0
        self.display = gamebox.from_image(x_pos, y_pos, self.idle_sprites[self.frame])
        self.display.scale_by(1)
        self.age = 0
        self.lifetime = lifetime
        self.triggered_early = False

    def trigger_early(self) -> None:
        self.triggered_early = True

    def next_frame(self) -> None:
        self.age += 1
        if not self.exploding and (self.triggered_early or self.age > self.lifetime * .75):
            self.exploding = True
            self.display.scale_by(self.explosion_scale)  # NOTE: this is not the most robust way to fix this but works for now
        self.frame += 1
        if (self.exploding and self.frame >= 1) or (not self.exploding and self.frame >= 18) :
            self.frame = 0
        self.display.image = self.explode_sprites[self.frame] if self.exploding else self.idle_sprites[self.frame]

    @property
    def is_activated(self) -> bool:
        return self.exploding
    
    def explosion_is_touching(self, other_display: gamebox.SpriteBox) -> bool:
        if not self.exploding:
            return False
        
        # this pixel by pixel strategy is not working
        # offset_x = int(other_display.x - self.display.x)
        # offset_y = int(other_display.y - self.display.y)

        # # check for non-transparent pixel overlap
        # # NOTE: This WILL count overlaps with the transparent parts of other_display
        # other_mask = pygame.mask.Mask((other_display.width, other_display.height), True)
        # return self.explosion_mask.overlap_area(other_mask, (offset_x, offset_y)) > 0

        if not self.display.touches(other_display):
            return False
        
        # this should work bc the explosion is cross shaped
        padding = 30
        return abs(self.display.x - other_display.x) <= padding or abs(self.display.y - other_display.y) <= padding
        
    

class ControlConfig:
    def __init__(self, right, left, up, down, special_1, special_2):
        self.right = right
        self.left = left
        self.up = up
        self.down = down
        self.special_1 = special_1
        self.special_2 = special_2


class Kombattant:
    bomb_life = 72 # frames

    """Player 0 is Krampus."""
    def __init__(self, player_number: int, all_weapons: set, control_config: ControlConfig, speed: int):
        self.speed = speed
        self.is_krampus = player_number == 0
        self.is_dead = False
        self.current_weapon = None
        self.all_weapons = all_weapons
        self.player_number = player_number
        if player_number == 0:
            idle_sprites_file = os.path.join(CURRENT_DIR, "krampus_idle_sprites.png")
            self.idle_sprites = gamebox.load_sprite_sheet(
               idle_sprites_file,
                2,
                4
            )
            attack_sprites_file = os.path.join(CURRENT_DIR, "krampus_attack_sprites.png")
            self.attack_sprites = gamebox.load_sprite_sheet(
                attack_sprites_file,
                1,
                4
            )
            self.num_idle_sprites = 8
            self.num_attack_sprites = 4
            self.origin_x_pos = 500
            self.origin_y_pos = 50
            display_scale = .4
        else:
            sprites_file = os.path.join(CURRENT_DIR, "egg.png") if player_number == 1 else os.path.join(CURRENT_DIR, "egg_green.png")
            self.idle_sprites = gamebox.load_sprite_sheet(
                sprites_file, 1, 1
            )
            self.attack_sprites = self.idle_sprites
            self.num_attack_sprites = 1
            self.num_idle_sprites = 1
            self.origin_y_pos = 700
            if player_number == 1:
                self.origin_x_pos = 100
            else:
                self.origin_x_pos = 900
            display_scale = .15
        
        self.is_idle = True
        death_sprites_file = os.path.join(CURRENT_DIR, "egg_death_sprites.png")
        self.death_sprites = gamebox.load_sprite_sheet(
            death_sprites_file,
            1,
            12
        )
        self.num_death_sprites = 12
        self.frame = 0
        self.display = gamebox.from_image(self.origin_x_pos, self.origin_y_pos, self.idle_sprites[self.frame])
        self.display.scale_by(display_scale)
        self.current_weapon_life = 0
        self.control_config = control_config
    
    def next_frame(self) -> None:
        if self.current_weapon:
            self.current_weapon_life -= 1
            if self.current_weapon_life <= 0:
                self.all_weapons.remove(self.current_weapon)
                self.current_weapon = None

        self.frame += 1
        if self.current_weapon:
            self.is_idle = False
        else:
            self.is_idle = True
        if self.is_dead:
            # hack to slow down animation
            adjusted_frame = self.frame // 4
            if self.frame >= self.num_death_sprites:
                adjusted_frame = self.num_death_sprites - 1
        elif (self.is_idle and self.frame >= self.num_idle_sprites) or (not self.is_idle and self.frame >= self.num_attack_sprites):
            self.frame = 0
            adjusted_frame = self.frame
        else:
            # yucky
            adjusted_frame = self.frame
        if self.is_dead:
            sprites = self.death_sprites
        elif self.is_idle:
            sprites = self.idle_sprites
        else:
            sprites = self.attack_sprites
        self.display.image = sprites[adjusted_frame]

    def read_key(self, key):
        # can't do anything if you're dead
        if self.is_dead:
            return
        if key == self.control_config.right:
            self.display.xspeed = self.speed
        if key == self.control_config.left:
            self.display.xspeed = -self.speed
        if key == self.control_config.up:
            self.display.yspeed = -self.speed
        if key == self.control_config.down:
            self.display.yspeed = self.speed
        if key in {self.control_config.special_1, self.control_config.special_2}:
            self._attack()

    def _attack(self) -> None:
        if self.current_weapon:
            logging.info(f'Player #{self.player_number} blocked from dropping bomb bc it has already deployed 1')
            return
        self.current_weapon = Bomb(self.display.x, self.display.y, self.bomb_life)
        self.current_weapon_life = self.bomb_life
        self.all_weapons.add(self.current_weapon)

    def die(self) -> None:
        self.display.xspeed = 0
        self.display.yspeed = 0
        self.is_dead = True
        self.frame = 0
    
    def reset(self) -> None:
        self.is_dead = False
        self.display.x = self.origin_x_pos
        self.display.y = self.origin_y_pos
        self.current_weapon = None
        self.is_idle = True
        self.frame = 0




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
