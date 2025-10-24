import pygame
import gif_pygame
from gif_pygame import transform

#function to resize sprites acording scale factors
def resize(sprite, scale_x, scale_y):
        
    resize_sprite = pygame.transform.scale(sprite, (int(sprite.get_width() * scale_x), int(sprite.get_height() * scale_y)))
    
    return resize_sprite

#Function to change between 960x540 to fullscrean (1920x1080) if wanted 
def setup_screen(isFullScreen = False):
    if isFullScreen: 
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else: 
        screen = pygame.display.set_mode((960, 540))
    
    return screen

#load gif player acording screen size using gif_pygame library 
def setup_player_gif(screen):
    
    screen_width, screen_height = screen.get_size()
    
    if screen_width == 960 and screen_height == 540: 
        player_image = gif_pygame.load("./assets/Personaje_Arnaldo_Escaledx3.gif")
    
    if screen_width == 1920 and screen_height == 1080:
        player_image = gif_pygame.load("./assets/Personaje_Arnaldo_Escaledx6.gif")
    
    return player_image
    