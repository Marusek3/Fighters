import sys
import pygame
import os
from random import randint

pygame.init()
pygame.font.init()
pygame.mixer.init()

FPS = 60

WIN = pygame.display.set_mode((0, 0), pygame.FULLSCREEN)
pygame.display.set_caption("Fighters")
# Inicialising window

PLAYER_WIDTH, PLAYER_HEIGHT = 55, 55
SCREEN_WIDTH, SCREEN_HEIGHT = pygame.display.get_surface().get_size()
# Dimentions of objects

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
PINK = (225, 0, 225)

PLATFORM_COLOR = (60, 60, 60)
BACKGROUND_COLOR = (60, 90, 140)

HEALTH_FONT = pygame.font.SysFont('comicsans', 50)
DEATHSCREEN_FONT1 = pygame.font.SysFont('comicsans', 150)
DEATHSCREEN_FONT2 = pygame.font.SysFont('comicsans', 100)


class Files:
    def __init__(self) -> None:
        # Get the directory of the script
        script_dir = os.path.dirname(os.path.abspath(__file__))
        image_folder = os.path.join(script_dir, "images")
        audio_folder = os.path.join(script_dir, "audio")

        self.player1_image = pygame.transform.smoothscale(pygame.image.load(
            os.path.join(image_folder, "player1.png")), (PLAYER_WIDTH, PLAYER_HEIGHT))
        self.player2_image = pygame.transform.smoothscale(pygame.image.load(
            os.path.join(image_folder, "player2.png")), (PLAYER_WIDTH, PLAYER_HEIGHT))

        self.pushgun_image = pygame.transform.scale_by(pygame.image.load(
            os.path.join(image_folder, 'pushgun.png')), 0.5)
        self.pistol_image = pygame.transform.scale_by(pygame.image.load(
            os.path.join(image_folder, 'pistol.png')), 0.7)
        self.sniper_image = pygame.transform.scale_by(pygame.image.load(
            os.path.join(image_folder, 'sniper.png')), 0.6)

        self.sniper_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'sniper_shot.mp3'))
        self.pistol_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'pistol_shot.mp3'))
        self.pushgun_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'shotgun_shot.mp3'))
        self.dry_fire_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'dry_firing.mp3'))

        self.sniper_get_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'sniper_get.mp3'))
        self.pistol_get_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'pistol_get.mp3'))
        self.pushgun_get_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'shotgun_get.mp3'))

        self.background_music = pygame.mixer.Sound(
            os.path.join(audio_folder, 'background_music.mp3'))

        self.player_death_sound = pygame.mixer.Sound(
            os.path.join(audio_folder, 'player_death_sound.mp3'))


class Sniper:
    def __init__(self, player) -> None:
        self.x = player.x
        self.y = player.y

        self.direction = str(player.direction)

        self.cooldown = 120
        self.cooldown_wait = 0

        self.bullet_velocity = 30
        self.damage = 5

    def update(self, player):
        self.x = player.x + 35 if player.direction == 'right' else player.x - 70
        self.y = player.y + 20
        self.cooldown_wait += 1
        self.direction = player.direction

    def shoot(self, player, game_logic, files):
        if self.cooldown_wait >= self.cooldown:
            if player.direction == 'right':
                game_logic.sniper_bullets_right.append(
                    pygame.Rect(player.x + 50, self.y + 17, 7, 5))
            else:
                game_logic.sniper_bullets_left.append(
                    pygame.Rect(player.x - 40, self.y + 17, 7, 5))
            files.sniper_sound.play()
            self.cooldown_wait = 0
        else:
            files.dry_fire_sound.play()


