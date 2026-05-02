import pygame 


clock = pygame.time.Clock()

pygame.init()
screen = pygame.display.set_mode((1920, 1080), flags=pygame.NOFRAME)
pygame.display.set_caption("No start No end")
icon = pygame.image.load('images/icon.png').convert_alpha()
pygame.display.set_icon(icon)

bg = pygame.image.load('floors/floor mainwood.jpg').convert()
walk_right = [ pygame.image.load('images walk/r1.png').convert_alpha(),
              pygame.image.load('images walk/r2.png').convert_alpha()]
walk_left = [ pygame.image.load('images walk/l1.png').convert_alpha(),
              pygame.image.load('images walk/l2.png').convert_alpha()]
stay = [pygame.image.load('images walk/stay.png').convert_alpha()]

player_anim_count = 0
bg_x =0 
bg_y =0

player_speed = 10
player_x = 300
player_y = 350
walk_sound = pygame.mixer.Sound('sounds/steps.mp3')

walk_sound.play()
running = True
while running:
    
    screen.blit(bg, (bg_x, bg_y))
    screen.blit(bg, (bg_x + 2000, bg_y))
    screen.blit(bg, (bg_x, bg_y + 2000))
    screen.blit(bg, (bg_x, bg_y - 2000))
    
    keys = pygame.key.get_pressed()
    if not any(keys):
        screen.blit(stay)
    if keys[pygame.K_LEFT] and player_x > 300:
        player_x -= player_speed
        screen.blit(walk_left[int(player_anim_count)], (player_x, player_y))
        bg_x +=10
    elif keys[pygame.K_RIGHT] and player_x < 1600:
        player_x += player_speed
        screen.blit(walk_right[int(player_anim_count)], (player_x, player_y))
        bg_x -=10
    
    if keys[pygame.K_UP] and player_y > 120:
        player_y -= player_speed
        bg_y +=10
    elif keys[pygame.K_DOWN] and player_y < 900:
        player_y += player_speed
        bg_y -=10
    if player_anim_count >1:
        player_anim_count = 0
    else:
        player_anim_count = player_anim_count + 0.125
    
    pygame.display.update()
    
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
            pygame.quit()
    
    
    clock.tick(30)
