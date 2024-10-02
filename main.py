import pygame
import time
import math
import utils
from utils import *
import button
pygame.font.init()

pygame.init()

pygame.display.set_caption("Main Menu")

# game variables
game_paused = False
menu_state = "MAIN"
game_state = None
display_info = True

# define fonts
font = pygame.font.SysFont("arial black", 40)

# define colours
TEXT_COL = (255, 255, 255)

# load game images
GRASS = scale_image(pygame.image.load("images/grass.jpg"), 3)
TRACK = scale_image(pygame.image.load("images/track.png"), 1.2)

TRACK_BORDER = scale_image(pygame.image.load("images/track-border.png"), 1.2)
TRACK_BORDER_mask = pygame.mask.from_surface(TRACK_BORDER)
FINISH = scale_image(pygame.image.load("images/finish.png"), 1.55)
FINISH_MASK = pygame.mask.from_surface(FINISH)
FINISH_POSITION = (130, 250)

# load car images
PURPLE_CAR = scale_image(pygame.image.load("images/purple-car.png"), 0.65)
GREY_CAR = scale_image(pygame.image.load("images/grey-car.png"), 0.65)

# initialising display width and height
WIDTH, HEIGHT = TRACK.get_width(), TRACK.get_height()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))

# displaying the title of the game
pygame.display.set_caption("Racing Game!")

# initialising font style
MAIN_FONT = pygame.font.SysFont("consolas", 35)

# max FPS and computer car path pixel locations
FPS = 120
PATH = [(146, 96), (76, 177), (82, 626), (415, 973), (539, 921), (538, 727), (671, 633), (793, 715), (812, 948),
        (978, 953), (988, 540), (871, 484), (570, 484), (532, 377), (675, 344), (961, 337), (1000, 214), (943, 106),
        (426, 98), (368, 175), (370, 474), (304, 537), (224, 479), (224, 264)]

# load button images
resume_img = pygame.image.load("images/button_resume.png").convert_alpha()
options_img = pygame.image.load("images/button_options.png").convert_alpha()
quit_img = pygame.image.load("images/button_quit.png").convert_alpha()
video_img = pygame.image.load('images/button_video.png').convert_alpha()
audio_img = pygame.image.load('images/button_audio.png').convert_alpha()
keys_img = pygame.image.load('images/button_keys.png').convert_alpha()
back_img = pygame.image.load('images/button_back.png').convert_alpha()
two_player_img = pygame.image.load('images/image_1v1.png').convert_alpha()
vs_computer_img = pygame.image.load('images/image_vs-computer.png').convert_alpha()

# create button instances
resume_button = button.Button(448, 250, resume_img, 1)
options_button = button.Button(441, 400, options_img, 1)
quit_button = button.Button(480, 550, quit_img, 1)
two_player_button = button.Button(459, 250, two_player_img, 0.9)
vs_computer_button = button.Button(389, 400, vs_computer_img, 0.8)


# creating a class for game information
class GameInfo:
    LEVELS = 10

    def __init__(self, level=1):
        self.level = level
        self.started = False
        self.level_started_time = 0

    def next_level(self):
        self.level += 1
        self.started = False

    def reset(self):
        self.level = 1
        self.started = False
        self.level_started_time = 0

    def game_finished(self):
        return self.level > self.LEVELS

    def start_level(self):
        self.started = True
        self.level_started_time = time.time()

    def get_level_time(self):
        if not self.started:
            return 0
        return round(time.time() - self.level_started_time)


# creating an abstract class for all car functions
class AbstractCar:

    def __init__(self, max_vel, rotation_vel):
        self.img = self.IMG
        self.max_vel = max_vel
        self.vel = 0
        self.rotation_vel = rotation_vel
        self.angle = 0
        self.x, self.y = self.START_POS
        self.acceleration = 0.1

    def rotate(self, left=False, right=False):
        if left:
            self.angle += self.rotation_vel

        elif right:
            self.angle -= self.rotation_vel

    def draw(self, win):
        blit_rotate_center(win, self.img, (self.x, self.y), self.angle)

    def move_forward(self):
        self.vel = min(self.vel + self.acceleration, self.max_vel)
        self.move()

    def move_backward(self):
        self.vel = max(self.vel - self.acceleration, -self.max_vel/2)
        self.move()

    def move(self):
        radians = math.radians(self.angle)
        vertical = math.cos(radians) * self.vel
        horizontal = math.sin(radians) * self.vel

        self.y -= vertical
        self.x -= horizontal

    def collide(self, mask, x=0, y=0):
        car_mask = pygame.mask.from_surface(self.img)
        offset = (int(self.x - x), int(self.y - y))
        poi = mask.overlap(car_mask, offset)
        return poi

    def reset(self):
        self.x, self.y = self.START_POS
        self.angle = 0
        self.vel = 0


