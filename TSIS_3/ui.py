import pygame
import sys
from persistence import (load_leaderboard, load_settings,
                          save_settings, DEFAULT_SETTINGS)

# ====================== ЦВЕТА ======================
BLACK      = (0,   0,   0)
WHITE      = (255, 255, 255)
GRAY       = (50,  50,  50)
LIGHT_GRAY = (180, 180, 180)
DARK_GRAY  = (30,  30,  30)
ACCENT     = (255, 200, 0)
RED        = (220, 50,  50)
GREEN      = (50,  200, 80)
BLUE       = (70,  130, 200)

# ====================== ВСПОМОГАТЕЛЬНЫЙ КЛАСС КНОПКИ ======================

class Button:
    """Простая кнопка с текстом."""

    def __init__(self, rect, text, font,
                 color=ACCENT, text_color=BLACK,
                 border_radius=8):
        self.rect         = pygame.Rect(rect)
        self.text         = text
        self.font         = font
        self.color        = color
        self.text_color   = text_color
        self.border_radius = border_radius
        self.hovered      = False

    def draw(self, surface):
        col = tuple(min(255, c + 30) for c in self.color) if self.hovered else self.color
        pygame.draw.rect(surface, col, self.rect, border_radius=self.border_radius)
        pygame.draw.rect(surface, WHITE, self.rect, 2, border_radius=self.border_radius)
        label = self.font.render(self.text, True, self.text_color)
        surface.blit(label, label.get_rect(center=self.rect.center))

    def update(self, mouse_pos):
        self.hovered = self.rect.collidepoint(mouse_pos)

    def is_clicked(self, event):
        return (event.type == pygame.MOUSEBUTTONDOWN
                and event.button == 1
                and self.rect.collidepoint(event.pos))


# ====================== ГЛАВНОЕ МЕНЮ ======================

