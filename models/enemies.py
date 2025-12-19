import pygame
from abc import ABC, abstractmethod
import models.mixin as mixin
from models.utils import Orientation
from models.utils import States
from models.utils import AttackState
from models.models import GameObject
import gif_pygame


class Enemy(GameObject, mixin.Gravity, mixin.CrossScreen):

    def __init__(self, screen, orientation):
        # Los grupos se pasarán desde el GameMaster al crear el enemigo
        super().__init__()

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
    def __init__(self, screen, orientation):
        # Crear/Cargar la imagen específica para el enemig0

        # Llamar al constructor de la clase padre (Enemy) con estos atributos
        super().__init__(screen, orientation)
        
        self.x_orientation = orientation
        self.enemy_sprites = self.enemy_sprites()
        self.set_up_sprite(screen)
        self.rect = self.image.get_rect()
        self.hitbox = (self.rect.x, self.rect.y + 20, 80, 38)

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
        self.state = States.WALKING
        self.isDead = False

        # --- ORIENTATION AND POSITION ---
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
        self.update_orientation()
        self.set_up_sprite(screen)
        self.hitbox = (self.rect.x, self.rect.y + 10, 83, 40)

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
            self.state = States.WALKING
            self.timer = 0.0
            # Importante: resetear la velocidad X al salir del knockback
            self.x_vel = 0

    def spawning(self):
        # animacion de spawn
        pass
    
    def update_orientation(self):
        
        if self.state != States.KNOCKBACK:
            
            if self.x_vel >= 0:
                self.x_orientation = Orientation.RIGHT
            elif self.x_vel < 0:
                self.x_orientation = Orientation.LEFT
        
    def enemy_sprites(self):
        
        enemy_sprites = {
            
            "RIGHT": 
                {
            "walking_x3": gif_pygame.load("./assets/Crawlid/Crawlid_x3.gif"),
            "walking_x6": gif_pygame.load("./assets/Crawlid/Crawlid_x6.gif"),  
            
            },
            
            "LEFT": 
                {
            "walking_x3": gif_pygame.load("./assets/Crawlid/Crawlid_x3_left.gif"),
            "walking_x6": gif_pygame.load("./assets/Crawlid/Crawlid_x6_left.gif"),  
                }
        
        }
        
        return enemy_sprites
    
    def set_up_sprite(self, screen: pygame.Surface):
        
        screen_width, screen_height = screen.get_size()
        # Funcion que se encarga de establecer el sprite inicial del jugador basado en su estado actual.
        current_sprite = None
        
        if screen_width == 960 and screen_height == 540:
            current_sprite = self.enemy_sprites[self.x_orientation.name]["walking_x3"]
                
        elif screen_width == 1920 and screen_height == 1080:
            current_sprite = self.enemy_sprites[self.x_orientation.name]["walking_x6"]

        
        self.image = current_sprite 
    

