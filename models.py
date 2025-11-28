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
    HURT = 3
    RECOIL = 4
    SPAWNING = 5
    RECOILING = 6


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

        # --- SPRITES ---
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

        # --- STATE OF ACTION ---
        self.state = States.IDDLE

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

    def update_player(
        self,
        delta_time,
        screen,
        ground,
    ):

        # triggrs should NEVER be in update method. Only in the main cycle. This method will only receive methods to update the player position that are triggered by trigger methods that change player states. Acording those states, this method will work in one way or another
        
        get_pressed_keys = pygame.key.get_pressed()
        # set a key that occurrs while the player get pressed a button on the keyboard

        move_right = get_pressed_keys[pygame.K_RIGHT]
        move_left = get_pressed_keys[pygame.K_LEFT]
        jumping = get_pressed_keys[pygame.K_SPACE]
        face_up = get_pressed_keys[pygame.K_UP]
        face_down = get_pressed_keys[pygame.K_DOWN]


        # --- TIMERS ---

        if self.state == States.ATTACKING:

            self.attack_update(delta_time)

        if self.is_invulnerable:

            self.invulnerability_timer += delta_time

            if self.invulnerability_timer >= self.invulnerability_duration:
                self.is_invulnerable = False

        # --- X-Vel CONTROL ---

        delta_x = 0  # variation in x
        delta_y = 0  # variation in y

        current_x_speed = 0

        # Knockback State
        if self.state == States.HURT:
            self.knockback_update(delta_time)

        #recoil state
        elif self.state == States.RECOILING:
            self.attack_recoil_timer += delta_time
            if self.attack_recoil_timer >= self.attack_recoil_duration:
                self.state = States.IDDLE
                self.attack_recoil_timer = 0.0


        else:

            current_x_speed = self.movement(move_right, move_left)
            self.x_vel = current_x_speed
            self.jump(jumping)
            self.facing_input(face_down, face_up)

        delta_x = self.x_vel * delta_time
        delta_y = self.y_vel * delta_time

        # Check screen collision
        delta_x = self.not_cross_edge_screen(screen, delta_x)

        # updates rect position
        self.rect.x += delta_x
        self.rect.y += delta_y

        # Check ground collision
        super().check_ground_collision(ground)

        # aply gravity
        super().apply_gravity(delta_time)

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

        if attack and self.state == States.IDDLE:

            # setting self state
            self.state = States.ATTACKING

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
            # return to iddle animation
            self.state = States.IDDLE
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
        
        if self.state == States.ATTACKING or self.state == States.RECOILING:
                
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

        if self.state == States.HURT:
            return

        self.state = States.HURT

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
            self.state = States.IDDLE
            self.timer = 0.0
            # Importante: resetear la velocidad X al salir del knockback
            self.x_vel = 0

    def start_attack_recoil(
        self,
    ):  # <-- Funcion que llama el arbitro de juego (disparador)

        # start the timer
        self.attack_recoil_timer = 0

        self.state = States.RECOILING

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
        #animacion de spawn 
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
        if self.state == States.HURT:

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

        self.state = States.HURT

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
        #animacion de spawn 
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
        # El GameMaster ahora es dueño de los grupos de sprites
        self.all_sprites = pygame.sprite.Group()
        self.moving_sprites = pygame.sprite.Group()
        self.enemy_group = pygame.sprite.Group()
        
        # El GameMaster ya no es un sprite, así que no necesita llamar a super().__init__()
        # super().__init__(all_sprites, moving_sprites, enemy_group)
        
        self.timer = 0.0 
        self.GAME_STATE = GameState.MAIN_MENU
        self.GAME_PHASE = 0
        self.transition_state_duration = 2
        #pygame.font.Font('ruta_del_archivo', tamaño)
        self.title_font = pygame.font.Font("fonts/HarnoldpixelRegularDemo-Yqw84.otf", 40)
        self.subtitle_font = pygame.font.Font("fonts/HarnoldpixelRegularDemo-Yqw84.otf", 25)
        self.start_button_rect = None
        self.resume_button_rect = None
        self.return_button_rect = None
        self.game_phases = 2
        
    def update_game(self, player, delta_time, screen, ground):
        
        if self.GAME_STATE == GameState.MAIN_MENU:
            
            pass
            
        elif self.GAME_STATE == GameState.PAUSE:
            pass
        
        elif self.GAME_STATE == GameState.GAME_OVER:
            pass

        
        elif self.GAME_STATE == GameState.VICTORY:
            pass
                    
        else: 
            #en los siguientes estados se lee el movimiento del jugador en todo momento
            
            #leer input de movimiento jugador 
            player.update_player(delta_time, screen, ground)
            
            #detectar colisiones con el suelo

            if self.GAME_STATE == GameState.SPAWNING:
                
                if self.GAME_PHASE == 1:
                    self.phase_1(screen, ground) #Aqui se spawmean los enemigos de la fase correspondiente y se agregan enemigos a la lista enemies[]
                    self.GAME_STATE = GameState.PLAYING
                    
                elif self.GAME_PHASE == 2:
                    self.phase_2(screen, ground)    
                    self.GAME_STATE = GameState.PLAYING
                #(...)
                
            elif self.GAME_STATE == GameState.TRANSITION: 
                self.timer += delta_time 
                
                if self.timer > self.transition_state_duration: 
                    self.timer = 0.0 
                    self.GAME_PHASE += 1
                    self.GAME_STATE = GameState.SPAWNING
                            
            elif self.GAME_STATE == GameState.PLAYING:
                
                self.moving_sprites.update()
                
                #enemigos.update()
                for enemy in self.enemy_group:
                    enemy.update_enemy(delta_time, screen, ground)
                    
                #detectar colisiones con enemigos
                self.handle_enemies_collision(player)
                self.handle_attack_collision(player)
                
                if not self.enemy_group and self.GAME_PHASE < self.game_phases: 
                    self.timer = 0.0
                    self.GAME_STATE = GameState.TRANSITION
                    
                elif not self.enemy_group and self.GAME_PHASE == self.game_phases: 
                    self.GAME_STATE = GameState.VICTORY
                    
                else: 
                    if player.isDead:
                        self.GAME_STATE = GameState.GAME_OVER

    def handle_events(self, events, player, screen, ground):
        
        for event in events: 
            if self.GAME_STATE == GameState.MAIN_MENU:
                
                if event.type == pygame.MOUSEBUTTONDOWN or event.type == pygame.KEYDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.start_button_rect.collidepoint(mouse_pos):
                        self.GAME_STATE = GameState.SPAWNING
                        self.GAME_PHASE = 1
                
                elif event.type == pygame.K_ESCAPE:
                    pygame.quit()
            
            elif self.GAME_STATE == GameState.PAUSE:
                
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_pos = pygame.mouse.get_pos()
                    
                    if self.resume_button_rect.collidepoint(mouse_pos) or event.type == pygame.K_ESCAPE:
                        self.GAME_STATE = GameState.PLAYING
                    
                    elif self.return_button_rect.collidepoint(mouse_pos):
                        self.all_sprites.remove(self.enemy_group)
                        self.moving_sprites.empty()
                        self.enemy_group.empty()
                        self.set_up_player_position(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU
            
            elif self.GAME_STATE == GameState.GAME_OVER:
                
                if event.type == pygame.KEYDOWN:
                        self.all_sprites.remove(self.enemy_group)
                        self.moving_sprites.empty()
                        self.enemy_group.empty()
                        self.set_up_player_position(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU
                
                elif event.key == pygame.K_ESCAPE:
                    pygame.quit()
            
            elif self.GAME_STATE == GameState.VICTORY:
                
                if event.type == pygame.KEYDOWN:
                        self.all_sprites.remove(self.enemy_group)
                        self.moving_sprites.empty()
                        self.enemy_group.empty()
                        self.set_up_player_position(player, screen, ground)
                        self.GAME_STATE = GameState.MAIN_MENU
                
                elif event.type == pygame.K_ESCAPE:
                    pygame.quit()
            
            else:
                
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.GAME_STATE = GameState.PAUSE
                    elif event.key == pygame.K_s:
                        player.trigger_attack(attack=True)

    def draw(self, screen, player, background, ground):
        
        
        if self.GAME_STATE == GameState.MAIN_MENU:
            screen.blit(background, (0,0))
            self.display_main_menu(screen)
            
        elif self.GAME_STATE == GameState.PAUSE:
            screen.blit(background, (0,0))
            #Quiero que se dibujen los sprites en la pausa tambien debajo del boton de pausa
            for sprite in self.all_sprites:
                sprite.draw(screen)
                
            self.display_pause_menu(screen)
        
        elif self.GAME_STATE == GameState.GAME_OVER:
            screen.blit(background, (0,0))
            self.display_game_over_screen(screen)

        
        elif self.GAME_STATE == GameState.VICTORY:
            screen.blit(background, (0,0))
            self.display_victory_screen(screen)
        
        else:
            ground.draw(screen)
            screen.blit(background, (0,0))
            #quiero que en todos los demas estados se dibujen los sprites 
            for sprite in self.all_sprites:
                sprite.draw(screen)
                # call to .draw() method from GameObjects that can handle gifs
            player.draw_attack(screen)

    def set_up_player_position(self, player, screen, ground):
        
        player.set_position(screen.get_width() / 2, ground.rect.top, True)

    def display_main_menu(self, screen):
        start_title = self.title_font.render("Start", False, (15, 15, 27))
        
        start_title_rect = start_title.get_rect()
        start_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        
        self.start_button_rect = start_title_rect
                
        screen.blit(start_title, start_title_rect)
    
    def display_pause_menu(self, screen):
        
        pause_title = self.title_font.render("Pause", False, (15, 15, 27))
        pause_title_rect = pause_title.get_rect()
        pause_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        
        resume_title = self.subtitle_font.render("Resume", False, (15, 15, 27))
        resume_title_rect = resume_title.get_rect()
        resume_title_rect.midtop = (screen.get_width() / 2, pause_title_rect.bottom + 10)
        self.resume_button_rect = resume_title_rect
        
        return_title = self.subtitle_font.render("Return to Menu", False, (15, 15, 27))
        return_title_rect = return_title.get_rect()
        return_title_rect.midtop = (screen.get_width() / 2, resume_title_rect.bottom + 10)
        self.return_button_rect = return_title_rect

        
        screen.blit(pause_title, pause_title_rect)
        screen.blit(resume_title, resume_title_rect)
        screen.blit(return_title, return_title_rect)
    
    def display_game_over_screen(self, screen):
        
        game_over_title = self.title_font.render("Game Over", False, (15, 15, 27))
        game_over_title_rect = game_over_title.get_rect()
        game_over_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        
        press_enter_title = self.subtitle_font.render("Press Enter to Restart", False, (15, 15, 27))
        press_enter_title_rect = press_enter_title.get_rect()
        press_enter_title_rect.midtop = (screen.get_width() / 2, game_over_title_rect.bottom + 10)
        
        screen.blit(game_over_title, game_over_title_rect)
        screen.blit(press_enter_title, press_enter_title_rect)
        
    def display_victory_screen(self, screen):
        
        victory_title = self.title_font.render("Victory", False, (15, 15, 27))
        victory_title_rect = victory_title.get_rect()
        victory_title_rect.center = (screen.get_width() / 2, screen.get_height() / 2)
        
        press_enter_title = self.subtitle_font.render("Press Enter to Restart", False, (15, 15, 27))
        press_enter_title_rect = press_enter_title.get_rect()
        press_enter_title_rect.midtop = (screen.get_width() / 2, victory_title_rect.bottom + 10)
        
        screen.blit(victory_title, victory_title_rect)
        screen.blit(press_enter_title, press_enter_title_rect)
        
    def handle_enemies_collision(self, player):
        
        enemies_collision = pygame.sprite.spritecollide(player, self.enemy_group, False)

        if enemies_collision:

            for enemy in enemies_collision: # enemies_collision es una lista de enemigos que colisionaron

                if player.state == States.HURT or player.is_invulnerable:
                    pass
                else:
                    player.take_damage()
                    functions.knockback(player, enemy, True)
                    
    def handle_attack_collision(self, player):
        
                        # check hitbox collision
        if player.active_hitbox:

            for enemy in self.enemy_group:

                if player.active_hitbox.colliderect(enemy.rect):

                    if enemy not in player.enemies_attacked:

                        if player.orientation == Orientation.DOWN:
                            enemy.take_damage()
                            # functions.knockback(player, enemy, False)
                            player.trigger_pogo()
                            player.enemies_attacked.append(enemy)

                        else:
                            enemy.take_damage()
                            functions.knockback(player, enemy, False)
                            player.start_attack_recoil()
                            player.enemies_attacked.append(enemy)
                    else:
                        pass

                else:
                    pass
    
    
    
    def phase_1(self, screen, ground): 
        
        enemies_phase_1 = []
        
        for _ in range(2):
        
            enemy_image = pygame.Surface([90, 90])
            enemy_image.fill((255, 0, 0))
            enemy = Crawlid() # Ahora creas una instancia de Crawlid directamente
            enemies_phase_1.append(enemy)
        
        for enemy in enemies_phase_1:
        
            self.all_sprites.add(enemy)
            self.moving_sprites.add(enemy)
            self.enemy_group.add(enemy)
        
        enemy_coords = coordinates(screen, ground, enemies_phase_1[0]) # Usar un enemigo de la lista
        
        enemies_phase_1[0].set_position(*enemy_coords["ground_right_edge"])
        
        enemies_phase_1[1].set_position(*enemy_coords["ground_left_edge"])
        
    def phase_2(self, screen, ground): 
        
        enemies_phase_2 = []
        
        for _ in range(2):
        
            enemy_image = pygame.Surface([90, 90])
            enemy_image.fill((255, 0, 0))
            enemy = Crawlid() # Igual aquí, creas una instancia de Crawlid
            enemies_phase_2.append(enemy)
        
        for enemy in enemies_phase_2:
        
            self.all_sprites.add(enemy)
            self.moving_sprites.add(enemy)
            self.enemy_group.add(enemy)
        
        enemy_coords = coordinates(screen, ground, enemies_phase_2[0]) # Usar un enemigo de la lista
        
        enemies_phase_2[0].set_position(*enemy_coords["ground_right_edge"])
        
        #El asteriscto es importante porque el método set_position(x, y) espera dos argumentos separados (x e y), pero enemy_coords["ground_right_edge"] devuelve una tupla (x, y). El asterisco "desempaqueta" la tupla, pasando sus elementos como argumentos individuales a la función.
        
        enemies_phase_2[1].set_position(*enemy_coords["ground_left_edge"])
    
    
    def returnEnemyWithPosition(screen, ground, enemy, position):
        
        enemy_coords = coordinates(screen, ground, enemy)
        
        if position in enemy_coords:
            
            enemy_image = pygame.Surface([90, 90])
            enemy_image.fill((255, 0, 0))
            
            new_enemy = Crawlid()
            new_enemy.set_position(*enemy_coords[position])
            
            return new_enemy

    
    def generic_phase(self, phases):
        
        pass
        

# phases = {
#     phase_1: {
#         wave_1: [
#             returnEnemyWithPosition(caracol, POSTION.top_right_edge),
#             returnEnemyWithPosition(caracol, POSTION.top_left_edge),
            
#             returnEnemyWithPosition(caracol, POSTION.top_left_edge),
#             returnEnemyWithPosition(caracol, POSTION.top_left_edge),
#         ],
#         wave_2: [
            
#         ],
#         wave_3: [
            
#         ]
#     },
#     phase_2: {
#         wave_1: [
            
#         ]
#     },
#     phase_3: {
#         wave_1: [
            
#         ]
#     },
#     phase_4: {
#         wave_1: [
            
#         ]
#     }
# }
