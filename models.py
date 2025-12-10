import pygame
import gif_pygame
import gif_pygame.transform
from abc import ABC, abstractmethod
from enum import Enum
import mixin
import functions
from functions import coordinates

pygame.init()
pygame.font.init()


class States(Enum):
    IDDLE = 1
    ATTACKING = 2
    KNOCKBACK = 3
    RECOILING = 4
    SPAWNING = 5
    WALKING = 6
    JUMPING = 7
    FALLING = 8
    DEAD = 9




class Orientation(Enum):
    RIGTH = 1
    LEFT = 2
    UP = 3
    DOWN = 4


class GameObject(ABC, pygame.sprite.Sprite):

    def __init__(self, image, *groups):
        super().__init__(*groups)
        self.image = image
        self.rect = self.image.get_rect()  # get the size of the image to create a rects

    # if self.image is .gif, it has to be place on the screen diferently than static images that uses blit(). Gifs have to be placed with .render()

    # sintaxis: gif.render(screen_size, (gif_coordinates_tobe_placed))

    @abstractmethod
    def draw(self, screen):
        if hasattr(
            self.image, "render"
        ):  # this condition check if an object (self.image in this case) has certain atribute ("render" in this case, proper of gif_pygame library (gif objects))

            self.image.render(screen, (self.rect))

        else:  # if not, it can draw also png and jpg images as well
            screen.blit(self.image, (self.rect))
            # .move_ip(x, y) moves the rect to those coordenates

    def set_position(self, x_pos, y_pos, aling_bottom=False):

        if aling_bottom:
            self.rect.midbottom = (x_pos, y_pos)
            # midbottom: Se refiere a la coordenada X y a la coordenada Y del punto central inferior de un rectángulo.

        else:
            self.rect.topleft = (x_pos, y_pos)


