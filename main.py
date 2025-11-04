import pygame
import gif_pygame
import models
import functions
from gif_pygame import transform
import time

# Initiate pygame
pygame.init()

# Set screen size
screen = functions.setup_screen(False)
screen_width, screen_height = screen.get_size()

#creating scale factors acording background asset
base_width = 320
base_height = 180

# scales factors 
scale_x = screen_width / base_width
scale_y = screen_height / base_height

# Load background image
background = pygame.image.load("./assets/Backgruound_320x180.png").convert()

# Resize background image to fit window
background = pygame.transform.scale(background, (screen_width, screen_height))

#load background image
ground_image = pygame.image.load("./assets/Ground.png")

#scaling ground image acording scale factors
ground_image = functions.resize(ground_image, scale_x, scale_y)

#creating ground object 
ground = models.Platform("ground", ground_image)

#set ground position
ground.set_position((screen_width - ground.rect.width), (screen_height - ground.rect.height))

# Set player image using gif-pygame library
player_image = functions.setup_player_gif(screen)

# Set player speed
player_x_speed = 300

#Player name
player_name = "Arnaldo"

# creating player object
player = models.Player(player_name, player_image, player_x_speed)

#set player inicial position
player.set_position(screen_width/2, ground.rect.top, True)

#creating enemy object and setting position 
enemy_image = pygame.Surface([90, 90])
enemy_image.fill((255, 0, 0))
enemy = models.Enemy("Luki", enemy_image)
enemy.set_position((player.rect.width/2), ground.rect.top, True)



# set game clock to control the time the loop
clock = pygame.time.Clock()
# Each round loop is a frame
# without the control (clock), the loop will run at the fastest speed that the computer can allow

# convert()= returns us a new Surface of the image, but now converted to the same pixel format as our display. Since the images will be the same format at the screen, they will blit very quickly. If we did not convert, the blit() function is slower, since it has to convert from one type of pixel to another as it goes.

running = True

#Creating pygame groups and adding sprites into them
models.all_sprites.add(player)
models.all_sprites.add(enemy)
models.enemy_group.add(enemy)


# Initial game bucle
while running:
    
    counter = []

    #1. CLOCK

    # set the frames per second
    pased_miliseconds = clock.tick(60)  
    # limita el juego a 60 FPS
    #esto devuelve los milisegundos que pasaron desde el ultimo frame (duracion del frame anterior en milisegundos)
    # clock.tick returns the miliseconds since the last frame

    # delta time
    delta_time = pased_miliseconds / 1000.0
    # we divide it between 1000 to tranform into seconds
    # if speed = 200 and delta_time = 0.016 (1/60 fps), the player is moving at 200 * 0.016 = 3.2 píxels in that frame
    
    #2. INPUT (events)
    
    TrigerAttack = False
    
    for event in pygame.event.get():  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # pygame.K_SCAPE event means the user press Esc button to close your window
        
        if event.type == pygame.MOUSEBUTTONDOWN:
            
            if event.button == 1:
                TrigerAttack = True
                

    get_pressed_keys = pygame.key.get_pressed()
    # set a key that occurrs while the player get pressed a button on the keyboard

    move_right = get_pressed_keys[pygame.K_d]
    move_left = get_pressed_keys[pygame.K_a]
    jumping = get_pressed_keys[pygame.K_SPACE]
    face_up = get_pressed_keys[pygame.K_w]
    face_down = get_pressed_keys[pygame.K_s]
    
    
    #3. MOVEMENT
    
    #set attack
    if TrigerAttack: 
        player.trigger_attack(attack=True)
    
    player.update_player(delta_time, screen, ground, enemy, move_right, move_left, jumping, face_up, face_down)
    print(player.state)
    
    enemy.movement(screen, delta_time)
    
    models.moving_sprites.update()
    
    #4. CHECK COLLISIONS 
    
    enemies_collision = pygame.sprite.spritecollide(player, models.enemy_group, False)
    
    if enemies_collision: 
        player.take_damage(enemy)
        print(player.state, "colisionando!")

    #5. DRAW

    # Set ground rect & image
    ground.draw(screen)
    
    #set background
    screen.blit(background, (0, 0))

    #Set moving objects 
    for sprite in models.moving_sprites:
        sprite.draw(screen) # call to .draw() method from GameObjects that can handle gifs
        
    player.draw_hitbox(screen, enemy)
    
    
    # update screen
    pygame.display.flip()

pygame.quit()
