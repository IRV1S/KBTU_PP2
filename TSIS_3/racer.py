import pygame
import random
import time

# ====================== КОНСТАНТЫ ======================
WIDTH, HEIGHT = 400, 700
ROAD_WIDTH    = 280
ROAD_LEFT     = (WIDTH - ROAD_WIDTH) // 2
ROAD_RIGHT    = ROAD_LEFT + ROAD_WIDTH

LANE_W   = ROAD_WIDTH // 3
LANE_CXS = [ROAD_LEFT + LANE_W * i + LANE_W // 2 for i in range(3)]

# Цвета (оставляем как было)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GRAY = (50, 50, 50)
ROAD_COLOR = (30, 30, 30)
MARK_COLOR = (255, 255, 255)
GOLD = (255, 215, 0)
PURPLE = (180, 0, 255)
RED = (220, 40, 40)
GREEN = (50, 200, 80)
ORANGE = (255, 140, 0)
CYAN = (0, 220, 220)
YELLOW = (255, 230, 0)
OIL_COLOR = (20, 20, 60)
NITRO_COLOR = (0, 255, 180)
SHIELD_COL = (80, 160, 255)
REPAIR_COL = (255, 100, 100)
LIFE_COLOR = (255, 50, 50)

DIFF_PARAMS = {
    "easy":   {"enemy_interval": 90,  "obs_interval": 120, "base_speed": 5},
    "normal": {"enemy_interval": 65,  "obs_interval": 90,  "base_speed": 6},
    "hard":   {"enemy_interval": 42,  "obs_interval": 60,  "base_speed": 8},
}

# ====================== ИГРОК ======================

class Player(pygame.sprite.Sprite):
    def __init__(self, car_color):
        super().__init__()
        self.base_speed  = 6
        self.speed       = self.base_speed
        self.lives       = 3          # ← НОВОЕ: 3 жизни
        self.max_lives   = 3
        self.shield      = False
        self.nitro_end   = 0
        self.car_color   = tuple(car_color)
        self._build_image()

        self.rect = self.image.get_rect()
        self.rect.centerx = WIDTH // 2
        self.rect.bottom  = HEIGHT - 40

    def _build_image(self):
        img = pygame.Surface((50, 90), pygame.SRCALPHA)
        pygame.draw.rect(img, self.car_color, (0, 0, 50, 90), border_radius=8)
        pygame.draw.rect(img, WHITE, (8, 12, 34, 22), border_radius=3)
        pygame.draw.rect(img, WHITE, (8, 58, 34, 18), border_radius=3)
        # колёса
        pygame.draw.rect(img, BLACK, (0,  8,  10, 22))
        pygame.draw.rect(img, BLACK, (40, 8,  10, 22))
        pygame.draw.rect(img, BLACK, (0,  60, 10, 22))
        pygame.draw.rect(img, BLACK, (40, 60, 10, 22))

        if self.shield:
            pygame.draw.rect(img, SHIELD_COL, (0, 0, 50, 90), 4, border_radius=8)

        self.image = img

    def update(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] or keys[pygame.K_a]: self.rect.x -= self.speed
        if keys[pygame.K_RIGHT] or keys[pygame.K_d]: self.rect.x += self.speed
        if keys[pygame.K_UP] or keys[pygame.K_w]: self.rect.y -= 2
        if keys[pygame.K_DOWN] or keys[pygame.K_s]: self.rect.y += 2

        self.rect.left  = max(ROAD_LEFT + 5,  self.rect.left)
        self.rect.right = min(ROAD_RIGHT - 5, self.rect.right)
        self.rect.top   = max(HEIGHT // 2, self.rect.top)
        self.rect.bottom = min(HEIGHT - 10, self.rect.bottom)

        # Нитро
        if self.nitro_end and time.time() > self.nitro_end:
            self.speed = self.base_speed
            self.nitro_end = 0

        self._build_image()

    def apply_nitro(self, duration=4):
        self.speed = self.base_speed * 2
        self.nitro_end = time.time() + duration

    def apply_shield(self):
        self.shield = True

    def remove_shield(self):
        self.shield = False

    def lose_life(self):
        if self.shield:
            self.remove_shield()
            return False  # щит спас
        self.lives -= 1
        return self.lives <= 0

    def repair(self):
        if self.lives < self.max_lives:
            self.lives += 1
            return True
        return False


# ====================== POWER-UPS ======================

class PowerUp(pygame.sprite.Sprite):
    COLORS = {"nitro": NITRO_COLOR, "shield": SHIELD_COL, "repair": REPAIR_COL}
    LABELS = {"nitro": "N", "shield": "S", "repair": "R"}
    TIMEOUT = 8

    def __init__(self, ptype, speed):
        super().__init__()
        self.ptype = ptype
        self.spawn_time = time.time()
        color = self.COLORS[ptype]
        img = pygame.Surface((36, 36), pygame.SRCALPHA)
        pygame.draw.rect(img, color, (0,0,36,36), border_radius=10)
        pygame.draw.rect(img, WHITE, (0,0,36,36), 2, border_radius=10)
        font = pygame.font.SysFont("arial", 18, bold=True)
        lbl = font.render(self.LABELS[ptype], True, BLACK)
        img.blit(lbl, lbl.get_rect(center=(18,18)))
        self.image = img
        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-500, -150)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT or time.time() - self.spawn_time > self.TIMEOUT:
            self.kill()


# ====================== Остальные классы (Enemy, Coin, OilSpill, Barrier, NitroStrip) ======================
# (оставляем без изменений — они уже были хорошие)

class Enemy(pygame.sprite.Sprite):
    COLORS = [(220,40,40),(180,0,200),(200,100,0),(0,160,200),(160,160,0)]
    def __init__(self, speed):
        super().__init__()
        color = random.choice(self.COLORS)
        img = pygame.Surface((50, 90), pygame.SRCALPHA)
        pygame.draw.rect(img, color, (0,0,50,90), border_radius=8)
        pygame.draw.rect(img, WHITE, (8,12,34,22), border_radius=3)
        pygame.draw.rect(img, BLACK, (0,8,10,22))
        pygame.draw.rect(img, BLACK, (40,8,10,22))
        pygame.draw.rect(img, BLACK, (0,60,10,22))
        pygame.draw.rect(img, BLACK, (40,60,10,22))
        self.image = img
        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-250, -60)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Coin(pygame.sprite.Sprite):
    def __init__(self, value=10, speed=6):
        super().__init__()
        self.value = value
        img = pygame.Surface((28, 28), pygame.SRCALPHA)
        if value == 50:
            pygame.draw.circle(img, PURPLE, (14,14), 14)
            pygame.draw.circle(img, WHITE, (14,14), 9)
            pygame.draw.circle(img, PURPLE, (14,14), 5)
        else:
            pygame.draw.circle(img, GOLD, (14,14), 14)
            pygame.draw.circle(img, WHITE, (14,14), 9)
        self.image = img
        self.rect = img.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-300, -80)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class OilSpill(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((60, 40), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, OIL_COLOR, (0, 0, 60, 40))
        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-400, -100)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class Barrier(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((LANE_W - 10, 22))
        self.image.fill((220, 80, 0))
        for i in range(0, LANE_W, 20):
            pygame.draw.rect(self.image, WHITE, (i, 0, 10, 22))
        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-400, -100)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


