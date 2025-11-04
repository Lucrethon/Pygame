import pygame
import gif_pygame
import gif_pygame.transform

class Gravity:
    
    def apply_gravity(self, delta_time, delta_y):
        
        #Gravity that pull down the character to the ground - important
        self.y_vel += (self.gravity * delta_time)
    
    
    def check_ground_collision(self, ground):
        
        # #check collision with the ground
        if self.rect.colliderect(ground.rect): 
            
            self.y_vel = 0
            self.rect.bottom = ground.rect.top
            self.is_on_ground = True

class CrossScreen: 
    
    #setting the character go to the oposite side if he goes off the edge of one side of the screen }
    
    def cross_edge_screen(self, screen): 
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0
                        
        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()
    
    #setting the enemy to don't go off the edge of the screen 
    def not_cross_edge_screen(self, screen):
            
        if self.rect.right >= screen.get_width() and self.facing_right:
            self.facing_right = False
            self.move_speed *= -1
            
        if self.rect.left <= 0 and not self.facing_right:
            self.facing_right = True
            self.move_speed *= -1