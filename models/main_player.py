import pygame
import gif_pygame
import models.mixin as mixin
from models.models import GameObject
from models.utils import Orientation
from models.utils import States
from models.utils import AttackState
    
class Player(GameObject, mixin.Gravity):
    def __init__(self, sprite_attack_slash, image):
        # Los grupos se pasarán desde el GameMaster
        
        super().__init__(image)

        self.player_sprites = self.player_sprites()
        
        # --- HEALTH ---
        self.HP = 5

        # --- ATTACK SPRITES ---
        self.sprite_attack_slash = sprite_attack_slash
        self.active_slash_sprite = None
        self.attack_state = None

        # --- CURRENT SPEED ---
        self.x_vel = 0
        self.y_vel = 0

        # --- CONSTANTES DE FUERZA ---
        self.move_speed = 300
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
        #self.orientation = Orientation.RIGHT
        self.x_orientation = Orientation.RIGHT
        self.y_orientation = Orientation.NEUTRAL
        self.is_on_ground = True  # <-- Is not jumping
        self.attack_orientation = Orientation.RIGHT

        # --- DURATION OF STATES (SECONDS) ---
        # Knockback state
        self.knockback_duration = 0.2
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
        self.jumping_time = 0.0
        self.falling_time = 0.0

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
        # Gestion de estados prioritarios
        move_right, move_left, jumping, face_up, face_down = self.keyboard_input()

        # Actualiza timers de acción
        if self.action_state == States.ATTACKING:
            self.attack_update(delta_time)

        if self.is_invulnerable:
            self.invulnerability_timer += delta_time
            if self.invulnerability_timer >= self.invulnerability_duration:
                self.is_invulnerable = False

        # Lógica de estados que bloquean el movimiento del jugador (knockback, recoiling)
        if self.action_state == States.KNOCKBACK:
            self.knockback_update(delta_time)
            
        elif self.action_state == States.RECOILING:
            self.attack_recoil_timer += delta_time
            if self.attack_recoil_timer >= self.attack_recoil_duration:
                self.action_state = None
                self.attack_recoil_timer = 0.0
        else:
            # Si no hay bloqueo, se procesa el movimiento normal del jugador
            current_x_speed = 0
            current_x_speed = self.movement(move_right, move_left)
            self.x_vel = current_x_speed
            self.jump(jumping)
            self.facing_input(face_down, face_up)

        # 2. FÍSICAS
        # -----------------
        # Aplicar fuerzas globales como la gravedad para tener las velocidades finales
        super().apply_gravity(delta_time)

        # 3. MOVER AL JUGADOR
        # -------------------
        # Calculo del desplazamiento y actualizacion de la posición del rect.
        delta_x = 0  # variation in x
        delta_y = 0  # variation in y
        delta_x = self.x_vel * delta_time
        delta_y = self.y_vel * delta_time

        # Evita que el jugador salga de la pantalla
        delta_x = self.not_cross_edge_screen(screen, delta_x)

        # Aplicar el movimiento al rect
        self.rect.x += delta_x
        self.rect.y += delta_y

        # 4. COLISIONES
        # -----------------------
        # Corrige la posición del jugador si colisiona con el entorno (ej. suelo).
        super().check_ground_collision(ground)

        # 5. ACTUALIZAR ESTADO DE MOVIMIENTO
        # ----------------------------------
        # Con la posición y velocidades finales, determina el estado de animación (IDLE, WALKING, etc.).
        self.update_movement_state()
        self.set_up_sprite_state(screen)

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
            
            #right orientation (x_orientation)
            if self.x_orientation == Orientation.RIGHT:
                pass
            
            else:
                self.x_orientation = Orientation.RIGHT
        #left orientation (x_orientation)
        elif left:
            current_x_speed = -self.move_speed

            if self.x_orientation == Orientation.LEFT:
                pass

            else:
                self.x_orientation = Orientation.LEFT

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
        
        #up orientation (y_orientation)
        if up:
            if self.y_orientation == Orientation.UP:
                pass
            else:
                self.y_orientation = Orientation.UP

        #down orientation (y_orientation)
        elif down:
            if self.y_orientation == Orientation.DOWN:
                pass
            else:
                self.y_orientation = Orientation.DOWN
        
        else:
            self.y_orientation = Orientation.NEUTRAL
            
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
            
            self.attack_state = AttackState.BUILDUP

            self.active_hitbox = None

            # buildup animation
            pass

        # active phase
        elif self.timer < (
            self.build_up_attack_duration + self.active_frames_attack_duration
        ):
            if self.active_hitbox is None:
                
                self.attack_state = AttackState.ACTIVE

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
            self.attack_state = AttackState.RECOVERY

            self.active_hitbox = None

            # recovery animation
            pass

        else:
            # reset
            self.action_state = None
            self.attack_state = None
            # reset timer
            self.timer = 0.0

    def lock_attack_ortientation(self):
        
        if self.y_orientation != Orientation.NEUTRAL:

            # up the player
            if self.y_orientation == Orientation.UP:

                self.attack_orientation = Orientation.UP

            # down the player
            elif self.y_orientation == Orientation.DOWN:

                self.attack_orientation = Orientation.DOWN

        # right the player
        elif self.x_orientation == Orientation.RIGHT:

            self.attack_orientation = Orientation.RIGHT

        # left the player
        else:
            if self.x_orientation == Orientation.LEFT:

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
        elif self.attack_orientation == Orientation.RIGHT:

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
        if self.x_orientation == Orientation.RIGHT:
            x_direction = -1  # empuje a la izquierda

        elif self.x_orientation == Orientation.LEFT:
            x_direction = 1  # empuje a la derecha

        else:
            pass

        # --- ADD UP AND DOWN DIRECTION --

        # set up knockback x speed
        self.x_vel = self.attack_recoil_force * x_direction

    def trigger_pogo(self):
        self.just_pogoed = True

    def reset(self, screen: pygame.Surface):
        # Funcion que se encarga de reiniciar el estado del jugador a sus valores iniciales.
        self.HP = 5
        self.action_state = None
        self.movement_state = States.IDDLE
        self.image = self.set_up_sprite_state(screen)
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
        
        #Diccionario que contiene todos los sprites del jugador organizados por estado y orientación
        #Dentro de cada estado, hay sub-diccionarios para cada orientación (DERECHA, IZQUIERDA, ARRIBA, ABAJO)
        
        player_sprites = {
            
            "IDDLE": {
                
                "RIGHT": 
                    {
                "iddle_x3": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x3.gif"),
                "iddle_x6": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x6.gif"),  
                
                },
                
                "LEFT": 
                    {
                "iddle_x3": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x3_left.gif"),
                "iddle_x6": gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x6_left.gif"),                    
                
                },
                

            },
            
            "WALKING": {
                
                "RIGHT": 
                    {
                "walking_x3": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x3.gif"),
                "walking_x6": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x6.gif"),  
                
                },
                
                "LEFT": 
                    {
                "walking_x3": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x3_left.gif"),
                "walking_x6": gif_pygame.load("./assets/Player_Sprites/Player_Walking_x6_left.gif"), 
                
                },
            },
            
            "ATTACKING": {
                
                "RIGHT": {
                    
                    "buildup_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing1.png").convert_alpha(),
                    "active_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing2.png").convert_alpha(),
                    "recovery_phase": pygame.image.load("./assets/Player_Sprites/Player_Slashing3.png").convert_alpha(),
                    
                },
                
                "LEFT": {
                    
                    "buildup_phase": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Slashing1.png").convert_alpha()), True, False),
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
            
            "RECOILING": {
                
                "RIGHT": {
                    
                    "recoil": pygame.image.load("./assets/Player_Sprites/Player_Slashing3.png").convert_alpha(),
                    
                },
                
                "LEFT": {
                    

                    "recoil": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Slashing3.png").convert_alpha()), True, False),
                    
                },
                
                "UP": {
                    
                    "recoil": pygame.image.load("./assets/Player_Sprites/Up_Slashing3.png").convert_alpha(),
                    
                },
                
                "DOWN": {
                    
                    "recoil": pygame.image.load("./assets/Player_Sprites/Down_Slashing3.png").convert_alpha(),
                
                },
            
            },

            
            "JUMPING": {
                
                "RIGHT": 
                    {
                "jumping1": pygame.image.load("./assets/Player_Sprites/Player_Jumping1.png").convert_alpha(),
                "jumping2": pygame.image.load("./assets/Player_Sprites/Player_Jumping2.png").convert_alpha(),
                "jumping3": pygame.image.load("./assets/Player_Sprites/Player_Jumping3.png").convert_alpha(),
                "jumping4": pygame.image.load("./assets/Player_Sprites/Player_Jumping4.png").convert_alpha(),                        
                
                },
                    
                "LEFT": 
                    {
                "jumping1": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Jumping1.png").convert_alpha()), True, False),
                "jumping2": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Jumping2.png").convert_alpha()), True, False), 
                "jumping3": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Jumping3.png").convert_alpha()), True, False),
                "jumping4": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Jumping4.png").convert_alpha()), True, False),                        
                
                },
                
            },
            
            "FALLING": {
                
                "RIGHT": 
                    {
                    "falling1": pygame.image.load("./assets/Player_Sprites/Player_Falling1.png").convert_alpha(),
                    "falling2": pygame.image.load("./assets/Player_Sprites/Player_Falling2.png").convert_alpha(),
                    "falling3": pygame.image.load("./assets/Player_Sprites/Player_Falling3.png").convert_alpha(),
                    "falling4": pygame.image.load("./assets/Player_Sprites/Player_Falling4.png").convert_alpha(),
                    "falling5": pygame.image.load("./assets/Player_Sprites/Player_Falling5.png").convert_alpha(),                        
                    },
                    
                "LEFT": 
                    {
                    "falling1": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Falling1.png").convert_alpha()), True, False),
                    "falling2": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Falling2.png").convert_alpha()), True, False), 
                    "falling3": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Falling3.png").convert_alpha()), True, False),
                    "falling4": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Falling4.png").convert_alpha()), True, False),
                    "falling5": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Falling5.png").convert_alpha()), True, False),
                        
                        },


            },
            
            "KNOCKBACK": {
                
                "RIGHT": {"knockback": pygame.image.load("./assets/Player_Sprites/Player_Knockback.png").convert_alpha(),},
                "LEFT": {"knockback": pygame.transform.flip((pygame.image.load("./assets/Player_Sprites/Player_Knockback.png").convert_alpha()), True, False)},
            },
            
        }
        
        return player_sprites

    def set_up_sprite_state(self, screen: pygame.Surface):
        
        #Funcion para gestionar y actualizar el sprite actual del jugador en función de su estado y orientación.
        #Algunos estados tienen prioridad sobre otros (por ejemplo, atacar tiene prioridad sobre caminar).
        #Algunos estados leen solamente la orientacion vertical y otros la horizontal.
        #El estado de attacking lee la orientacion del ataque (lockeada al iniciar el ataque).
        
        screen_width, screen_height = screen.get_size()
        
        #se gestionan primero los estados de acción que tienen prioridad sobre los estados de movimiento (attack, knockback, recoiling)
        if self.action_state != None: 
            
            if self.action_state == States.KNOCKBACK:
                
                current_sprite = self.player_sprites[self.action_state.name][self.x_orientation.name]["knockback"]
            
            elif self.action_state == States.RECOILING: 
                
                #el sprite de recoil es el mismo que el de recovery del ataque
                current_sprite = self.player_sprites[self.action_state.name][self.attack_orientation.name]["recoil"]
            
            elif self.action_state == States.ATTACKING: 
                
                #el sprite de attacking depende de la fase del ataque (build up, active, recovery)
                    
                current_sprite = self.player_sprites[self.action_state.name][self.attack_orientation.name][self.attack_state.value]
        else: 
            if self.movement_state == States.IDDLE: 
                
                if screen_width == 960 and screen_height == 540:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["iddle_x3"]
                
                elif screen_width == 1920 and screen_height == 1080:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["iddle_x6"]
            
            elif self.movement_state == States.WALKING:
                
                if screen_width == 960 and screen_height == 540:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["walking_x3"]
                
                elif screen_width == 1920 and screen_height == 1080:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["walking_x6"]
            
            elif self.movement_state == States.JUMPING: 
                
                #en el estado de jumping, el sprite depende de la velocidad vertical del jugador hacia arriba. Va cambiado a corde al cambio de velocidad
                if self.y_vel < -750:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["jumping1"]
                elif self.y_vel >= -750 and self.y_vel < -500:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["jumping2"]
                elif self.y_vel >= -500 and self.y_vel < -250:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["jumping3"]
                elif self.y_vel >= -250 and self.y_vel < 0:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["jumping4"]
            
            elif self.movement_state == States.FALLING: 
                
                #en el estado de falling, el sprite depende de la velocidad vertical del jugador hacia abajo. Va cambiado a corde al cambio de velocidad
                if self.y_vel >= 0 and self.y_vel < 200:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["falling1"]
                elif self.y_vel >= 200 and self.y_vel < 400:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["falling2"]
                elif self.y_vel >= 400 and self.y_vel < 600:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["falling3"]
                elif self.y_vel >= 600 and self.y_vel < 800:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["falling4"]
                elif self.y_vel >= 800:
                    current_sprite = self.player_sprites[self.movement_state.name][self.x_orientation.name]["falling5"]
        
        self.image = current_sprite
        
        return current_sprite