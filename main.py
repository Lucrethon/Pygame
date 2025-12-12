import pygame
import functions
import game_master
import main_player

# Initiate pygame
pygame.init()


# SET UP REAL SCREEN
screen = functions.setup_screen(True)
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

# --------------------------------------------------------------------------

game_master = game_master.GameMaster()

# Ahora que GameMaster gestiona los grupos, creamos los objetos y los añadimos a sus grupos
ground = functions.set_up_ground(virtual_canvas)
player = functions.set_up_player(virtual_canvas, ground)

game_master.all_sprites.add(player)


# set game clock to control the time the loop
clock = pygame.time.Clock()
# Each round loop is a frame
# without the control (clock), the loop will run at the fastest speed that the computer can allow

running = True


# Initial game bucle
while running:

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

    events = pygame.event.get()

    for event in events:  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False

    game_master.handle_events(events, player, virtual_canvas, ground, screen)

    # 3. UPDATES

    game_master.update_game(player, delta_time, virtual_canvas, ground)

    # 4. DRAW

    game_master.draw(virtual_canvas, player, background, ground)

    streched_canvas = pygame.transform.scale(
        virtual_canvas, (screen_width, screen_height)
    )

    screen.blit(streched_canvas, (0, 0))

    # update screen
    pygame.display.flip()

pygame.quit()
