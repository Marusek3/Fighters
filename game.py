import pygame
from pathlib import Path

FPS = 60

PLAYER_WIDTH, PLAYER_HEIGTH = 55, 55
SCREEN_WIDTH, SCREEN_HEIGTH = 1000, 700
# Dimentions of objects

WIN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGTH))
pygame.display.set_caption("Fighters")
# Inicialising window


class Files:
    def __init__(self) -> None:
        root_dir = Path("Fighters").parent
        image_folder = root_dir / "images"
        audio_folder = root_dir / "audio"

        self.background_image = pygame.transform.smoothscale(
            pygame.image.load(str(image_folder / "background.jpg")),
            (SCREEN_WIDTH, SCREEN_HEIGTH),
        )
        self.player1_image = pygame.transform.smoothscale(
            pygame.image.load(str(image_folder / "player1.png")),
            (PLAYER_WIDTH, PLAYER_HEIGTH),
        )
        self.player2_image = pygame.transform.smoothscale(
            pygame.image.load(str(image_folder / "player2.png")),
            (PLAYER_WIDTH, PLAYER_HEIGTH),
        )


class Player:
    def __init__(self, x, y, direction) -> None:
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGTH)

        self.speed = 10
        self.direction = direction
        self.can_move = True
        self.can_move_left = True
        self.can_move_right = True

        self.health = 10

    def move(self, keys_pressed, up, down, left, right):
        if self.can_move:
            if keys_pressed[up] and self.y > 0:  # UP
                self.y -= self.speed
            if keys_pressed[down] and self.y + PLAYER_HEIGTH < SCREEN_HEIGTH:  # DOWN
                self.y += self.speed
            if keys_pressed[left] and self.x > 0 and self.can_move_left:  # LEFT
                self.direction = "left"
                self.x -= self.speed
            if (
                keys_pressed[right]
                and self.x + PLAYER_WIDTH < SCREEN_WIDTH
                and self.can_move_right
            ):  # RIGHT
                self.direction = "right"
                self.x += self.speed
            self.rect.x = self.x
            self.rect.y = self.y


class GameLogic:
    def __init__(self) -> None:
        pass

    def update_window(self, files, player1, player2):
        WIN.blit(files.background_image, (0, 0))

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

        pygame.display.update()

    def check_for_player_collision(self, player1, player2):
        if player1.rect.colliderect(player2.rect):
            if (
                player1.rect.centerx < player2.rect.centerx
            ):  # Player1 collides from the left
                player1.can_move_right = False
                player2.can_move_left = False
            else:
                # Player 1 collides from the right, push right
                player1.can_move_left = False
                player2.can_move_right = False

            player1.rect.x = player1.x
            player1.rect.y = player1.y
            player2.rect.x = player2.x
            player2.rect.y = player2.y
        else:
            player1.can_move_right = True
            player1.can_move_left = True
            player2.can_move_right = True
            player2.can_move_left = True


def main():
    playing = True
    clock = pygame.time.Clock()

    files = Files()
    game_logic = GameLogic()

    player1 = Player(100, 100, "right")
    player2 = Player(400, 100, "right")
    while playing:
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False

        player1.move(keys_pressed, pygame.K_w, pygame.K_s, pygame.K_a, pygame.K_d)
        player2.move(
            keys_pressed, pygame.K_UP, pygame.K_DOWN, pygame.K_LEFT, pygame.K_RIGHT
        )
        game_logic.update_window(files, player1, player2)
        game_logic.check_for_player_collision(player1, player2)


if __name__ == "__main__":
    main()
