import pygame
import gif_pygame
import gif_pygame.transform
from abc import ABC, abstractmethod, abstractclassmethod
import time


# Initiate pygame
pygame.init()


class GameObject(ABC):

    def __init__(self, name, image):
        self.name = name
        self.image = image
        self.rect = self.image.get_rect()  # get the size of the image to create a rect

    # if self.image is .gif, it has to be place on the screen diferently than static images that uses blit(). Gifs have to be placed with .render()

    # sintaxis: gif.render(screen_size, (gif_coordinates_tobe_placed))
    
    @abstractmethod
    def draw(self, screen):
        if hasattr(
            self.image, "render"
        ):  # this condition check if an object (self.image in this case) has certain atribute ("render" in this case, proper of gif_pygame library (gif objects))
                
            self.image.render(screen, (self.rect))

        else:  # if not, it can draw also png and jpg images as well
            screen.blit(self.image, (self.rect))
            # .move_ip(x, y) moves the rect to those coordenates
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        
        if aling_bottom: 
            self.rect.midbottom = (x_pos, y_pos)
            #midbottom: Se refiere a la coordenada X y a la coordenada Y del punto central inferior de un rectángulo. 
        
        else:
            self.rect.topleft = (x_pos, y_pos)
        
    @abstractmethod
    def movement(self): 
        pass

    
            

class Player(GameObject):
    def __init__(self, name, image, x_speed):
        super().__init__(name, image)
        self.x_speed = x_speed
        self.y_speed = 0
        self.gravity = 2700
        self.jump_speed = -1000
        self.isJumping = False 
        self.HP = 5
        self.isAttacking = False 
        self.AttackDuration = 500 #miliseconds
        self.facing_right = True
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)
    
    def facing(self):
        pass
    
    def movement(self, delta_time, screen, ground, right=False, left=False, jump=False):
        
        delta_x = 0 #variation in x
        delta_y = 0 #variation in y
        
        if right:
            delta_x += self.x_speed * delta_time
            
            if self.facing_right: 
                pass
            else:
            
            #flip sprite to right
                self.facing_right = True 
                gif_pygame.transform.flip(self.image, True, False)
                # self.facing_right = True 
                # actual_surface = self.image.blit_ready()
                # flip_surface = pygame.transform.flip(actual_surface, True, False)
            
        if left:
            delta_x -= self.x_speed * delta_time
            
            #flip sprite to left 
            if not self.facing_right: 
                pass
            else:
            
            #flip sprite to left
                self.facing_right = False 
                gif_pygame.transform.flip(self.image, True, False)
        
        #if the player is not jumping and maitain Space button pressed (long jump)
        if jump and self.isJumping == False:
            self.y_speed = self.jump_speed
            self.isJumping = True
        
        #if the player is jumping (no ground collision yet, self.isJumping = True) and press space for a short time (short jump)
        if not jump and self.y_speed < 0:    
            self.y_speed *= 0.5       
            
            
        #setting the character go to the oposite side if he goes off the edge of one side of the screen 
            
        if self.rect.right > screen.get_width() + self.rect.width:
            self.rect.left = 0
                        
        elif self.rect.left < -self.rect.width:
            self.rect.right = screen.get_width()
            
        #Gravity that pull down the character to the ground 
        self.y_speed += (self.gravity * delta_time)
        delta_y += self.y_speed * delta_time
        
        
        #updates rect position 
        self.rect.x += delta_x
        self.rect.y += delta_y        
        
        # #check collition with the ground
        if self.rect.colliderect(ground.rect): 
            self.y_speed = 0
            self.rect.bottom = ground.rect.top
            self.isJumping = False
    
    def attack(self, attack = False):
        if attack and self.isAttacking == False:
            
            #setting self state
            self.isAttacking == True
            
            #set player sprite attack 
            
            #get time when the attack start
            start_attack_time = pygame.time.get_ticks
            
            #create temporal rect 
            
            #right the player 
            hitbox = pygame.Rect(self.rect.x + 50, 0, 90, 90)
            
            #check collision 
            
            #disapear rect 
            
            #attack end 
            now = pygame.time.get_ticks
            if now - start_attack_time > self.AttackDuration: 
                self.isAttacking = False
            
            
            
            
            

class Platform(GameObject):
    def __init__(self, name, image):
        super().__init__(name, image)
        
    def draw(self, screen):
        return super().draw(screen)
    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        return super().set_position(x_pos, y_pos, aling_bottom)

    def movement(self):
        pass


class Ememy():
    def __init__(self, name):
        self.name = name
        self.rect = pygame.Rect(0, 0, 90, 90)
        self.x_speed = 300
        self.HP = 6
    
    def draw(self, screen):
        pygame.draw.rect(screen, (255, 0, 0), (self.rect))

    
    def set_position(self, x_pos, y_pos, aling_bottom=False):
        if aling_bottom: 
            self.rect.midbottom = (x_pos, y_pos)
            #midbottom: Se refiere a la coordenada X y a la coordenada Y del punto central inferior de un rectángulo. 
        
        else:
            self.rect.topleft = (x_pos, y_pos)
    
    def movement(self, screen, delta_time):
        
        delta_x = 0
        delta_y = 0
        
        delta_x += self.x_speed * delta_time
        
        #updates rect position 
        self.rect.move_ip(delta_x, 0)
        
        #setting the enemy to don't go off the edge of the screen 
            
        if self.rect.right >= screen.get_width():
            self.x_speed *= -1

                                
        if self.rect.left <= 0:
            self.x_speed *= -1
        
        