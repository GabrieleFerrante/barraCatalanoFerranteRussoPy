import os
from pathlib import Path
import pygame
from random import randint
from math import *
from coniche.retta import Retta


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
_acceleration = 3
font18 = pygame.font.Font(
    os.path.join(basefolder, 'font.ttf'), 18)


class Spritesheet:
    '''Classe per le spritesheet
    
    Il file deve avere come colore RGB per la trasparenza (255, 0, 255)
    '''

    def __init__(self, filename, size, horizontal=True) -> None:
        self.filename = filename
        self.size = size
        self.sprite_sheet = pygame.image.load(self.filename).convert_alpha()
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

    def __init__(self, x, y, image_path, sprite_size, width=32, height=32) -> None:
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

    def __init__(self, x, y, group, acceleration=_acceleration) -> None:
        '''Costruttore del bersaglio
        
        x: Posizione x del bersaglio
        y: Posizione y del bersaglio
        group: Gruppo contenente il bersaglio
        acceleration: Accelerazione del bersaglio
        '''
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(basefolder, 'sprites', 'target.png')
        ).convert_alpha()
        self.rect = self.image.get_rect(center=(x, y))
        self.mask = pygame.mask.from_surface(self.image)
        self.speed = 0
        self.acceleration = acceleration
        self.score = 10
        self.group = group
        self.equation = Retta(2, (x, y), (0, y)).eqEsplicita()

    def draw(self, screen, mouse_pos):
        '''Disegna il bersaglio
        
        screen: Riferimento alla finestra di gioco
        '''

        eq = font18.render(self.equation, False, (0, 0, 0))
        eq_rect = eq.get_rect(centerx=self.rect.centerx)
        eq_rect.centery = self.rect.centery + 48


        screen.blit(self.image, self.rect)
        if self.rect.collidepoint(mouse_pos.x, mouse_pos.y):
            screen.blit(eq, eq_rect)

    def update(self, state, delta=1):
        '''Aggiorna la posizione del bersaglio'''


        if state != 2:
            self.speed -= self.acceleration * delta
            self.rect.move_ip(self.speed, 0)
        if self.speed < -1:
            self.speed = 0
        
        if self.rect.right <= 0:
            self.destroy()
            return True
        else:
            return False


    def on_hit(self, glob_score):
        '''Aumenta il punteggio quando il bersaglio viene colpito
        
        glob_score: Punteggio (Sottoforma di lista)
        '''

        glob_score[0] += self.score
        self.destroy()
    
    def destroy(self):
        '''Rimuove il bersaglio dal gruppo di sprite, eliminandola'''

        self.group.remove(self)

    
    @classmethod
    def target_spawner(cls, group, time_passed, spawn_time, score=0):
        '''Crea una freccia (Metodo di classe)
        
        group: Gruppo che dovrà contenere 
               il bersaglio creato (pygame.sprite.Group)
        time_passed: Tempo passato dalla creazione 
                     dell'ultimo bersaglio in millisecondi
        spawn_time: Tempo di spawn del bersaglio
        score: Il punteggio al momento della creazione del bersaglio
        '''

        
        if time_passed >= spawn_time:
            # Se passa abbastanza tempo aggiungi un bersaglio
            new_acceleration = _acceleration + (score * 0.003)
            group.add(Target(WIDTH, randint(
                0,HEIGHT - 110), group, new_acceleration))
            return True



