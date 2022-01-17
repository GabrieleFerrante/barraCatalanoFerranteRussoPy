from fnmatch import translate
import os
import sys
import pygame
from random import randint
from pathlib import WindowsPath
basefolder = str(WindowsPath().parent.absolute()) + '\\pygame-prototype\\'
sys.path.insert(
    1, basefolder.replace('pygame-prototype', 'coniche')
)
import parabola

# Initialization
pygame.init()

WIDTH, HEIGHT = 1024, 576
screen = pygame.display.set_mode((WIDTH, HEIGHT))
debug = False

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
        self.dirx = 0
        self.diry = 0

    def draw(self):
        rectangle = pygame.draw.rect(screen, (255, 0, 0), self.rect)


# Target class


class Target:
    def __init__(self, x, y, acceleration=0.25):
        self.x, self.y = x, y
        self.image = pygame.image.load(
            basefolder + 'target.png'
        )
        self.speed = 0
        self.acceleration = acceleration

    def draw(self):
        screen.blit(self.image, (self.x, self.y))

    def update(self):
        self.speed -= self.acceleration
        self.x += int(self.speed)
        if self.speed < -1:
            self.speed = 0


# Arrow class


class Arrow:
    def __init__(self, trajectory, angle):
        self.image = pygame.image.load(
            basefolder + 'arrow.png'
        )
        self.rect = self.image.get_rect()
        self.trajectory = trajectory
        self.angle = angle
        self.counter = 0
        self.prev_counter = 0

    def draw(self):
        rotated_arrow, rotated_arrow_rect = rot_from_zero(self.image, self.angle)
        rotated_arrow_rect.center = self.rect.center
        screen.blit(rotated_arrow, rotated_arrow_rect)

    def update(self):

        if self.counter < len(self.trajectory):
            if int(self.counter) > int(self.prev_counter):            
                self.rect.center = self.trajectory[int(self.counter)]
                self.prev_counter = self.counter
            self.counter += map_range(len(self.trajectory), 0, WIDTH, 0.15, 3.5)


player = Player(64, HEIGHT - 128)

# Targets init
targets = []
targets_spawn_time = 3000
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
fire_rate = 750
previous_fire_ticks = pygame.time.get_ticks()

while 1:

    # Handling the targets
    current_ticks = pygame.time.get_ticks()
    if current_ticks - previous_target_ticks >= targets_spawn_time:
        targets.append(Target(WIDTH, randint(0, HEIGHT - 110)))
        previous_target_ticks = current_ticks

    screen.fill((101, 203, 214))
    player.draw()

    for i, e in list(enumerate(targets))[::-1]:
        e.update()
        e.draw()
        if e.x <= -e.image.get_rect().width:
            del targets[i]

    # Calculating the angle of the bow
    mouse_pos = pygame.Vector2(pygame.mouse.get_pos())
    angle = map_range(mouse_pos.x, 0, WIDTH, 90, 0)

    # Rotate the bow
    rotated_bow, rotated_bow_rect = rot_from_zero(bow, angle)
    rotated_bow_rect.center = player.rect.center
    screen.blit(rotated_bow, rotated_bow_rect)

    # Handling the arrows
    for i, e in list(enumerate(arrows))[::-1]:
        e.update()
        e.draw()
        if e.rect.bottom >= HEIGHT - ground_frames[ground_frame_counter].get_rect().height or e.counter >= len(e.trajectory):
            del arrows[i]

    # Animate the ground
    if frame_counter % 24 == 0:
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
        mouse_pos.x if mouse_pos.x != rotated_bow_rect.centerx else mouse_pos.x + 1
    )
    v_x = rotated_bow_rect.centerx + \
        ((mouse_pos.x - rotated_bow_rect.centerx) / 2)
    trajectory_parabola = parabola.Parabola(
        1,
        rotated_bow_rect.center,
        (mouse_pos.x, rotated_bow_rect.centery),
        (v_x, mouse_pos.y),
    )
    trajectory = [(i[0], int(i[1])) for i in trajectory_parabola.punti(
        rotated_bow_rect.centerx, mouse_pos.x)]

    # Input detection
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LSHIFT:
                debug = not debug
        elif event.type == pygame.MOUSEBUTTONDOWN:
            if current_ticks - previous_fire_ticks >= fire_rate:
                arrows.append(Arrow(trajectory, angle))
                previous_fire_ticks = current_ticks

    # Debug view
    if debug:
        pygame.draw.lines(screen, (0, 0, 0), False, trajectory)
        pygame.draw.ellipse(
            screen, (128, 128, 128), pygame.Rect(
                v_x - 15, mouse_pos.y - 15, 30, 30)
        )
        pygame.draw.ellipse(
            screen,
            (128, 128, 128),
            pygame.Rect(mouse_pos.x - 15,
                        rotated_bow_rect.centery - 15, 30, 30),
        )

    pygame.display.update()

    frame_counter += 1
