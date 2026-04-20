import pygame
import random
import sys

# ====================== ИНИЦИАЛИЗАЦИЯ ======================
pygame.init()

# ====================== КОНСТАНТЫ ======================
WIDTH, HEIGHT = 400, 600
ROAD_WIDTH = 280
LANE_WIDTH = ROAD_WIDTH // 4

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
YELLOW = (255, 220, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)

# Настройки окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - Practice 10")
clock = pygame.time.Clock()
font = pygame.font.SysFont("arial", 30)
font_big = pygame.font.SysFont("arial", 50, bold=True)


# ====================== КЛАССЫ ======================
class Player(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 80))
        self.image.fill((0, 120, 255))  # синяя машинка
        pygame.draw.rect(self.image, WHITE, (10, 10, 30, 20))  # окна
        pygame.draw.rect(self.image, WHITE, (10, 50, 30, 20))
        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom = HEIGHT - 30
        self.speed = 5

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Ограничение по бокам дороги
        if self.rect.left < (WIDTH - ROAD_WIDTH) // 2:
            self.rect.left = (WIDTH - ROAD_WIDTH) // 2
        if self.rect.right > (WIDTH + ROAD_WIDTH) // 2:
            self.rect.right = (WIDTH + ROAD_WIDTH) // 2


class Enemy(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((50, 80))
        self.image.fill((255, 50, 50))  # красная машинка
        pygame.draw.rect(self.image, WHITE, (10, 10, 30, 20))
        pygame.draw.rect(self.image, WHITE, (10, 50, 30, 20))
        self.rect = self.image.get_rect()
        self.rect.x = random.randint((WIDTH - ROAD_WIDTH) // 2 + 10,
                                     (WIDTH + ROAD_WIDTH) // 2 - 60)
        self.rect.y = random.randint(-150, -50)
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.Surface((25, 25), pygame.SRCALPHA)
        pygame.draw.circle(self.image, YELLOW, (12, 12), 12)
        pygame.draw.circle(self.image, WHITE, (12, 12), 8)
        self.rect = self.image.get_rect()
        self.rect.x = random.randint((WIDTH - ROAD_WIDTH) // 2 + 20,
                                     (WIDTH + ROAD_WIDTH) // 2 - 45)
        self.rect.y = random.randint(-200, -50)
        self.speed = 6

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# ====================== ОСНОВНАЯ ФУНКЦИЯ ======================
def main():
    player = Player()
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()

    score = 0
    game_over = False
    speed_increase = 0

    # Таймеры спавна
    enemy_timer = 0
    coin_timer = 0

    while True:
        clock.tick(60)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                # Рестарт игры
                return main()  # перезапускаем игру

        if not game_over:
            # Обновление
            all_sprites.update()
            enemies.update()
            coins.update()

            # Спавн врагов
            enemy_timer += 1
            if enemy_timer > 45 - speed_increase:  # ускоряем спавн со временем
                enemy = Enemy()
                enemies.add(enemy)
                all_sprites.add(enemy)
                enemy_timer = 0

            # Спавн монеток
            coin_timer += 1
            if coin_timer > 70:
                if random.random() < 0.7:  # шанс появления монетки
                    coin = Coin()
                    coins.add(coin)
                    all_sprites.add(coin)
                coin_timer = 0

            # Сбор монеток
            collected = pygame.sprite.spritecollide(player, coins, True)
            for c in collected:
                score += 10

            # Столкновение с врагами
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True

            # Увеличение сложности
            if score > 0 and score % 100 == 0 and speed_increase < 12:
                speed_increase += 1

        # ====================== ОТРИСОВКА ======================
        screen.fill(GRAY)  # фон

        # Рисуем дорогу
        road_left = (WIDTH - ROAD_WIDTH) // 2
        pygame.draw.rect(screen, BLACK, (road_left, 0, ROAD_WIDTH, HEIGHT))

        # Разметка дороги (движущиеся линии)
        for i in range(-2, 12):
            y = (i * 60 + pygame.time.get_ticks() // 8) % (HEIGHT + 100) - 50
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, y, 10, 40))

        # Отрисовка всех спрайтов
        all_sprites.draw(screen)

        # HUD
        score_text = font.render(f"Монеты: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        high_speed = font.render(f"Скорость: {5 + speed_increase}", True, WHITE)
        screen.blit(high_speed, (10, 45))

        # Game Over экран
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            go_text = font_big.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(go_text, go_rect)

            final = font.render(f"Собрано монет: {score}", True, WHITE)
            final_rect = final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(final, final_rect)

            restart = font.render("Нажми R для рестарта", True, WHITE)
            restart_rect = restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70))
            screen.blit(restart, restart_rect)

        pygame.display.flip()


if __name__ == "__main__":
    main()