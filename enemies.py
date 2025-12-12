import pygame
from abc import ABC, abstractmethod
import mixin
from utils import Orientation
from utils import States
from utils import AttackState
from models import GameObject


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
        self.orientation = Orientation.RIGHT
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