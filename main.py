import pygame
import gif_pygame
import models
import functions
from gif_pygame import transform
import time

# Initiate pygame
pygame.init()

# Set screen size
screen = functions.setup_screen(True)
screen_width, screen_height = screen.get_size()

virtual_width = 960
virtual_height = 540

virtual_canvas = pygame.Surface((virtual_width, virtual_height))

# Load background image
background = pygame.image.load("./assets/Background_960x540.png").convert()

# load background image
ground_image = pygame.image.load("./assets/Ground_scaled_960x540.png")

# creating ground object
ground = models.Platform("ground", ground_image)

# set ground position
ground.set_position(
    (virtual_width - ground.rect.width), (virtual_height - ground.rect.height)
)

# Set player image using gif-pygame library
player_image = functions.setup_player_gif(virtual_canvas)

#Player attack slash sprite 
sprite_attack_slash = pygame.image.load("./assets/Attack_Slashx3.png").convert_alpha()

# Set player speed
player_x_speed = 300

# Player name
player_name = "Arnaldo"

# creating player object
player = models.Player(player_name, player_image, player_x_speed, sprite_attack_slash)

# set player inicial position
player.set_position(virtual_width / 2, ground.rect.top, True)

# creating enemy object and setting position
enemy_image = pygame.Surface([90, 90])
enemy_image.fill((255, 0, 0))
enemy = models.Enemy("Luki", enemy_image)
enemy.set_position((virtual_width / 4), ground.rect.top, True)


# set game clock to control the time the loop
clock = pygame.time.Clock()
# Each round loop is a frame
# without the control (clock), the loop will run at the fastest speed that the computer can allow

# convert()= returns us a new Surface of the image, but now converted to the same pixel format as our display. Since the images will be the same format at the screen, they will blit very quickly. If we did not convert, the blit() function is slower, since it has to convert from one type of pixel to another as it goes.

running = True

# Creating pygame groups and adding sprites into them
models.all_sprites.add(player)
models.all_sprites.add(enemy)
models.enemy_group.add(enemy)


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

    for event in pygame.event.get():  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # pygame.K_SCAPE event means the user press Esc button to close your window
            if event.key == pygame.K_s:
                TrigerAttack = True

    get_pressed_keys = pygame.key.get_pressed()
    # set a key that occurrs while the player get pressed a button on the keyboard

    move_right = get_pressed_keys[pygame.K_RIGHT]
    move_left = get_pressed_keys[pygame.K_LEFT]
    jumping = get_pressed_keys[pygame.K_SPACE]
    face_up = get_pressed_keys[pygame.K_UP]
    face_down = get_pressed_keys[pygame.K_DOWN]

    # 3. MOVEMENT

    # set attack
    if TrigerAttack:
        player.trigger_attack(attack=True)

    player.update_player(
        delta_time, virtual_canvas, ground, move_right, move_left, jumping, face_up, face_down
    )

    enemy.update_enemy(delta_time, virtual_canvas, ground)

    models.moving_sprites.update()

    # 4. CHECK COLLISIONS

    enemies_collision = pygame.sprite.spritecollide(player, models.enemy_group, False)

    if enemies_collision:    
        
        for enemy in enemies_collision:

            if player.state == models.States.HURT or player.is_invulnerable:
                pass
            else:
                player.take_damage()
                functions.knockback(player, enemy, True)


    #check hitbox collision 
    if player.active_hitbox: 
        
        for enemy in models.enemy_group:

            if player.active_hitbox.colliderect(enemy.rect):
                
                if enemy not in player.enemies_attacked:
                    
                    if player.orientation == models.Orientation.DOWN:
                        enemy.take_damage()
                        #functions.knockback(player, enemy, False)
                        player.trigger_pogo()
                        player.enemies_attacked.append(enemy)
                        
                    else:
                        enemy.take_damage()
                        functions.knockback(player, enemy, False)
                        player.start_attack_recoil()
                        player.enemies_attacked.append(enemy)
                else:
                    pass
            
            else: 
                pass
            

    # 5. DRAW

    # Set ground rect & image
    ground.draw(virtual_canvas)
    
    # set background
    virtual_canvas.blit(background, (0, 0))
    
    # Set moving objects
    for sprite in models.moving_sprites:
        sprite.draw(
            virtual_canvas
        )  # call to .draw() method from GameObjects that can handle gifs

    player.draw_attack(virtual_canvas)
    
    streched_canvas = pygame.transform.scale(virtual_canvas, (screen_width, screen_height))
    
    screen.blit(streched_canvas, (0, 0))

    # update screen
    pygame.display.flip()

pygame.quit()
