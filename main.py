import os
import sys
from pathlib import Path
import pygame
from math import *
from random import randint
from coniche.parabola import Parabola
from assets.classes import Player, Arrow, Target, Ground, rot_from_zero, map_range


basefolder = str(Path(__file__).parent)


class Game:
    '''Classe del gioco'''

    def __init__(self):
        '''Costruttore della classe di gioco'''
        pygame.init()

        self.WIDTH, self.HEIGHT = 1024, 576
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Gioco Pygame')
        self.score = [0]
        self.lives = 3
        self.debug_mode = False
        self.clock = pygame.time.Clock()
        self.font_obj = pygame.font.Font(
            os.path.join(basefolder, 'assets', 'font.ttf'), 32)

        self.player = Player(64, self.HEIGHT - (64 + 96), os.path.join(
            basefolder, 'assets', 'sprites', 'player.png'), 32, 96, 96)

        # Inizializza i bersagli
        self.targets = pygame.sprite.Group()
        self.targets_spawn_time = 3500
        self.previous_target_ticks = pygame.time.get_ticks()

        # Inizializza il terreno
        self.ground = Ground(0, self.HEIGHT-64)

        self.frame_counter = 0

        # Inizializza l'arco
        self.bow = pygame.image.load(os.path.join(
            basefolder, 'assets', 'sprites', 'bow.png'))
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
        arrow_shot = Arrow.arrow_spawner(self.arrows, ticks - self.previous_fire_ticks, self.fire_rate, trajectory, mouse_pos)
        if arrow_shot:
            self.previous_fire_ticks = ticks


    def draw_all(self, trajectory):
        '''Disegna tutti gli elementi di gioco
        
        trajectory: La traiettoria parabolica
        '''

        self.screen.fill((101, 203, 214))

        self.player.draw(self.screen, self.frame_counter, 12)
        for target in list(self.targets)[::-1]:
            target.draw(self.screen)
        for arrow in list(self.arrows)[::-1]:
            arrow.draw(self.screen)
        self.ground.draw(self.screen)
        self.draw_bow(trajectory)

        for i in range(len(trajectory)):
            if i % 30 == 0 and i != 0:
                decrement = map_range(i, 0, len(trajectory) / 2 - 1, 20, 0)
                rect1 = pygame.Rect(-100, 0, decrement + 2, decrement + 2)
                rect2 = pygame.Rect(-100, 0, decrement, decrement)
                rect1.center = trajectory[i]
                rect2.center = trajectory[i]
                pygame.draw.ellipse(self.screen, (0, 0, 0), rect1)
                pygame.draw.ellipse(self.screen, (255, 255, 255), rect2)


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
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    self.debug_mode = not self.debug_mode
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.shoot(ticks, trajectory, mouse_pos)

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
        return trajectory

    def gameloop(self):
        '''Loop di gioco'''

        while self.lives > 0:

            dt = self.clock.tick(60)

            current_ticks = pygame.time.get_ticks()
            mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
            mouse_pos.x = (
                mouse_pos.x if mouse_pos.x != self.player.rect.centerx else mouse_pos.x + 1
            )

            trajectory = self.calculate_trajectory(mouse_pos)

            # Gestione dei bersagli
            target_spawned = Target.target_spawner(self.targets, current_ticks - self.previous_target_ticks, self.targets_spawn_time)
            if target_spawned:
                self.previous_target_ticks = current_ticks

            for i in list(self.targets)[::-1]:
                out_of_screen = i.update(dt)
                if out_of_screen:
                    self.lives -= 1
                # Aggiorna i bersagli

            # Aggiorna il terreno
            self.ground.update(dt)

            self.input(current_ticks, trajectory, mouse_pos)

            # Gestione delle frecce
            for i in list(self.arrows)[::-1]:
                i.check_collisions(self.targets, self.score)
                i.update(self.player)
                # Aggiorna tutte le frecce

            # Debug mode
            if self.debug_mode:
                self.debug(mouse_pos, trajectory)

            self.draw_all(trajectory)
            self.hud()

            pygame.display.update()

            self.frame_counter += 1

    def hud(self):
        '''Disegna e gestisci la HUD'''

        score_label = self.font_obj.render(f"{self.score[0]}", 1, (0, 0, 0))
        score_rect = score_label.get_rect(center=(self.WIDTH/2, 32))
        self.screen.blit(score_label, score_rect)

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


if __name__ == '__main__':
    gm = Game()

    gm.gameloop()
