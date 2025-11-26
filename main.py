import pygame
import gif_pygame
import models
import functions
from gif_pygame import transform
import time

# Initiate pygame
pygame.init()

# SET UP REAL SCREEN
screen = functions.setup_screen(False)
screen_width, screen_height = screen.get_size()

# --------------------------------------------------------------------------

# SET UP VIRTUAL CANVAS (game logic)
virtual_width = 960
virtual_height = 540
virtual_canvas = pygame.Surface((virtual_width, virtual_height))

# --------------------------------------------------------------------------
# UPLOAD ASSETS

# background image
background = pygame.image.load("./assets/Background_960x540.png").convert()

ground = functions.set_up_ground(virtual_canvas)

player = functions.set_up_player(virtual_canvas, ground)

# --------------------------------------------------------------------------

# set game clock to control the time the loop
clock = pygame.time.Clock()
# Each round loop is a frame
# without the control (clock), the loop will run at the fastest speed that the computer can allow

running = True


# Initial game bucle
while running:

    counter = 0

    # 1. CLOCK

    # set the frames per second
    pased_miliseconds = clock.tick(60)
    # limita el juego a 60 FPS
    # esto devuelve los milisegundos que pasaron desde el ultimo frame (duracion del frame anterior en milisegundos)
    # clock.tick returns the miliseconds since the last frame

    # delta time
    delta_time = pased_miliseconds / 1000.0
    # we divide it between 1000 to tranform into seconds
    # if speed = 200 and delta_time = 0.016 (1/60 fps), the player is moving at 200 * 0.016 = 3.2 píxels in that frame

    # 2. INPUT (events)

    TrigerAttack = False
    
    events = pygame.event.get()


    for event in events:  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

        # if event.type == pygame.KEYDOWN:
        #     if event.key == pygame.K_ESCAPE:
        #         running = False
            # pygame.K_SCAPE event means the user press Esc button to close your window
        if event.key == pygame.K_s:
            TrigerAttack = True

    # 3. MOVEMENT

    # set attack
    if TrigerAttack:
        player.trigger_attack(attack=True)


    # 5. DRAW

    # Set ground rect & image
    ground.draw(virtual_canvas)

    # set background
    virtual_canvas.blit(background, (0, 0))

    player.draw_attack(virtual_canvas)

    streched_canvas = pygame.transform.scale(
        virtual_canvas, (screen_width, screen_height)
    )

    screen.blit(streched_canvas, (0, 0))

    # update screen
    pygame.display.flip()

pygame.quit()