def main_menu(screen, clock, settings):
    """
    Возвращает одно из: 'play', 'leaderboard', 'settings', 'quit'
    """
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("arial", 52, bold=True)
    font_btn   = pygame.font.SysFont("arial", 28, bold=True)

    bw, bh = 260, 52
    cx = WIDTH // 2 - bw // 2
    buttons = [
        Button((cx, 220, bw, bh), "▶  Играть",        font_btn, color=GREEN),
        Button((cx, 290, bw, bh), "🏆  Лидеры",        font_btn, color=BLUE),
        Button((cx, 360, bw, bh), "⚙  Настройки",     font_btn, color=GRAY),
        Button((cx, 430, bw, bh), "✕  Выйти",          font_btn, color=RED),
    ]
    actions = ["play", "leaderboard", "settings", "quit"]

    road_offset = 0

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            for btn, action in zip(buttons, actions):
                if btn.is_clicked(event):
                    return action

        for btn in buttons:
            btn.update(mouse_pos)

        # Анимированный фон (дорога)
        road_offset = (road_offset + 3) % 80
        screen.fill(GRAY)
        rl = WIDTH // 2 - 120
        pygame.draw.rect(screen, BLACK, (rl, 0, 240, HEIGHT))
        for i in range(-2, 12):
            y = (i * 80 + road_offset) % (HEIGHT + 80) - 40
            pygame.draw.rect(screen, WHITE, (WIDTH // 2 - 6, y, 12, 44))

        # Заголовок
        title = font_title.render("RACER", True, ACCENT)
        sub   = pygame.font.SysFont("arial", 20).render("TSIS 3  —  Advanced Edition", True, LIGHT_GRAY)
        screen.blit(title, title.get_rect(center=(WIDTH // 2, 130)))
        screen.blit(sub,   sub.get_rect(center=(WIDTH // 2, 185)))

        for btn in buttons:
            btn.draw(screen)

        pygame.display.flip()


# ====================== ЭКРАН ВВОДА ИМЕНИ ======================

def username_screen(screen, clock, settings):
    """Возвращает введённое имя (строка)."""
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("arial", 38, bold=True)
    font_input = pygame.font.SysFont("arial", 30)
    font_hint  = pygame.font.SysFont("arial", 20)
    font_btn   = pygame.font.SysFont("arial", 26, bold=True)

    name = settings.get("username", "")
    input_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 25, 300, 50)
    ok_btn = Button((WIDTH // 2 - 80, HEIGHT // 2 + 60, 160, 46), "Начать", font_btn, color=GREEN)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        ok_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_RETURN and name.strip():
                    return name.strip()
                elif event.key == pygame.K_BACKSPACE:
                    name = name[:-1]
                elif len(name) < 16 and event.unicode.isprintable():
                    name += event.unicode
            if ok_btn.is_clicked(event) and name.strip():
                return name.strip()

        screen.fill(DARK_GRAY)
        t = font_title.render("Введите имя", True, ACCENT)
        screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 100)))

        pygame.draw.rect(screen, WHITE, input_rect, border_radius=6)
        pygame.draw.rect(screen, ACCENT, input_rect, 2, border_radius=6)
        txt = font_input.render(name + "|", True, BLACK)
        screen.blit(txt, txt.get_rect(center=input_rect.center))

        hint = font_hint.render("Enter или кнопка для старта", True, LIGHT_GRAY)
        screen.blit(hint, hint.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 30)))
        ok_btn.draw(screen)
        pygame.display.flip()


# ====================== НАСТРОЙКИ ======================

def settings_screen(screen, clock, settings):
    """Изменяет и сохраняет настройки. Возвращает обновлённый словарь."""
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("arial", 36, bold=True)
    font_lbl   = pygame.font.SysFont("arial", 24)
    font_btn   = pygame.font.SysFont("arial", 22, bold=True)

    CAR_COLORS = {
        "Синий":     (0,   100, 255),
        "Красный":   (220, 40,  40),
        "Зелёный":   (30,  180, 60),
        "Жёлтый":    (240, 200, 0),
        "Фиолетовый":(150, 0,   220),
    }
    DIFFICULTIES = ["easy", "normal", "hard"]
    diff_labels  = {"easy": "Лёгкий", "normal": "Нормальный", "hard": "Сложный"}

    back_btn = Button((WIDTH // 2 - 80, HEIGHT - 80, 160, 44), "← Назад", font_btn, color=GRAY)

    # Кнопка звука
    def sound_btn():
        label = "🔊 Звук: ВКЛ" if settings["sound"] else "🔇 Звук: ВЫКЛ"
        return Button((WIDTH // 2 - 120, 180, 240, 44), label, font_btn,
                      color=GREEN if settings["sound"] else RED)

    # Кнопки сложности
    def diff_buttons():
        btns = []
        for i, d in enumerate(DIFFICULTIES):
            active = settings["difficulty"] == d
            btns.append(Button((WIDTH // 2 - 180 + i * 125, 300, 115, 40),
                               diff_labels[d], font_btn,
                               color=ACCENT if active else GRAY))
        return btns

    # Кнопки цвета машины
    def color_buttons():
        btns = []
        for i, (name, rgb) in enumerate(CAR_COLORS.items()):
            btns.append((Button((60 + i * 75, 420, 65, 32), name, font_btn,
                                color=rgb, text_color=WHITE), rgb))
        return btns

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        s_btn  = sound_btn()
        d_btns = diff_buttons()
        c_btns = color_buttons()
        all_btns = [s_btn, back_btn] + d_btns + [b for b, _ in c_btns]
        for b in all_btns:
            b.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if s_btn.is_clicked(event):
                settings["sound"] = not settings["sound"]
            for b, d in zip(d_btns, DIFFICULTIES):
                if b.is_clicked(event):
                    settings["difficulty"] = d
            for b, rgb in c_btns:
                if b.is_clicked(event):
                    settings["car_color"] = list(rgb)
            if back_btn.is_clicked(event):
                save_settings(settings)
                return settings

        screen.fill(DARK_GRAY)
        t = font_title.render("Настройки", True, ACCENT)
        screen.blit(t, t.get_rect(center=(WIDTH // 2, 100)))

        screen.blit(font_lbl.render("Звук:", True, LIGHT_GRAY), (60, 185))
        s_btn.draw(screen)

        screen.blit(font_lbl.render("Сложность:", True, LIGHT_GRAY), (60, 305))
        for b in d_btns:
            b.draw(screen)

        screen.blit(font_lbl.render("Цвет машины:", True, LIGHT_GRAY), (60, 395))
        for b, _ in c_btns:
            b.draw(screen)

        # Текущий цвет — превью
        cur = tuple(settings["car_color"])
        pygame.draw.rect(screen, cur, (60, 460, 50, 90))
        pygame.draw.rect(screen, WHITE, (60, 460, 50, 90), 2)

        back_btn.draw(screen)
        pygame.display.flip()


# ====================== ТАБЛИЦА ЛИДЕРОВ ======================

def leaderboard_screen(screen, clock):
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("arial", 36, bold=True)
    font_row   = pygame.font.SysFont("arial", 22)
    font_btn   = pygame.font.SysFont("arial", 22, bold=True)

    back_btn = Button((WIDTH // 2 - 80, HEIGHT - 70, 160, 44), "← Назад", font_btn, color=GRAY)
    entries  = load_leaderboard()

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        back_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if back_btn.is_clicked(event):
                return

        screen.fill(DARK_GRAY)
        t = font_title.render("🏆  Таблица лидеров", True, ACCENT)
        screen.blit(t, t.get_rect(center=(WIDTH // 2, 60)))

        # Заголовок таблицы
        headers = ["#", "Имя", "Очки", "Дистанция"]
        cols    = [40, 120, 280, 380]
        for col, hdr in zip(cols, headers):
            h = font_row.render(hdr, True, LIGHT_GRAY)
            screen.blit(h, (col, 110))
        pygame.draw.line(screen, LIGHT_GRAY, (30, 135), (WIDTH - 30, 135), 1)

        if not entries:
            msg = font_row.render("Записей пока нет", True, LIGHT_GRAY)
            screen.blit(msg, msg.get_rect(center=(WIDTH // 2, 250)))
        else:
            for i, e in enumerate(entries[:10]):
                y   = 148 + i * 38
                col = ACCENT if i == 0 else WHITE
                row = [str(i+1), e.get("name","?"),
                       str(e.get("score", 0)),
                       f"{e.get('distance', 0)} м"]
                for cx, val in zip(cols, row):
                    screen.blit(font_row.render(val, True, col), (cx, y))

        back_btn.draw(screen)
        pygame.display.flip()


# ====================== GAME OVER ======================

def game_over_screen(screen, clock, score, distance, coins_collected):
    """Возвращает 'retry' или 'menu'."""
    WIDTH, HEIGHT = screen.get_size()
    font_title = pygame.font.SysFont("arial", 52, bold=True)
    font_stat  = pygame.font.SysFont("arial", 26)
    font_btn   = pygame.font.SysFont("arial", 26, bold=True)

    bw, bh = 200, 50
    retry_btn = Button((WIDTH // 2 - 215, HEIGHT // 2 + 110, bw, bh), "↺  Заново",   font_btn, color=GREEN)
    menu_btn  = Button((WIDTH // 2 + 15,  HEIGHT // 2 + 110, bw, bh), "⌂  Меню",     font_btn, color=BLUE)

    while True:
        clock.tick(60)
        mouse_pos = pygame.mouse.get_pos()
        retry_btn.update(mouse_pos)
        menu_btn.update(mouse_pos)

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if retry_btn.is_clicked(event): return "retry"
            if menu_btn.is_clicked(event):  return "menu"
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r: return "retry"
                if event.key == pygame.K_ESCAPE: return "menu"

        overlay = pygame.Surface((WIDTH, HEIGHT))
        overlay.set_alpha(210)
        overlay.fill(BLACK)
        screen.blit(overlay, (0, 0))

        t = font_title.render("GAME OVER", True, RED)
        screen.blit(t, t.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 120)))

        stats = [
            f"Очки:       {score}",
            f"Дистанция:  {distance} м",
            f"Монет:      {coins_collected}",
        ]
        for i, s in enumerate(stats):
            surf = font_stat.render(s, True, WHITE)
            screen.blit(surf, surf.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 30 + i * 40)))

        retry_btn.draw(screen)
        menu_btn.draw(screen)
        pygame.display.flip()
