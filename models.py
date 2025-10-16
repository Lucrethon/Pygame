import pygame
import gif_pygame

# Initiate pygame
pygame.init()


class GameObject:

    def __init__(self, name, image, speed):
        self.name = name
        self.image = image
        self.speed = speed
        self.rect = self.image.get_rect()  # get the size of the image to create a rect

    # if self.image is .gif, it has to be place on the screen diferently than static images that uses blit(). Gifs have to be placed with .render()

    # sintaxis: gif.render(screen_size, (gif_coordinates_tobe_placed))
    

    def draw(self, screen, x_pos, y_pos):
        if hasattr(
            self.image, "render"
        ):  # this condition check if an object (self.image in this case) has certain atribute ("render" in this case, proper of gif_pygame library (gif objects))
                
            self.image.render(screen, (self.rect))
            self.rect.move_ip(x_pos, y_pos)

        else:  # if not, it can draw also png and jpg images as well
            screen.blit(self.image, (x_pos, y_pos))
            self.rect.move_ip(x_pos, y_pos)
            # .move_ip(x, y) moves the rect to those coordenates

    def movement(self, delta_time, screen, right=False, left=False):
        
        if right:
            self.rect.x += self.speed * delta_time
            
        if left:
            self.rect.x -= self.speed * delta_time
            
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0
            
        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()
    
            

class Platform:
    def __init__(self, name, image ):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()
        
    
    def draw(self, screen, x_pos, y_pos):
        screen.blit(self.image, (x_pos, y_pos))
        self.rect.move_ip(x_pos, y_pos)