class Arrow(pygame.sprite.Sprite):
    '''Classe della freccia'''

    def __init__(self, trajectory, mouse_pos, group) -> None:
        '''Costruttore della freccia
        
        trajectory: Traiettoria della freccia sotto forma di parabola
        mouse_pos: Posizione del cursore nell'istante di inizializzazione
        group: Gruppo di sprite contenente la freccia (pygame.sprite.Group)
        '''
        
        super().__init__()
        self.image = pygame.image.load(
            os.path.join(basefolder, 'sprites', 'arrow.png')
        ).convert_alpha()
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
        self.group = group

    def draw(self, screen):
        '''Disegna la freccia sullo schermo
        
        screen: Riferimento alla finestra di gioco
        '''

        rotated_arrow, rotated_arrow_rect = rot_from_zero(
            self.image, self.angle)
        rotated_arrow_rect.center = self.rect.center
        self.rect = rotated_arrow_rect
        
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


        if (self.rect.bottom >= HEIGHT - 64) or self.counter >= len(self.trajectory):
            self.destroy()
        
        

    def check_collisions(self, targets, glob_score):
        '''Controlla collisioni con la freccia
        
        targets: Gruppo di sprite di pygame
        glob_score: Punteggio (Sottoforma di lista)
        '''

        hits = pygame.sprite.spritecollide(self, targets, True, pygame.sprite.collide_mask)
        for i in hits:
            i.on_hit(glob_score)
        
        if hits:
            self.destroy()

    def destroy(self):
        '''Rimuove la freccia dal gruppo di sprite, eliminandola'''

        self.group.remove(self)


    @classmethod
    def arrow_spawner(cls, group, time_passed, spawn_time, trajectory, mouse_pos):
        '''Crea una freccia (Metodo di classe)
        
        group: Gruppo che dovrà contenere la freccia creata (pygame.sprite.Group)
        time_passed: Tempo passato dalla creazione 
                    dell'ultima freccia in millisecondi
        spawn_time: Tempo di spawn della freccia
        trajectory: La traiettoria parabolica
        mouse_pos: Posizione del mouse
        '''

        if time_passed >= spawn_time:
            # Se passa abbastanza tempo aggiungi un bersaglio
            group.add(Arrow(trajectory, mouse_pos, group))
            return True


class ScrollingElement:
    '''Classe di un elemento scorrevole'''

    def __init__(self, x, y, image, acceleration=_acceleration) -> None:
        '''Costruttore dell'elemento'''

        self.image = image
        self.rect = self.image.get_rect()
        self.rect.topleft = x, y
        self.speed = 0
        self.acceleration = acceleration

    def draw(self, screen):
        '''Disegna l'elemento
        
        screen: Riferimento alla finestra di gioco
        '''

        offset_rect = self.rect.copy()
        offset_rect.x += self.image.get_width()
        screen.blit(self.image, self.rect)
        screen.blit(self.image, offset_rect)

    def update(self, state, delta=1):
        '''Aggiorna la posizione dell'elemento'''

        if state != 2:
            self.speed -= self.acceleration * delta
            self.rect.x += int(self.speed)
        if self.speed < -1:
            self.speed = 0
        if self.rect.right <= 0:
            self.rect.left = 0


class Sky:
    '''Classe del cielo'''

    def __init__(self) -> None:
        '''Costruttore del cielo'''
        
        layer1_image = pygame.image.load(os.path.join(basefolder, 'sprites', 'background', 'layer1.png')).convert_alpha()
        layer2_image = pygame.image.load(os.path.join(basefolder, 'sprites', 'background', 'layer2.png')).convert_alpha()
        layer3_image = pygame.image.load(os.path.join(basefolder, 'sprites', 'background', 'layer3.png')).convert_alpha()

        self.layer3 = ScrollingElement(0, 30, layer3_image, 0.10)
        self.layer2 = ScrollingElement(-70, 172, layer2_image, 0.14)
        self.layer1 = ScrollingElement(47, 250, layer1_image, 0.18)

    def draw(self, screen):
        '''Disegna il cielo'''

        self.layer3.draw(screen)
        self.layer2.draw(screen)
        self.layer1.draw(screen)

    def update(self, state):
        '''Aggiorna le posizioni del cielo'''

        self.layer1.update(state)
        self.layer2.update(state)
        self.layer3.update(state)


class BaseButton:
    '''Classe base del bottone'''

    def __init__(self, x, y, image, command=None, scale=1, return_bool=False) -> None:
        '''Costruttore del bottone'''

        width = image.get_width()
        height = image.get_height()
        self.image = pygame.transform.scale(image, (int(width * scale), int(height * scale)))
        self.rect = self.image.get_rect()
        self.rect.topleft = (x, y)
        self.command = command
        self.clicked = False
        self.return_bool = return_bool

    def draw(self, screen):
        mouse_pos = pygame.math.Vector2(pygame.mouse.get_pos())

        if self.rect.collidepoint(mouse_pos):
            if pygame.mouse.get_pressed()[0] == 1 and self.clicked == False:
                self.clicked = True
                if self.command:
                    self.command()
                if self.return_bool:
                    return self.clicked
        
        if pygame.mouse.get_pressed()[0] == 0:
            self.clicked = False

        screen.blit(self.image, (self.rect.x, self.rect.y))