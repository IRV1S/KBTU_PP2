import pygame
import random
import sys
import time

# ====================== ИНИЦИАЛИЗАЦИЯ PYGAME ======================
pygame.init()

# ====================== НАСТРОЙКИ ИГРЫ ======================
WIDTH = HEIGHT = 600  # Размер игрового окна (квадрат)
GRID_SIZE = 20  # Размер одной клетки
GRID_W = WIDTH // GRID_SIZE  # Количество клеток по ширине
GRID_H = HEIGHT // GRID_SIZE  # Количество клеток по высоте

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake - Practice 11")
clock = pygame.time.Clock()

# Шрифты
font = pygame.font.SysFont("arial", 50, bold=True)
small_font = pygame.font.SysFont("arial", 28)

# ====================== ЦВЕТА ======================
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 200, 0)
RED = (255, 0, 0)
GOLD = (255, 215, 0)
GRAY = (40, 40, 40)


# ====================== КЛАСС ЗМЕЙКИ ======================
class Snake:
    """Главный класс змейки — содержит всю логику движения, роста и столкновений"""

    def __init__(self):
        self.reset()

    def reset(self):
        """Сброс змейки в начальное состояние (при старте и рестарте)"""
        self.body = [(10, 10), (9, 10), (8, 10)]  # Начальное тело змейки
        self.direction = (1, 0)  # Начальное направление — вправо
        self.score = 0
        self.level = 1

    def move(self):
        """Перемещение змейки на одну клетку в текущем направлении"""
        head = (self.body[0][0] + self.direction[0],
                self.body[0][1] + self.direction[1])
        self.body.insert(0, head)  # Добавляем новую голову

    def check_collision(self):
        """Проверка столкновений со стенами и с собой"""
        head = self.body[0]

        # Столкновение со стенами
        if (head[0] < 0 or head[0] >= GRID_W or
                head[1] < 0 or head[1] >= GRID_H):
            return True

        # Столкновение с собственным телом
        if head in self.body[1:]:
            return True

        return False


# ====================== ВСПОМОГАТЕЛЬНЫЕ ФУНКЦИИ ======================
def generate_food(snake_body):
    """Генерация новой еды в случайном месте, где нет змейки"""
    while True:
        pos = (random.randint(0, GRID_W - 1), random.randint(0, GRID_H - 1))
        if pos not in snake_body:
            return pos


# ====================== ОСНОВНАЯ ФУНКЦИЯ ИГРЫ ======================
def main():
    snake = Snake()
    food = generate_food(snake.body)
    is_special = False  # Флаг специальной (золотой) еды
    food_timer = time.time()  # Таймер для исчезновения еды
    game_over = False

    while True:
        # ====================== ОБРАБОТКА СОБЫТИЙ ======================
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if game_over:
                    if event.key == pygame.K_r:
                        main()  # Рестарт игры
                else:
                    # Управление направлением змейки (запрет разворота на 180°)
                    if event.key == pygame.K_UP and snake.direction != (0, 1):
                        snake.direction = (0, -1)
                    elif event.key == pygame.K_DOWN and snake.direction != (0, -1):
                        snake.direction = (0, 1)
                    elif event.key == pygame.K_LEFT and snake.direction != (1, 0):
                        snake.direction = (-1, 0)
                    elif event.key == pygame.K_RIGHT and snake.direction != (-1, 0):
                        snake.direction = (1, 0)

        if not game_over:
            snake.move()

            ate = False
            # ====================== ПОЕДАНИЕ ЕДЫ ======================
            if snake.body[0] == food:
                ate = True
                points = 30 if is_special else 10  # Золотая еда даёт больше очков
                snake.score += points

                # Увеличение уровня каждые 60 очков
                if snake.score // 60 + 1 > snake.level:
                    snake.level += 1

                # С шансом 22% следующая еда будет специальной
                is_special = random.random() < 0.22
                food = generate_food(snake.body)
                food_timer = time.time()

            # Удаляем хвост, если не съели еду
            if not ate:
                snake.body.pop()

            # ====================== ИСЧЕЗНОВЕНИЕ ЕДЫ ======================
            # Обычная еда исчезает через 9 сек, золотая — через 4.5 сек
            if time.time() - food_timer > (4.5 if is_special else 9):
                is_special = random.random() < 0.22
                food = generate_food(snake.body)
                food_timer = time.time()

            # Проверка на поражение
            if snake.check_collision():
                game_over = True

        # ====================== ОТРИСОВКА ======================
        screen.fill(BLACK)

        # Отрисовка змейки
        for i, segment in enumerate(snake.body):
            color = (0, 255, 120) if i == 0 else GREEN  # Голова ярче
            pygame.draw.rect(screen, color,
                             (segment[0] * GRID_SIZE,
                              segment[1] * GRID_SIZE,
                              GRID_SIZE, GRID_SIZE))

        # Отрисовка еды
        food_color = GOLD if is_special else RED
        pygame.draw.rect(screen, food_color,
                         (food[0] * GRID_SIZE,
                          food[1] * GRID_SIZE,
                          GRID_SIZE, GRID_SIZE))

        # ====================== HUD (интерфейс) ======================
        score_txt = small_font.render(f"Счёт: {snake.score}", True, WHITE)
        level_txt = small_font.render(f"Уровень: {snake.level}", True, WHITE)
        screen.blit(score_txt, (15, 10))
        screen.blit(level_txt, (15, 45))

        # ====================== ЭКРАН GAME OVER ======================
        if game_over:
            # Полупрозрачный затемнённый фон
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(170)
            overlay.fill(BLACK)
            screen.blit(overlay, (0, 0))

            go_text = font.render("GAME OVER", True, RED)
            screen.blit(go_text, (WIDTH // 2 - go_text.get_width() // 2, HEIGHT // 2 - 80))

            final_score = small_font.render(f"Итоговый счёт: {snake.score}", True, WHITE)
            screen.blit(final_score, (WIDTH // 2 - final_score.get_width() // 2, HEIGHT // 2 - 10))

            restart_text = small_font.render("Нажми R для рестарта", True, WHITE)
            screen.blit(restart_text, (WIDTH // 2 - restart_text.get_width() // 2, HEIGHT // 2 + 40))

        pygame.display.flip()

        # Скорость игры увеличивается с уровнем
        clock.tick(7 + snake.level * 3)


# ====================== ЗАПУСК ИГРЫ ======================
if __name__ == "__main__":
    main()