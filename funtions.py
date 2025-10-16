import pygame
import gif_pygame
from gif_pygame import transform


def resize(sprite, scale_x, scale_y):
        
    resize_sprite = pygame.transform.scale(sprite, (int(sprite.get_width() * scale_x), int(sprite.get_height() * scale_y)))
    
    return resize_sprite
    


    
    