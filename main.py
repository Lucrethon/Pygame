import pygame
import gif_pygame
import models
import funtions
from gif_pygame import transform

# Initiate pygame
pygame.init()

# Set screen size
screen = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
screen_width, screen_height = screen.get_size()

base_width = 320
base_height = 180

# Factores de escala
scale_x = screen_width / base_width
scale_y = screen_height / base_height

# Load background image
background = pygame.image.load("./assets/Backgruound_320x180.png").convert()

# Resize background image to fit window
background = pygame.transform.scale(background, (screen_width, screen_height))

ground_image = pygame.image.load("./assets/Ground.png")
ground_image = funtions.resize(ground_image, scale_x, scale_y)

ground = models.Platform("ground", ground_image, 0)
ground.set_position((screen_width - ground.rect.width), (screen_height - ground.rect.height))


# Set player image using gif-pygame library
player_image = gif_pygame.load("./assets/Personaje_Arnaldo_Escaledx6.gif")
#player_image = funtions.resize_gif(player_image, scale_x, scale_y)

# Set player speed
player_speed = 300

#Player name
player_name = "Arnaldo"

# creating player object
player = models.Player(player_name, player_image, player_speed)
#set inicial position
player.set_position((player.rect.width/2), ground.rect.top, True)


# set game clock to control the time the loop
clock = pygame.time.Clock()
# Each round loop is a frame
# without the control (clock), the loop will run at the fastest speed that the computer can allow

# player_initial_position = pygame.Vector2(0, 510)


# convert()= returns us a new Surface of the image, but now converted to the same pixel format as our display. Since the images will be the same format at the screen, they will blit very quickly. If we did not convert, the blit() function is slower, since it has to convert from one type of pixel to another as it goes.

running = True
x = 0


# Initial game bucle
while running:

    # set the frames per second
    fps = clock.tick(60)  # limita el juego a 60 FPS
    # clock.tick returns the miliseconds since the last frame

    # delta time
    delta_time = fps / 1000
    # we divide it between 1000 to tranform into seconds

    # if speed = 200 and delta_time = 0.016 (1/60 fps), the player is moving at 200 * 0.016 = 3.2 píxels in that frame

    #x & y position in the lower right corner

    # Set ground rect & image
    ground.draw(screen)
    
    #set background
    screen.blit(background, (0, 0))


    # set player using gif-pygame library in initial position
    player.draw(screen)

    for event in pygame.event.get():  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # pygame.K_SCAPE event means the user press Esc button to close your window

    get_pressed_keys = pygame.key.get_pressed()
    # set a key that occurrs while the player get pressed a button on the keyboard

    if get_pressed_keys[pygame.K_RIGHT]:
        player.movement(delta_time, screen, right=True)

    if get_pressed_keys[pygame.K_LEFT]:
        player.movement(delta_time, screen, left=True)

    # update screen
    pygame.display.flip()

pygame.quit()
