import os
import sys
import pygame
from math import *
from random import randint
basefolder = os.path.dirname(os.path.abspath(__file__)).replace(
    os.path.basename(__file__), '') + '\\'
sys.path.insert(
    1, basefolder.replace('pygame-prototype', 'coniche')
)
import parabola

# Initialization
pygame.init()

WIDTH, HEIGHT = 1024, 576
screen = pygame.display.set_mode((WIDTH, HEIGHT))
score = 0
lives = 3
debug = False
clock = pygame.time.Clock()
font_obj = pygame.font.SysFont("impact", 32)


# Function to rotate without losing quality


def rot_from_zero(surface, angle):
    rotated_surface = pygame.transform.rotozoom(surface, angle, 1)
    rotated_rect = rotated_surface.get_rect()
    return rotated_surface, rotated_rect


# Function to map a range of values to another


def map_range(value, leftMin, leftMax, rightMin, rightMax):
    # Figure out how 'wide' each range is
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Convert the left range into a 0-1 range (float)
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Convert the 0-1 range into a value in the right range.
    return rightMin + (valueScaled * rightSpan)


# Player class


class Player:
    def __init__(self, x, y, width=64, height=64):
        self.rect = pygame.Rect(x, y, width, height)

    def draw(self):
        pygame.draw.rect(screen, (255, 0, 0), self.rect)


# Target class


class Target:
    def __init__(self, x, y, acceleration=0.2):
        self.x, self.y = x, y
        self.image = pygame.image.load(
            basefolder + 'target.png'
        )
        self.speed = 0
        self.acceleration = acceleration
        self.score = 10

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def update(self, delta):
        self.speed -= self.acceleration * delta
        self.x += int(self.speed)
        if self.speed < -1:
            self.speed = 0


# Arrow class


class Arrow:
    def __init__(self, trajectory):
        self.image = pygame.image.load(
            basefolder + 'arrow.png'
        )
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width
        self.trajectory = trajectory
        self.counter = 0
        self.prev_counter = 0
        self.angle = -45
        self.mouse = mouse_pos
        self.mouse.y = HEIGHT - self.mouse.y

    def draw(self):
        rotated_arrow, rotated_arrow_rect = rot_from_zero(
            self.image, self.angle)
        rotated_arrow_rect.center = self.rect.center
        screen.blit(rotated_arrow, rotated_arrow_rect)

    def update(self):
        if int(self.counter) <= len(self.trajectory):
            if int(self.counter) > int(self.prev_counter):

                self.rect.center = self.trajectory[int(self.counter)]
                self.prev_counter = self.counter

                if (rot_point := 5) > len(self.trajectory)- 1 - int(self.counter):
                    rot_point = len(self.trajectory) - int(self.counter) - 1

                if rot_point != 0:
                    base = self.trajectory[int(
                        self.counter)+rot_point].x - self.rect.centerx
                    height = self.trajectory[int(
                        self.counter)+rot_point].y - self.rect.centery
                    hypo = hypot(base, height)
                    self.angle = -degrees(asin(height / hypo)) - 90


            counter_increase = map_range(
                pygame.Vector2(player.rect.center).distance_to(self.mouse), 0, pygame.Vector2(
                    player.rect.center).distance_to(pygame.Vector2(WIDTH, 0)), 0.15, 5
            )
            if counter_increase < 0.15:
                counter_increase = 0.15
            self.counter += counter_increase


player = Player(64, HEIGHT - 128)

# Targets init
targets = []
targets_spawn_time = 3500
previous_target_ticks = pygame.time.get_ticks()

# Ground animation init
ground_frames = []
for i in os.listdir(basefolder + 'ground_frames\\'):
    ground_frames.append(
        pygame.image.load(
            basefolder + 'ground_frames\\' + i
        )
    )  # Load all ground frames
ground_frame_counter = 0  # Keep track of the current ground frame
frame_counter = 0

# Bow
bow = pygame.image.load(basefolder + 'bow.png')
angle = 0

# Arrow init
arrows = []
fire_rate = 1000
previous_fire_ticks = pygame.time.get_ticks()

while lives > 0:

    dt = clock.tick()

    current_ticks = pygame.time.get_ticks()
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())

    screen.fill((101, 203, 214))
    player.draw()

    
    score_label = font_obj.render(f"Score: {score}", 1, (0, 0, 0))
    screen.blit(score_label, (0, 0))
    lives_label = font_obj.render(f"Lives: {lives}", 1, (0, 0, 0))
    screen.blit(lives_label, (0, 32))

    # Handling the targets
    if current_ticks - previous_target_ticks >= targets_spawn_time:
        targets.append(Target(WIDTH, randint(0, HEIGHT - 110)))
        previous_target_ticks = current_ticks

    for i, e in list(enumerate(targets))[::-1]:
        e.update(dt)
        e.draw()
        if e.x <= -e.image.get_rect().width:
            del targets[i]
            # lives -= 1

    # Animate the ground
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

    # Calculating the trajectory
    mouse_pos.x = (
        mouse_pos.x if mouse_pos.x != player.rect.centerx else mouse_pos.x + 1
    )
    v_x = player.rect.centerx + \
        ((mouse_pos.x - player.rect.centerx) / 2)
    trajectory_parabola = parabola.Parabola(
        1,
        player.rect.center,
        mouse_pos,
        (mouse_pos.x + (mouse_pos.x - player.rect.centerx) , HEIGHT),
    )
    trajectory = [pygame.Vector2(i[0], int(i[1])) for i in trajectory_parabola.punti(
        player.rect.centerx, mouse_pos.x * 2)]

    # Calculating the angle of the bow
    bow_rot_index = 5
    if bow_rot_index > len(trajectory) - 1:
        bow_rot_index = len(trajectory) - 1
    bow_base, bow_height = trajectory[bow_rot_index].x - player.rect.centerx, trajectory[bow_rot_index].y - player.rect.centery
    bow_hypo = hypot(bow_base, bow_height)
    bow_angle = -degrees(asin(bow_height / bow_hypo))

    # Rotate the bow
    rotated_bow, rotated_bow_rect = rot_from_zero(bow, bow_angle)
    rotated_bow_rect.center = player.rect.center
    screen.blit(rotated_bow, rotated_bow_rect)
    
    # Input detection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                debug = not debug
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_ticks - previous_fire_ticks >= fire_rate:
                arrows.append(Arrow(trajectory))
                previous_fire_ticks = current_ticks

    for i in range(len(trajectory)):
        if i % 30 == 0 and i != 0:
            decrement = map_range(i, 0, len(trajectory) / 2 - 1, 20, 0)
            rect = pygame.Rect(-100, 0, decrement, decrement)
            rect.center = trajectory[i]
            pygame.draw.ellipse(screen, (255, 255, 255), rect)

    # Handling the arrows
    for i, e in list(enumerate(arrows))[::-1]:
        e.update()
        e.draw()
        hit = e.rect.collidelist([i.image.get_rect() for i in targets])
        print(hit)
        if hit != -1:
            score += targets[hit].score
            del targets[hit]
        if e.rect.bottom >= HEIGHT - ground_frames[ground_frame_counter].get_rect().height or e.counter >= len(e.trajectory):
            del arrows[i]

    # Debug view
    if debug:
        
        pygame.draw.lines(screen, (0, 0, 0), False, trajectory)
        
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
