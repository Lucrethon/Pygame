import pygame
import functions
from functions import coordinates
from models.main_player import Player
from models.models import Platform
from models.enemies import Enemy, Crawlid, Gruzzer
from models.utils import Orientation
from models.utils import States
from models.utils import Position
from models.utils import GameState

pygame.init()
pygame.font.init()


class GameMaster:

    def __init__(self):
        # El GameMaster es dueño de los grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.moving_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()

        # super().__init__(all_sprites, moving_sprites, enemy_group)

        self.timer = 0.0
        self.GAME_STATE = GameState.MAIN_MENU
        self.GAME_PHASE = 0
        self.GAME_WAVE = 0
        self.transition_state_duration = 2  # secs - wave_transition duration
        # pygame.font.Font('ruta_del_archivo', tamaño)
        self.title_font = pygame.font.Font(
            "fonts/HarnoldpixelRegularDemo-Yqw84.otf", 40
        )
        self.subtitle_font = pygame.font.Font(
            "fonts/HarnoldpixelRegularDemo-Yqw84.otf", 25
        )
        self.start_button_rect = None
        self.resume_button_rect = None
        self.return_button_rect = None
        self.game_phases = None
        self.waves_per_phase = None
        self.is_full_screen = False

    def update_game(
        self,
        player: Player,
        delta_time: float,
        screen: pygame.Surface,
        ground: Platform,
    ):

        # Funcion que se encarga de actualizar los diferentes estados del juego. No dibuja nada

        if (
            self.GAME_STATE == GameState.MAIN_MENU
            or self.GAME_STATE == GameState.PAUSE
            or self.GAME_STATE == GameState.GAME_OVER
            or self.GAME_STATE == GameState.VICTORY
        ):

            pass

        else:
            # en los siguientes estados se lee el movimiento del jugador en todo momento

            # leer input de movimiento jugador y detectar colisiones con el suelo
            player.update_player(delta_time, screen, ground)

            # Spawn phase
            if self.GAME_STATE == GameState.SPAWNING:

                # Handle spawning of enemies according to phase and wave

                # Se le pasa el numero de fase y oleada actual para spawnear los enemigos correspondientes
                # Se le pasa en strings para facilitar la lectura del diccionario, archivos json o similares
                current_phase = "phase_" + str(self.GAME_PHASE)
                current_wave = "wave_" + str(self.GAME_WAVE)

                self.current_phase(current_phase, current_wave, screen, ground)

                # After spawning, change state to playing
                self.GAME_STATE = GameState.PLAYING

            elif self.GAME_STATE == GameState.TRANSITION:
                self.timer += delta_time  # empieza a contar el tiempo de transicion

                if self.timer > self.transition_state_duration:
                    self.timer = 0.0  # reinicio del timer
                    self.GAME_WAVE += (
                        1  # se suma 1 a la oleada actual para ir a la siguiente oleada
                    )
                    self.GAME_STATE = (
                        GameState.SPAWNING
                    )  # cambio de estado a spawning para spawnear la siguiente oleada

                    # si la oleada actual es mayor que las oleadas por fase, se pasa a la siguiente fase
                    if self.GAME_WAVE > self.waves_per_phase:
                        self.GAME_PHASE += 1  # Cambio de fase
                        self.GAME_WAVE = 1  # reinicio de oleada a 1

                    else:
                        pass

            elif self.GAME_STATE == GameState.PLAYING:

                # actualizar todos los sprites en pantalla
                self.moving_sprites.update()

                # enemigos.update()
                for enemy in self.enemy_group:
                    enemy.update_enemy(delta_time, screen, ground)

                # detectar colisiones con enemigos
                self.handle_enemies_collision(player)
                self.handle_player_attack_collision(player)

                # verificar si hay enemigos en pantalla
                if not self.enemy_group:

                    # si no hay enemigos,
                    # la fase actual es igual al numero total de fases
                    # y la oleada actual es igual al numero total de oleadas por fase,
                    # se gana el juego
                    if (
                        self.GAME_PHASE == self.game_phases
                        and self.GAME_WAVE == self.waves_per_phase
                    ):
                        self.GAME_STATE = GameState.VICTORY

                    else:
                        # si no hay enemigos en pantalla, pasar a estado de transicion entre oleadas
                        self.timer = 0.0
                        player.reset_attack()
                        self.GAME_STATE = GameState.TRANSITION

                elif player.isDead:
                    # Si el jugador muere, cambiar a estado de game over
                    self.GAME_STATE = GameState.GAME_OVER

    def handle_events(
        self,
        events,
        player: Player,
        screen: pygame.Surface,
        ground: Platform,
        real_screen_size,
    ):

        # Funcion que se encarga de manejar los eventos de los diferentes estados del juego
        # Maneja tambien el imput del jugador en los diferentes estados del juego

        self.is_fullscreen(real_screen_size)
        mouse_pos = self.mouse_pos(real_screen_size)

        for event in events:

            # ------------ MAIN MENU ------------

            if self.GAME_STATE == GameState.MAIN_MENU:

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.start_button_rect.collidepoint(mouse_pos):
                        self.GAME_STATE = GameState.SPAWNING
                        self.GAME_PHASE = 1
                        self.GAME_WAVE = 1

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        self.GAME_STATE = GameState.SPAWNING
                        self.GAME_PHASE = 1
                        self.GAME_WAVE = 1

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()

            # ------------ PAUSE ------------

            elif self.GAME_STATE == GameState.PAUSE:

                if event.type == pygame.MOUSEBUTTONDOWN:

                    if self.resume_button_rect.collidepoint(mouse_pos):
                        self.GAME_STATE = GameState.PLAYING

                    elif self.return_button_rect.collidepoint(mouse_pos):

                        self.reset_game(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU

                elif event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:
                        self.GAME_STATE = GameState.PLAYING

            # ------------ GAME OVER ------------

            elif self.GAME_STATE == GameState.GAME_OVER:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()

                    elif event.key == pygame.K_RETURN:
                        self.reset_game(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU

            # ------------ VICTORY ------------

            elif self.GAME_STATE == GameState.VICTORY:

                if event.type == pygame.KEYDOWN:

                    if event.key == pygame.K_RETURN:

                        self.reset_game(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU

                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit()

            # ------------ PLAYING, TRANSICION OR SPAWING ------------

            else:

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.GAME_STATE = GameState.PAUSE

                    elif event.key == pygame.K_s:
                        player.trigger_attack(attack=True)

    def draw(
        self,
        screen: pygame.Surface,
        player: Player,
        background: pygame.Surface,
        ground: Platform,
    ):

        # Funcion que se encarga de dibujar los diferentes estados del juego

        if self.GAME_STATE == GameState.MAIN_MENU:
            screen.blit(background, (0, 0))
            self.display_main_menu(screen)

        elif self.GAME_STATE == GameState.PAUSE:
            screen.blit(background, (0, 0))
            # Los sprites se dibujan en la pausa debajo del boton de pausa
            for sprite in self.all_sprites:
                sprite.draw(screen)

            self.display_pause_menu(screen)

        elif self.GAME_STATE == GameState.GAME_OVER:
            screen.blit(background, (0, 0))
            self.display_game_over_screen(screen)

        elif self.GAME_STATE == GameState.VICTORY:
            screen.blit(background, (0, 0))
            self.display_victory_screen(screen)

        else:
            # ground platform se dibuja primero
            ground.draw(screen)
            screen.blit(background, (0, 0))
            # En todos los demas estados se dibujen los sprites
            for sprite in self.all_sprites:
                sprite.draw(screen)
                # call to .draw() method from GameObjects that can handle gifs
            player.draw_attack(screen)

    def set_up_player_position(
        self, player: Player, screen: pygame.Surface, ground: Platform
    ):
        # centrar al jugador en la pantalla al reiniciar el juego

        player.set_position(screen.get_width() / 2, ground.rect.top, True)

    def display_main_menu(self, screen: pygame.Surface):
        start_title = self.title_font.render(
            "Start", False, (15, 15, 27), (250, 251, 246)
        )

        start_title_rect = start_title.get_rect()
        start_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)

        self.start_button_rect = start_title_rect

        screen.blit(start_title, start_title_rect)

    def display_pause_menu(self, screen: pygame.Surface):

        pause_title = self.title_font.render(
            "Pause", False, (15, 15, 27), (250, 251, 246)
        )
        pause_title_rect = pause_title.get_rect()
        pause_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)

        resume_title = self.subtitle_font.render(
            "Resume", False, (15, 15, 27), (250, 251, 246)
        )
        resume_title_rect = resume_title.get_rect()
        resume_title_rect.midtop = (
            screen.get_width() / 2,
            pause_title_rect.bottom + 10,
        )
        self.resume_button_rect = resume_title_rect

        return_title = self.subtitle_font.render(
            "Return to Menu", False, (15, 15, 27), (250, 251, 246)
        )
        return_title_rect = return_title.get_rect()
        return_title_rect.midtop = (
            screen.get_width() / 2,
            resume_title_rect.bottom + 10,
        )
        self.return_button_rect = return_title_rect

        screen.blit(pause_title, pause_title_rect)
        screen.blit(resume_title, resume_title_rect)
        screen.blit(return_title, return_title_rect)

    def display_game_over_screen(self, screen: pygame.Surface):

        game_over_title = self.title_font.render(
            "Game Over", False, (15, 15, 27), (250, 251, 246)
        )
        game_over_title_rect = game_over_title.get_rect()
        game_over_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)

        press_enter_title = self.subtitle_font.render(
            "Press Enter to Restart", False, (15, 15, 27), (250, 251, 246)
        )
        press_enter_title_rect = press_enter_title.get_rect()
        press_enter_title_rect.midtop = (
            screen.get_width() / 2,
            game_over_title_rect.bottom + 10,
        )

        screen.blit(game_over_title, game_over_title_rect)
        screen.blit(press_enter_title, press_enter_title_rect)

    def display_victory_screen(self, screen: pygame.Surface):

        victory_title = self.title_font.render(
            "Victory", False, (15, 15, 27), (250, 251, 246)
        )
        victory_title_rect = victory_title.get_rect()
        victory_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)

        press_enter_title = self.subtitle_font.render(
            "Press Enter to Restart", False, (15, 15, 27), (250, 251, 246)
        )
        press_enter_title_rect = press_enter_title.get_rect()
        press_enter_title_rect.midtop = (
            screen.get_width() / 2,
            victory_title_rect.bottom + 10,
        )

        screen.blit(victory_title, victory_title_rect)
        screen.blit(press_enter_title, press_enter_title_rect)

    def handle_enemies_collision(self, player: Player):

        # Funcion que se encarga de manejar las colisiones entre el jugador y los enemigos

        # lista que comprueba colisiones entre el jugador y los enemigos
        enemies_collision = pygame.sprite.spritecollide(player, self.enemy_group, False)

        if enemies_collision:

            for enemy in enemies_collision:

                # si hay colision y el jugador esta en estado de daño o invulnerable, el jugador no recibe daño
                if player.action_state == States.KNOCKBACK or player.is_invulnerable:
                    pass
                else:
                    # si no esta en esos estados, el jugador recibe daño
                    player.take_damage()
                    functions.knockback(player, enemy, True)

    def handle_player_attack_collision(self, player: Player):

        # Funcion que se encarga de manejar las colisiones entre el ataque del jugador y los enemigos

        if player.active_hitbox:
            # Si el jugador tiene una hitbox activa (esta atacando)

            for enemy in self.enemy_group:

                # si el rect del enemigo colisiona con la hitbox activa del jugador
                if player.active_hitbox.colliderect(enemy.rect):

                    # si el enemigo no ha sido atacado ya en este ataque (comprobacion con lista interna del jugador)
                    if enemy not in player.enemies_attacked:

                        # si el jugador esta orientado hacia abajo, se aplica pogo y el enemigo recibe daño
                        if player.y_orientation == Orientation.DOWN:
                            enemy.take_damage()
                            functions.knockback(player, enemy, False)
                            player.trigger_pogo()
                            player.enemies_attacked.append(enemy)

                        # si el jugador tiene cualquier otra orientacion, no se aplica pogo y el enemigo recibe daño
                        else:
                            enemy.take_damage()
                            functions.knockback(player, enemy, False)
                            player.start_attack_recoil()
                            player.enemies_attacked.append(enemy)
                    else:
                        # si el enemigo ha sido atacado ya en este ataque, no se le aplica daño
                        pass

                else:
                    pass

    def returnEnemyWithPosition(
        self, screen: pygame.Surface, ground: Platform, enemy: Enemy, position: Position, facing: Orientation,
    ):
        # funcion que devuelve un enemigo en una posicion determinada de la pantalla

        # se recibe una clase de enemigo y se instancia un nuevo objeto de esa clase
        new_enemy = enemy(screen, facing)

        # se obtienen las coordenadas posibles para spawnear enemigos en la pantalla
        enemy_coords = coordinates(screen, ground, new_enemy)

        # se obtiene el valor del enum Position
        pos_key = position.value

        # si la clave existe en el diccionario de coordenadas, se retorna al enemigo posicionado en esas coordenadas
        if pos_key in enemy_coords:

            new_enemy.set_position(*enemy_coords[pos_key])

            return new_enemy

        else:
            # si no existe la clave, se retorna el enemigo en la posicion por defecto (centro de la pantalla)
            new_enemy.set_position(screen.get_width() / 2, ground.rect.top, True)
            
            return new_enemy

    def current_phase(
        self,
        phase_number: str,
        wave_number: str,
        screen: pygame.Surface,
        ground: Platform,
    ):
        # Funcion que se encarga de spawnear los enemigos de la fase y oleada actual

        phases = self.phases(
            screen, ground
        )  # se obtienen las fases y oleadas definidas
        total_phases = len(
            list(phases.keys())
        )  # se obtiene el numero total de fases definidas
        self.game_phases = (
            total_phases  # se actualiza el numero total de fases en el GameMaster
        )

        if phase_number in phases:
            # se comprueba si la fase actual existe en las fases definidas.
            # se tiene que recibir un string con el formato "phase_X", donde X es el numero de fase

            current_wave = list(phases[phase_number].keys())
            # Se obtiene el numero total de olas definidas en la fase actual
            self.waves_per_phase = len(
                current_wave
            )  # se actualiza el numero total de oleadas por fase en el GameMaster

            wave = phases[phase_number].get(wave_number, [])
            # se obtienen los enemigos de la oleada actual. Si no existe, se retorna una lista vacia

            for enemy in wave:
                # por cada enemigo en la oleada actual, se añade a los grupos de sprites del GameMaster

                self.all_sprites.add(enemy)
                self.moving_sprites.add(enemy)
                self.enemy_group.add(enemy)

    def phases(self, screen: pygame.Surface, ground: Platform):

        # Diccionario que define las fases y oleadas del juego

        phases = {
            "phase_1": {
                "wave_1": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_RIGHT_EDGE, Orientation.LEFT
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_LEFT_EDGE, Orientation.RIGHT
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Gruzzer, Position.MIDDLE_RIGHT_EDGE, Orientation.LEFT
                    ),
                ],
                "wave_2": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_RIGHT_EDGE, Orientation.LEFT
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_LEFT_EDGE, Orientation.RIGHT
                    ),
                ],
            },
            "phase_2": {
                "wave_1": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.QUARTER_TOP_EDGE, Orientation.LEFT
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.THREE_QUARTER_TOP_EDGE, Orientation.RIGHT
                    ),
                ],
                "wave_2": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.QUARTER_TOP_EDGE, Orientation.LEFT
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.THREE_QUARTER_TOP_EDGE, Orientation.RIGHT
                    ),
                ],
            },
        }

        return phases

    def reset_game(self, player: Player, screen: pygame.Surface, ground: Platform):
        # Funcion que se encarga de reiniciar el juego

        self.all_sprites.remove(self.enemy_group)
        self.moving_sprites.empty()
        self.enemy_group.empty()
        player.reset(screen)
        self.set_up_player_position(player, screen, ground)
        self.GAME_PHASE = 0
        self.GAME_WAVE = 0
        self.timer = 0.0

    def mouse_pos(self, real_screen: pygame.Surface):

        # Funcion que se encarga de calcular correctamente la posición del ratón, ya sea en pantalla completa o en modo ventana.
        # Devuelve la posición del ratón ajustada si está en pantalla completa, o la posición normal si está en modo ventana.

        mouse_virtual_pos = pygame.mouse.get_pos()

        virtual_width = 960
        virtual_height = 540

        # Calcular el factor de escala actual (Dinámico)
        # ¿Cuántas veces cabe mi juego pequeño en la pantalla actual?
        scale_x = real_screen.get_width() / virtual_width
        scale_y = real_screen.get_height() / virtual_height

        # Usamos el menor de los dos para mantener la proporción (aspect ratio)
        scale_factor = min(scale_x, scale_y)

        adj_mouse_x = (mouse_virtual_pos[0]) / scale_factor
        adj_mouse_y = (mouse_virtual_pos[1]) / scale_factor

        mouse_adj_pos = (adj_mouse_x, adj_mouse_y)

        if self.is_full_screen:
            return mouse_adj_pos
        else:
            return mouse_virtual_pos

    def is_fullscreen(self, real_screen: pygame.Surface):

        # Funccion que se encarga de actualizar el estado self.is_full_screen
        # para que el método mouse_pos pueda calcular correctamente la posición del ratón

        if real_screen.get_size() != (960, 540):
            self.is_full_screen = True
        else:
            self.is_full_screen = False
