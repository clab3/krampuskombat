import os

import gamebox
import imagelib


# TODO: This is copypasta from game.py and shouldn't be needed
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

class Snowball:
    def __init__(self, x_pos: int, y_pos: int, xspeed: int, yspeed: int):
        sprites_dir = os.path.join(CURRENT_DIR, "images/snowball_sprites")
        self.sprites = imagelib.load_images_from_directory(sprites_dir)
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