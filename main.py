import pygame
import gif_pygame
import models 

#Initiate pygame
pygame.init()

#Set screen size
screen = pygame.display.set_mode((1600, 960))

#Set player image using gif-pygame library
player_image = gif_pygame.load("./assets/Personaje_Arnaldo_pequeño_escalado.gif")

#Set player speed
player_speed = 300

player = models.GameObject(player_image, player_speed)

#Load background image
background = pygame.image.load("./assets/Fondo.png").convert()

# Resize background image to fit window
background = pygame.transform.scale(background, (1600, 960))

#set game clock to control the time the loop
clock = pygame.time.Clock() 
#Each round loop is a frame 
#without the control (clock), the loop will run at the fastest speed that the computer can allow 

#player_initial_position = pygame.Vector2(0, 510)



#convert()= returns us a new Surface of the image, but now converted to the same pixel format as our display. Since the images will be the same format at the screen, they will blit very quickly. If we did not convert, the blit() function is slower, since it has to convert from one type of pixel to another as it goes.

running = True
x = 0



#Initial game bucle
while running:
    
    #set the frames per second 
    fps = clock.tick(60)  # limita el juego a 60 FPS
    #clock.tick returns the miliseconds since the last frame
    
    #delta time 
    delta_time = fps / 1000
    #we divide it between 1000 to tranform into seconds 
        
    #if speed = 200 and delta_time = 0.016 (1/60 fps), the player is moving at 200 * 0.016 = 3.2 píxels in that frame

    #Set background image
    screen.blit(background, (0, 0))
    
    #set player using gif-pygame library in initial position
    player.draw_in_screen(screen)


    
    for event in pygame.event.get(): #iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # pygame.K_SCAPE event means the user press Esc button to close your window       
        
    get_pressed_keys = pygame.key.get_pressed()
    #set a key that occurrs while the player get pressed a button on the keyboard

    if get_pressed_keys[pygame.K_RIGHT]:
        player.rect.x += player.speed * delta_time
    
    
    if get_pressed_keys[pygame.K_LEFT]:
        player.rect.x -= player.speed * delta_time
        
            



    #update screen            
    pygame.display.flip()
            
pygame.quit()
            
            