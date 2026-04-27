# game.py
import pygame
import random
import time
from settings import load_settings
from db import get_personal_best

# ====================== КОНСТАНТЫ ======================
WIDTH = HEIGHT = 620
GRID_SIZE = 20
GRID_W = WIDTH // GRID_SIZE
GRID_H = HEIGHT // GRID_SIZE

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
POISON_COLOR = (139, 0, 0)  # Тёмно-красный
GRAY = (40, 40, 40)
ACCENT = (0, 255, 100)


class SnakeGame:
    def __init__(self, screen, settings, username):
        self.screen = screen
        self.settings = settings
        self.username = username

        self.snake_color = tuple(settings.get("snake_color", [0, 200, 0]))
        self.show_grid = settings.get("grid_overlay", True)

        self.reset_game()

    def reset_game(self):
        """Сброс игры в начальное состояние"""
        self.snake = [(10, 10), (9, 10), (8, 10)]
        self.direction = (1, 0)
        self.score = 0
        self.level = 1
        self.speed = 8  # базовая скорость

        self.food = None
        self.is_special = False
        self.is_poison = False
        self.food_timer = pygame.time.get_ticks()

        self.powerup = None
        self.powerup_timer = 0
        self.active_powerup = None
        self.active_powerup_end = 0
        self.shield_active = False

        self.obstacles = []  # ← Сначала создаём obstacles!
        self.personal_best = get_personal_best(self.username)

        self.game_over = False
        self.last_move_time = pygame.time.get_ticks()

        # Теперь безопасно генерируем еду
        self.food = self.generate_food()
        self.generate_obstacles()  # генерируем препятствия для текущего уровня

    def generate_food(self, avoid_obstacles=True):
        """Генерация еды (обычная / специальная / ядовитая)"""
        while True:
            pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))

            if pos in self.snake:
                continue
            if avoid_obstacles and pos in self.obstacles:
                continue

            return pos

    def generate_powerup(self):
        """Спавн power-up"""
        if self.powerup is not None:
            return

        types = ["speed", "slow", "shield"]
        ptype = random.choice(types)

        while True:
            pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
            if pos not in self.snake and pos not in self.obstacles:
                self.powerup = {"type": ptype, "pos": pos, "spawn_time": pygame.time.get_ticks()}
                break

    def generate_obstacles(self):
        """Генерация препятствий (с Level 3)"""
        self.obstacles = []
        if self.level < 3:
            return

        num_obstacles = 4 + (self.level - 3) * 2  # увеличиваем с уровнем

        for _ in range(num_obstacles):
            while True:
                pos = (random.randint(2, GRID_W - 3), random.randint(2, GRID_H - 3))
                if (pos not in self.snake and
                        pos not in self.obstacles and
                        abs(pos[0] - self.snake[0][0]) > 3 and
                        abs(pos[1] - self.snake[0][1]) > 3):
                    self.obstacles.append(pos)
                    break

    def move(self):
        """Основное движение змейки"""
        head = (self.snake[0][0] + self.direction[0],
                self.snake[0][1] + self.direction[1])

        # Проверка столкновений
        if self.check_collision(head):
            if self.shield_active:
                self.shield_active = False
                self.active_powerup = None
                # продолжаем движение, но щит потрачен
            else:
                self.game_over = True
                return

        self.snake.insert(0, head)

        ate = False

        # Съели еду
        if head == self.food:
            ate = True
            if self.is_poison:
                # Ядовитая еда
                if len(self.snake) > 3:
                    self.snake.pop()
                    self.snake.pop()  # укорачиваем на 2
                else:
                    self.game_over = True
                    return
                points = 0
            else:
                points = 30 if self.is_special else 10
                self.score += points

                # Уровень вверх
                if self.score // 60 + 1 > self.level:
                    self.level += 1
                    self.generate_obstacles()

            # Новая еда
            self.is_special = random.random() < 0.22
            self.is_poison = random.random() < 0.15 and not self.is_special
            self.food = self.generate_food()
            self.food_timer = pygame.time.get_ticks()

        # Power-up
        if self.powerup and head == self.powerup["pos"]:
            self.activate_powerup(self.powerup["type"])
            self.powerup = None

        # Удаляем хвост, если ничего не съели
        if not ate:
            self.snake.pop()

    def check_collision(self, head):
        """Проверка всех видов столкновений"""
        # Стены
        if (head[0] < 0 or head[0] >= GRID_W or
                head[1] < 0 or head[1] >= GRID_H):
            return True

        # Сама в себя
        if head in self.snake[1:]:
            return True

        # Препятствия
        if head in self.obstacles:
            return True

        return False

    def activate_powerup(self, ptype):
        """Активация power-up"""
        current_time = pygame.time.get_ticks()

        if ptype == "speed":
            self.active_powerup = "speed"
            self.active_powerup_end = current_time + 5000
            self.speed = 12
        elif ptype == "slow":
            self.active_powerup = "slow"
            self.active_powerup_end = current_time + 5000
            self.speed = 4
        elif ptype == "shield":
            self.shield_active = True
            self.active_powerup = "shield"
            self.active_powerup_end = current_time + 8000  # щит живёт дольше

    def update_powerups(self):
        """Обновление таймеров power-up'ов"""
        current = pygame.time.get_ticks()

        # Активный эффект
        if self.active_powerup and current > self.active_powerup_end:
            if self.active_powerup in ["speed", "slow"]:
                self.speed = 7 + self.level * 3
            self.active_powerup = None

        # Power-up на поле исчезает через 8 секунд
        if self.powerup and current - self.powerup["spawn_time"] > 8000:
            self.powerup = None

    def draw(self):
        """Отрисовка всего"""
        self.screen.fill(BLACK)

        # Сетка
        if self.show_grid:
            for x in range(0, WIDTH, GRID_SIZE):
                pygame.draw.line(self.screen, GRAY, (x, 0), (x, HEIGHT))
            for y in range(0, HEIGHT, GRID_SIZE):
                pygame.draw.line(self.screen, GRAY, (0, y), (WIDTH, y))

        # Змейка
        for i, segment in enumerate(self.snake):
            color = (0, 255, 120) if i == 0 else self.snake_color
            rect = pygame.Rect(segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            pygame.draw.rect(self.screen, WHITE, rect, 1)

        # Еда
        food_color = POISON_COLOR if self.is_poison else (GOLD if self.is_special else RED)
        food_rect = pygame.Rect(self.food[0] * GRID_SIZE, self.food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(self.screen, food_color, food_rect)

        # Power-up
        if self.powerup:
            ptype = self.powerup["type"]
            colors = {"speed": (255, 100, 0), "slow": (100, 100, 255), "shield": (0, 255, 255)}
            color = colors[ptype]
            pos = self.powerup["pos"]
            rect = pygame.Rect(pos[0] * GRID_SIZE, pos[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, color, rect)
            # Символ
            font = pygame.font.SysFont("arial", 14, bold=True)
            text = font.render(ptype[0].upper(), True, BLACK)
            self.screen.blit(text, (rect.centerx - 6, rect.centery - 8))

        # Препятствия
        for obs in self.obstacles:
            rect = pygame.Rect(obs[0] * GRID_SIZE, obs[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(self.screen, (180, 180, 180), rect)

        # HUD
        font = pygame.font.SysFont("arial", 24)
        small_font = pygame.font.SysFont("arial", 18)

        texts = [
            f"Счёт: {self.score}",
            f"Уровень: {self.level}",
            f"Игрок: {self.username}"
        ]

        for i, txt in enumerate(texts):
            surf = font.render(txt, True, WHITE)
            self.screen.blit(surf, (15, 10 + i * 30))

        # Personal Best
        if self.personal_best:
            pb_text = small_font.render(f"Лучший: {self.personal_best[0]}", True, ACCENT)
            self.screen.blit(pb_text, (15, 100))

        # Активный power-up
        if self.active_powerup:
            rem = max(0, (self.active_powerup_end - pygame.time.get_ticks()) // 1000)
            names = {"speed": "УСКОРЕНИЕ", "slow": "ЗАМЕДЛЕНИЕ", "shield": "ЩИТ"}
            col = (255, 140, 0) if self.active_powerup == "speed" else (100, 100,
                                                                        255) if self.active_powerup == "slow" else (0,
                                                                                                                    255,
                                                                                                                    255)
            pu_surf = font.render(f"{names[self.active_powerup]} {rem}s", True, col)
            self.screen.blit(pu_surf, (WIDTH - pu_surf.get_width() - 15, 15))

    def run(self):
        """Основной игровой цикл"""

        while not self.game_over:
            current_time = pygame.time.get_ticks()

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    import sys
                    sys.exit()

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_UP and self.direction != (0, 1):
                        self.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and self.direction != (0, -1):
                        self.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and self.direction != (1, 0):
                        self.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and self.direction != (-1, 0):
                        self.direction = (1, 0)
                    elif event.key == pygame.K_ESCAPE:
                        return self.score, self.level

            # Управление скоростью движения
            if current_time - self.last_move_time > (1000 // self.speed):
                self.move()
                self.last_move_time = current_time

                # Спавн power-up'а
                if random.random() < 0.015 and not self.powerup:
                    self.generate_powerup()

                self.update_powerups()

            self.draw()
            pygame.display.flip()

            # Исчезновение еды
            if pygame.time.get_ticks() - self.food_timer > (4500 if self.is_special or self.is_poison else 9000):
                self.is_special = random.random() < 0.22
                self.is_poison = random.random() < 0.15 and not self.is_special
                self.food = self.generate_food()
                self.food_timer = pygame.time.get_ticks()

        return self.score, self.level


def run_game(screen, clock, settings, username):
    """Запуск игры"""
    game = SnakeGame(screen, settings, username)
    return game.run()