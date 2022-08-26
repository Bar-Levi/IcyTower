import sys
import pygame
import random

GAME_FPS = 150
WIDTH, HEIGHT = 1000, 700
JUMPING_HEIGHT = 20
MAX_ACCELERATION = 13
VEL_X = 3  # Setting the moving speed.
VEL_Y = JUMPING_HEIGHT  # Setting the jumping height.
pygame.init()
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
GAMEPLAY_SOUND_LENGTH = 31  # 31 seconds.
SHELVES_COUNT = 500  # Number of shelves in the game.

# Images:
BODY_IMAGE = pygame.image.load("Assets/body.png")
BACKGROUND = pygame.image.load("Assets/background.png")
BRICK_IMAGE = pygame.image.load("Assets/brick_block.png")
SHELF_BRICK_IMAGE = pygame.image.load("Assets/shelf_brick.png")

# Walls settings:
WALLS_Y = -128
WALL_WIDTH = 128
WALLS_ROLLING_SPEED = 2
RIGHT_WALL_BOUND = WIDTH - WALL_WIDTH
LEFT_WALL_BOUND = WALL_WIDTH

# Background settings:
BACKGROUND_WIDTH = WIDTH - 2 * WALL_WIDTH  # 2*64 is for two walls on the sides.
BACKGROUND_ROLLING_SPEED = 1
BACKGROUND_Y = HEIGHT - BACKGROUND.get_height()
background_y = BACKGROUND_Y

# Booleans:
jumping = False
falling = False
standing = False
rolling_down = False
new_movement = False
current_direction = None
current_standing_shelf = None

# Colors:
GRAY = (180, 180, 180)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


class Shelf:
    def __init__(self, number):
        self.number = number
        self.image = None
        self.width = random.randint(4, 7) * 32
        self.x = random.randint(LEFT_WALL_BOUND, RIGHT_WALL_BOUND - self.width)
        self.y = - number * 130 + HEIGHT - 25
        self.rect = pygame.Rect(self.x, self.y, self.width, 32)


class Body:
    def __init__(self):
        self.size = 64
        self.x = WIDTH / 2 - self.size / 2
        self.y = HEIGHT - 25 - self.size
        self.vel_y = 0
        self.acceleration = 0
        self.jumpable = self.vel_y <= 0  # If body is hitting a level, then it can jump only if the body is going down.


body = Body()

total_shelves_list = []
for num in range(0, SHELVES_COUNT + 1):  # Creating all the game shelves.
    new_shelf = Shelf(num)
    if num % 50 == 0:
        new_shelf.width = BACKGROUND_WIDTH
        new_shelf.rect.width = BACKGROUND_WIDTH
        new_shelf.x = WALL_WIDTH
        new_shelf.rect.x = WALL_WIDTH
    total_shelves_list.append(new_shelf)

# Sounds:
JUMPING_SOUND = pygame.mixer.Sound("Assets/jumping_sound.wav")
GAMEPLAY_SOUND = pygame.mixer.Sound("Assets/gameplay_sound.wav")
HOORAY_SOUND = pygame.mixer.Sound("Assets/hooray_sound.wav")


def Move(direction):  # Moving the body according to the wanted direction.
    if direction == "Left":
        if body.x - body.acceleration >= LEFT_WALL_BOUND:  # If the body isn't about to pass the left wall on the next step.
            body.x -= body.acceleration  # Take the step.
        else:  # If the body is about to pass the left wall on the next step.
            body.x = LEFT_WALL_BOUND  # Force it to stay inside.
    else:  # If direction is right
        if body.x + body.acceleration <= RIGHT_WALL_BOUND - body.size:  # If the body isn't about to pass the right wall on the next step.
            body.x += body.acceleration  # Take the step.
        else:  # If the body is about to pass the right wall on the next step.
            body.x = RIGHT_WALL_BOUND - body.size  # Force the body to stay inside.
    body.acceleration -= 1  # Decreasing body's movement speed.


def HandleMovement(keys_pressed):  # Handling the Left/Right buttons pressing.
    global body, new_movement, current_direction
    if keys_pressed[pygame.K_LEFT] and body.x > LEFT_WALL_BOUND:  # If pressed "Left", and body is inside the bounding.
        current_direction = "Left"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION
    if keys_pressed[
        pygame.K_RIGHT] and body.x < RIGHT_WALL_BOUND:  # If pressed "Right", and body is inside the bounding.
        current_direction = "Right"
        if body.acceleration + 3 <= MAX_ACCELERATION:  # If body's movement speed isn't maxed.
            body.acceleration += 3  # Accelerating the body's movement speed.
        else:
            body.acceleration = MAX_ACCELERATION


def DrawWindow():  # Basically, drawing the screen.
    global WALLS_Y
    font = pygame.font.SysFont("Arial", 26)
    HandleBackground()
    for shelf in total_shelves_list:
        for x in range(shelf.rect.x, shelf.rect.x + shelf.width, 32):
            WIN.blit(SHELF_BRICK_IMAGE, (x, shelf.rect.y))  # Drawing the shelf.
            if shelf.number % 10 == 0 and shelf.number != 0:
                shelf_number = pygame.Rect(shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y,
                                           16 * len(str(shelf.number)), 25)
                pygame.draw.rect(WIN, GRAY, shelf_number)
                txt = font.render(str(shelf.number), True, BLACK)
                WIN.blit(txt,
                         (shelf.rect.x + shelf.rect.width / 2 - 16, shelf.rect.y))  # Drawing the number of the shelf.
    for y in range(WALLS_Y, HEIGHT, 108):  # Drawing the walls.
        WIN.blit(BRICK_IMAGE, (0, y))
        WIN.blit(BRICK_IMAGE, (WIDTH - WALL_WIDTH, y))
    WIN.blit(BODY_IMAGE, (body.x, body.y))  # Drawing the body.
    pygame.display.update()


