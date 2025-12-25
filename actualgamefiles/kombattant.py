import logging
import os

from bomb import Bomb
from controlconfig import ControlConfig
import gamebox
from loadout import Loadout

# TODO: This is copypasta from game.py and shouldn't be needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Kombattant:
    bomb_life = 72  # frames

    """Player 0 is Krampus."""

    def __init__(
            self,
            player_number: int,
            all_weapons: set,
            control_config: ControlConfig,
            loadout: Loadout,
            speed: int,
            x_origin: int,
            y_origin: int,
    ):
        self.speed = speed
        self.origin_x_pos = x_origin
        self.origin_y_pos = y_origin
        self.is_krampus = player_number == 0
        self.is_dead = False
        self.current_weapon = None
        self.all_weapons = all_weapons
        self.player_number = player_number
        self.loadout = loadout
        self.is_idle = True
        self.frame = 0
        self.sprite_box = gamebox.from_image(self.origin_x_pos, self.origin_y_pos, self.loadout.idle_sprites[self.frame])
        self.sprite_box.scale_by(self.loadout.display_scale)
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
            if self.frame >= self.loadout.num_death_sprites:
                adjusted_frame = self.loadout.num_death_sprites - 1
        elif (self.is_idle and self.frame >= self.loadout.num_idle_sprites) or (
                not self.is_idle and self.frame >= self.loadout.num_attack_sprites):
            self.frame = 0
            adjusted_frame = self.frame
        else:
            # yucky
            adjusted_frame = self.frame
        if self.is_dead:
            sprites = self.loadout.death_sprites
        elif self.is_idle:
            sprites = self.loadout.idle_sprites
        else:
            sprites = self.loadout.attack_sprites
        self.sprite_box.image = sprites[adjusted_frame]

    def read_key(self, key):
        # can't do anything if you're dead
        if self.is_dead:
            return
        if key == self.control_config.right:
            self.sprite_box.xspeed = self.speed
        if key == self.control_config.left:
            self.sprite_box.xspeed = -self.speed
        if key == self.control_config.up:
            self.sprite_box.yspeed = -self.speed
        if key == self.control_config.down:
            self.sprite_box.yspeed = self.speed
        if key in {self.control_config.special_1, self.control_config.special_2}:
            self._attack()

    def _attack(self) -> None:
        if self.current_weapon:
            logging.info(f'Player #{self.player_number} blocked from dropping bomb bc it has already deployed 1')
            return
        # Krampus bombs have blue fire
        self.current_weapon = Bomb(self.sprite_box.x, self.sprite_box.y, self.bomb_life, is_blue=self.is_krampus)
        self.current_weapon_life = self.bomb_life
        self.all_weapons.add(self.current_weapon)

    def die(self) -> None:
        self.sprite_box.xspeed = 0
        self.sprite_box.yspeed = 0
        self.is_dead = True
        self.frame = 0

    def reset(self) -> None:
        self.is_dead = False
        self.sprite_box.x = self.origin_x_pos
        self.sprite_box.y = self.origin_y_pos
        self.current_weapon = None
        self.is_idle = True
        self.frame = 0
