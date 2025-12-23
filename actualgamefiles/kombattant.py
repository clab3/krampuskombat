import logging
import os

import gamebox

from bomb import Bomb
from controlconfig import ControlConfig

# TODO: This is copypasta from game.py and shouldn't be needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Kombattant:
    bomb_life = 72  # frames

    """Player 0 is Krampus."""

    def __init__(self, player_number: int, all_weapons: set, control_config: ControlConfig, speed: int):
        self.speed = speed
        self.is_krampus = player_number == 0
        self.is_dead = False
        self.current_weapon = None
        self.all_weapons = all_weapons
        self.player_number = player_number
        if player_number == 0:
            idle_sprites_file = os.path.join(CURRENT_DIR, "images/krampus_idle_sprites.png")
            self.idle_sprites = gamebox.load_sprite_sheet(
                idle_sprites_file,
                2,
                4
            )
            attack_sprites_file = os.path.join(CURRENT_DIR, "images/krampus_attack_sprites.png")
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
            sprites_file = os.path.join(CURRENT_DIR,
                                        "images/egg.png") if player_number == 1 else os.path.join(CURRENT_DIR,
                                                                                                  "images/egg_green.png")
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
        death_sprites_file = os.path.join(CURRENT_DIR, "images/egg_death_sprites.png")
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
        elif (self.is_idle and self.frame >= self.num_idle_sprites) or (
                not self.is_idle and self.frame >= self.num_attack_sprites):
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