class Player(GameObject, mixin.Gravity):
    def __init__(self, image, move_speed, sprite_attack_slash):
        # Los grupos se pasarán desde el GameMaster
        super().__init__(image)

        # --- HEALTH ---
        self.HP = 5

        # --- ATTACK SPRITES ---
        self.sprite_attack_slash = sprite_attack_slash
        self.active_slash_sprite = None

        # --- CURRENT SPEED ---
        self.x_vel = 0
        self.y_vel = 0

        # --- CONSTANTES DE FUERZA ---
        self.move_speed = move_speed
        self.gravity = 2700
        self.jump_force = -1000
        self.knockback_y_force = -100
        self.knockback_x_force = 600
        self.air_friction = 0.90  # fuerza de arrastre que se opone al movimiento de un objeto al atravesar el aire
        self.attack_recoil_force = 300
        self.pogo_force = -800

        # --- STATES ---
        self.movement_state = States.IDDLE #state that handles only movement (walking, jumping, falling). It allows player input
        self.action_state = None #state that handles actions that block player input (attacking, hurt, recoiling)

        # --- EFFECTS OF ACCTION ---
        self.active_hitbox = None
        self.is_invulnerable = False  # invulnerability state after knockback to avoid multiple collisions at the same time

        # --- ORIENTATION AND POSITION ---
        self.orientation = Orientation.RIGTH
        self.is_on_ground = True  # <-- Is not jumping
        self.attack_orientation = Orientation.RIGTH

        # --- DURATION OF STATES (SECONDS) ---
        # Knockback state
        self.knockback_duration = 0.08
        # Attacking state
        self.build_up_attack_duration = 0.08
        self.active_frames_attack_duration = 0.07
        self.recovery_attack_duration = 0.08
        # Invulnerability state
        self.invulnerability_duration = 0.9
        # Recoil state
        self.attack_recoil_duration = 0.07

        # --- TIMERS ---
        self.timer = 0.0
        self.attack_recoil_timer = 0.0
        self.invulnerability_timer = (
            0.0  # separate time to count time even if the player is attacking or iddle.
        )
        self.knockback_timer = 0.0

        # --- FLAGS ---
        self.just_pogoed = False
        self.just_jumped = False
        self.isDead = False

        # --- ARRAYS ---
        self.enemies_attacked = []

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)
    
    def keyboard_input(self):
        get_pressed_keys = pygame.key.get_pressed()
        # set a key that occurrs while the player get pressed a button on the keyboard

        move_right = get_pressed_keys[pygame.K_RIGHT]
        move_left = get_pressed_keys[pygame.K_LEFT]
        jumping = get_pressed_keys[pygame.K_SPACE]
        face_up = get_pressed_keys[pygame.K_UP]
        face_down = get_pressed_keys[pygame.K_DOWN]

        return move_right, move_left, jumping, face_up, face_down

    def update_player(
        self,
        delta_time,
        screen,
        ground,
    ):

        # 1. INPUTS Y ESTADOS DE ACCIÓN
        # -----------------------------
        # Gestiona estados prioritarios (atacar, herido) que pueden anular el control del jugador.
        move_right, move_left, jumping, face_up, face_down = self.keyboard_input()

        # Actualiza timers de acción
        if self.action_state == States.ATTACKING:
            self.attack_update(delta_time)

        if self.is_invulnerable:
            self.invulnerability_timer += delta_time
            if self.invulnerability_timer >= self.invulnerability_duration:
                self.is_invulnerable = False

        # Lógica de estados que bloquean el movimiento
        if self.action_state == States.KNOCKBACK:
            self.knockback_update(delta_time)
            
        elif self.action_state == States.RECOILING:
            self.attack_recoil_timer += delta_time
            if self.attack_recoil_timer >= self.attack_recoil_duration:
                self.action_state = None
                self.attack_recoil_timer = 0.0
        else:
            # Si no hay bloqueo, procesa el movimiento normal del jugador
            current_x_speed = 0
            current_x_speed = self.movement(move_right, move_left)
            self.x_vel = current_x_speed
            self.jump(jumping)
            self.facing_input(face_down, face_up)

        # 2. APLICAR FÍSICA
        # -----------------
        # Aplica fuerzas globales como la gravedad para tener las velocidades finales.
        super().apply_gravity(delta_time)

        # 3. MOVER AL JUGADOR
        # -------------------
        # Calcula el desplazamiento y actualiza la posición del rect.
        delta_x = 0  # variation in x
        delta_y = 0  # variation in y
        delta_x = self.x_vel * delta_time
        delta_y = self.y_vel * delta_time

        # Evita que el jugador salga de la pantalla
        delta_x = self.not_cross_edge_screen(screen, delta_x)

        # Aplica el movimiento al rect
        self.rect.x += delta_x
        self.rect.y += delta_y

        # 4. GESTIONAR COLISIONES
        # -----------------------
        # Corrige la posición del jugador si colisiona con el entorno (ej. suelo).
        super().check_ground_collision(ground)

        # 5. ACTUALIZAR ESTADO DE MOVIMIENTO
        # ----------------------------------
        # Con la posición y velocidades finales, determina el estado de animación (IDLE, WALKING, etc.).
        self.update_movement_state()

    def update_movement_state(self):
        
        if self.is_on_ground == False: 
            if self.y_vel < 0: #SI ESTA SUBIENDO
                self.movement_state = States.JUMPING
            
            elif self.y_vel >= 0: #SI ESTA CAYENDO 
                    self.movement_state = States.FALLING
        
        else: #SI ESTA EN EL SUELO
            if self.x_vel != 0:
                self.movement_state = States.WALKING
                
            elif self.x_vel == 0 and self.y_vel == 0:
                self.movement_state = States.IDDLE
                

        return self.movement_state
    
    def movement(
        self, right=False, left=False
    ):  # --> Return x speed (update player position)

        current_x_speed = 0

        if right:
            current_x_speed = self.move_speed

            if self.orientation == Orientation.RIGTH:
                pass
            else:

                # flip sprite to right
                self.orientation = Orientation.RIGTH
                gif_pygame.transform.flip(self.image, True, False)

        if left:
            current_x_speed = -self.move_speed

            if self.orientation == Orientation.LEFT:
                pass

            else:
                # flip sprite to left
                self.orientation = Orientation.LEFT
                gif_pygame.transform.flip(self.image, True, False)

        return current_x_speed

    def jump(self, jump=False):  # (update player y position)

        # Pogo
        if self.just_pogoed:
            self.y_vel = self.pogo_force
            # self.is_on_ground = True
            self.just_pogoed = False
            self.just_jumped = False

        # if the player is not jumping and maitain Space button pressed (long jump)
        elif jump and self.is_on_ground:

            self.y_vel = self.jump_force
            self.is_on_ground = False
            self.just_jumped = True

        # if the player is jumping (no ground collision yet, self.isJumping = True) and press space for a short time (short jump)
        elif not jump and self.y_vel < 0 and self.just_jumped:
            self.y_vel *= 0.5
            self.is_on_ground = False

        # Resetea el flag de salto corto si empezamos a caer
        if self.y_vel >= 0:
            self.just_jumped = False

    def facing_input(self, down=False, up=False):  # (update player facing)

        # Facing up
        if up and not down:
            self.orientation = Orientation.UP

        # Facing down
        elif down and not up:
            self.orientation = Orientation.DOWN

        # else:
        #     self.facing_up = False
        #     self.facing_down = False

    def not_cross_edge_screen(self, screen, delta_x):  # return position variation in X
        # setting player to don't go off the edge of the screen

        if self.rect.right + delta_x >= screen.get_width():
            delta_x = screen.get_width() - self.rect.right

        if self.rect.left + delta_x <= 0:
            delta_x -= self.rect.left

        return delta_x

    def trigger_attack(
        self, attack=False
    ):  # call this method in the main cycle (trigger. This method changes player state)

        if attack and self.action_state == None:

            # setting self state
            self.action_state = States.ATTACKING

            # restart self.timer
            self.timer = 0.0

    def attack_update(
        self, delta_time
    ):  # this method updates player movements on the screen

        self.timer += delta_time

        # buildup phase
        if self.timer < self.build_up_attack_duration:

            self.active_hitbox = None

            # buildup animation
            pass

        # active phase
        elif self.timer < (
            self.build_up_attack_duration + self.active_frames_attack_duration
        ):
            if self.active_hitbox is None:

                self.enemies_attacked.clear()  # vaciar lista de enemigos golpeados anteriormente

                # lock orientation
                self.lock_attack_ortientation()

                # attack animation

            # create hitbox & slash attack animation
            self.active_hitbox, self.active_slash_sprite = self.get_attack_components()

        # recovery phase
        elif self.timer < (
            self.build_up_attack_duration
            + self.active_frames_attack_duration
            + self.recovery_attack_duration
        ):

            self.active_hitbox = None

            # recovery animation
            pass

        else:
            # reset
            self.action_state = None
            # reset timer
            self.timer = 0.0

    def lock_attack_ortientation(self):

        # up the player
        if self.orientation == Orientation.UP:

            self.attack_orientation = Orientation.UP

        # down the player
        elif self.orientation == Orientation.DOWN:

            self.attack_orientation = Orientation.DOWN

        # right the player
        elif self.orientation == Orientation.RIGTH:

            self.attack_orientation = Orientation.RIGTH

        # left the player
        else:
            if self.orientation == Orientation.LEFT:

                self.attack_orientation = Orientation.LEFT

    def get_attack_components(
        self,
    ):  # --> RECT & SPRITE POSITION ACORDING PLAYER ORIENTATION

        hitbox = None
        rotate_slash_sprite = None

        # up the player
        if self.attack_orientation == Orientation.UP:

            rotate_slash_sprite = pygame.transform.rotate(
                self.sprite_attack_slash, -270
            )
            hitbox = rotate_slash_sprite.get_rect()
            hitbox.midbottom = self.rect.midtop

        # down the player
        elif self.attack_orientation == Orientation.DOWN and not self.is_on_ground:

            rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, -90)
            hitbox = rotate_slash_sprite.get_rect()
            hitbox.midtop = self.rect.midbottom

        # right the player
        elif self.attack_orientation == Orientation.RIGTH:

            rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, 0)
            hitbox = rotate_slash_sprite.get_rect()
            hitbox.midleft = self.rect.midright

        # left the player
        else:
            if self.attack_orientation == Orientation.LEFT:

                rotate_slash_sprite = pygame.transform.rotate(
                    self.sprite_attack_slash, -180
                )
                hitbox = rotate_slash_sprite.get_rect()
                hitbox.midright = self.rect.midleft

        return hitbox, rotate_slash_sprite

    def draw_attack(self, screen):  # DRAW SLASH SPRITE AND RECT

        if self.action_state == States.ATTACKING or self.action_state == States.RECOILING:

            # draw hitbox
            if self.active_hitbox and self.active_slash_sprite:

                screen.blit(self.active_slash_sprite, self.active_hitbox)

        else:
            pass

    def take_damage(self):  # call this method in the main cycle

        # set up HP
        self.HP -= 1

        self.trigger_knockback()
        self.trigger_invulnerability()

    def trigger_knockback(self):

        if self.action_state == States.KNOCKBACK:
            return

        self.action_state = States.KNOCKBACK

        self.timer = 0.0

        self.is_on_ground = False

        # Cancelar cualquier ataque activo para evitar bugs
        self.active_hitbox = None
        self.active_slash_sprite = None

    def trigger_invulnerability(self):

        if self.is_invulnerable:
            return
        # The player cannot reaceive damage while self.is_invulnerable = True

        # set invulnerability state
        self.is_invulnerable = True

        self.invulnerability_timer = 0.0

    def knockback_update(self, delta_time):

        # start the timer
        self.timer += delta_time

        # apply friction
        self.x_vel *= self.air_friction

        # Detenerlo si es muy lento
        if abs(self.x_vel) < 10:
            self.x_vel = 0

        if self.timer >= self.knockback_duration:
            self.action_state = None
            self.timer = 0.0
            # Importante: resetear la velocidad X al salir del knockback
            self.x_vel = 0

    def start_attack_recoil(
        self,
    ):  # <-- Funcion que llama el arbitro de juego (disparador)

        # start the timer
        self.attack_recoil_timer = 0

        self.action_state = States.RECOILING

        self.attack_recoil()

    def attack_recoil(self):

        x_direction = 0

        # set up knockback direction
        if self.orientation == Orientation.RIGTH:
            x_direction = -1  # empuje a la izquierda

        elif self.orientation == Orientation.LEFT:
            x_direction = 1  # empuje a la derecha

        else:
            pass

        # --- ADD UP AND DOWN DIRECTION --

        # set up knockback x speed
        self.x_vel = self.attack_recoil_force * x_direction

    def trigger_pogo(self):
        self.just_pogoed = True

    def reset(self):
        # Funcion que se encarga de reiniciar el estado del jugador a sus valores iniciales.
        self.HP = 5
        self.action_state = States.IDDLE
        self.movement_state = None
        self.x_vel = 0
        self.y_vel = 0
        self.is_on_ground = True
        self.is_invulnerable = False
        self.isDead = False

        # --- Limpiar estado de ataque ---
        self.active_hitbox = None
        self.active_slash_sprite = None
        self.enemies_attacked.clear()

        # --- Reiniciar Timers ---
        self.timer = 0.0
        self.attack_recoil_timer = 0.0
        self.invulnerability_timer = 0.0
        self.knockback_timer = 0.0

    def reset_attack(self):
        self.active_hitbox = None
        self.active_slash_sprite = None
        self.enemies_attacked.clear()

    def player_sprites(self):
        
        player_sprites = {
            
            "IDDLE": {
                "iddle_x3": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x3.gif"),
                "iddle_x6": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x6.gif"),
            },
            
            "WALKING": {
                    "walking_x3": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x3.gif"),
                    "walking_x6": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x6.gif"),
            },
            
            "ATTACKING": {
                
                "RIGTH": {
                    
                    "buildup_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing1.png").convert_alpha(),
                    "active_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing2.png").convert_alpha(),
                    "recovery_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing3.png").convert_alpha(),
                    
                },
                
                "LEFT": {
                    
                    "abuildup_phase": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Slashing1.png").convert_alpha()), True, False),
                    "active_phase": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Slashing2.png").convert_alpha()), True, False),
                    "recovery_phase": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Slashing3.png").convert_alpha()), True, False),
                    
                },
                
                "UP": {
                    "buildup_phase": pygame.image.load("./assets/Player_Sprites/Up_Slashing1.png").convert_alpha(),
                    "active_phase": pygame.image.load("./assets/Player_Sprites/Up_Slashing2.png").convert_alpha(),
                    "recovery_phase": pygame.image.load("./assets/Player_Sprites/Up_Slashing3.png").convert_alpha(),
                    
                },
                
                "DOWN": {
                    "buildup_phase": pygame.image.load("./assets/Player_Sprites/Down_Slashing1.png").convert_alpha(),
                    "active_phase": pygame.image.load("./assets/Player_Sprites/Down_Slashing2.png").convert_alpha(),
                    "recovery_phase": pygame.image.load("./assets/Player_Sprites/Down_Slashing3.png").convert_alpha(),
                
                },
                
            },
            
            "JUMPING": {
                
                "jumping1": pygame.image.load("./assets/Player_Sprites/Player_Jumping1.png").convert_alpha(),
                "jumping2": pygame.image.load("./assets/Player_Sprites/Player_Jumping2.png").convert_alpha(),
                "jumping3": pygame.image.load("./assets/Player_Sprites/Player_Jumping3.png").convert_alpha(),
                "jumping4": pygame.image.load("./assets/Player_Sprites/Player_Jumping4.png").convert_alpha(),
            
            },
            
            "FALLING": {
            
                    "falling1": pygame.image.load("./assets/Player_Sprites/Player_Falling1.png").convert_alpha(),
                    "falling2": pygame.image.load("./assets/Player_Sprites/Player_Falling2.png").convert_alpha(),
                    "falling3": pygame.image.load("./assets/Player_Sprites/Player_Falling3.png").convert_alpha(),
                    "falling4": pygame.image.load("./assets/Player_Sprites/Player_Falling4.png").convert_alpha(),
                    "falling5": pygame.image.load("./assets/Player_Sprites/Player_Falling5.png").convert_alpha(),
            },
            
            "KNOCKBACK": {
            "knockback": pygame.image.load("./assets/Player_Sprites/Player_Knockback.png").convert_alpha(),
            
            },
            
        }
        
        return player_sprites

    def draw_player_states(self):
        
        pass

