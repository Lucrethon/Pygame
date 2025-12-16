import pygame
import gif_pygame
import models.models as models
import models.main_player as main_player


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
        player_image = gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x3.gif")

    if screen_width == 1920 and screen_height == 1080:
        player_image = gif_pygame.load("./assets/Player_Sprites/Player_Iddle_x6.gif")

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
    y_direction = 0

    # set up knockback direction
    if sprite_beaten.rect.centerx < sprite_beater.rect.centerx:
        x_direction = -1  # empuje a la izquierda

    else:
        x_direction = 1  # empuje a la derecha
    
    if sprite_beaten.rect.centery < sprite_beater.rect.centery:
        y_direction = -1  # empuje hacia arriba

    else:
        y_direction = 1  # empuje hacia abajo
    

    # --- ADD UP AND DOWN DIRECTION --

    # set up knockback x speed
    sprite_beaten.x_vel = sprite_beater.knockback_x_force * x_direction

    # set up knockback y speed (jump)
    sprite_beaten.y_vel = sprite_beater.knockback_y_force * y_direction


def coordinates(screen, ground, enemy):

    screen_width, screen_height = screen.get_size()

    coordinates = {
        # LADO DERECHO (Para que caminen hacia la izquierda)
        # X: Ancho de pantalla (afuera). Y: Suelo menos altura del enemigo (pisando el suelo).
        "ground_right_edge": (screen_width, ground.rect.top - enemy.rect.height),
        # VOLADORES DERECHA
        "1/2_right_edge": (screen_width, screen_height / 2),
        # LADO IZQUIERDO (Para que caminen hacia la derecha)
        # X: Menos ancho del enemigo (afuera a la izq).
        "ground_left_edge": (-enemy.rect.width, ground.rect.top - enemy.rect.height),
        # VOLADORES IZQUIERDA
        "1/2_left_edge": (-enemy.rect.width, screen_height / 2),
        # TECHO (Para que caigan)
        # X: Posicion deseada. Y: Menos altura del enemigo (escondido arriba).
        "1/4_top_edge": (screen_width / 4, -enemy.rect.height),
        "1/2_top_edge": (screen_width / 2, -enemy.rect.height),
        "1/8_top_edge": (screen_width / 8, -enemy.rect.height),
    }
    return coordinates


def set_up_player(screen, ground):

    screen_width, screen_height = screen.get_size()

    # Set player image using gif-pygame library
    player_image = setup_player_gif(screen)

    # Player attack slash sprite
    sprite_attack_slash = pygame.image.load(
        "./assets/Attack_Slashx3.png"
    ).convert_alpha()

    # creating player object
    player = main_player.Player(sprite_attack_slash, player_image)

    # set player inicial position
    player.set_position(screen_width / 2, ground.rect.top, True)

    return player


def set_up_ground(screen):

    screen_width, screen_height = screen.get_size()

    # Set ground image# ground image
    ground_image = pygame.image.load("./assets/Ground_scaled_960x540.png")

    # creating ground object
    ground = models.Platform(ground_image)

    # set ground position
    ground.set_position(
        (screen_width - ground.rect.width), (screen_height - ground.rect.height)
    )

    return ground
