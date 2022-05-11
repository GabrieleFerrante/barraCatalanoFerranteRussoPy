import os
import sys
from pathlib import Path
import pygame
from math import *
from random import randint
from coniche.parabola import Parabola
from assets.classes import Player, Arrow, Target, ScrollingElement, Sky, BaseButton, rot_from_zero, map_range


basefolder = str(Path(__file__).parent)


class Game:
    '''Classe del gioco'''


    def __init__(self):
        '''Costruttore della classe di gioco'''
        pygame.init()

        self.WIDTH, self.HEIGHT = 1024, 576
        self.DIFFICULTIES = ['FACILE', 'NORMALE', 'DIFFICILE']
        self.difficulty = 1
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Gioco Pygame')
        self.score = [0]
        self.high_scores = [0, 0, 0]
        self.lives = 3
        self.debug_mode = False

        self.STATES = {'MENU': 0, 'GAME': 1, 'PAUSED': 2, 'END': 3}
        self.state = self.STATES['MENU']
        
        self.clock = pygame.time.Clock()
        self.frame_counter = 0
        self.font32 = pygame.font.Font(
            os.path.join(basefolder, 'assets', 'font.ttf'), 32)
        self.font24 = pygame.font.Font(
            os.path.join(basefolder, 'assets', 'font.ttf'), 24)
        self.font18 = pygame.font.Font(
            os.path.join(basefolder, 'assets', 'font.ttf'), 18)


        # Inizializza il giocatore
        self.player = Player(64, self.HEIGHT - (64 + 96), os.path.join(
            basefolder, 'assets', 'sprites', 'player.png'), 32, 96, 96)

        # Inizializza i bersagli
        self.targets = pygame.sprite.Group()
        self.targets_spawn_time = 3500
        self.previous_target_ticks = pygame.time.get_ticks()

        # Inizializza il terreno
        self.ground = ScrollingElement(0, self.HEIGHT-64, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'ground.png')).convert_alpha())

        # Inizializza il cielo
        self.sky = Sky()

        # Inizializza l'arco
        self.bow = pygame.image.load(os.path.join(
            basefolder, 'assets', 'sprites', 'bow.png')).convert_alpha()
        self.angle = 0

        # Inizializza le frecce
        self.arrows = pygame.sprite.Group()
        self.fire_rate = 1000
        self.previous_fire_ticks = pygame.time.get_ticks()

    def shoot(self, ticks, trajectory, mouse_pos):
        '''Scocca una freccia
        
        ticks: I tick al momento del richiamo (pygame.time.get_ticks) 
        trajectory: La traiettoria parabolica
        mouse_pos: Posizione del mouse
        '''

        if mouse_pos.x <= self.player.rect.centerx:
            return
        arrow_shot = Arrow.arrow_spawner(self.arrows, ticks - self.previous_fire_ticks, self.fire_rate, trajectory, mouse_pos)
        if arrow_shot:
            self.previous_fire_ticks = ticks


    def draw_all(self, trajectory, mouse_pos, equation = ''):
        '''Disegna tutti gli elementi di gioco
        
        trajectory: La traiettoria parabolica
        '''

        self.screen.fill((129, 212, 221))
        self.sky.draw(self.screen)

        self.player.draw(self.screen, self.frame_counter, 12)
        for target in list(self.targets)[::-1]:
            target.draw(self.screen)

        for i in range(len(trajectory)):
            if i % 30 == 0 and i != 0:
                decrement = map_range(i, 0, len(trajectory) // 2 - 1, 20, 0)
                rect1 = pygame.Rect(-100, 0, decrement + 4, decrement + 4)
                rect2 = pygame.Rect(-100, 0, decrement, decrement)
                rect1.center = trajectory[i]
                rect2.center = trajectory[i]
                if rect2.width > 0:
                    pygame.draw.ellipse(self.screen, (0, 0, 0), rect1)
                    pygame.draw.ellipse(self.screen, (255, 255, 255), rect2)

        for arrow in list(self.arrows)[::-1]:
            arrow.draw(self.screen)
        self.ground.draw(self.screen)
        self.draw_bow(trajectory)

        equation_label = self.font18.render(equation, False, (0, 0, 0))
        equation_rect = equation_label.get_rect()
        equation_rect.center = (mouse_pos.x, mouse_pos.y - 28)
        self.screen.blit(equation_label, equation_rect)

    def draw_bow(self, trajectory):
        '''Disegna l'arco propriamente ruotato
        
        trajectory: La traiettoria parabolica
        '''

        # Calcolare l'angolo dell'arco con il seno
        bow_rot_index = 5
        if bow_rot_index > len(trajectory) - 1:
            bow_rot_index = len(trajectory) - 1
        bow_base, bow_height = trajectory[bow_rot_index].x - \
            self.player.rect.centerx, trajectory[bow_rot_index].y - \
            self.player.rect.centery
        bow_hypo = hypot(bow_base, bow_height)
        try:
            bow_angle = -degrees(asin(bow_height / bow_hypo))
        except:
            bow_hypo += 1
            bow_angle = -degrees(asin(bow_height / bow_hypo))

        # Disegna l'arco ruotato
        rotated_bow, rotated_bow_rect = rot_from_zero(self.bow, bow_angle)
        rotated_bow_rect.center = self.player.rect.center
        self.screen.blit(rotated_bow, rotated_bow_rect)

    def input(self, ticks, trajectory, mouse_pos):
        '''Gestisci gli input
        
        ticks: I tick al momento del richiamo (pygame.time.get_ticks) 
        trajectory: La traiettoria parabolica
        mouse_pos: Posizione del mouse
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_ESCAPE:
                    self.set_state('PAUSED')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.shoot(ticks, trajectory, mouse_pos)

    def quit(self):
        sys.exit()

    def set_state(self, state):
        self.state = self.STATES[state]

    def calculate_trajectory(self, mouse_pos):
        '''Calcola la traiettoria
        
        mouse_pos: Posizione del mouse
        '''
        trajectory_parabola = Parabola(
            1,
            self.player.rect.center,
            mouse_pos,
            (mouse_pos.x + (mouse_pos.x - self.player.rect.centerx), self.HEIGHT),
        )
        trajectory = [pygame.Vector2(i[0], int(i[1])) for i in trajectory_parabola.punti(
            self.player.rect.centerx, mouse_pos.x * 2)]
        return trajectory, trajectory_parabola.equazione()

    def cycle_difficulty(self):
        '''Cambia la difficoltà'''

        self.difficulty += 1
        if self.difficulty >= len(self.DIFFICULTIES):
            self.difficulty = 0
        
        self.lives = 5 - (2 * self.difficulty)

    def start(self):
        self.set_state('GAME')

        self.targets.empty()
        self.arrows.empty()

        self.score[0] = 0
        self.lives = 5 - (2 * self.difficulty)

    def main_menu(self):
        '''Schermata principale'''
        title_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'title.png')).convert_alpha()
        title_rect = title_image.get_rect()
        title_y = 32
        title_rect.topleft = (332, title_y)


        play_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'play.png')).convert_alpha()
        mode_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'mode.png')).convert_alpha()
        quit_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'quit.png')).convert_alpha()
        leaderboard_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard.png')).convert_alpha()


        play_button = BaseButton(46, 280, play_image, self.start)
        mode_button = BaseButton(46, 350, mode_image, self.cycle_difficulty)
        quit_button = BaseButton(46, 425, quit_image, sys.exit)
        leaderboard_button = BaseButton(646, 521, leaderboard_image, lambda: print('LEADERBOARD'))

        mode_text_coords = (mode_button.rect.left + mode_button.image.get_width() + 12, mode_button.rect.centery)


        time = 0

        while self.state == self.STATES['MENU']:

            dt = self.clock.tick(60)
            time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            title_rect.y = title_y + (sin(time / 250) * 10)

            self.screen.fill((129, 212, 221))
            self.sky.update(self.state)
            self.sky.draw(self.screen)
            self.screen.blit(title_image, title_rect)
            play_button.draw(self.screen)
            mode_button.draw(self.screen)
            quit_button.draw(self.screen)
            leaderboard_button.draw(self.screen)

            mode_label = self.font32.render(self.DIFFICULTIES[self.difficulty], False, (255,255,255))
            outline = self.font32.render(self.DIFFICULTIES[self.difficulty], False, (0,0,0))
            mode_rect = mode_label.get_rect()
            mode_rect.left = mode_text_coords[0]
            mode_rect.centery = mode_text_coords[1]

            outline_width = 2.5
            self.screen.blit(outline, mode_rect.move(-outline_width, -outline_width))
            self.screen.blit(outline, mode_rect.move(outline_width, -outline_width))
            self.screen.blit(outline, mode_rect.move(outline_width, outline_width))
            self.screen.blit(outline, mode_rect.move(-outline_width, outline_width))
            self.screen.blit(mode_label, mode_rect)

            pygame.display.update()

    def gameloop(self):
        '''Loop di gioco'''

        while self.state == self.STATES['GAME']:

            dt = self.clock.tick(60)


            current_ticks = pygame.time.get_ticks()
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            mouse_pos.x = (
                mouse_pos.x if mouse_pos.x != self.player.rect.centerx else mouse_pos.x + 1
            )

            self.sky.update(self.state)

            trajectory, equation = self.calculate_trajectory(mouse_pos)

        
            # Gestione dei bersagli
            target_spawned = Target.target_spawner(self.targets, current_ticks - self.previous_target_ticks, self.targets_spawn_time)
            if target_spawned:
                self.previous_target_ticks = current_ticks

            for i in list(self.targets)[::-1]:
                out_of_screen = i.update(dt, self.state)
                if out_of_screen:
                    print('OUT OF SCREEN')
                    self.lives -= 1
                # Aggiorna i bersagli

            # Aggiorna il terreno
            self.ground.update(dt, self.state)

            # Gestione delle frecce
            for i in list(self.arrows)[::-1]:
                # Aggiorna tutte le frecce
                i.check_collisions(self.targets, self.score)
                i.update(self.player)

            self.input(current_ticks, trajectory, mouse_pos)
            self.draw_all(trajectory, mouse_pos, equation)
            self.hud()

            # Debug mode
            if self.debug_mode:
                self.debug(mouse_pos, trajectory)


            pygame.display.update()

            if self.score[0] > self.high_scores[self.difficulty]:
                self.high_scores[self.difficulty] = self.score[0]

            self.frame_counter += 1
            if self.lives <= 0:
                self.set_state('MENU')

    def pause(self):
        
        continue_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'pausemenu', 'continue.png')).convert_alpha()
        menu_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'pausemenu', 'menu.png')).convert_alpha()

        continue_button = BaseButton(325, 270, continue_image, lambda: self.set_state('GAME'))
        menu_button = BaseButton(230, 330, menu_image, lambda: self.set_state('MENU'))


        while self.state == self.STATES['PAUSED']:

            self.screen.fill((129, 212, 221))
            self.sky.draw(self.screen)
            self.hud()
            continue_button.draw(self.screen)
            menu_button.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_state('GAME')
            pygame.display.update()
        



    def hud(self):
        '''Disegna e gestisci la HUD'''

        score_label = self.font32.render(f"{self.score[0]}", 1, (0, 0, 0))
        score_rect = score_label.get_rect(center=(self.WIDTH/2, 32))

        high_score_label = self.font24.render(f"{self.high_scores[self.difficulty]}", 1, (0, 0, 0))
        high_score_rect = high_score_label.get_rect(center=(self.WIDTH/2, 72))

        life_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'life.png')).convert_alpha()
        life_rect = life_image.get_rect()
        life_rect.topleft = (4, 4)
        for i in range(self.lives):
            self.screen.blit(life_image, life_rect.move(i * life_rect.width, 0))
        
        pause_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'pausemenu', 'pause_button.png')).convert_alpha()
        pause_button = BaseButton(self.WIDTH - pause_image.get_width() - 1, 1, pause_image, lambda: self.set_state('PAUSED'))

        self.screen.blit(score_label, score_rect)
        self.screen.blit(high_score_label, high_score_rect)
        if self.state != self.STATES['PAUSED']:
            pause_button.draw(self.screen)


    def debug(self, mouse_pos, trajectory):
        '''Modalità debug
        
        mouse: Posizione del mouse
        trajectory: La traiettoria
        '''
        try:
            pygame.draw.lines(self.screen, (0, 0, 0), False, trajectory)
        except:
            pass

        pygame.draw.ellipse(
            self.screen, (128, 128, 128), pygame.Rect(
                mouse_pos.x - 15, mouse_pos.y - 15, 30, 30)
        )
        pygame.draw.ellipse(
            self.screen,
            (128, 128, 128),
            pygame.Rect(mouse_pos.x + (mouse_pos.x -
                        self.player.rect.centerx) - 15, self.HEIGHT - 15, 30, 30),
        )

    def mainloop(self):
        while True:
            self.main_menu()
            self.gameloop()
            self.pause()


if __name__ == '__main__':
    gm = Game()

    gm.mainloop()