class Pistol:
    def __init__(self, player) -> None:
        self.x = player.x
        self.y = player.y

        self.direction = str(player.direction)

        self.cooldown = 10
        self.cooldown_wait = 0

        self.bullet_velocity = 20
        self.damage = 1

    def update(self, player):
        self.x = player.x + 45 if player.direction == 'right' else player.x - 20
        self.y = player.y + 30
        self.cooldown_wait += 1
        self.direction = player.direction

    def shoot(self, player, game_logic, files):
        if self.cooldown_wait >= self.cooldown:
            if player.direction == 'right':
                game_logic.pistol_bullets_right.append(
                    pygame.Rect(player.x + 50, self.y + 6, 7, 5))
            else:
                game_logic.pistol_bullets_left.append(
                    pygame.Rect(player.x - 40, self.y + 6, 7, 5))
            files.pistol_sound.play()
            self.cooldown_wait = 0
        else:
            files.dry_fire_sound.play()


class PushGun:
    def __init__(self, player) -> None:
        self.x = player.x
        self.y = player.y

        self.direction = str(player.direction)

        self.cooldown = 30
        self.cooldown_wait = 0

        self.knockback = 300
        self.knockback_length = 0
        self.knockback_strength = 30

        self.bullets_right = []
        self.bullets_left = []

        self.bullet_velocity = 20

    def update(self, player):
        self.x = player.x + 25 if player.direction == 'right' else player.x - 25
        self.y = player.y + 30
        self.cooldown_wait += 1
        self.direction = player.direction

    def shoot(self, player, game_logic, files):
        if self.cooldown_wait >= self.cooldown:
            if player.direction == 'right':
                game_logic.pushgun_bullets_right.append(
                    pygame.Rect(player.x + 50, self.y + 6, 12, 8))
            else:
                game_logic.pushgun_bullets_left.append(
                    pygame.Rect(player.x - 40, self.y + 6, 15, 10))
            files.pushgun_sound.play()
            self.cooldown_wait = 0
        else:
            files.dry_fire_sound.play()