class NitroStrip(pygame.sprite.Sprite):
    def __init__(self, speed):
        super().__init__()
        self.image = pygame.Surface((LANE_W - 10, 18), pygame.SRCALPHA)
        pygame.draw.rect(self.image, NITRO_COLOR, (0,0,LANE_W-10,18), border_radius=4)
        font = pygame.font.SysFont("arial", 13, bold=True)
        lbl = font.render("NITRO", True, BLACK)
        self.image.blit(lbl, lbl.get_rect(center=(self.image.get_width()//2, 9)))
        self.rect = self.image.get_rect()
        lane = random.randint(0, 2)
        self.rect.centerx = LANE_CXS[lane]
        self.rect.y = random.randint(-500, -150)
        self.speed = speed

    def update(self):
        self.rect.y += self.speed
        if self.rect.top > HEIGHT:
            self.kill()


# ====================== ОСНОВНАЯ ИГРА ======================

def run_game(screen, clock, settings, username):
    diff = settings.get("difficulty", "normal")
    params = DIFF_PARAMS[diff]

    car_color = settings.get("car_color", [0, 100, 255])

    player = Player(car_color)
    all_sprites = pygame.sprite.Group(player)
    enemies = pygame.sprite.Group()
    coins = pygame.sprite.Group()
    obstacles = pygame.sprite.Group()
    road_events = pygame.sprite.Group()
    powerups = pygame.sprite.Group()

    score = 0
    coins_collected = 0
    distance = 0
    frames = 0
    game_over = False

    enemy_timer = obs_timer = event_timer = powerup_timer = coin_timer = 0

    active_powerup = None
    active_powerup_end = 0

    font = pygame.font.SysFont("arial", 22)
    font_sm = pygame.font.SysFont("arial", 16)
    font_big = pygame.font.SysFont("arial", 46, bold=True)

    road_offset = 0

    def current_speed():
        return params["base_speed"] + (score // 150)

    def safe_spawn(sprite_class, *args):
        obj = sprite_class(*args)
        if abs(obj.rect.centerx - player.rect.centerx) < 60 and obj.rect.y > -200:
            obj.kill()
            return None
        return obj

    while True:
        clock.tick(60)
        frames += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); import sys; sys.exit()
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                game_over = True

        if not game_over:
            spd = current_speed()

            distance = frames * spd // 60
            score_road = frames // 30

            player.update()
            enemies.update()
            coins.update()
            obstacles.update()
            road_events.update()
            powerups.update()

            # Спавн
            enemy_timer += 1
            if enemy_timer >= max(25, params["enemy_interval"] - score // 500):
                e = Enemy(spd + 1)
                enemies.add(e); all_sprites.add(e)
                enemy_timer = 0

            coin_timer += 1
            if coin_timer >= 45:
                value = 50 if random.random() < 0.18 else 10
                c = Coin(value, spd)
                coins.add(c); all_sprites.add(c)
                coin_timer = 0

            obs_timer += 1
            if obs_timer >= max(20, params["obs_interval"] - score // 400):
                cls = random.choice([OilSpill, Barrier])
                obj = safe_spawn(cls, spd)
                if obj:
                    obstacles.add(obj); all_sprites.add(obj)
                obs_timer = 0

            event_timer += 1
            if event_timer >= 120:
                road_events.add(NitroStrip(spd)); all_sprites.add(road_events.sprites()[-1])
                event_timer = 0

            powerup_timer += 1
            if powerup_timer >= 200:
                ptype = random.choice(["nitro", "shield", "repair"])
                pu = PowerUp(ptype, spd)
                powerups.add(pu); all_sprites.add(pu)
                powerup_timer = 0

            # Коллизии
            for c in pygame.sprite.spritecollide(player, coins, True):
                score += c.value
                coins_collected += 1

            for pu in pygame.sprite.spritecollide(player, powerups, True):
                if pu.ptype == "nitro":
                    player.apply_nitro(4)
                    active_powerup = "nitro"
                    active_powerup_end = time.time() + 4
                elif pu.ptype == "shield":
                    player.apply_shield()
                    active_powerup = "shield"
                    active_powerup_end = time.time() + 15
                elif pu.ptype == "repair":
                    if player.repair():
                        score += 30
                    active_powerup = "repair"
                    active_powerup_end = time.time() + 0.5   # короткое отображение

            # Щит истекает
            if active_powerup == "shield" and time.time() > active_powerup_end:
                player.remove_shield()
                active_powerup = None

            # NitroStrip
            for ns in pygame.sprite.spritecollide(player, road_events, True):
                player.apply_nitro(3)

            # Препятствия
            for obj in pygame.sprite.spritecollide(player, obstacles, False):
                if isinstance(obj, OilSpill):
                    player.speed = max(2, player.base_speed // 2)
                elif isinstance(obj, Barrier):
                    if player.lose_life():
                        game_over = True
                    else:
                        obj.kill()

            # Враги
            if pygame.sprite.spritecollide(player, enemies, False):
                if player.lose_life():
                    game_over = True
                else:
                    # убираем только одну машину при ударе
                    for e in pygame.sprite.spritecollide(player, enemies, True):
                        break

            # Восстановление скорости после масла
            if not player.nitro_end and player.speed < player.base_speed:
                player.speed = player.base_speed

            score = score_road + coins_collected * 10 + (50 if player.shield else 0)

        # ====================== ОТРИСОВКА ======================
        screen.fill(GRAY)
        road_offset = (road_offset + current_speed()) % 80
        pygame.draw.rect(screen, ROAD_COLOR, (ROAD_LEFT, 0, ROAD_WIDTH, HEIGHT))

        # линии полос
        for i in range(1, 3):
            lx = ROAD_LEFT + LANE_W * i
            for j in range(-2, 12):
                y = (j * 80 + road_offset) % (HEIGHT + 80) - 40
                pygame.draw.rect(screen, (80,80,80), (lx-2, y, 4, 44))

        all_sprites.draw(screen)

        # HUD
        screen.blit(font.render(f"Очки: {score}", True, WHITE), (8, 8))
        screen.blit(font.render(f"Дистанция: {distance} м", True, WHITE), (8, 34))
        screen.blit(font_sm.render(f"Монет: {coins_collected}", True, GOLD), (8, 60))

        # Жизни
        for i in range(player.lives):
            pygame.draw.circle(screen, LIFE_COLOR, (WIDTH - 30 - i*35, 25), 12)
            pygame.draw.circle(screen, WHITE, (WIDTH - 30 - i*35, 25), 12, 2)

        # Активный power-up
        if active_powerup and time.time() < active_powerup_end + 1:
            rem = max(0, active_powerup_end - time.time())
            names = {"nitro": "НИТРО", "shield": "ЩИТ", "repair": "РЕМОНТ"}
            cols = {"nitro": NITRO_COLOR, "shield": SHIELD_COL, "repair": REPAIR_COL}
            label = f"{names.get(active_powerup,'')} {rem:.1f}s"
            pu_surf = font.render(label, True, cols.get(active_powerup, WHITE))
            screen.blit(pu_surf, (WIDTH - pu_surf.get_width() - 10, 50))

        if game_over:
            break

        pygame.display.flip()

    return score, distance, coins_collected