import pygame
import gif_pygame
import gif_pygame.transform
import models


class Gravity:

    def apply_gravity(self, delta_time):

        # Gravity that pull down the character to the ground - important
        self.y_vel += self.gravity * delta_time

    def check_ground_collision(self, ground):

        # #check collision with the ground
        if self.rect.colliderect(ground.rect):

            self.y_vel = 0
            self.rect.bottom = ground.rect.top
            self.is_on_ground = True


class CrossScreen:

    # setting the character go to the oposite side if he goes off the edge of one side of the screen }

    def cross_edge_screen(self, screen):
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0

        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()

    # setting the enemy to don't go off the edge of the screen
    def not_cross_edge_screen(self, screen):

        if self.rect.right >= screen.get_width():

            if self.orientation == models.Orientation.RIGTH:
                self.orientation = models.Orientation.LEFT
                self.move_speed *= -1

            # "Si te pasaste, te traigo de vuelta al borde exacto"
            self.rect.right = screen.get_width()

        if self.rect.left <= 0:

            if self.orientation == models.Orientation.LEFT:
                self.orientation = models.Orientation.RIGTH
                self.move_speed *= -1

            self.rect.left = 0
