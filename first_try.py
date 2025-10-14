import pygame
import gif_pygame

#Initiate pygame
pygame.init()

#Set screen size
screen = pygame.display.set_mode((1600, 960))

#Set player using gif-pygame library
player = gif_pygame.load("./assets/Personaje_Arnaldo_pequeño_escalado.gif").convert()

#Load background image
background = pygame.image.load("./assets/Fondo.png").convert()

# Resize image to fit window
background = pygame.transform.scale(background, (1600, 960))


#convert()=

running = True
x = 0

#Initial game bucle
while running:
    
    for event in pygame.event.get(): #iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False
        # pygame.QUIT event means the user clicked X to close your window

            
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
        # pygame.K_SCAPE event means the user press Esc button to close your window

    #Set background image
    screen.blit(background, (0, 0))
    
    #set player using gif-pygame library
    screen.blit(player, (x, 0))

            
    pygame.display.flip()
            
pygame.quit()
            
            