class Gruzzer(Enemy):
    
    def __init__(self, screen, orientation):
        # Crear/Cargar la imagen específica para el enemig0

        # Llamar al constructor de la clase padre (Enemy) con estos atributos
        super().__init__(screen, orientation)
        
        self.hitbox = (self.rect.x + 18, self.rect.y + 30, 38, 80)
        self.x_orientation = orientation
        self.enemy_sprites = self.enemy_sprites()
        self.set_up_sprite(screen)
        self.rect = self.image.get_rect()

        # --- CONSTANTES DE FUERZA ---
        self.x_speed = 240
        self.y_speed = 240
        self.knockback_y_force = -500
        self.knockback_x_force = 600
        self.gravity = 0
        self.air_friction = 0.90

        # --- CURRENT SPEED ---
        if self.x_orientation == Orientation.RIGHT:
            self.x_vel = self.x_speed
        else:
            self.x_vel = -self.x_speed

        self.y_vel = self.y_speed

        # --- HEALTH ---
        self.HP = 5

        # --- STATE OF ACTION ---
        self.state = States.FLYING
        self.isDead = False

        # --- TIMERS ---
        self.timer = 0.0
        self.knockback_duration = 0.2
        
    def draw(self, screen):
        return super().draw(screen)

    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def update_enemy(self, delta_time, screen, ground):
        
        screen_width, screen_height = screen.get_size()
        
        delta_x = 0  # variation in x
        delta_y = 0  # variation in y
        
        if self.state == States.KNOCKBACK:

            self.knockback_update(delta_time)
            
        else:
        
            if self.rect.right >= screen_width:
                self.x_vel = -self.x_speed
                self.rect.right = screen_width
                
            elif self.rect.left <= 0:
                self.x_vel = self.x_speed
                self.rect.left = 0
                
            if self.rect.bottom >= ground.rect.top:
                self.y_vel = -self.y_speed
                self.rect.bottom = ground.rect.top
                
            elif self.rect.top <= 0:
                self.y_vel = self.y_speed
                self.rect.top = 0

        delta_x += (self.x_vel * self.air_friction) * delta_time
        delta_y = (self.y_vel * self.air_friction) * delta_time

        # Move rect
        self.rect.move_ip(delta_x, delta_y)

        self.update_orientation()
        self.set_up_sprite(screen)
        self.hitbox = (self.rect.x, self.rect.y + 20, 80, 38)

    def update_orientation(self):
        
        if self.state != States.KNOCKBACK:
        
            if self.x_vel >= 0:
                self.x_orientation = Orientation.RIGHT
            elif self.x_vel < 0:
                self.x_orientation = Orientation.LEFT
                
            if self.y_vel >= 0:
                self.y_orientation = Orientation.DOWN
            elif self.y_vel < 0:
                self.y_orientation = Orientation.UP
    
    def take_damage(self):

        self.HP -= 1

        self.state = States.KNOCKBACK

        # restart timer
        self.timer = 0.0

        if self.HP <= 0:
            self.isDead = True
            super().kill()
    
    def knockback_update(self, delta_time):  # update player position in knockbak state

        # start the timer
        self.timer += delta_time

        # apply friction
        self.x_vel *= self.air_friction

        # Detenerlo si es muy lento
        if abs(self.x_vel) < 10:
            self.x_vel = 0

        if self.timer >= self.knockback_duration:
            self.state = States.FLYING
            self.timer = 0.0
            
            # Restaurar velocidad X
            if self.x_orientation == Orientation.RIGHT:
                self.x_vel = self.x_speed
            else:
                self.x_vel = -self.x_speed
            
            # Restaurar velocidad Y
            if self.y_orientation == Orientation.DOWN:
                self.y_vel = self.y_speed
            else:
                self.y_vel = -self.y_speed
    
    def enemy_sprites(self):
        
        enemy_sprites = {
            
            "RIGHT": 
                {
            "walking_x3": gif_pygame.load("./assets/Gruzzer/Gruzzer_x3.gif"),
            "walking_x6": gif_pygame.load("./assets/Gruzzer/Gruzzer_x6.gif"),  
            
            },
            
            "LEFT": 
                {
            "walking_x3": gif_pygame.load("./assets/Gruzzer/Gruzzer_x3_left.gif"),
            "walking_x6": gif_pygame.load("./assets/Gruzzer/Gruzzer_x6_left.gif"),  
                }
        
        }
        
        return enemy_sprites
    
    def set_up_sprite(self, screen: pygame.Surface):
        
        screen_width, screen_height = screen.get_size()
        # Funcion que se encarga de establecer el sprite inicial del jugador basado en su estado actual.
        current_sprite = None
        
        if screen_width == 960 and screen_height == 540:
            current_sprite = self.enemy_sprites[self.x_orientation.name]["walking_x3"]
                
        elif screen_width == 1920 and screen_height == 1080:
            current_sprite = self.enemy_sprites[self.x_orientation.name]["walking_x6"]

        
        self.image = current_sprite 
    
    def spawning(self):
        # animacion de spawn
        pass

        