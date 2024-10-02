import pygame
pygame.font.init()
font = pygame.font.SysFont("arial black", 40)


def scale_image(img, factor):
    size = round(img.get_width() * factor), round(img.get_height() * factor)
    return pygame.transform.scale(img, size)


def blit_rotate_center(win, image, top_left, angle):
    rotated_image = pygame.transform.rotate(image, angle)
    new_rect = rotated_image.get_rect(center=image.get_rect(topleft=top_left).center)
    win.blit(rotated_image, new_rect.topleft)


def car_2_movement(player_2_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_a]:
        player_2_car.rotate(left=True)
    if keys[pygame.K_d]:
        player_2_car.rotate(right=True)
    if keys[pygame.K_w]:
        moved = True
        player_2_car.move_forward()
    if keys[pygame.K_s]:
        moved = True
        player_2_car.move_backward()

    if not moved:
        player_2_car.reduce_speed()


def car_1_movement(player_1_car):
    keys = pygame.key.get_pressed()
    moved = False

    if keys[pygame.K_LEFT]:
        player_1_car.rotate(left=True)
    if keys[pygame.K_RIGHT]:
        player_1_car.rotate(right=True)
    if keys[pygame.K_UP]:
        moved = True
        player_1_car.move_forward()
    if keys[pygame.K_DOWN]:
        moved = True
        player_1_car.move_backward()

    if not moved:
        player_1_car.reduce_speed()


def blit_text_center(win, font, text):
    render = font.render(text, 1, (200, 200, 200))
    win.blit(render, (win.get_width()/2 - render.get_width()/2, win.get_height()/2 - render.get_height()/2))



