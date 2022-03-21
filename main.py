import os
import sys
from pathlib import Path
import pygame
from math import *
from random import randint
from coniche.parabola import Parabola
from assets.classes import Spritesheet, Player, Arrow, Target, rot_from_zero, map_range


# Inizializzazione
pygame.init()
basefolder = str(Path(__file__).parent)

WIDTH, HEIGHT = 1024, 576
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption('Gioco Pygame')
score = [0]
lives = 3
debug = False
clock = pygame.time.Clock()
font_obj = pygame.font.Font(os.path.join(basefolder, 'assets', 'font.ttf'), 32)

player = Player(64, HEIGHT - (64 + 96), os.path.join(basefolder, 'assets', 'sprites', 'player.png'), 32, 96, 96)

# Inizializza i bersagli
targets = pygame.sprite.Group()
targets_spawn_time = 3500
previous_target_ticks = pygame.time.get_ticks()

# Inizializza il terreno
ground_frames = []
for i in os.listdir(os.path.join(basefolder, 'assets', 'sprites', 'ground_frames')):
    ground_frames.append(
        pygame.image.load(
            os.path.join(basefolder, 'assets', 'sprites', 'ground_frames', i)
        )
    )  # Carica tutti i frame
ground_frame_counter = 0  # Tieni traccia del frame corrente
frame_counter = 0

# Inizializza l'arco
bow = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'bow.png'))
angle = 0

# Inizializza le frecce
arrows = pygame.sprite.Group()
fire_rate = 1000
previous_fire_ticks = pygame.time.get_ticks()


# Loop di gioco
while lives > 0:

    dt = clock.tick(60)

    current_ticks = pygame.time.get_ticks()
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    screen.fill((101, 203, 214))
    player.draw(screen, frame_counter)

    # Gestione dei bersagli
    if current_ticks - previous_target_ticks >= targets_spawn_time:
        targets.add(Target(WIDTH, randint(0, HEIGHT - 110))) # Se passa abbastanza tempo aggiungi un bersaglio
        previous_target_ticks = current_ticks

    for i in list(targets)[::-1]:
        i.update(dt)
        i.draw(screen) # Aggiorna e disegna i bersagli
        if i.x <= -i.image.get_rect().width:
            targets.remove(i)
            lives -= 1

    # Anima il terreno
    if frame_counter % 12 == 0:
        ground_frame_counter += 1

    if ground_frame_counter >= len(ground_frames):
        ground_frame_counter = 0

    for i in range(round(WIDTH / ground_frames[ground_frame_counter].get_rect().width)):
        screen.blit(
            ground_frames[ground_frame_counter],
            (
                ground_frames[ground_frame_counter].get_rect().width * i,
                HEIGHT - ground_frames[ground_frame_counter].get_rect().height,
            ),
        )

    # Calcolare la traiettoria
    mouse_pos.x = (
        mouse_pos.x if mouse_pos.x != player.rect.centerx else mouse_pos.x + 1
    )
    trajectory_parabola = Parabola(
        1,
        player.rect.center,
        mouse_pos,
        (mouse_pos.x + (mouse_pos.x - player.rect.centerx) , HEIGHT),
    )
    trajectory = [pygame.Vector2(i[0], int(i[1])) for i in trajectory_parabola.punti(
        player.rect.centerx, mouse_pos.x * 2)]

    # Calcolare l'angolo dell'arco con il seno
    bow_rot_index = 5
    if bow_rot_index > len(trajectory) - 1:
        bow_rot_index = len(trajectory) - 1
    bow_base, bow_height = trajectory[bow_rot_index].x - player.rect.centerx, trajectory[bow_rot_index].y - player.rect.centery
    bow_hypo = hypot(bow_base, bow_height)
    try:
        bow_angle = -degrees(asin(bow_height / bow_hypo))
    except:
        bow_hypo += 1
        bow_angle = -degrees(asin(bow_height / bow_hypo))

    # Disegna l'arco ruotato
    rotated_bow, rotated_bow_rect = rot_from_zero(bow, bow_angle)
    rotated_bow_rect.center = player.rect.center
    screen.blit(rotated_bow, rotated_bow_rect)
    
    # Input
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                debug = not debug
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_ticks - previous_fire_ticks >= fire_rate:
                arrows.add(Arrow(trajectory, mouse_pos))
                previous_fire_ticks = current_ticks

    for i in range(len(trajectory)):
        if i % 30 == 0 and i != 0:
            decrement = map_range(i, 0, len(trajectory) / 2 - 1, 20, 0)
            rect = pygame.Rect(-100, 0, decrement, decrement)
            rect.center = trajectory[i]
            pygame.draw.ellipse(screen, (255, 255, 255), rect)

    # Gestione delle frecce
    for i in list(arrows)[::-1]:
        i.update(player)
        i.draw(screen) # Disegna e aggiorna tutte le frecce
        hits = i.check_collisions(targets, score)
        if hits:
            arrows.remove(i)
        if i.rect.centery >= HEIGHT - ground_frames[ground_frame_counter].get_rect().height or i.counter >= len(i.trajectory):
            arrows.remove(i) # Se la freccia tocca il terreno o un bersaglio cancellala

    # HUD
    score_label = font_obj.render(f"{score[0]}", 1, (0, 0, 0))
    score_rect = score_label.get_rect(center=(WIDTH/2, 32))
    screen.blit(score_label, score_rect)

    # Debug mode
    if debug:
        
        try:
            pygame.draw.lines(screen, (0, 0, 0), False, trajectory)
        except:
            pass

        pygame.draw.ellipse(
            screen, (128, 128, 128), pygame.Rect(
                mouse_pos.x - 15, mouse_pos.y - 15, 30, 30)
        )
        pygame.draw.ellipse(
            screen,
            (128, 128, 128),
            pygame.Rect(mouse_pos.x + (mouse_pos.x - rotated_bow_rect.centerx) - 15, HEIGHT - 15, 30, 30),
        )

    pygame.display.update()

    frame_counter += 1
