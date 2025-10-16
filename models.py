import pygame
import gif_pygame
from abc import ABC, abstractmethod, abstractclassmethod


# Initiate pygame
pygame.init()


class GameObject(ABC):

    def __init__(self, name, image, speed):
        self.name = name
        self.image = image
        self.speed = speed
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
    def __init__(self, name, image, speed):
        super().__init__(name, image, speed)
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)
    
    def movement(self, delta_time, screen, right=False, left=False):
        
        if right:
            self.rect.x += self.speed * delta_time
            
        if left:
            self.rect.x -= self.speed * delta_time
            
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0
            
        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()
    
            

class Platform(GameObject):
    def __init__(self, name, image, speed):
        super().__init__(name, image, speed)
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self):
        pass