class Player:
    def __init__(self, x, y, direction, id) -> None:
        self.x = x
        self.y = y
        self.rect = pygame.Rect(self.x, self.y, PLAYER_WIDTH, PLAYER_HEIGHT)
        self.direction = direction
        self.current_gun = None
        self.id = id
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
        self.is_knocked_left = False
        self.is_knocked_right = False
        # Player's state

        self.jump_height = 200
        self.knock_goal = 0

        self.health = 10

    def movement(self, keys_pressed, up, left, right, pushgun):
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

        if self.is_knocked_left:
            if self.knock_goal < self.x:
                self.x -= pushgun.knockback_strength
            else:
                self.is_knocked_left = False

        if self.is_knocked_right:
            if self.knock_goal > self.x:
                self.x += pushgun.knockback_strength
            else:
                self.is_knocked_right = False

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

        if self.is_knocked_left:
            self.can_move_right = False

        if self.is_knocked_right:
            self.can_move_left = False

        if self.rect.left < 0:
            self.is_knocked_left = False
        if self.rect.right > SCREEN_WIDTH:
            self.is_knocked_right = False

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
            SCREEN_WIDTH // 2 - 700, 460, 300, 95)
        self.high_platform2 = pygame.Rect(
            SCREEN_WIDTH // 2 + 400, 460, 300, 95)
        self.high_platform3 = pygame.Rect(
            SCREEN_WIDTH // 2 - 150, 460, 300, 95)

        self.platforms = [self.main_platform,
                          self.side_platform1, self.side_platform2, self.high_platform1, self.high_platform2, self.high_platform3]
        # Platforms

        self.pushgun_bullets_left = []
        self.pushgun_bullets_right = []

        self.pistol_bullets_left = []
        self.pistol_bullets_right = []

        self.sniper_bullets_left = []
        self.sniper_bullets_right = []

    def update_window(self, files, player1, player2, game_logic):
        WIN.fill(BACKGROUND_COLOR)  # Drawing background
        pygame.draw.rect(WIN, RED, self.lava)
        for platform in self.platforms:
            pygame.draw.rect(WIN, PLATFORM_COLOR, platform)
        # Drawing platforms

        player1_health = HEALTH_FONT.render(
            f'PLAYER RED HEALTH: {player1.health}', 1, RED)
        player2_health = HEALTH_FONT.render(
            f'PLAYER GREEN HEALTH: {player2.health}', 1, GREEN)
        WIN.blit(player1_health, (5, 0))
        WIN.blit(player2_health, (SCREEN_WIDTH -
                 player2_health.get_width() - 5, 0))

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

        for bullet in game_logic.pushgun_bullets_left + game_logic.pushgun_bullets_right:
            pygame.draw.rect(WIN, YELLOW, bullet)

        for bullet in game_logic.pistol_bullets_left + game_logic.pistol_bullets_right:
            pygame.draw.rect(WIN, WHITE, bullet)

        for bullet in game_logic.sniper_bullets_left + game_logic.sniper_bullets_right:
            pygame.draw.rect(WIN, GREEN, bullet)

        for player in [player1, player2]:
            if isinstance(player.current_gun, PushGun):
                gun_image = files.pushgun_image
            elif isinstance(player.current_gun, Pistol):
                gun_image = files.pistol_image
            elif isinstance(player.current_gun, Sniper):
                gun_image = files.sniper_image

            if player.current_gun.direction == 'right':
                WIN.blit(gun_image, (player.current_gun.x, player.current_gun.y))
            else:
                WIN.blit(pygame.transform.flip(gun_image, True, False),
                         (player.current_gun.x, player.current_gun.y))

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

    def check_for_platform_collision(self, player, files):
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
            if player.health > 5:
                files.player_death_sound.play()
            player.health -= 5
            player.y = 0
            player.x = randint(0, SCREEN_WIDTH - PLAYER_WIDTH)

    def bullets_move(self, pushgun, pistol, sniper):
        for bullet in self.pushgun_bullets_left:
            bullet.x -= pushgun.bullet_velocity
        for bullet in self.pushgun_bullets_right:
            bullet.x += pushgun.bullet_velocity

        for bullet in self.pistol_bullets_left:
            bullet.x -= pistol.bullet_velocity
        for bullet in self.pistol_bullets_right:
            bullet.x += pistol.bullet_velocity

        for bullet in self.sniper_bullets_left:
            bullet.x -= sniper.bullet_velocity
        for bullet in self.sniper_bullets_right:
            bullet.x += sniper.bullet_velocity

    def pushgun_hit(self, player1, player2, pushgun):
        for player in [player1, player2]:
            for bullet in self.pushgun_bullets_right + self.pushgun_bullets_left:
                for platform in self.platforms:
                    if bullet.colliderect(platform):
                        if bullet in self.pushgun_bullets_right:
                            self.pushgun_bullets_right.remove(bullet)
                        else:
                            self.pushgun_bullets_left.remove(bullet)
                if bullet.colliderect(player):
                    if bullet in self.pushgun_bullets_right:
                        player.knock_goal = player.x + pushgun.knockback
                        player.is_knocked_right = True
                        self.pushgun_bullets_right.remove(bullet)
                    else:
                        player.knock_goal = player.x - pushgun.knockback
                        player.is_knocked_left = True
                        self.pushgun_bullets_left.remove(bullet)

    def pistol_hit(self, player1, player2, pistol):
        for player in [player1, player2]:
            for list_of_bullets in [self.pistol_bullets_right, self.pistol_bullets_left]:
                for bullet in list_of_bullets:
                    for platform in self.platforms:
                        if bullet.colliderect(platform):
                            list_of_bullets.remove(bullet)
                    if bullet.colliderect(player):
                        player.health -= pistol.damage
                        list_of_bullets.remove(bullet)

    def sniper_hit(self, player1, player2, sniper):
        for player in [player1, player2]:
            for list_of_bullets in [self.sniper_bullets_right, self.sniper_bullets_left]:
                for bullet in list_of_bullets:
                    for platform in self.platforms:
                        if bullet.colliderect(platform):
                            list_of_bullets.remove(bullet)
                    if bullet.colliderect(player):
                        player.health -= sniper.damage
                        list_of_bullets.remove(bullet)

    def death_screen(self, files, player):
        files.background_music.stop()
        files.player_death_sound.play()
        if player.id == 'red':
            text = 'PLAYER RED WON!'
            color = RED
        if player.id == 'green':
            text = 'PLAYER GREEN WON!'
            color = GREEN
        WIN.fill(BLACK)

        main_text = DEATHSCREEN_FONT1.render(text, 1, color)
        line2 = DEATHSCREEN_FONT2.render('Press \'R\' to play again', 1, WHITE)
        line3 = DEATHSCREEN_FONT2.render('Press \'Esc\' to leave', 1, WHITE)

        WIN.blit(main_text, ((SCREEN_WIDTH - main_text.get_width()) //
                 2, (SCREEN_HEIGHT-main_text.get_height())//7))
        WIN.blit(line2, ((SCREEN_WIDTH - line2.get_width()) //
                 2, (SCREEN_HEIGHT-line2.get_height())//7*4))
        WIN.blit(line3, ((SCREEN_WIDTH - line3.get_width()) //
                 2, (SCREEN_HEIGHT-line3.get_height())//7*6))
        pygame.display.update()
        while True:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_r:
                        main()
                    if event.key == pygame.K_ESCAPE:
                        pygame.quit()
                        sys.exit()


def main():
    playing = True
    clock = pygame.time.Clock()

    files = Files()
    game_logic = GameLogic()

    player1 = Player(
        randint(0, SCREEN_WIDTH-PLAYER_WIDTH),
        -200, "right", 'red')
    player2 = Player(randint(0, SCREEN_WIDTH-PLAYER_WIDTH),
                     -200, "left", 'green')

    player1.get_a_gun(PushGun(player1))
    player2.get_a_gun(PushGun(player2))

    Tplayer = Player(SCREEN_WIDTH//4 * 3 - PLAYER_WIDTH, 600, "left", 'T')
    Tpushgun = PushGun(Tplayer)
    Tpistol = Pistol(Tplayer)
    Tsniper = Sniper(Tplayer)

    files.background_music.play(-1)
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
                    player1.current_gun.shoot(player1, game_logic, files)
                if event.key == pygame.K_RCTRL:
                    player2.current_gun.shoot(player2, game_logic, files)

                if event.key == pygame.K_1:
                    player1.get_a_gun(PushGun(player1))
                    files.pushgun_get_sound.play()
                if event.key == pygame.K_2:
                    player1.get_a_gun(Pistol(player1))
                    files.pistol_get_sound.play()
                if event.key == pygame.K_3:
                    player1.get_a_gun(Sniper(player1))
                    files.sniper_get_sound.play()
                # Player 1 changing guns

                if event.key == pygame.K_DELETE:
                    player2.get_a_gun(Pistol(player2))
                    files.pistol_get_sound.play()
                if event.key == pygame.K_RSHIFT:
                    player2.get_a_gun(PushGun(player2))
                    files.pushgun_get_sound.play()
                if event.key == pygame.K_PAGEDOWN:
                    player2.get_a_gun(Sniper(player2))
                    files.sniper_get_sound.play()
                # Player 2 changing guns

        game_logic.check_for_player_collision(player1, player2)

        game_logic.check_for_platform_collision(player1, files)
        game_logic.check_for_platform_collision(player2, files)

        player1.check_state()
        player2.check_state()

        player1.movement(keys_pressed, pygame.K_w,
                         pygame.K_a, pygame.K_d, Tpushgun)
        player2.movement(keys_pressed, pygame.K_UP,
                         pygame.K_LEFT, pygame.K_RIGHT, Tpushgun)

        player1.current_gun.update(player1)
        player2.current_gun.update(player2)

        game_logic.bullets_move(Tpushgun, Tpistol, Tsniper)

        game_logic.pushgun_hit(player1, player2, Tpushgun)
        game_logic.pistol_hit(player1, player2, Tpistol)
        game_logic.sniper_hit(player1, player2, Tsniper)

        game_logic.update_window(files, player1, player2, game_logic)

        if player1.health <= 0:
            game_logic.death_screen(files, player2)
        if player2.health <= 0:
            game_logic.death_screen(files, player1)

    pygame.quit()
    sys.exit()


if __name__ == "__main__":
    main()
    print('To się nigdy nie wyświetli.')