class Platform(GameObject):
    def __init__(self, image, *groups):
        super().__init__(image, *groups)

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self):
        pass


class Enemy(GameObject, mixin.Gravity, mixin.CrossScreen):

    def __init__(self, image):
        # Los grupos se pasarán desde el GameMaster al crear el enemigo
        super().__init__(image)

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    @abstractmethod
    def update_enemy(self):
        pass

    @abstractmethod
    def spawning(self):
        # animacion de spawn
        pass


class Crawlid(Enemy):
    def __init__(self):
        # Crear/Cargar la imagen específica para el enemig0
        image = pygame.Surface([90, 90])
        image.fill((255, 0, 0))

        # Llamar al constructor de la clase padre (Enemy) con estos atributos
        super().__init__(image)

        # --- CONSTANTES DE FUERZA ---
        self.move_speed = 240
        self.knockback_y_force = -500
        self.knockback_x_force = 600
        self.gravity = 2700
        self.air_friction = 0.90

        # --- CURRENT SPEED ---
        self.x_vel = 0
        self.y_vel = 0

        # --- HEALTH ---
        self.HP = 5

        # --- STATE OF ACTION ---
        self.state = States.IDDLE
        self.isDead = False

        # --- ORIENTATION AND POSITION ---
        self.orientation = Orientation.RIGTH
        self.is_on_ground = True  # <-- Is not jumping

        # --- TIMERS ---
        self.timer = 0.0
        self.knockback_duration = 0.2

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def update_enemy(
        self,
        delta_time,
        screen,
        ground,
    ):

        delta_x = 0  # variation in x
        delta_y = 0  # variation in y

        # Knockback State
        if self.state == States.KNOCKBACK:

            self.knockback_update(delta_time)
            # Usa la velocidad de knockback
        else:
            self.x_vel = self.move_speed

        # aply gravity
        super().apply_gravity(delta_time)

        # Check screen collision
        super().not_cross_edge_screen(screen)

        # updates rect position

        delta_x += self.x_vel * delta_time
        delta_y = self.y_vel * delta_time

        # Move rect
        self.rect.move_ip(delta_x, delta_y)

        # Check ground collision
        super().check_ground_collision(ground)

    def take_damage(self):

        self.HP -= 1

        self.state = States.KNOCKBACK

        self.is_on_ground = False

        # restart timer
        self.timer = 0.0

        if self.HP <= 0:
            self.isDead = True
            super().kill()

        # Knockback physic

    def knockback_update(self, delta_time):  # update player position in knockbak state

        # start the timer
        self.timer += delta_time

        # apply friction
        self.x_vel *= self.air_friction

        # Detenerlo si es muy lento
        if abs(self.x_vel) < 10:
            self.x_vel = 0

        if self.timer >= self.knockback_duration:
            self.state = States.IDDLE
            self.timer = 0.0
            # Importante: resetear la velocidad X al salir del knockback
            self.x_vel = 0

    def spawning(self):
        # animacion de spawn
        pass


