# main.py
import pygame
import sys
from db import init_database, save_game_result, get_top_10, get_personal_best
from settings import load_settings, save_settings
from game import run_game

pygame.init()

WIDTH, HEIGHT = 620, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Snake - TSIS 4")
clock = pygame.time.Clock()

# Цвета
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (40, 40, 40)
ACCENT = (0, 255, 100)
GREEN = (0, 200, 0)
RED = (220, 50, 50)
BLUE = (70, 130, 255)


class Button:
    def __init__(self, x, y, w, h, text, color, action):
        self.rect = pygame.Rect(x, y, w, h)
        self.text = text
        self.color = color
        self.action = action
        self.hovered = False

    def draw(self, surface, font):
        color = tuple(min(255, c + 40) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(surface, color, self.rect, border_radius=12)
        pygame.draw.rect(surface, WHITE, self.rect, 3, border_radius=12)

        text_surf = font.render(self.text, True, WHITE)
        text_rect = text_surf.get_rect(center=self.rect.center)
        surface.blit(text_surf, text_rect)

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN and
                event.button == 1 and
                self.rect.collidepoint(event.pos))


def main_menu(screen, clock, settings):
    font_title = pygame.font.SysFont("arial", 72, bold=True)
    font_btn = pygame.font.SysFont("arial", 36, bold=True)

    buttons = [
        Button(WIDTH // 2 - 140, 220, 280, 60, "▶  ИГРАТЬ", GREEN, "play"),
        Button(WIDTH // 2 - 140, 300, 280, 60, "🏆  ЛИДЕРБОРД", BLUE, "leaderboard"),
        Button(WIDTH // 2 - 140, 380, 280, 60, "⚙  НАСТРОЙКИ", GRAY, "settings"),
        Button(WIDTH // 2 - 140, 460, 280, 60, "✕  ВЫХОД", RED, "quit"),
    ]

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            for btn in buttons:
                if btn.is_clicked(event):
                    return btn.action

        for btn in buttons:
            btn.update(mouse_pos)

        screen.fill(BLACK)

        title = font_title.render("SNAKE", True, ACCENT)
        subtitle = pygame.font.SysFont("arial", 24).render("TSIS 4 — Advanced", True, (180, 180, 180))
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 100))
        screen.blit(subtitle, (WIDTH // 2 - subtitle.get_width() // 2, 170))

        for btn in buttons:
            btn.draw(screen, font_btn)

        pygame.display.flip()


def get_username(screen, clock, settings):
    font = pygame.font.SysFont("arial", 40)
    small_font = pygame.font.SysFont("arial", 24)
    name = settings.get("username", "")

    input_rect = pygame.Rect(WIDTH // 2 - 160, 320, 320, 65)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit();
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode

        screen.fill(BLACK)
        title = font.render("Введите ваше имя", True, ACCENT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 200))

        pygame.draw.rect(screen, WHITE, input_rect, border_radius=10)
        pygame.draw.rect(screen, ACCENT, input_rect, 4, border_radius=10)

        txt_surf = font.render(name + "_", True, BLACK)
        screen.blit(txt_surf, (input_rect.x + 25, input_rect.y + 12))

        hint = small_font.render("Нажмите ENTER для продолжения", True, WHITE)
        screen.blit(hint, (WIDTH // 2 - hint.get_width() // 2, 440))

        pygame.display.flip()


def leaderboard_screen(screen, clock):
    font_title = pygame.font.SysFont("arial", 48, bold=True)
    font = pygame.font.SysFont("arial", 26)

    entries = get_top_10()

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                return

        screen.fill(BLACK)
        title = font_title.render("🏆 ТАБЛИЦА ЛИДЕРОВ", True, ACCENT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 60))

        if not entries:
            msg = font.render("Пока нет записей", True, WHITE)
            screen.blit(msg, (WIDTH // 2 - msg.get_width() // 2, 300))
        else:
            for i, row in enumerate(entries[:10]):
                y = 150 + i * 45
                rank_color = (255, 215, 0) if i == 0 else WHITE
                text = f"{i + 1:2d}. {row['username']:<12} {row['score']:5d} очков   (Lv.{row['level_reached']})"
                surf = font.render(text, True, rank_color)
                screen.blit(surf, (70, y))

        back = font.render("ESC — Вернуться в меню", True, GRAY)
        screen.blit(back, (WIDTH // 2 - back.get_width() // 2, HEIGHT - 80))

        pygame.display.flip()


def game_over_screen(screen, clock, score, level, personal_best):
    font_big = pygame.font.SysFont("arial", 65, bold=True)
    font = pygame.font.SysFont("arial", 28)

    while True:
        clock.tick(60)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_r, pygame.K_RETURN):
                    return "retry"
                if event.key == pygame.K_ESCAPE:
                    return "menu"

        screen.fill(BLACK)

        go = font_big.render("GAME OVER", True, RED)
        screen.blit(go, (WIDTH // 2 - go.get_width() // 2, 140))

        stats = [f"Счёт: {score}", f"Уровень: {level}"]
        if personal_best:
            stats.append(f"Ваш лучший: {personal_best[0]}")

        for i, text in enumerate(stats):
            surf = font.render(text, True, WHITE)
            screen.blit(surf, (WIDTH // 2 - surf.get_width() // 2, 270 + i * 55))

        hint1 = font.render("R или ENTER — Играть снова", True, GREEN)
        hint2 = font.render("ESC — В главное меню", True, WHITE)
        screen.blit(hint1, (WIDTH // 2 - hint1.get_width() // 2, 495))
        screen.blit(hint2, (WIDTH // 2 - hint2.get_width() // 2, 530))

        pygame.display.flip()


def settings_screen(screen, clock, settings):
    """Полноценный экран настроек"""
    font_title = pygame.font.SysFont("arial", 48, bold=True)
    font = pygame.font.SysFont("arial", 28)
    small_font = pygame.font.SysFont("arial", 22)

    # Доступные цвета змейки
    snake_colors = {
        "Зелёный": (0, 200, 0),
        "Синий": (0, 100, 255),
        "Красный": (220, 50, 50),
        "Фиолетовый": (180, 0, 255),
        "Жёлтый": (255, 200, 0),
        "Бирюзовый": (0, 220, 180)
    }

    color_buttons = []
    btn_width = 110
    start_x = (WIDTH - len(snake_colors) * btn_width - 40) // 2

    for i, (name, rgb) in enumerate(snake_colors.items()):
        x = start_x + i * (btn_width + 15)
        color_buttons.append({
            "rect": pygame.Rect(x, 280, btn_width, 55),
            "name": name,
            "color": rgb,
            "selected": tuple(settings["snake_color"]) == rgb
        })

    # Кнопки On/Off
    grid_btn = Button(WIDTH // 2 - 140, 380, 280, 55,
                      f"Сетка: {'ВКЛ' if settings['grid_overlay'] else 'ВЫКЛ'}",
                      GREEN if settings['grid_overlay'] else RED, "grid")

    sound_btn = Button(WIDTH // 2 - 140, 460, 280, 55,
                       f"Звук: {'ВКЛ' if settings['sound'] else 'ВЫКЛ'}",
                       GREEN if settings['sound'] else RED, "sound")

    back_btn = Button(WIDTH // 2 - 100, 560, 200, 55, "← Назад", GRAY, "back")

    all_buttons = [grid_btn, sound_btn, back_btn]

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Клик по цветам
            for cb in color_buttons:
                if cb["rect"].collidepoint(mouse_pos) and event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    settings["snake_color"] = list(cb["color"])
                    # Обновляем selected
                    for c in color_buttons:
                        c["selected"] = (tuple(settings["snake_color"]) == c["color"])

            # Клик по обычным кнопкам
            for btn in all_buttons:
                if btn.is_clicked(event):
                    if btn.action == "grid":
                        settings["grid_overlay"] = not settings["grid_overlay"]
                        btn.text = f"Сетка: {'ВКЛ' if settings['grid_overlay'] else 'ВЫКЛ'}"
                        btn.color = GREEN if settings['grid_overlay'] else RED
                    elif btn.action == "sound":
                        settings["sound"] = not settings["sound"]
                        btn.text = f"Звук: {'ВКЛ' if settings['sound'] else 'ВЫКЛ'}"
                        btn.color = GREEN if settings['sound'] else RED
                    elif btn.action == "back":
                        return settings

        # Hover эффект
        for btn in all_buttons:
            btn.update(mouse_pos)

        # Отрисовка
        screen.fill(BLACK)

        title = font_title.render("НАСТРОЙКИ", True, ACCENT)
        screen.blit(title, (WIDTH // 2 - title.get_width() // 2, 80))

        # Заголовок цвета
        color_title = font.render("Цвет змейки:", True, WHITE)
        screen.blit(color_title, (WIDTH // 2 - color_title.get_width() // 2, 220))

        # Кнопки цветов
        for cb in color_buttons:
            color = cb["color"]
            rect = cb["rect"]
            # Подсветка выбранного
            if cb["selected"]:
                pygame.draw.rect(screen, (255, 255, 255), rect.inflate(10, 10), border_radius=15)

            pygame.draw.rect(screen, color, rect, border_radius=12)
            pygame.draw.rect(screen, WHITE, rect, 3, border_radius=12)

            name_surf = small_font.render(cb["name"], True, BLACK)
            screen.blit(name_surf, name_surf.get_rect(center=rect.center))

        # Основные настройки
        for btn in all_buttons:
            btn.draw(screen, font)

        # Текущий цвет змейки (превью)
        preview_color = tuple(settings["snake_color"])
        pygame.draw.rect(screen, preview_color, (WIDTH // 2 - 40, 180, 80, 30), border_radius=8)

        pygame.display.flip()

def main():
    init_database()
    settings = load_settings()

    while True:
        action = main_menu(screen, clock, settings)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "play":
            username = get_username(screen, clock, settings)
            if not username:
                continue

            settings["username"] = username
            save_settings(settings)

            while True:  # цикл для Retry
                score, level = run_game(screen, clock, settings, username)

                save_game_result(username, score, level)

                result = game_over_screen(screen, clock, score, level, get_personal_best(username))

                if result != "retry":
                    break  # выход в главное меню

        elif action == "leaderboard":
            leaderboard_screen(screen, clock)

        elif action == "settings":
            settings = settings_screen(screen, clock, settings)
            save_settings(settings)


if __name__ == "__main__":
    main()