def OnShelf():  # Checking whether the body is on a shelf, returning True/False.
    global jumping, standing, falling, BACKGROUND_ROLLING_SPEED, current_standing_shelf
    if body.vel_y <= 0:  # Means the body isn't moving upwards, so now it's landing.
        for shelf in total_shelves_list:
            if body.y <= shelf.rect.y - body.size <= body.y - body.vel_y:  # If y values collide.shelf.rect.y - body.size >= body.y and shelf.rect.y - body.size <= body.y - body.vel_y
                if body.x + body.size * 2 / 3 >= shelf.rect.x and body.x + body.size * 1 / 3 <= shelf.rect.x + shelf.width:  # if x values collide.
                    body.y = shelf.rect.y - body.size
                    if current_standing_shelf != shelf.number and shelf.number % 50 == 0 and shelf.number != 0:
                        BACKGROUND_ROLLING_SPEED += 1  # Rolling speed increases every 50 shelves.
                        current_standing_shelf = shelf.number
                    if shelf.number % 100 == 0 and shelf.number != 0:
                        HOORAY_SOUND.play()
                    if shelf.number == SHELVES_COUNT:
                        GameOver()
                    return True
    else:  # Means body in not on a shelf.
        jumping, standing, falling = False, False, True


def ScreenRollDown():  # Increasing the y values of all elements.
    global background_y, WALLS_Y
    for shelf in total_shelves_list:
        shelf.rect.y += 1
    body.y += 1
    background_y += 0.5
    if background_y == BACKGROUND_Y + 164:
        background_y = BACKGROUND_Y
    WALLS_Y += WALLS_ROLLING_SPEED
    if WALLS_Y == 0:
        WALLS_Y = -108


def GameOver():  # Quitting the game.
    pygame.quit()
    sys.exit(1)


def CheckIfTouchingFloor():  # Checking if the body is still on the main ground.
    global standing, falling
    if body.y > HEIGHT - body.size:
        if not rolling_down:  # Still on the starting point of the game, can't lose yet.
            body.y = HEIGHT - body.size
            standing, falling = True, False
        else:  # In a more advanced part of the game, when can already lose.
            GameOver()


def HandleBackground(): # Drawing the background.
    if body.y >= total_shelves_list[500].rect.y:
        WIN.blit(BACKGROUND, (32, background_y))


def main():  # Main function.
    global body, keys_pressed, total_shelves_list, jumping, standing, falling, rolling_down, new_movement
    game_running = True
    rolling_down = False
    paused = False
    sound_timer = 0
    while game_running:
        while game_running and not paused:
            on_ground = not rolling_down and body.y == HEIGHT - 25 - body.size
            if sound_timer % (56 * GAMEPLAY_SOUND_LENGTH) == 0:  # 56 = Program loops count per second.
                GAMEPLAY_SOUND.play()
            sound_timer += 1
            if rolling_down:  # If screen should roll down.
                for _ in range(BACKGROUND_ROLLING_SPEED):
                    ScreenRollDown()
            DrawWindow()  # Draw shelves, body and background.
            keys_pressed = pygame.key.get_pressed()
            HandleMovement(keys_pressed)  # Moving according to the pressed buttons.
            if body.acceleration != 0:  # If there's any movement.
                Move(current_direction)
            if keys_pressed[pygame.K_SPACE] and (
                    standing or on_ground):  # If enter "Space" and currently not in mid-jump.
                body.vel_y = VEL_Y  # Resets the body's jumping velocity.
                jumping, standing, falling = True, False, False
            if jumping and body.vel_y >= 0:  # Jumping up.
                if body.vel_y == VEL_Y:  # First moment of the jump.
                    JUMPING_SOUND.play()
                print("Jumping...")
                body.y -= body.vel_y
                body.vel_y -= 1
                if body.y <= HEIGHT / 5:  # If the body get to the top quarter of the screen.
                    rolling_down = True  # Starts rolling down the screen.
                    for _ in range(10):  # Rolling 10 times -> Rolling faster, so he can't pass the top of the screen.
                        ScreenRollDown()
                if not body.vel_y:  # Standing in the air.
                    jumping, standing, falling = False, False, True
            if falling:  # Falling down.
                if OnShelf():  # Standing on a shelf.
                    print("Standing...")
                    jumping, standing, falling = False, True, False
                else:  # Not standing - keep falling down.
                    print("Falling...")
                    body.y -= body.vel_y
                    body.vel_y -= 1
            CheckIfTouchingFloor()
            if standing and not OnShelf() and not on_ground:  # If falling from a shelf.
                print("Falling from shelf...")
                body.vel_y = 0  # Falls slowly from the shelf and not as it falls at the end of a jumping.
                standing, falling = False, True
            if body.acceleration == MAX_ACCELERATION - 1:  # While on max acceleration, getting a jumping height boost.
                VEL_Y = JUMPING_HEIGHT + 5
            else:  # If not on max acceleration.
                VEL_Y = JUMPING_HEIGHT  # Back to normal jumping height.

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    game_running = False
            pygame.time.Clock().tick(GAME_FPS)


if __name__ == "__main__":
    main()