class GameState(Enum):

    MAIN_MENU = 1
    PLAYING = 2
    PAUSE = 3
    SPAWNING = 4
    GAME_OVER = 5
    VICTORY = 6
    TRANSITION = 7


class Position(Enum):
    GROUND_RIGHT_EDGE = "ground_right_edge"
    MIDDLE_RIGHT_EDGE = "1/2_right_edge"
    GROUND_LEFT_EDGE = "ground_left_edge"
    MIDDLE_LEFT_EDGE = "1/2_left_edge"
    QUARTER_TOP_EDGE = "1/4_top_edge"
    MIDDLE_TOP_EDGE = "1/2_top_edge"
    THREE_QUARTER_TOP_EDGE = "1/8_top_edge"


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
                        if player.orientation == Orientation.DOWN:
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
        self, screen: pygame.Surface, ground: Platform, enemy: Enemy, position: Position
    ):
        # funcion que devuelve un enemigo en una posicion determinada de la pantalla

        # se recibe una clase de enemigo y se instancia un nuevo objeto de esa clase
        new_enemy = enemy()

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
                        screen, ground, Crawlid, Position.GROUND_RIGHT_EDGE
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_LEFT_EDGE
                    ),
                ],
                "wave_2": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_RIGHT_EDGE
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.GROUND_LEFT_EDGE
                    ),
                ],
            },
            "phase_2": {
                "wave_1": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.QUARTER_TOP_EDGE
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.THREE_QUARTER_TOP_EDGE
                    ),
                ],
                "wave_2": [
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.QUARTER_TOP_EDGE
                    ),
                    self.returnEnemyWithPosition(
                        screen, ground, Crawlid, Position.THREE_QUARTER_TOP_EDGE
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
        player.reset()
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
