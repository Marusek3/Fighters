import pygame
import sys
from pathlib import Path

FPS = 60


WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fighters")
# Inicialising window

PLAYER_WIDTH, PLAYER_HEIGHT = 55, 55
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
# Dimentions of objects

PLATFORM_COLOR = (60, 60, 60)
RED = (255, 0, 0)
BACKGROUND_COLOR = (62, 91, 140)


class Files:
    def __init__(self) -> None:
        root_dir = Path("Fighters").parent
        image_folder = root_dir / "images"
        audio_folder = root_dir / "audio"

        self.player1_image = pygame.transform.smoothscale(
            pygame.image.load(str(image_folder / "player1.png")),
            (PLAYER_WIDTH, PLAYER_HEIGHT),
        )  # Player 1
        self.player2_image = pygame.transform.smoothscale(
            pygame.image.load(str(image_folder / "player2.png")),
            (PLAYER_WIDTH, PLAYER_HEIGHT),
        )  # Player 2


class Player:
    def __init__(self, x, y, direction) -> None:
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.direction = direction
        # Basic stats

        self.speed = 10
        self.jump_velocity = 15
        self.fall_velocity = 10
        # Speeds

        self.can_move_left = True
        self.can_move_right = True
        self.can_move_down = True
        self.can_move_up = True
        self.can_jump = False
        # Cheking if player can do sth

        self.is_falling = True
        self.is_jumping = False
        # Player's state

        self.jump_height = 200

        self.health = 10

    def move(self, keys_pressed, up, left, right):

        if keys_pressed[up] and self.y > 0 and self.can_move_up and not self.is_jumping and self.can_jump:  # JUMP
            self.is_jumping = True
            self.jump_goal = self.y - self.jump_height
        if keys_pressed[left] and self.x > 0 and self.can_move_left:  # LEFT
            self.direction = "left"
            self.x -= self.speed
        if keys_pressed[right] and self.x + PLAYER_WIDTH < SCREEN_WIDTH and self.can_move_right:  # RIGHT
            self.direction = "right"
            self.x += self.speed
        # Keybinds

        if self.is_jumping:  # Jump logic
            if self.y > self.jump_goal and self.can_move_up:  # If player haven't reached the jump_height
                self.y -= self.jump_velocity
            else:  # After it has reached, it is no longer jumping and begins to fall
                self.is_jumping = False
                self.is_falling = True

        if not self.is_jumping and self.is_falling:  # Fall logic
            self.y += self.fall_velocity

        self.rect.x = self.x
        self.rect.y = self.y


class GameLogic:
    def __init__(self) -> None:
        self.lava = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)

        self.main_platform = pygame.Rect(
            (SCREEN_WIDTH - 1400) // 2, SCREEN_HEIGHT // 3 * 2, 1400, SCREEN_HEIGHT // 3)
        # Pozycja x, y, szerokość, długość
        self.side_platform1 = pygame.Rect(0, 600, 120, 100)
        self.side_platform2 = pygame.Rect(SCREEN_WIDTH - 120, 600, 120, 100)

        self.high_platform1 = pygame.Rect(
            SCREEN_WIDTH // 2 - 700, 450, 300, 100)
        self.high_platform2 = pygame.Rect(
            SCREEN_WIDTH // 2 + 400, 450, 300, 100)
        self.high_platform3 = pygame.Rect(
            SCREEN_WIDTH // 2 - 150, 450, 300, 100)

        self.platforms = [self.main_platform,
                          self.side_platform1, self.side_platform2, self.high_platform1, self.high_platform2, self.high_platform3]

    def update_window(self, files, player1, player2):
        WIN.fill(BACKGROUND_COLOR)
        pygame.draw.rect(WIN, RED, self.lava)
        for platform in self.platforms:
            pygame.draw.rect(WIN, PLATFORM_COLOR, platform)
        # Drawing background

        if player1.direction == "left":
            WIN.blit(files.player1_image, (player1.x, player1.y))
        else:
            WIN.blit(
                pygame.transform.flip(files.player1_image, True, False),
                (player1.x, player1.y),
            )
        if player2.direction == "left":
            WIN.blit(files.player2_image, (player2.x, player2.y))
        else:
            WIN.blit(
                pygame.transform.flip(files.player2_image, True, False),
                (player2.x, player2.y),
            )
        # Drawing players

        pygame.display.update()

    def check_for_player_collision(self, player1, player2):
        if player1.rect.colliderect(player2.rect):
            if player1.rect.centery == player2.rect.centery:
                if player1.rect.centerx < player2.rect.centerx:
                    # Player1|Player2
                    player1.can_move_right = False
                    player2.can_move_left = False
                else:
                    # Player2|Player1
                    player1.can_move_left = False
                    player2.can_move_right = False

                # Updating players position
            if player1.rect.centery < player2.rect.centery:  # Player1 over player2
                if player1.rect.centerx < player2.rect.centerx:
                    player1.x -= player1.speed  # Player1 gets pushed to the right
                else:
                    player1.x += player1.speed  # Player1 gets pushed to the left
            if player1.rect.centery > player2.rect.centery:  # Player2 over player1
                if player1.rect.centerx < player2.rect.centerx:
                    player2.x += player2.speed  # Player2 gets pushed to the left
                else:
                    player2.x -= player2.speed  # Player2 gets pushed to the right
        else:
            player1.can_move_right = True
            player1.can_move_left = True
            player2.can_move_right = True
            player2.can_move_left = True

    def check_for_platform_collision(self, player):
        player.is_falling = True
        player.can_jump = False

        for platform in self.platforms:
            if player.rect.colliderect(platform):
                # Checking if the player is on top of the platform
                if player.rect.bottom <= platform.top + 9:
                    player.is_falling = False
                    player.can_jump = True
                # Checking if the player is colliding with the right side of the platform
                if player.rect.right > platform.left and player.rect.left < platform.left:
                    player.can_move_right = False
                # Checking if the player is colliding with the left side of the platform
                if player.rect.left < platform.right and player.rect.right > platform.right:
                    player.can_move_left = False
                if player.rect.top > platform.bottom:
                    player.can_move_up = False

        # Checking if the player fell into lava
        if player.rect.colliderect(self.lava):
            player.y = 300
            player.x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2


def main():
    playing = True
    clock = pygame.time.Clock()

    files = Files()
    game_logic = GameLogic()

    player1 = Player(SCREEN_WIDTH//4 * 1, 600, "right")
    player2 = Player(SCREEN_WIDTH//4 * 3 - PLAYER_WIDTH, 600, "left")
    while playing:
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                playing = False

        player1.move(keys_pressed, pygame.K_w, pygame.K_a, pygame.K_d)
        player2.move(keys_pressed, pygame.K_UP, pygame.K_LEFT, pygame.K_RIGHT)

        game_logic.check_for_player_collision(player1, player2)

        game_logic.check_for_platform_collision(player1)
        game_logic.check_for_platform_collision(player2)

        game_logic.update_window(files, player1, player2)
    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
