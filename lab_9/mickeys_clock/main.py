import pygame
import sys
from datetime import datetime
import math

# Инициализация
pygame.init()
WIDTH, HEIGHT = 800, 800
CENTER = (WIDTH // 2, HEIGHT // 2)
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Mickey's Clock")
clock = pygame.time.Clock()

# Загрузка ресурсов
try:
    # Загружаем фон
    background = pygame.image.load("images/mickey_background.png").convert_alpha()
    background = pygame.transform.scale(background, (WIDTH, HEIGHT))

    # Загружаем ОДНУ картинку руки, которую будем использовать для обеих стрелок
    hand_img = pygame.image.load("images/mickey_hand.png").convert_alpha()
    # Подгоняем размер руки
    hand_img = pygame.transform.scale(hand_img, (150, 150))
except Exception as e:
    print(f"Ошибка загрузки изображений: {e}")
    pygame.quit()
    sys.exit()


def get_angle(units, total_steps=60):
    # В Pygame rotate идет против часовой, поэтому вычитаем из 90
    return 90 - (units * (360 / total_steps))


def draw_hand(angle, distance):
    # Вычисляем позицию руки на циферблате
    rad = math.radians(angle)
    x = CENTER[0] + distance * math.cos(rad)
    y = CENTER[1] - distance * math.sin(rad)

    # Поворачиваем изображение руки
    # angle - 90, так как исходная рука обычно смотрит вверх
    rotated_hand = pygame.transform.rotate(hand_img, angle - 90)
    rect = rotated_hand.get_rect(center=(x, y))
    screen.blit(rotated_hand, rect)


# Главный цикл
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            sys.exit()

    # 1. Получаем время (только минуты и секунды по ТЗ)
    now = datetime.now()
    minutes = now.minute
    seconds = now.second

    # 2. Отрисовка фона
    screen.blit(background, (0, 0))

    # 3. Расчет углов
    m_angle = get_angle(minutes)
    s_angle = get_angle(seconds)

    # Правая рука (минуты) - сделаем чуть ближе к центру
    draw_hand(m_angle, 180)

    # Левая рука (секунды) - чуть дальше
    draw_hand(s_angle, 250)

    # 5. Центральная точка (чтобы закрыть пустоту в центре, если нужно)
    pygame.draw.circle(screen, (0, 0, 0), CENTER, 15)

    pygame.display.flip()
    clock.tick(60)  # Обновление (в ТЗ сказано раз в секунду, но 60 FPS даст плавность)