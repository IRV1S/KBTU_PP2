import pygame
import sys

from persistence import load_settings, save_settings, add_entry
from ui          import (main_menu, username_screen, settings_screen,
                          leaderboard_screen, game_over_screen)
from racer       import run_game

# ====================== ИНИЦИАЛИЗАЦИЯ ======================
pygame.init()
WIDTH, HEIGHT = 400, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Racer — TSIS 3")
clock = pygame.time.Clock()

# ====================== ГЛАВНЫЙ ЦИКЛ ======================

def main():
    settings = load_settings()
    username = settings.get("username", "")

    while True:
        action = main_menu(screen, clock, settings)

        if action == "quit":
            pygame.quit()
            sys.exit()

        elif action == "settings":
            settings = settings_screen(screen, clock, settings)
            save_settings(settings)

        elif action == "leaderboard":
            leaderboard_screen(screen, clock)


        elif action == "play":

            # Всегда спрашиваем имя перед игрой

            username = username_screen(screen, clock, settings)

            settings["username"] = username

            save_settings(settings)

            while True:

                score, distance, coins = run_game(screen, clock, settings, username)

                add_entry(username, score, distance)

                result = game_over_screen(screen, clock, score, distance, coins)

                if result == "retry":

                    continue

                else:

                    break

            while True:
                # Игровой цикл
                score, distance, coins = run_game(screen, clock, settings, username)

                # Сохранить результат
                add_entry(username, score, distance)

                # Экран Game Over
                result = game_over_screen(screen, clock, score, distance, coins)

                if result == "retry":
                    continue        # ещё раз
                else:
                    break           # в меню


if __name__ == "__main__":
    main()
