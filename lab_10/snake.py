import pygame
import random
import sys

# ====================== ИНИЦИАЛИЗАЦИЯ ======================
pygame.init()

# ====================== КОНСТАНТЫ ======================
WIDTH, HEIGHT = 600, 600
GRID_SIZE = 20
GRID_WIDTH = WIDTH // GRID_SIZE
GRID_HEIGHT = HEIGHT // GRID_SIZE

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
GRAY = (40, 40, 40)
DARK_GREEN = (0, 180, 0)

# Настройки окна
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake Game - Practice 10")
clock = pygame.time.Clock()
font_big = pygame.font.SysFont("arial", 60, bold=True)
font_medium = pygame.font.SysFont("arial", 35)
font_small = pygame.font.SysFont("arial", 25)

# Направления
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)


# ====================== КЛАСС ЗМЕЙКИ ======================
class Snake:
    def __init__(self):
        self.reset()

    def reset(self):
        """Сброс змейки в начальное состояние"""
        self.body = [(10, 10), (9, 10), (8, 10)]  # стартовая длина = 3
        self.direction = RIGHT
        self.score = 0
        self.level = 1
        self.food_eaten = 0

    def move(self):
        """Перемещение змейки (добавляем новую голову)"""
        head = self.body[0]
        new_head = (head[0] + self.direction[0], head[1] + self.direction[1])
        self.body.insert(0, new_head)

    def grow(self):
        """Рост змейки (хвост не удаляется)"""
        pass  # рост обрабатывается в main через отсутствие pop()

    def check_collision(self):
        """Проверка столкновений"""
        head = self.body[0]

        # 1. Столкновение со стенами
        if (head[0] < 0 or head[0] >= GRID_WIDTH or
                head[1] < 0 or head[1] >= GRID_HEIGHT):
            return True

        # 2. Столкновение с собой
        if head in self.body[1:]:
            return True

        return False

    def draw(self):
        """Отрисовка змейки"""
        for i, segment in enumerate(self.body):
            color = DARK_GREEN if i == 0 else GREEN  # голова чуть темнее
            pygame.draw.rect(screen, color,
                             (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))
            # красивые границы
            pygame.draw.rect(screen, BLACK,
                             (segment[0] * GRID_SIZE, segment[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE), 2)


# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================
def generate_food(snake_body):
    """Генерация еды в случайном месте (НЕ на змейке)"""
    while True:
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        if (x, y) not in snake_body:
            return (x, y)


def draw_grid():
    """Отрисовка сетки"""
    for x in range(0, WIDTH, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (x, 0), (x, HEIGHT))
    for y in range(0, HEIGHT, GRID_SIZE):
        pygame.draw.line(screen, GRAY, (0, y), (WIDTH, y))


# ====================== ОСНОВНАЯ ФУНКЦИЯ ======================
def main():
    snake = Snake()
    food = generate_food(snake.body)
    game_over = False
    game_started = True  # сразу начинаем игру

    while True:
        # ============== ОБРАБОТКА СОБЫТИЙ ==============
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:  # R — рестарт
                        snake.reset()
                        food = generate_food(snake.body)
                        game_over = False
                else:
                    # Управление стрелками (запрещаем разворот на 180°)
                    if event.key == pygame.K_UP and snake.direction != DOWN:
                        snake.direction = UP
                    elif event.key == pygame.K_DOWN and snake.direction != UP:
                        snake.direction = DOWN
                    elif event.key == pygame.K_LEFT and snake.direction != RIGHT:
                        snake.direction = LEFT
                    elif event.key == pygame.K_RIGHT and snake.direction != LEFT:
                        snake.direction = RIGHT

        # ============== ЛОГИКА ИГРЫ ==============
        if not game_over:
            snake.move()

            # Проверяем, съели ли еду
            ate = False
            if snake.body[0] == food:
                ate = True
                snake.score += 10
                snake.food_eaten += 1

                # Новый уровень каждые 4 съеденные еды
                if snake.food_eaten % 4 == 0:
                    snake.level += 1

                food = generate_food(snake.body)

            # Убираем хвост, если не съели еду
            if not ate:
                snake.body.pop()

            # Проверка столкновений
            if snake.check_collision():
                game_over = True

        # ============== ОТРИСОВКА ==============
        screen.fill(BLACK)
        draw_grid()
        snake.draw()

        # Рисуем еду
        pygame.draw.rect(screen, RED,
                         (food[0] * GRID_SIZE, food[1] * GRID_SIZE, GRID_SIZE, GRID_SIZE))

        # Счёт и уровень (только когда игра идёт)
        if not game_over:
            score_text = font_small.render(f"Очки: {snake.score}", True, WHITE)
            level_text = font_small.render(f"Уровень: {snake.level}", True, WHITE)
            screen.blit(score_text, (10, 10))
            screen.blit(level_text, (10, 40))

        # ============== ЭКРАН GAME OVER ==============
        if game_over:
            # Большой текст GAME OVER
            go_text = font_big.render("GAME OVER", True, RED)
            go_rect = go_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 40))
            screen.blit(go_text, go_rect)

            # Финальный счёт
            final_score = font_medium.render(f"Ваш счёт: {snake.score}", True, WHITE)
            fs_rect = final_score.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
            screen.blit(final_score, fs_rect)

            # Подсказка
            restart_text = font_small.render("Нажми R для рестарта", True, WHITE)
            r_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            screen.blit(restart_text, r_rect)

        pygame.display.update()

        # ============== СКОРОСТЬ ИГРЫ ==============
        if not game_over:
            speed = 8 + (snake.level - 1) * 3  # скорость растёт с уровнем
            clock.tick(speed)
        else:
            clock.tick(10)  # когда игра окончена — не нагружаем процессор


if __name__ == "__main__":
    main()