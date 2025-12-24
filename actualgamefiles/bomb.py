import os

import pygame

import gamebox

# TODO: This is copypasta from game.py and shouldn't be needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Bomb:
    def __init__(self, x_pos: int, y_pos: int, lifetime: int):
        self.exploding = False
        explode_sprites_file = os.path.join(CURRENT_DIR, "images/red_explosion_big.png")
        self.explode_sprites = gamebox.load_sprite_sheet(explode_sprites_file, 1, 1)
        # NOTE: This will not quite make sense if I animate the explosion
        explosion_surface = pygame.image.load(explode_sprites_file).convert_alpha()
        self.explosion_scale = 24
        explosion_surface = pygame.transform.scale_by(explosion_surface, self.explosion_scale)
        self.explosion_mask = pygame.mask.from_surface(explosion_surface)

        idle_sprites_file = os.path.join(CURRENT_DIR, "images/bomb_sprites.png")
        self.idle_sprites = gamebox.load_sprite_sheet(idle_sprites_file, 1, 18)
        self.frame = 0
        self.sprite_box = gamebox.from_image(x_pos, y_pos, self.idle_sprites[self.frame])
        self.sprite_box.scale_by(1)
        self.age = 0
        self.lifetime = lifetime
        self.explosion_sound = pygame.mixer.Sound("sounds/explosion.mp3")
        self.triggered_early = False

    def trigger_early(self) -> None:
        self.triggered_early = True

    def next_frame(self) -> None:
        self.age += 1

        # trigger explosion
        if not self.exploding and (self.triggered_early or self.age > self.lifetime * .75):
            self.exploding = True
            self.sprite_box.scale_by(
                self.explosion_scale)  # NOTE: this is not the most robust way to fix this but works for now
            self.explosion_sound.play()

        self.frame += 1
        if (self.exploding and self.frame >= 1) or (not self.exploding and self.frame >= 18):
            self.frame = 0
        self.sprite_box.image = self.explode_sprites[self.frame] if self.exploding else self.idle_sprites[self.frame]

    @property
    def is_activated(self) -> bool:
        return self.exploding

    def explosion_is_touching(self, other_display: gamebox.SpriteBox) -> bool:
        if not self.exploding:
            return False

        # this pixel by pixel strategy is not working
        # offset_x = int(other_display.x - self.sprite_box.x)
        # offset_y = int(other_display.y - self.sprite_box.y)

        # # check for non-transparent pixel overlap
        # # NOTE: This WILL count overlaps with the transparent parts of other_display
        # other_mask = pygame.mask.Mask((other_display.width, other_display.height), True)
        # return self.explosion_mask.overlap_area(other_mask, (offset_x, offset_y)) > 0

        if not self.sprite_box.touches(other_display):
            return False

        # this should work bc the explosion is cross shaped
        padding = 30
        return abs(self.sprite_box.x - other_display.x) <= padding or abs(self.sprite_box.y - other_display.y) <= padding
