from pathlib import Path
from random import choice
import sys
import pygame

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

PLAYER1_HIT = pygame.USEREVENT + 1
PLAYER2_HIT = pygame.USEREVENT + 2


class PushGun:
    def __init__(self, player) -> None:
        self.owner = player

        self.x = self.owner.x
        self.y = self.owner.y

        self.direction = str(self.owner.direction)

        self.cooldown = 300
        self.knockback = 100

        self.bullets_right = []
        self.bullets_left = []

        self.bullet_velocity = 15

    def shoot(self, owner):
        if owner.direction == 'right':
            self.bullets_right.append(
                pygame.Rect(owner.x + 40, self.y + 6, 5, 3))
        else:
            self.bullets_left.append(
                pygame.Rect(owner.x - 40, self.y + 6, 5, 3))

    def update_position(self, owner):
        self.x = owner.x + 25 if owner.direction == 'right' else owner.x - 25
        self.y = owner.y + 30
        self.direction = owner.direction


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
        self.pushgun_image = pygame.transform.scale_by(
            pygame.image.load(str(image_folder / 'pushgun.png')), 0.5)


class Player:
    def __init__(self, x, y, direction) -> None:
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.direction = direction
        self.current_gun = None
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
        self.is_on_platform = False
        # Player's state

        self.jump_height = 200

        self.health = 10

    def movement(self, keys_pressed, up, left, right):
        if keys_pressed[up] and not self.is_jumping and self.can_jump:  # JUMP
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
            if self.y > self.jump_goal:  # If player haven't reached the jump_height
                self.y -= self.jump_velocity
            else:  # After it has reached, it is no longer jumping and begins to fall
                self.is_jumping = False
                self.is_falling = True

        if self.is_falling:  # Fall logic
            self.y += self.fall_velocity

        self.rect.x = self.x
        self.rect.y = self.y

    def check_state(self):
        if self.is_on_platform:
            self.is_falling = False
            self.is_jumping = False
            self.can_jump = True
            self.can_move_left = True
            self.can_move_right = True
        else:
            self.is_falling = True
            self.can_jump = False

        if self.is_jumping:
            self.is_falling = False
            self.can_jump = False

    def get_a_gun(self, gun):
        self.current_gun = gun


class GameLogic:
    def __init__(self) -> None:
        self.lava = pygame.Rect(0, SCREEN_HEIGHT - 100, SCREEN_WIDTH, 100)

        self.main_platform = pygame.Rect(
            (SCREEN_WIDTH - 1400) // 2, SCREEN_HEIGHT // 3 * 2, 1400, SCREEN_HEIGHT // 3)
        # Pozycja x, y, szerokość, wysokość
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

    def update_window(self, files, player1, player2, guns):
        WIN.fill(BACKGROUND_COLOR)  # Drawing background
        pygame.draw.rect(WIN, RED, self.lava)
        for platform in self.platforms:
            pygame.draw.rect(WIN, PLATFORM_COLOR, platform)
        # Drawing platforms

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

        for bullet in player1.current_gun.bullets_right + player1.current_gun.bullets_left + player2.current_gun.bullets_right + player2.current_gun.bullets_left:
            pygame.draw.rect(WIN, (255, 255, 255), bullet)

        for gun in guns:
            if gun.direction == 'right':
                WIN.blit(files.pushgun_image, (gun.x, gun.y))
            else:
                WIN.blit(pygame.transform.flip(
                    files.pushgun_image, True, False), (gun.x, gun.y))

        pygame.display.update()

    def check_for_player_collision(self, player1, player2):
        if player1.rect.colliderect(player2.rect):
            if player1.rect.centery == player2.rect.centery:
                if player1.rect.centerx < player2.rect.centerx:
                    # Player1|Player2
                    player1.x -= player1.speed
                    player2.x += player2.speed
                else:
                    # Player2|Player1
                    player1.x += player1.speed
                    player2.x -= player2.speed

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

    def check_for_platform_collision(self, player):
        player.is_on_platform = False
        player.can_move_left = True
        player.can_move_right = True

        for platform in self.platforms:
            if player.rect.colliderect(platform):
                if player.rect.bottom <= platform.top + player.jump_velocity:
                    player.is_on_platform = True
                else:
                    player.is_on_platform = False

                if player.rect.centery >= platform.bottom:
                    player.is_falling = True
                    player.is_jumping = False

                if player.rect.left < platform.right:
                    player.can_move_left = False
                if player.rect.right > platform.left:
                    player.can_move_right = False

        # Checking if the player fell into lava
        if player.rect.colliderect(self.lava):
            player.y = 300
            player.x = (SCREEN_WIDTH - PLAYER_WIDTH) // 2 + 100

    def handle_bullets(self, player1, player2):
        for bullet in player1.current_gun.bullets_left + player2.current_gun.bullets_left:
            bullet.x -= player1.current_gun.bullet_velocity
        for bullet in player1.current_gun.bullets_right + player2.current_gun.bullets_right:
            bullet.x += player1.current_gun.bullet_velocity

        bullets = [player1.current_gun.bullets_left, player2.current_gun.bullets_left,
                   player1.current_gun.bullets_right, player2.current_gun.bullets_right]

        for list_of_bullets in bullets:
            for bullet in list_of_bullets:
                for platform in self.platforms:
                    if bullet.colliderect(platform):
                        list_of_bullets.remove(bullet)

                if bullet.colliderect(player1):
                    pygame.event.post(pygame.event.Event(PLAYER1_HIT))
                    list_of_bullets.remove(bullet)
                if bullet.colliderect(player2):
                    pygame.event.post(pygame.event.Event(PLAYER2_HIT))
                    list_of_bullets.remove(bullet)


def main():
    playing = True
    clock = pygame.time.Clock()

    files = Files()
    game_logic = GameLogic()

    player1 = Player(SCREEN_WIDTH//4 * 1, 600, "right")
    player2 = Player(SCREEN_WIDTH//4 * 3 - PLAYER_WIDTH, 600, "left")

    player1.get_a_gun(PushGun(player1))
    player2.get_a_gun(PushGun(player2))

    guns = []
    guns.append(player1.current_gun)
    guns.append(player2.current_gun)
    while playing:
        clock.tick(FPS)
        keys_pressed = pygame.key.get_pressed()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                playing = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    playing = False
                if event.key == pygame.K_SPACE:
                    player1.current_gun.shoot(player1)
                if event.key == pygame.K_RCTRL:
                    player2.current_gun.shoot(player2)

        game_logic.check_for_player_collision(player1, player2)

        game_logic.check_for_platform_collision(player1)
        game_logic.check_for_platform_collision(player2)

        player1.check_state()
        player2.check_state()

        player1.movement(keys_pressed, pygame.K_w, pygame.K_a, pygame.K_d)
        player2.movement(keys_pressed, pygame.K_UP,
                         pygame.K_LEFT, pygame.K_RIGHT)

        player1.current_gun.update_position(player1)
        player2.current_gun.update_position(player2)

        game_logic.handle_bullets(player1, player2)

        game_logic.update_window(
            files, player1, player2, guns)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
