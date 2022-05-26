import os
import sys
import pygame
import pygame_textinput
import assets.database as db
from pathlib import Path
from math import *
from random import randint
from coniche.parabola import Parabola
from assets.classes import Player, Arrow, Target, ScrollingElement, Sky, BaseButton, rot_from_zero, map_range


pygame.init()
basefolder = str(Path(__file__).parent)
save_folder = os.path.join(basefolder, 'bigshot_savedata')
set_prefix = 'bigShot_scores_'

# Font
font32 = pygame.font.Font(
    os.path.join(basefolder, 'assets', 'font.ttf'), 32)
font24 = pygame.font.Font(
    os.path.join(basefolder, 'assets', 'font.ttf'), 24)
font18 = pygame.font.Font(
    os.path.join(basefolder, 'assets', 'font.ttf'), 18)


class Game:
    '''Classe del gioco'''

    def __init__(self):
        '''Costruttore della classe di gioco'''

        # Inizializza tutte le variabili e costanti interne
        self.WIDTH, self.HEIGHT = 1024, 576
        self.DIFFICULTIES = ['FACILE', 'NORMALE', 'DIFFICILE']
        self.difficulty = 1
        self.screen = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('Big Shot')
        self.score = [0]
        self.high_scores = [0, 0, 0]
        self.lives = 3
        self.debug_mode = False
        self.synced = False

        self.STATES = {'MENU': 0, 'GAME': 1, 'PAUSED': 2, 'END': 3, 'LEADERBOARD': 4, 'ASK_NAME': 5}
        self.state = self.STATES['MENU']
        
        self.clock = pygame.time.Clock()
        self.frame_counter = 0

        # Inizializza il giocatore
        self.player = Player(64, self.HEIGHT - (64 + 96), os.path.join(
            basefolder, 'assets', 'sprites', 'player.png'), 32, 96, 96)

        # Inizializza i bersagli
        self.targets = pygame.sprite.Group()
        self.targets_spawn_time = 3000
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

        # Controlla se il giocatore ha scelto un nome
        # Se no chiedi al giocatore di impostarlo

        if not os.path.exists(os.path.join(save_folder, 'name.dat')):
            self.state = self.STATES['ASK_NAME']



    def sync_data(self):
        '''Sincronizza i dati di gioco all'avvio'''

        # Se il file name.dat esiste leggi il contenuto e assegna il nome
        if os.path.exists(os.path.join(save_folder, 'name.dat')):
            with open(os.path.join(save_folder, 'name.dat'), 'r') as f:
                lines = f.readlines()
                self.name = lines[0][:8] # Assegna solo i primi otto caratteri, nel caso il nome
                                         # eccedesse il limite tramite modifiche esterne al file

        # Se il file id.dat esiste leggi il contenuto e assegna l'id
        id_path = os.path.join(save_folder, 'id.dat')
        db.id_file(id_path, db.generate_id())
        if os.path.exists(id_path):
            with open(id_path, 'r') as f:
                lines = f.readlines()
                self.id = int(lines[0])

        # Sincronizza i punteggi dal database
        for i, difficulty in enumerate(['EASY', 'NORMAL', 'HARD']):
            score = db.get_score(set_prefix + difficulty, str(self.id))
            self.high_scores[i] = score

    def shoot(self, ticks, trajectory, mouse_pos):
        '''Scocca una freccia
        
        ticks: I tick al momento del richiamo (pygame.time.get_ticks) 
        trajectory: La traiettoria parabolica
        mouse_pos: Posizione del mouse
        '''

        if mouse_pos.x <= self.player.rect.centerx: # Limita il raggio d'azione. Non si può sparare dietro al giocatore
            return
        arrow_was_shot = Arrow.arrow_spawner(self.arrows, ticks - self.previous_fire_ticks, self.fire_rate, trajectory, mouse_pos)
        if arrow_was_shot:
            self.previous_fire_ticks = ticks # Resetta il timer per sparare


    def draw_all(self, trajectory, mouse_pos, equation = ''):
        '''Disegna tutti gli elementi di gioco
        
        trajectory: La traiettoria parabolica
        mouse_pos: La posizione del mouse
        equation: L'equazione della parabola
        '''

        self.screen.fill((129, 212, 221))
        self.sky.draw(self.screen)

        self.player.draw(self.screen, self.frame_counter, 12)
        for target in list(self.targets)[::-1]: # Disegna i bersagli
            target.draw(self.screen, mouse_pos)

        # Disegna i punti rappresentanti la traiettoria
        for i in range(len(trajectory)):
            if i % 30 == 0 and i != 0: # Ogni trenta punti disegna un cerchio per indicare la traiettoria
                decrement = map_range(i, 0, len(trajectory) // 2 - 1, 20, 0)
                rect1 = pygame.Rect(-100, 0, decrement + 4, decrement + 4) # Linea di contorno
                rect2 = pygame.Rect(-100, 0, decrement, decrement)
                rect1.center = trajectory[i]
                rect2.center = trajectory[i]
                if rect2.width > 0:
                    pygame.draw.ellipse(self.screen, (0, 0, 0), rect1)
                    pygame.draw.ellipse(self.screen, (255, 255, 255), rect2)

        for arrow in list(self.arrows)[::-1]: # Disegna le frecce
            arrow.draw(self.screen)
        # Disegna l'arco e il terreno
        self.ground.draw(self.screen)
        self.draw_bow(trajectory)

        equation_label = font18.render(equation, False, (0, 0, 0))
        equation_rect = equation_label.get_rect()
        equation_rect.center = (mouse_pos.x, mouse_pos.y - 28)
        self.screen.blit(equation_label, equation_rect) # Disegna l'equazione sotto al cursore

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
            # Se c'è una divisione per zero, dividi invece per uno
            bow_hypo += 1
            bow_angle = -degrees(asin(bow_height / bow_hypo))

        # Disegna l'arco ruotato
        rotated_bow, rotated_bow_rect = rot_from_zero(self.bow, bow_angle)
        rotated_bow_rect.center = self.player.rect.center
        self.screen.blit(rotated_bow, rotated_bow_rect)

    def game_input(self, ticks, trajectory, mouse_pos):
        '''Gestisci gli input
        
        ticks: I tick al momento del richiamo (pygame.time.get_ticks) 
        trajectory: La traiettoria parabolica
        mouse_pos: Posizione del mouse
        '''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.game_quit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_BACKSLASH:
                    self.debug_mode = not self.debug_mode
                elif event.key == pygame.K_ESCAPE or event.key == pygame.K_p:
                    self.set_state('PAUSED')
            elif event.type == pygame.MOUSEBUTTONDOWN:
                self.shoot(ticks, trajectory, mouse_pos)

    def game_quit(self):
        '''Chiudi il gioco'''

        self.save_data() # Salva i dati prima di chiudere il gioco
        sys.exit()

    def set_state(self, state):
        '''Imposta lo stato del gioco'''

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
        '''Inizia la partita'''

        self.set_state('GAME')

        # Elimina tutti i bersagli e le frecce
        self.targets.empty()
        self.arrows.empty()

        # Resetta il punteggio e le vite
        self.score[0] = 0
        self.lives = 5 - (2 * self.difficulty)

    def mainmenu(self):
        '''Schermata principale'''

        if not self.synced: # Se i dati non sono sincronizzati, sincronizzali
            self.sync_data()
            self.synced = True
        
        # Immagine del titolo
        title_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'title.png')).convert_alpha()
        title_rect = title_image.get_rect()
        title_y = 32
        title_rect.topleft = (332, title_y)

        # Le immagini dei pulsanti
        play_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'play.png')).convert_alpha()
        mode_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'mode.png')).convert_alpha()
        quit_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'quit.png')).convert_alpha()
        leaderboard_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard.png')).convert_alpha()
        name_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'namechange.png')).convert_alpha()

        # I pulsanti del menu
        play_button = BaseButton(46, 280, play_image, self.start)
        mode_button = BaseButton(46, 350, mode_image, self.cycle_difficulty)
        quit_button = BaseButton(46, 425, quit_image, self.game_quit)
        leaderboard_button = BaseButton(646, 521, leaderboard_image, lambda: self.set_state('LEADERBOARD'))
        name_button = BaseButton(610, 465, name_image, lambda: self.set_state('ASK_NAME'))

        mode_text_coords = (mode_button.rect.left + mode_button.image.get_width() + 12, mode_button.rect.centery)


        time = 0

        while self.state == self.STATES['MENU']:

            dt = self.clock.tick(60)
            time += dt

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()

            title_rect.y = title_y + (sin(time / 250) * 10) # Calcola il moto armonico del titolo

            # Disegna i vari elementi
            self.screen.fill((129, 212, 221))
            self.sky.update(self.state)
            self.sky.draw(self.screen)
            self.screen.blit(title_image, title_rect)
            play_button.draw(self.screen)
            mode_button.draw(self.screen)
            quit_button.draw(self.screen)
            leaderboard_button.draw(self.screen)
            name_button.draw(self.screen)

            mode_label = font32.render(self.DIFFICULTIES[self.difficulty], False, (255,255,255))
            outline = font32.render(self.DIFFICULTIES[self.difficulty], False, (0,0,0))
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
            target_spawned = Target.target_spawner(self.targets, current_ticks - self.previous_target_ticks, self.targets_spawn_time, self.score[0])
            if target_spawned:
                self.previous_target_ticks = current_ticks

            for i in list(self.targets)[::-1]:
                out_of_screen = i.update(dt, self.state)
                if out_of_screen:
                    self.lives -= 1
                # Aggiorna i bersagli

            # Aggiorna il terreno
            self.ground.update(dt, self.state)

            # Gestione delle frecce
            for i in list(self.arrows)[::-1]:
                # Aggiorna tutte le frecce
                i.check_collisions(self.targets, self.score)
                i.update(self.player)

            self.game_input(current_ticks, trajectory, mouse_pos)
            self.draw_all(trajectory, mouse_pos, equation)
            self.hud()

            # Debug mode
            if self.debug_mode:
                self.debug(mouse_pos, trajectory)


            pygame.display.update()

            self.score[0] += db.receive_bonus()

            if self.score[0] > self.high_scores[self.difficulty]:
                self.high_scores[self.difficulty] = self.score[0]

            self.frame_counter += 1
            if self.lives <= 0:
                self.save_data()
                self.set_state('END')

    def save_data(self):
        '''Salva i dati'''

        print('Saving...')
        db.save_score(set_prefix + ['EASY', 'NORMAL', 'HARD'][self.difficulty], str(self.id), self.name, self.high_scores[self.difficulty])
        print('Saved.')

    def pause(self):
        '''Schermata di pausa'''

        continue_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'pausemenu', 'continue.png')).convert_alpha()
        menu_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'pausemenu', 'menu.png')).convert_alpha()
        # Pulsanti e relative immagini
        continue_button = BaseButton(325, 270, continue_image, lambda: self.set_state('GAME'))
        menu_button = BaseButton(230, 330, menu_image, return_bool=True)


        while self.state == self.STATES['PAUSED']:

            # Disegna gli elementi sullo schermo
            self.screen.fill((129, 212, 221))
            self.sky.draw(self.screen)
            self.hud()
            continue_button.draw(self.screen)
            if menu_button.draw(self.screen):
                self.save_data()
                self.set_state('MENU')

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_state('GAME')
            pygame.display.update()
        
    def ask_name(self):
        '''Schermata dove inserire il nome'''

        # Casella di testo dal modulo pygame_textinput
        box = pygame_textinput.TextInputVisualizer(font_object=font32)

        # Pulsante di conferma
        confirm_image = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'confirm.png')).convert_alpha()
        confirm_button = BaseButton(321, 357, confirm_image, lambda: self.set_name(box.value))

        choosename_label = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'choosename_label.png')).convert_alpha()

        while self.state == self.STATES['ASK_NAME']:

            events = pygame.event.get()

            # Disegna gli elementi della schermata
            self.screen.fill((129, 212, 221))
            self.sky.update(self.state)
            self.sky.draw(self.screen)

            box.update(events)
            if len(box.value) > 8:
                box.value = box.value[:-1]
                # Limita il nome a otto caratteri
            
            box_rect = box.surface.get_rect(center=(self.WIDTH // 2, self.HEIGHT // 2))
            confirm_button.draw(self.screen)
            self.screen.blit(box.surface, box_rect)
            self.screen.blit(choosename_label, choosename_label.get_rect(topleft=(190, self.HEIGHT // 3)))

            for event in events:
                if event.type == pygame.QUIT:
                    self.game_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_RETURN:
                        self.set_name(box.value)
                        self.state == self.STATES['MENU']

            pygame.display.update()

    def endscreen(self):
        '''Schermata di fine partita'''

        # Vari elementi della schermata
        gameover_label = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'endscreen', 'gameover.png')).convert_alpha()
        yourscore_label = pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'endscreen', 'score.png')).convert_alpha()
        continue_button = BaseButton(357, 374, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'endscreen', 'continue.png')), self.start)
        menu_button = BaseButton(288, 422, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'endscreen', 'menu.png')), lambda: self.set_state('MENU'))

        gameover_rect = gameover_label.get_rect(topleft=(266, 98))
        yourscore_rect = yourscore_label.get_rect(topleft=(216, 195))


        while self.state == self.STATES['END']:

            # Disegna tutti gli elementi della schermata
            score_label = font32.render(str(self.score[0]), False, (0, 0, 0))
            score_rect = score_label.get_rect(topleft=(474, 278))
            
            self.screen.fill((129, 212, 221))
            self.sky.update(self.state)
            self.sky.draw(self.screen)

            self.screen.blit(gameover_label, gameover_rect)
            self.screen.blit(yourscore_label, yourscore_rect)
            self.screen.blit(score_label, score_rect)
            continue_button.draw(self.screen)
            menu_button.draw(self.screen)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()

            pygame.display.update()

    def leaderboard(self):
        '''Schermata della classifica'''

        back_button = BaseButton(24, 528, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard', 'back.png')), lambda: self.set_state('MENU'))

        easy_button = BaseButton(26, 90, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard', 'easy.png')), return_bool=True)
        normal_button = BaseButton(26, 130, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard', 'normal.png')), return_bool=True)
        hard_button = BaseButton(26, 170, pygame.image.load(os.path.join(basefolder, 'assets', 'sprites', 'mainmenu', 'leaderboard', 'hard.png')), return_bool=True)

        timer = 0
        update_interval = 60e3 # Secondi di intervallo tra due aggiornamenti della classifica
        set_difficulty = 1
        DIFFICULTIES = ['EASY', 'NORMAL', 'HARD']
        top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
        score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)


        while self.state == self.STATES['LEADERBOARD']:
            
            # print(score_and_rank)
            dt = self.clock.tick()
            timer += dt

            if timer >= update_interval:
                top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)
                timer = 0

            self.screen.fill((129, 212, 221))
            self.sky.update(self.state)
            self.sky.draw(self.screen)

            if easy_button.draw(self.screen):
                set_difficulty = 0
                top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)

            if normal_button.draw(self.screen):
                set_difficulty = 1
                top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)

            if hard_button.draw(self.screen):
                set_difficulty = 2
                top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)

            back_button.draw(self.screen)

            for i, player in enumerate(top_players):
                rank = font18.render(str(i+1), False, (0, 0, 0))
                name = font18.render(player[0], False, (0, 0, 0))
                score = font18.render(str(player[1]), False, (0, 0, 0))

                y_position = 60 + (30 * i)

                self.screen.blit(rank, rank.get_rect(right=457, top=y_position))
                self.screen.blit(name, name.get_rect(topleft=(500, y_position)))
                self.screen.blit(score, score.get_rect(topleft=(687, y_position)))

            
            rank = font18.render(str(score_and_rank[1]), False, (0, 0, 0))
            name = font18.render(self.name, False, (0, 0, 0))
            score = font18.render(str(score_and_rank[0]), False, (0, 0, 0))

            self.screen.blit(font18.render('TU:', False, (0, 0, 0)), (500, 430))
            self.screen.blit(rank, rank.get_rect(right=457, top=460))
            self.screen.blit(name, name.get_rect(topleft=(500, 460)))
            self.screen.blit(score, score.get_rect(topleft=(687, 460)))

            # Disegna un indicatore affianco alla difficoltà selezionata
            outline_1 = pygame.Vector2(16, 85 + (40 * set_difficulty))
            outline_2 = pygame.Vector2(16, 116 + (40 * set_difficulty))

            indicator_1 = pygame.Vector2(16, 86 + (40 * set_difficulty))
            indicator_2 = pygame.Vector2(16, 115 + (40 * set_difficulty))

            pygame.draw.line(self.screen, 0, outline_1, outline_2, 5)
            pygame.draw.line(self.screen, (255, 255, 255), indicator_1, indicator_2, 3)

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game_quit()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.set_state('MENU')
                    if event.key == pygame.K_UP:
                        set_difficulty -= 1
                        if set_difficulty < 0:
                            set_difficulty = 2
                        top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                        score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)
                    elif event.key == pygame.K_DOWN:
                        set_difficulty += 1
                        if set_difficulty > len(DIFFICULTIES) - 1:
                            set_difficulty = 0
                        top_players = db.get_leaderboard(set_prefix + DIFFICULTIES[set_difficulty])
                        score_and_rank = db.get_score(set_prefix + DIFFICULTIES[set_difficulty], self.id, True)
                        
            
            pygame.display.update()



    def set_name(self, name):
        '''Imposta il nome'''

        if name == '':
            return
            # Se il nome è nullo non fare niente

        path = os.path.join(save_folder, 'name.dat')

        if not os.path.exists(str(Path(path).parent)):
            os.makedirs(str(Path(path).parent))
        with open(path, 'w') as f:
            f.write(name)
            self.name = name
        self.set_state('MENU')


    def hud(self):
        '''Disegna e gestisci la HUD'''

        # Testo del punteggio
        score_label = font32.render(f"{self.score[0]}", 1, (0, 0, 0))
        score_rect = score_label.get_rect(center=(self.WIDTH/2, 32))

        # Testo del record
        high_score_label = font24.render(f"{self.high_scores[self.difficulty]}", 1, (0, 0, 0))
        high_score_rect = high_score_label.get_rect(center=(self.WIDTH/2, 72))

        # Disegna le vite
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
        # Visualizza nel dettaglio la traiettoria e
        # i tre punti per la quale passa

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
        '''Loop principale'''

        while True: # Il loop è infinito siccome la chiusura del gioco è gestita dagli altri loop interni a questo
            self.ask_name()
            self.mainmenu()
            self.leaderboard()
            self.gameloop()
            self.endscreen()
            self.pause()


if __name__ == '__main__':
    gm = Game()

    gm.mainloop()
