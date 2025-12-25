import os

import gamebox
from spriteconfig import SpriteConfig

# TODO: This is copypasta from game.py and shouldn't be needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Loadout:
    def __init__(
            self,
            display_scale: float,
            idle_sprites_config: SpriteConfig,
            attack_sprites_config: SpriteConfig,
            # death_sprites_config: SpriteConfig,
    ):
        self.idle_sprites = gamebox.load_sprite_sheet(
            idle_sprites_config.sprite_file,
            idle_sprites_config.rows,
            idle_sprites_config.columns,
        )
        self.num_idle_sprites = idle_sprites_config.num_sprites

        self.attack_sprites = gamebox.load_sprite_sheet(
            attack_sprites_config.sprite_file,
            attack_sprites_config.rows,
            attack_sprites_config.columns,
        )
        self.num_attack_sprites = attack_sprites_config.num_sprites

        death_sprites_file = os.path.join(CURRENT_DIR, "images/egg_death_sprites.png")
        self.death_sprites = gamebox.load_sprite_sheet(
            death_sprites_file,
            1,
            12
        )
        self.num_death_sprites = 12

        self.display_scale = display_scale
