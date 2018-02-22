"""
CREDITS:

Inspired from the tutorial at:
https://www.youtube.com/watch?v=uWvb3QzA48c&list=PLsk-HSGFjnaG-BwZkuAOcVwWldfCLu1pq
Which is on the YT channel of KidsCanCode

Art from Kenney.nl

"A Journey Awaits" by Pierre Bondoerffer (@pbondoer)

"Fast Fight/battle music by Ville Nousiainen / Xythe / mutkanto at:
http://soundcloud.com/mutkanto
"""


# Creativity game
import sys
import os
import pygame as pg
import random
from settings import *
from sprites import *
from os import path

class Game:
    def __init__(self):
        """
        Initialize game window, etc
        """
        pg.init()
        pg.mixer.init()
        self.screen = pg.display.set_mode((WIDTH, HEIGHT))
        pg.display.set_caption('My Game')
        self.clock = pg.time.Clock()
        self.running = True
        self.all_sprites = None
        self.playing = False
        self.font_name = pg.font.match_font(FONT_NAME)
        self.load_data()

    def load_data(self):
        # load high score
        self.dir = path.dirname(__file__)
        img_dir = path.join(self.dir, 'img')
        with open(path.join(self.dir, HS_FILE), 'w') as f:
            try:
                self.highscore = int(f.read())
            except:
                self.highscore = 0
        # load spritesheet image
        self.spritesheet = Spritesheet(path.join(img_dir, SPRITESHEET))
        # load sounds
        self.snd_dir = path.join(self.dir, 'snd')
        self.jump_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump33.wav'))
        self.boost_sound = pg.mixer.Sound(path.join(self.snd_dir, 'Jump33.wav'))  # You can change this sound

    def new(self):
        # start a new game
        self.score = 0
        # This special goups allow you to specify the order you want the sprites drawn in
        self.all_sprites = pg.sprite.LayeredUpdates()
        self.platforms = pg.sprite.Group()
        self.powerups = pg.sprite.Group()
        self.mobs = pg.sprite.Group()
        # player
        self.player = Player(self)
        # platform
        for plat in PLATFORM_LIST:
            Platform(self, *plat)
        self.mob_timer = 0
        pg.mixer.music.load(path.join(self.snd_dir, 'fight.ogg'))
        self.run()

    def run(self):
        # Game Loop
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.1)
        self.playing = True
        while self.playing:
            self.clock.tick(FPS)
            self.events()
            self.update()
            self.draw()
        pg.mixer.music.fadeout(500)

    def update(self):
        # Game Loop - Update
        self.all_sprites.update()
        # check if player hits a platform - only if falling

        # spawn a mob?
        now = pg.time.get_ticks()
        if now - self.mob_timer > 5000 + random.choice([-1000, -500, 0, 500, 1000]):
            self.mob_timer = now
            Mob(self)
        # hit mobs?
        mob_hits = pg.sprite.spritecollide(self.player, self.mobs, False)
        if mob_hits:
            self.playing = False

        if self.player.vel.y > 0:
            hits = pg.sprite.spritecollide(self.player,
                                           self.platforms,
                                           dokill=False)
            if hits:
                # to make sure the lowest platforms is always the lower one
                # cause if their is multiples hits they are set in random order
                lowest = hits[0]
                for hit in hits:
                    if hit.rect.bottom > lowest.rect.bottom:
                        lowest = hit
                # what puts us on the plateform:
                if self.player.pos.x < lowest.rect.right + 10 and \
                   self.player.pos.x > lowest.rect.left - 10:
                    if self.player.pos.y < lowest.rect.centery:
                        self.player.pos.y = lowest.rect.top + 1
                        self.player.vel.y = 0
                        self.player.jumping = False


        # if player reaches top 1/4 of screen
        if self.player.rect.top <= HEIGHT / 4:
            self.player.pos.y += max(abs(self.player.vel.y), 2)
            # scrolling the mobs down (so they seem to stay at the same place
            # when the player is moving up)
            for mob in self.mobs:
                mob.rect.y += max(abs(self.player.vel.y), 2)
            # scrolling the platforms down
            for plat in self.platforms:
                plat.rect.y += max(abs(self.player.vel.y), 2)
                if plat.rect.top >= HEIGHT:
                    plat.kill() # clear the platform so that they don't accumulate
                    self.score += 10

        # if player hits powerup
        pow_hits = pg.sprite.spritecollide(self.player, self.powerups, True)
        for pow in pow_hits:
            if pow.type == 'boost':
                self.boost_sound.play()
                self.player.vel.y = - BOOST_POWER
                self.player.jumping = False

        # Die !
        if self.player.rect.bottom > HEIGHT:
            for sprite in self.all_sprites:
                sprite.rect.y -= max(self.player.vel.y, 10)
                if sprite.rect.bottom < 0:
                    sprite.kill()
        if len(self.platforms) == 0:
            self.playing = False

        # spawn new platforms to keep same average number
        while len(self.platforms) < 6:
            width = random.randrange(50, 100)
            Platform(self, random.randrange(0, WIDTH-width),
                     random.randrange(-75, -30))

    def events(self):
        # Game Loop - events
        for event in pg.event.get():
            # check for closing window
            if event.type == pg.QUIT:
                if self.playing:
                    self.playing = False
                    self.running = False
            if event.type == pg.KEYDOWN:
                if event.key == pg.K_SPACE:
                    self.player.jump()
            if event.type == pg.KEYUP:
                if event.key == pg.K_SPACE:
                    self.player.jump_cut()

    def draw(self):
        # Game Loop - draw
        self.screen.fill(BGCOLOR)
        self.all_sprites.draw(self.screen)
        self.draw_text(str(self.score), 22, WHITE, WIDTH / 2, 15)
        pg.display.flip()

    def show_start_screen(self):
        # music
        pg.mixer.music.load(path.join(self.snd_dir, 'A_Journey_Awaits.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.1)
        # game splash/start screen
        self.screen.fill(BGCOLOR)
        self.draw_text(TITLE, 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text("Arrows to move, Space to jump", 22, WHITE, WIDTH / 2,
                       HEIGHT / 2)
        self.draw_text("press a key to play", 22, WHITE, WIDTH / 2,
                       HEIGHT * 3 / 4)
        self.draw_text(f"High Score: {self.highscore}", 22, WHITE, WIDTH / 2,
                       15)
        pg.display.flip()
        self.wait_for_key()
        pg.mixer.music.fadeout(500)

    def show_go_screen(self):
        # music
        pg.mixer.music.load(path.join(self.snd_dir, 'A_Journey_Awaits.ogg'))
        pg.mixer.music.play(loops=-1)
        pg.mixer.music.set_volume(0.1)
        # game over/continue
        if not self.running:  # if we want to quit in the middle of a game and
            return            # not see the go screen
        self.screen.fill(BGCOLOR)
        self.draw_text("GAME OVER", 48, WHITE, WIDTH / 2, HEIGHT / 4)
        self.draw_text(f"Score: {self.score}", 22, WHITE, WIDTH / 2, HEIGHT / 2)
        self.draw_text("press a key to play again", 22, WHITE,
                       WIDTH / 2, HEIGHT * 3 / 4)

        if self.score > self.highscore:
            self.highscore = self.score
            self.draw_text("NEW HIGH SCORE !", 22, WHITE,
                           WIDTH / 2, HEIGHT / 2 + 40)

            with open(path.join(self.dir, HS_FILE), 'w') as f:
                f.write(str(self.score))
        else:
            self.draw_text(f"High Score: {self.highscore}", 22,
                           WHITE, WIDTH / 2, HEIGHT / 2 + 40)
        pg.display.flip()
        self.wait_for_key()

    def wait_for_key(self):
        waiting = True
        while waiting:
            self.clock.tick(FPS)
            for event in pg.event.get():
                if event.type == pg.QUIT:
                    self.running = False
                if event.type == pg.KEYUP:
                    waiting = False

    def draw_text(self, text, size, color, x, y):
        font = pg.font.Font(self.font_name, size)
        text_surface = font.render(text, True, color)
        text_rect = text_surface.get_rect()
        text_rect.midtop = (x, y)
        self.screen.blit(text_surface, text_rect)


g = Game()
g.show_start_screen()
while g.running:
    g.new()
    g.show_go_screen()

pg.quit()


