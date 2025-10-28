import pygame
import gif_pygame
import gif_pygame.transform

class GravityMixin:
    
    def apply_gravity(self, delta_time):
        
        #Gravity that pull down the character to the ground 
        self.y_speed += (self.gravity * delta_time)
        delta_y += self.y_speed * delta_time
    
    
    def check_ground_collision(self, ground):
        
        # #check collision with the ground
        if self.rect.colliderect(ground.rect): 
            self.y_speed = 0
            self.rect.bottom = ground.rect.top
            self.isJumping = False
            self.isFalling = False
        
        else:
            self.isFalling = True