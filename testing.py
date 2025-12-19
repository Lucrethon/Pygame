
import pygame
import functions
pygame.init()

screen = functions.setup_screen(True)

background = pygame.image.load("./assets/Background_960x540.png").convert()


player = (pygame.image.load("./assets/Player_Sprites/Down_Slashing1.png").convert_alpha())
player_copy = player.copy().convert_alpha()
player_copy.fill((255, 255, 255), special_flags=pygame.BLEND_RGB_ADD)
# rect = player.get_rect()
# hitbox = (rect.x + 6, rect.y + 10, 27, 52)
running = True

while running:
    
    events = pygame.event.get()

    for event in events:  # iteracion sobre todos los eventos de pygame
        if event.type == pygame.QUIT:
            running = False

    screen.blit(background, (0, 0))
    screen.blit(player_copy, (100, 100))
    #pygame.draw.rect(screen, (255, 0, 0), hitbox, 1)
    pygame.display.flip()