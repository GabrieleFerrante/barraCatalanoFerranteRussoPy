import os
from pathlib import Path
import pygame
from math import *


def rot_from_zero(surface, angle):
    '''Ruota un immagine senza perdere qualità'''

    rotated_surface = pygame.transform.rotozoom(surface, angle, 1)
    rotated_rect = rotated_surface.get_rect()
    return rotated_surface, rotated_rect


def map_range(value, leftMin, leftMax, rightMin, rightMax):
    '''Converte un valore da un range ad un altro'''

    # Calcola la lunghezza dei range
    leftSpan = leftMax - leftMin
    rightSpan = rightMax - rightMin

    # Converti il valore in decimale in un range da 0 a 1 
    valueScaled = float(value - leftMin) / float(leftSpan)

    # Converti il range da 0 a 1 al range finale.
    return rightMin + (valueScaled * rightSpan)



basefolder = str(Path(__file__).parent)

WIDTH, HEIGHT = 1024, 576

class Spritesheet:
    '''Classe per le spritesheet
    
    Il file deve avere come colore RGB per la trasparenza (255, 0, 255)
    '''

    def __init__(self, filename, size, horizontal=True):
        self.filename = filename
        self.size = size
        self.sprite_sheet = pygame.image.load(self.filename).convert()
        if horizontal:
            self.frames = self.sprite_sheet.get_width() // self.size
        else:
            self.frames = self.sprite_sheet.get_height() // self.size

    def get_sprite(self, x, y, w, h):
        '''Recupera un frame dalla spritesheet'''

        sprite = pygame.Surface((w, h))
        sprite.set_colorkey((255, 0, 255))
        sprite.blit(self.sprite_sheet, (0, 0), (x, y, w, h))
        return sprite



class Player:
    '''Classe del giocatore'''

    def __init__(self, x, y, image_path, sprite_size, width=32, height=32):
        '''Costruttore del giocatore
        
        x: Posizione x del giocatore
        y: Posizione y del giocatore
        image_path: Percorso per la spritesheet del giocatore
        sprite_size: Dimensioni di un frame della spritesheet
        width: Larghezza del giocatore
        height: Altezza del giocatore
        '''
        self.sprite_sheet = Spritesheet(image_path, sprite_size)
        self.rect = pygame.Rect(x, y, width, height)
        self.frame = 0

    def draw(self, screen, frame_counter, frame_rate=24):
        '''Disegna il giocatore
        
        screen: Riferimento alla finestra di gioco
        frame_counter: Frame contato dall'apertura del gioco al
        richiamo della funzione
        frame_rate: Frame rate dell'animazione
        '''

        if frame_counter % frame_rate == 0:
            self.frame += 1
        if self.frame >= self.sprite_sheet.frames:
            self.frame = 0
        

        image = self.sprite_sheet.get_sprite(self.sprite_sheet.size * self.frame, 0, self.sprite_sheet.size, self.sprite_sheet.size)
        image = pygame.transform.scale(image, self.rect.size)
        screen.blit(image, self.rect)



class Target(pygame.sprite.Sprite):
    '''Classe del bersaglio'''

    def __init__(self, x, y, acceleration=0.2):
        '''Costruttore del bersaglio
        
        x: Posizione x del bersaglio
        y: Posizione y del bersaglio
        acceleration: Accelerazione del bersaglio
        '''
        super().__init__()
        self.x, self.y = x, y
        self.image = pygame.image.load(
            os.path.join(basefolder, 'sprites', 'target.png')
        )
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 0
        self.acceleration = acceleration
        self.score = 10

    def draw(self, screen):
        '''Disegna il bersaglio
        
        screen: Riferimento alla finestra di gioco
        '''

        screen.blit(self.image, (self.x, self.y))

    def update(self, delta):
        '''Aggiorna la posizione del bersaglio
        
        delta: Il delta-time
        '''

        self.speed -= self.acceleration * delta
        self.x += int(self.speed)
        self.rect.center = self.x, self.y
        if self.speed < -1:
            self.speed = 0
    
    def on_hit(self, glob_score):
        '''Aumenta il punteggio quando il bersaglio viene colpito
        
        glob_score: Punteggio (Sottoforma di lista)
        '''

        glob_score[0] += self.score



class Arrow(pygame.sprite.Sprite):
    '''Classe della freccia'''

    def __init__(self, trajectory, mouse_pos):
        '''Costruttore della freccia
        
        trajectory: Traiettoria della freccia sotto forma di parabola
        mouse_pos: Posizione del cursore nell'istante di inizializzazione
        '''
        
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(basefolder, 'sprites', 'arrow.png')
        )
        self.image = pygame.transform.scale(self.image, (48, 48))
        self.rect = self.image.get_rect()
        self.rect.x = -self.rect.width
        self.mask = pygame.mask.from_surface(self.image)
        self.trajectory = trajectory
        self.counter = 0
        self.prev_counter = 0
        self.angle = -45
        self.mouse = mouse_pos
        self.mouse.y = HEIGHT - self.mouse.y

    def draw(self, screen):
        '''Disegna la freccia sullo schermo
        
        screen: Riferimento alla finestra di gioco
        '''

        rotated_arrow, rotated_arrow_rect = rot_from_zero(
            self.image, self.angle)
        rotated_arrow_rect.center = self.rect.center
        self.mask = pygame.mask.from_surface(rotated_arrow)
        screen.blit(rotated_arrow, rotated_arrow_rect)

    def update(self, player):
        '''Aggiorna la posizione e l'angolazione della freccia
        
        player: Riferimento all'oggetto del giocatore
        '''

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
                    player.rect.center).distance_to(pygame.Vector2(WIDTH, 0)), 0.15, 10
            )
            if counter_increase < 0.15:
                counter_increase = 0.15
            self.counter += counter_increase

    def check_collisions(self, targets, glob_score):
        '''Controlla collisioni con la freccia
        
        targets: Gruppo di sprite di pygame
        glob_score: Punteggio (Sottoforma di lista)
        '''

        hits = pygame.sprite.spritecollide(self, targets, True, pygame.sprite.collide_mask)
        for i in hits:
            i.on_hit(glob_score)
        return hits