# creating class for player_1 car which is inherited from abstract class
class Player1Car(AbstractCar):
    IMG = PURPLE_CAR
    START_POS = (240, 190)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


# creating class for player_2 car which is inherited from abstract class
class Player2Car(AbstractCar):
    IMG = GREY_CAR
    START_POS = (210, 190)

    def reduce_speed(self):
        self.vel = max(self.vel - self.acceleration / 2, 0)
        self.move()

    def bounce(self):
        self.vel = -self.vel
        self.move()


# creating class for computer car which is inherited from abstract class
class ComputerCar(AbstractCar):
    IMG = GREY_CAR
    START_POS = (210, 190)

    def __init__(self, max_vel, rotation_vel, path=[]):
        super().__init__(max_vel, rotation_vel)
        self.path = path
        self.current_point = 0
        self.vel = max_vel

    def calculate_angle(self):
        target_x, target_y = self.path[self.current_point]
        x_diff = target_x - self.x
        y_diff = target_y - self.y

        if y_diff == 0:
            desired_radian_angle = math.pi / 2
        else:
            desired_radian_angle = math.atan(x_diff / y_diff)

        if target_y > self.y:
            desired_radian_angle += math.pi

        difference_in_angle = self.angle - math.degrees(desired_radian_angle)
        if difference_in_angle >= 180:
            difference_in_angle -= 360

        if difference_in_angle > 0:
            self.angle -= min(self.rotation_vel, abs(difference_in_angle))
        else:
            self.angle += min(self.rotation_vel, abs(difference_in_angle))

    def update_path_point(self):
        target = self.path[self.current_point]
        rect = pygame.Rect(self.x, self.y, self.img.get_width(), self.img.get_height())
        if rect.collidepoint(*target):
            self.current_point += 1

    def move(self):
        if self.current_point >= len(self.path):
            return

        self.calculate_angle()
        self.update_path_point()
        super().move()

    def next_level(self, level):
        self.reset()
        self.vel = self.max_vel + ((level - 1) * 0.2)
        self.current_point = 0


# function to draw images and game information on the screen
def draw(win, images, player_car, computer_car, game_info):
    for img, pos in images:
        WIN.blit(img, pos)

    if display_info:

        level_text = MAIN_FONT.render(f"Level {game_info.level}", 1, (255, 255, 255))
        win.blit(level_text, (10, HEIGHT - level_text.get_height() - 70))

        time_text = MAIN_FONT.render(f"Time: {game_info.get_level_time()}s", 1, (255, 255, 255))
        win.blit(time_text, (10, HEIGHT - time_text.get_height() - 40))

        vel_text = MAIN_FONT.render(f"Vel: {round(player_car.vel, 1)}px/s", 1, (255, 255, 255))
        win.blit(vel_text, (10, HEIGHT - vel_text.get_height() - 10))

    player_car.draw(win)
    computer_car.draw(win)
    pygame.display.update()


# functions to move cars
def move_player_1(player_1_car):
    utils.car_1_movement(player_1_car)


def move_player_2(player_2_car):
    utils.car_2_movement(player_2_car)


