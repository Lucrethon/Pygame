import pygame
import gif_pygame
import gif_pygame.transform
from abc import ABC, abstractmethod
from enum import Enum
import mixin


class States(Enum):
    IDDLE = 1
    ATTACKING = 2
    KNOCKBACK = 3

class Orientation(Enum):
    RIGTH = 1
    LEFT = 2
    UP = 3
    DOWN = 4

# Initiate pygame
pygame.init()

# Grupos de srpites
all_sprites = pygame.sprite.Group()  # Grupo para DIBUJAR todo
moving_sprites = pygame.sprite.Group()  # Grupo para ACTUALIZAR solo lo que se mueve
enemy_group = pygame.sprite.Group()  # Grupo para colisiones de enemigos


class GameObject(ABC, pygame.sprite.Sprite):

    def __init__(self, name, image, *groups):
        super().__init__(*groups)
        self.name = name
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

    @abstractmethod
    def movement(self):
        pass


class Player(GameObject, mixin.Gravity):
    def __init__(self, name, image, move_speed, sprite_attack_slash):
        super().__init__(name, image, all_sprites, moving_sprites)
        self.move_speed = move_speed
        self.HP = 5
        
        # --- SPRITES ---
        self.sprite_attack_slash = sprite_attack_slash
        self.active_slash_sprite = None
        
        # --- VELOCIDAD ACTUAL ---
        self.x_vel = 0
        self.y_vel = 0

        # --- CONSTANTES DE FUERZA ---
        self.gravity = 2700
        self.jump_force = -1000
        self.knockback_y_force = -500
        self.knockback_x_force = 600
        self.air_friction = 0.90  # fuerza de arrastre que se opone al movimiento de un objeto al atravesar el aire

        # --- ESTADOS ---
        self.state = States.IDDLE
        self.facing_right = True
        self.facing_up = False
        self.facing_down = False
        self.is_on_ground = True  # <-- Is not jumping
        self.active_hitbox = None
        self.is_invulnerable = False #invulnerability state after knockback to avoid multiple collisions at the same time 
        self.attack_orientation = Orientation.RIGTH

        # --- DURACION DE ESTADOS ---
        self.timer = 0.0
        self.knockback_duration = 0.5  # seconds
        self.build_up_attack_duration = 0.1  # seconds
        self.active_frames_attack_duration = 0.07  # seconds
        self.recovery_attack_duration = 0.3  # seconds
        self.invulnerability_duration = 1 #seconds 
        self.invulnerability_timer = 0.0 #separate time to count time even if the player is attacking or iddle. 

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def update_player(
        self,
        delta_time,
        screen,
        ground,
        right=False,
        left=False,
        jump=False,
        up=False,
        down=False,
    ):

        # triggrs should NEVER be in update method. Only in the main cycle

        delta_x = 0  # variation in x
        delta_y = 0  # variation in y

        current_x_speed = 0

        # Knockback State
        if self.state == States.KNOCKBACK:

            self.knockback_update(delta_time)
            # Usa la velocidad de knockback
        else:

            if self.state == States.ATTACKING:

                self.attack_update(delta_time)

            current_x_speed = self.movement(right, left)
            self.x_vel = current_x_speed
            self.jump(jump)
            self.facing_input(down, up)
        
        if self.is_invulnerable: #invulnerability state after knockback 
            self.invulnerability_timer += delta_time
            if self.invulnerability_timer >= self.invulnerability_duration:
                self.is_invulnerable = False 

        # aply gravity
        super().apply_gravity(delta_time)

        delta_x = self.x_vel * delta_time
        delta_y = self.y_vel * delta_time

        # Check screen collision
        delta_x = self.not_cross_edge_screen(screen, delta_x)

        # updates rect position
        self.rect.x += delta_x
        self.rect.y += delta_y

        # Check ground collision
        super().check_ground_collision(ground)

    def movement(self, right=False, left=False):

        current_x_speed = 0

        if right:
            current_x_speed = self.move_speed

            if self.facing_right:
                pass
            else:

                # flip sprite to right
                self.facing_right = True
                gif_pygame.transform.flip(self.image, True, False)

        if left:
            current_x_speed = -self.move_speed

            if not self.facing_right:
                pass
            else:

                # flip sprite to left
                self.facing_right = False
                gif_pygame.transform.flip(self.image, True, False)

        return current_x_speed

    def jump(self, jump=False):

        # if the player is not jumping and maitain Space button pressed (long jump)
        if jump and self.is_on_ground:

            self.y_vel = self.jump_force
            self.is_on_ground = False

        # if the player is jumping (no ground collision yet, self.isJumping = True) and press space for a short time (short jump)
        if not jump and self.y_vel < 0:
            self.y_vel *= 0.5
            self.is_on_ground = False

    def facing_input(self, down=False, up=False):

        # Facing up
        if up and not down:
            self.facing_down = False
            self.facing_up = True

        # Facing down
        elif down and not up:
            self.facing_up = False
            self.facing_down = True

        else:
            self.facing_up = False
            self.facing_down = False

    def not_cross_edge_screen(self, screen, delta_x):
        # setting player to don't go off the edge of the screen

        if self.rect.right + delta_x >= screen.get_width():
            delta_x = screen.get_width() - self.rect.right

        if self.rect.left + delta_x <= 0:
            delta_x -= self.rect.left

        return delta_x

    def trigger_attack(self, attack=False):  # call this method in the main cycle

        if attack and self.state != States.KNOCKBACK and self.state != States.ATTACKING:

            # setting self state
            self.state = States.ATTACKING

            # restart self.timer
            self.timer = 0.0

    def attack_update(self, delta_time):

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
                
                #lock orientation
                self.lock_attack_ortientation() 
                
                # attack animation

                # create hitbox & slash attack animation
            self.active_hitbox, self.active_slash_sprite = self. get_attack_components()


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
        if self.facing_up and not self.facing_down:

            self.attack_orientation = Orientation.UP

        # down the player
        elif self.facing_down and not self.facing_up:

            self.attack_orientation = Orientation.DOWN

        # right the player
        elif self.facing_right and not self.facing_down:

            self.attack_orientation = Orientation.RIGTH

        # left the player
        else:
            if not self.facing_right and not self.facing_down:

                self.attack_orientation = Orientation.LEFT

    def get_attack_components(self): #--> RECT & SPRITE POSITION ACORDING PLAYER ORIENTATION

        hitbox = None
        rotate_slash_sprite = None

        # up the player
        if self.attack_orientation == Orientation.UP:

            rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, -270)
            hitbox =  rotate_slash_sprite.get_rect()
            hitbox.midbottom = self.rect.midtop

        # down the player
        elif self.attack_orientation == Orientation.DOWN and not self.is_on_ground:

            rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, -90)
            hitbox =  rotate_slash_sprite.get_rect()
            hitbox.midtop = self.rect.midbottom

        # right the player
        elif self.attack_orientation == Orientation.RIGTH:

            rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, 0)
            hitbox =  rotate_slash_sprite.get_rect()
            hitbox.midleft = self.rect.midright

        # left the player
        else:
            if self.attack_orientation == Orientation.LEFT:

                rotate_slash_sprite = pygame.transform.rotate(self.sprite_attack_slash, -180)
                hitbox =  rotate_slash_sprite.get_rect()
                hitbox.midright = self.rect.midleft

        return hitbox, rotate_slash_sprite
    

    def draw_attack(self, screen, enemy): #DRAW SLASH SPRITE AND RECT

        # draw hitbox
        if self.active_hitbox and self.active_slash_sprite:
            
            screen.blit(self.active_slash_sprite, self.active_hitbox)
            
            # check collision
            if self.active_hitbox.colliderect(enemy.rect):
                enemy.take_damage()

            else:
                pass

    def take_damage(self, enemy):  # call this method in the main cycle

        x_direction = 0

        if self.state == States.KNOCKBACK or self.is_invulnerable:
            return
        #The player cannot reaceive damage while elf.is_invulnerable = True

        # set knockback state
        self.state = States.KNOCKBACK

        # restart timer
        self.timer = 0.0

        # set up HP
        self.HP -= 1

        # set up knockback direction
        if self.rect.centerx < enemy.rect.centerx:
            x_direction = -1  # empuje a la izquierda

        else:
            x_direction = 1  # empuje a la derecha
        
        # --- ADD UP AND DOWN DIRECTION --

        # set up knockback x speed
        self.x_vel = self.knockback_x_force * x_direction

        # set up knockback y speed (jump)
        self.y_vel = self.knockback_y_force

        self.is_on_ground = False

    def knockback_update(self, delta_time):

        # start the timer
        self.timer += delta_time

        # apply friction
        self.x_vel *= self.air_friction

        # Detenerlo si es muy lento
        if abs(self.x_vel) < 10:
            self.x_vel = 0

        if self.timer >= self.knockback_duration:
            self.is_invulnerable = True #invulnerability state after knockback 
            self.invulnerability_timer = 0.0
            self.state = States.IDDLE
            self.timer = 0.0
            # Importante: resetear la velocidad X al salir del knockback
            self.x_vel = 0


class Platform(GameObject):
    def __init__(self, name, image):
        super().__init__(name, image, all_sprites)

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self):
        pass


class Enemy(GameObject):

    def __init__(self, name, image):
        super().__init__(name, image, all_sprites, moving_sprites, enemy_group)
        self.move_speed = 300
        self.HP = 6
        self.isDead = False
        self.facing_right = True

    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self, screen, delta_time):

        delta_x = 0
        delta_y = 0

        delta_x += self.move_speed * delta_time

        # updates rect position
        self.rect.move_ip(delta_x, 0)

        # setting the enemy to don't go off the edge of the screen

        if self.rect.right >= screen.get_width() and self.facing_right:
            self.facing_right = False
            self.move_speed *= -1

        if self.rect.left <= 0 and not self.facing_right:
            self.facing_right = True
            self.move_speed *= -1
    
    def take_damage(self): 
        
        self.HP -= 1
        
        if self.HP >= 0: 
            self.isDead = True
            super().kill()
        
        #Knockback physic 
    
    