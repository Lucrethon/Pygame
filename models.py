import pygame
import gif_pygame
from abc import ABC, abstractmethod, abstractclassmethod
import time


# Initiate pygame
pygame.init()


class GameObject(ABC):

    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()  # get the size of the image to create a rect

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
            #midbottom: Se refiere a la coordenada X y a la coordenada Y del punto central inferior de un rectángulo. 
        
        else:
            self.rect.topleft = (x_pos, y_pos)
        
    @abstractmethod
    def movement(self): 
        pass

    
            

class Player(GameObject):
    def __init__(self, name, image, x_speed):
        super().__init__(name, image)
        self.x_speed = x_speed
        self.y_speed = 0
        self.gravity = 940
        self.jump_speed = -1000
        self.isJumping = False 
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)
    
    def movement(self, delta_time, screen, ground, right=False, left=False, jump=False):
        
        delta_x = 0 #variation in x
        delta_y = 0 #variation in y
        
        if right:
            delta_x += self.x_speed * delta_time
            
        if left:
            delta_x -= self.x_speed * delta_time
        
        if jump and self.isJumping == False:
            self.y_speed = self.jump_speed
            self.isJumping = True
            
        #setting the character go to the oposite side if he goes off the edge of one side of the screen 
            
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0
                        
        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()
            
        #Gravity that pull down the character to the ground 
        self.y_speed += (self.gravity * delta_time)
        delta_y += self.y_speed * delta_time
        
        
        #updates rect position 
        self.rect.x += delta_x
        self.rect.y += delta_y        
        
        # #check collition with the ground
        if self.rect.colliderect(ground.rect): 
            self.y_speed = 0
            self.rect.bottom = ground.rect.top
            self.isJumping = False
    

class Platform(GameObject):
    def __init__(self, name, image):
        super().__init__(name, image)
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self):
        pass