# function to handel collision between two entities
def handel_collision(player1car, player2car, game_info):
    if player1car.collide(TRACK_BORDER_mask) != None:
        player_1_car.bounce()
    if game_state == "1v1":
        if player2car.collide(TRACK_BORDER_mask) != None:
            player_2_car.bounce()

    player_1_finish_poi_collide = player1car.collide(FINISH_MASK, *FINISH_POSITION)
    player_2_finish_poi_collide = player2car.collide(FINISH_MASK, *FINISH_POSITION)

    if game_state == "vs_computer":
        if player_2_finish_poi_collide != None:
            blit_text_center(WIN, MAIN_FONT, "You lost!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_1_car.reset()
            computer_car.reset()

        if player_1_finish_poi_collide != None:
            if player_1_finish_poi_collide[1] == 0:
                player_1_car.bounce()
            else:
                game_info.next_level()
                player_1_car.reset()
                computer_car.next_level(game_info.level)

    if game_state == "1v1":
        if player_1_finish_poi_collide != None:
            if player_1_finish_poi_collide[1] == 0:
                player_1_car.bounce()
            else:
                blit_text_center(WIN, MAIN_FONT, "Player 1 won the game!")
                pygame.display.update()
                pygame.time.wait(5000)
                player_1_car.reset()
                player_2_car.reset()

        if player_2_finish_poi_collide != None:
            if player_2_finish_poi_collide[1] == 0:
                player_2_car.bounce()
            else:
                blit_text_center(WIN, MAIN_FONT, "Player 2 won the game!")
                pygame.display.update()
                pygame.time.wait(5000)
                player_1_car.reset()
                player_2_car.reset()


def draw_text(text, font, text_col, x, y):
    img = font.render(text, True, text_col)
    WIN.blit(img, (x, y))


def countdown(num):
    if num >= 1:
        draw(WIN, images, player_1_car, computer_car, game_info)
        blit_text_center(WIN, MAIN_FONT, f"{num}")
        pygame.display.update()
        pygame.time.wait(1000)
        countdown(num-1)

    if num == 0:
        draw(WIN, images, player_1_car, computer_car, game_info)
        blit_text_center(WIN, MAIN_FONT, "Go!")
        pygame.display.update()
        pygame.time.wait(200)


clock = pygame.time.Clock()
images = [(GRASS, (0, 0)), (TRACK, (0, 0)), (FINISH, FINISH_POSITION), (TRACK_BORDER, (0, 0))]
player_1_car = Player1Car(6, 4)
player_2_car = Player2Car(6, 4)
computer_car = ComputerCar(2, 4, PATH)
game_info = GameInfo()
keys = pygame.key.get_pressed()
grass = GRASS

# game loop
run = True
while run:
    clock.tick(FPS)

    if menu_state == "MAIN":
        WIN.fill((52, 78, 91))
        if two_player_button.draw(WIN):
            game_state = "1v1"
        if vs_computer_button.draw(WIN):
            game_state = "vs_computer"
        if quit_button.draw(WIN):
            run = False

    # check if game is paused
    if game_paused:
        WIN.fill((52, 78, 91))
        # check menu state
        if menu_state == "PAUSED":
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_SPACE:
                        game_paused = False
                        game_state = game_type
            # draw pause screen buttons
            if resume_button.draw(WIN):
                game_paused = False
                game_state = game_type
            if options_button.draw(WIN):
                player_1_car.reset()
                player_2_car.reset()
                game_info.reset()
                computer_car.reset()
                game_paused = False
                game_state = game_type

            if quit_button.draw(WIN):
                run = False

# event handler
    for event in pygame.event.get():
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_SPACE:
                game_paused = True
                menu_state = "PAUSED"
                game_state = None
        if event.type == pygame.QUIT:
            run = False

    # game starts against computer if the condition is true
    if game_state == "vs_computer":
        game_type = game_state
        draw(WIN, images, player_1_car, computer_car, game_info)
        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, f"press any key to start level {game_info.level}!")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break

                if event.type == pygame.KEYDOWN:
                    countdown(3)
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True
                    menu_state = "PAUSED"
                    game_state = None

        move_player_1(player_1_car)
        computer_car.move()

        handel_collision(player_1_car, computer_car, game_info)

        if game_info.game_finished():
            blit_text_center(WIN, MAIN_FONT, "You won the game!")
            pygame.display.update()
            pygame.time.wait(5000)
            game_info.reset()
            player_1_car.reset()
            computer_car.reset()

    # game starts in two player mode if the condition is true
    if game_state == "1v1":
        game_type = game_state
        display_info = False
        draw(WIN, images, player_1_car, player_2_car, game_info)
        while not game_info.started:
            blit_text_center(WIN, MAIN_FONT, "Press any key to start")
            pygame.display.update()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    break
                if event.type == pygame.KEYDOWN:
                    countdown(3)
                    game_info.start_level()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    game_paused = True
                    menu_state = "PAUSED"
                    game_state = None

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                break

        move_player_1(player_1_car)
        move_player_2(player_2_car)

        handel_collision(player_1_car, player_2_car, None)

    pygame.display.update()

pygame.quit()
