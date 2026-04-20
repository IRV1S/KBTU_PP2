import pygame
import random
import sys

# ====================== ИНИЦИАЛИЗАЦИЯ PYGAME ======================
pygame.init()

# ====================== НАСТРОЙКИ ИГРЫ ======================
WIDTH, HEIGHT = 400, 700  # Размер игрового окна
ROAD_WIDTH = 340  # Ширина дороги (сделана шире для удобства)

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer - Practice 11")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont("arial", 28)
font_big = pygame.font.SysFont("arial", 50, bold=True)

# ====================== ЦВЕТА ======================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
GOLD = (255, 215, 0)
PURPLE = (180, 0, 255)


# ====================== КЛАСС ИГРОКА ======================
class Player(pygame.sprite.Sprite):
    """Класс игрока — синяя машина, которой управляет пользователь"""

    def __init__(self):
        super().__init__()
        # Создаём поверхность для машины
        self.image = pygame.Surface((50, 90))
        self.image.fill((0, 100, 255))  # Основной цвет машины

        # Рисуем "окна" и детали машины
        pygame.draw.rect(self.image, WHITE, (8, 15, 34, 25))  # Переднее стекло
        pygame.draw.rect(self.image, WHITE, (8, 55, 34, 20))  # Заднее стекло

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2  # Начальная позиция по центру
        self.rect.bottom = HEIGHT - 40  # Немного отступаем от низа
        self.speed = 6  # Скорость движения

    def update(self):
        """Обработка нажатий клавиш и ограничение движения по дороге"""
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.rect.x += self.speed

        # Ограничение движения — игрок не может выехать за пределы дороги
        left_border = (WIDTH - ROAD_WIDTH) // 2 + 10
        right_border = (WIDTH + ROAD_WIDTH) // 2 - 60
        if self.rect.left < left_border:
            self.rect.left = left_border
        if self.rect.right > right_border:
            self.rect.right = right_border


# ====================== КЛАСС ВРАГОВ (красные машины) ======================
class Enemy(pygame.sprite.Sprite):
    """Класс вражеских машин"""

    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((50, 90))
        self.image.fill((255, 40, 40))  # Красный цвет врага

        # Детали машины
        pygame.draw.rect(self.image, WHITE, (8, 15, 34, 25))

        self.rect = self.image.get_rect()
        # Случайная позиция по горизонтали на дороге
        self.rect.x = random.randint((WIDTH - ROAD_WIDTH) // 2 + 15,
                                     (WIDTH + ROAD_WIDTH) // 2 - 65)
        self.rect.y = random.randint(-200, -50)  # Появляется сверху за экраном
        self.speed = speed  # Скорость зависит от счёта

    def update(self):
        """Движение вниз и удаление при выходе за экран"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()  # Удаляем объект


# ====================== КЛАСС МОНЕТ ======================
class Coin(pygame.sprite.Sprite):
    """Класс собираемых монет (обычные и редкие)"""

    def __init__(self, value=10):
        super().__init__()
        self.value = value  # Ценность монеты
        self.image = pygame.Surface((30, 30), pygame.SRCALPHA)

        # Разные виды монет
        if value == 50:  # Редкая золотая с фиолетовым
            pygame.draw.circle(self.image, PURPLE, (15, 15), 15)
            pygame.draw.circle(self.image, WHITE, (15, 15), 10)
            pygame.draw.circle(self.image, PURPLE, (15, 15), 6)
        else:  # Обычная золотая
            pygame.draw.circle(self.image, GOLD, (15, 15), 15)
            pygame.draw.circle(self.image, WHITE, (15, 15), 10)

        self.rect = self.image.get_rect()
        self.rect.x = random.randint((WIDTH - ROAD_WIDTH) // 2 + 25,
                                     (WIDTH + ROAD_WIDTH) // 2 - 55)
        self.rect.y = random.randint(-300, -100)
        self.speed = 6

    def update(self):
        """Движение вниз и удаление при выходе за экран"""
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# ====================== ОСНОВНАЯ ФУНКЦИЯ ИГРЫ ======================
def main():
    # ====================== СОЗДАНИЕ ОБЪЕКТОВ ======================
    player = Player()
    all_sprites = pygame.sprite.Group(player)  # Все спрайты для отрисовки
    enemies = pygame.sprite.Group()  # Группа только врагов
    coins = pygame.sprite.Group()  # Группа только монет

    # Игровые переменные
    score = 0
    game_over = False
    enemy_timer = 0
    coin_timer = 0
    base_enemy_speed = 6

    while True:
        clock.tick(60)  # Ограничение FPS

        # ====================== ОБРАБОТКА СОБЫТИЙ ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Рестарт игры после поражения
            if game_over and event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                return main()  # Перезапуск игры

        if not game_over:
            # Обновление всех объектов
            all_sprites.update()
            enemies.update()
            coins.update()

            # ====================== СПАВН ВРАГОВ ======================
            enemy_timer += 1
            if enemy_timer > 38:  # Примерно каждые 38 кадров
                # Сложность растёт со временем
                speed = base_enemy_speed + (score // 90)
                enemy = Enemy(speed)
                enemies.add(enemy)
                all_sprites.add(enemy)
                enemy_timer = 0

            # ====================== СПАВН МОНЕТ ======================
            coin_timer += 1
            if coin_timer > 50:
                # 18% шанс выпадения редкой монеты (50 очков)
                value = 50 if random.random() < 0.18 else 10
                coin = Coin(value)
                coins.add(coin)
                all_sprites.add(coin)
                coin_timer = 0

            # ====================== СТОЛКНОВЕНИЯ ======================
            # Сбор монет
            collected = pygame.sprite.spritecollide(player, coins, True)
            for c in collected:
                score += c.value

            # Столкновение с врагами → конец игры
            if pygame.sprite.spritecollide(player, enemies, False):
                game_over = True

        # ====================== ОТРИСОВКА ======================
        screen.fill(GRAY)  # Фон

        # Рисуем дорогу
        road_left = (WIDTH - ROAD_WIDTH) // 2
        pygame.draw.rect(screen, BLACK, (road_left, 0, ROAD_WIDTH, HEIGHT))

        # Анимированная разметка дороги (движение вниз)
        for i in range(-3, 14):
            y = (i * 80 + pygame.time.get_ticks() // 7) % (HEIGHT + 100) - 50
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 5, y, 10, 45))

        # Отрисовка всех спрайтов
        all_sprites.draw(screen)

        # Отображение счёта
        score_text = font.render(f"Счёт: {score}", True, WHITE)
        screen.blit(score_text, (10, 10))

        # ====================== ЭКРАН GAME OVER ======================
        if game_over:
            # Полупрозрачный затемняющий слой
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(190)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            # Текст Game Over
            txt = font_big.render("GAME OVER", True, (255, 0, 0))
            screen.blit(txt, txt.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 60)))

            final = font.render(f"Счёт: {score}", True, WHITE)
            screen.blit(final, final.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 10)))

            restart = font.render("Нажми R для рестарта", True, WHITE)
            screen.blit(restart, restart.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 70)))

        pygame.display.flip()


# ====================== ЗАПУСК ИГРЫ ======================
if __name__ == "__main__":
    main()