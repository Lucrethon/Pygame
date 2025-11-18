import pygame
import gif_pygame
from gif_pygame import transform


# function to resize sprites acording scale factors
def resize(sprite, screen):

    screen_width, screen_height = screen.get_size()

    # creating scale factors acording background asset
    background_base_width = 320
    background_base_height = 180

    # scales factors
    scale_x = screen_width / background_base_width
    scale_y = screen_height / background_base_height

    resize_sprite = pygame.transform.scale(
        sprite, (int(sprite.get_width() * scale_x), int(sprite.get_height() * scale_y))
    )

    return resize_sprite


# Function to change between 960x540 to fullscrean (1920x1080) if wanted
def setup_screen(isFullScreen=False):
    if isFullScreen:
        screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
    else:
        screen = pygame.display.set_mode((960, 540))

    return screen


# load gif player acording screen size using gif_pygame library
def setup_player_gif(screen):

    screen_width, screen_height = screen.get_size()

    if screen_width == 960 and screen_height == 540:
        player_image = gif_pygame.load("./assets/Personaje_Arnaldo_Escaledx3.gif")

    if screen_width == 1920 and screen_height == 1080:
        player_image = gif_pygame.load("./assets/Personaje_Arnaldo_Escaledx6.gif")

    return player_image


def knockback(player, enemy, player_beaten=False):

    sprite_beaten = None
    sprite_beater = None

    if player_beaten:

        sprite_beaten = player
        sprite_beater = enemy

    else:
        sprite_beaten = enemy
        sprite_beater = player

    x_direction = 0

    # set up knockback direction
    if sprite_beaten.rect.centerx < sprite_beater.rect.centerx:
        x_direction = -1  # empuje a la izquierda

    else:
        x_direction = 1  # empuje a la derecha

    # --- ADD UP AND DOWN DIRECTION --

    # set up knockback x speed
    sprite_beaten.x_vel = sprite_beater.knockback_x_force * x_direction

    # set up knockback y speed (jump)
    sprite_beaten.y_vel = sprite_beater.knockback_y_force
