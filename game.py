import pygame
from settings import s, SW, SH, TILE, JUMP_FORCE, PLAYER_LIVES
from levels  import get_level_map, new_random_level
from sprites import Tile, Coin, Flag, Enemy, Player
from camera  import Camera


def load_level(idx):
    data   = get_level_map(idx)
    rows   = len(data)
    cols   = max(len(r) for r in data)

    tiles   = pygame.sprite.Group()
    coins   = pygame.sprite.Group()
    enemies = pygame.sprite.Group()
    flags   = pygame.sprite.Group()
    player  = None

    # Уровень прилегает к низу экрана; если тайлов больше чем экран — прижимаем к низу
    offset_y = max(0, SH - rows * TILE)

    # Находим строку земли (последнюю непустую строку)
    ground_row = rows - 1
    spawn_y = offset_y + ground_row * TILE - TILE  # одна строка над землёй

    for ri, row in enumerate(data):
        for ci, ch in enumerate(row):
            x = ci * TILE
            y = offset_y + ri * TILE
            if ch == 'G':
                tiles.add(Tile(x, y, kind='ground'))
            elif ch == '#':
                tiles.add(Tile(x, y, kind='stone'))
            elif ch == 'C':
                coins.add(Coin(x, y))
            elif ch == 'E':
                enemies.add(Enemy(x, y))
            elif ch == 'F':
                flags.add(Flag(x, y))
            elif ch == 'P':
                player = Player(x, y)

    if player is None:
        player = Player(TILE * 2, spawn_y)

    level_width = cols * TILE
    camera = Camera(level_width)
    return tiles, coins, enemies, flags, player, camera


# ──────────────────────────────────────────────────────────
class GameSession:
    """Хранит всё состояние текущей игровой сессии."""

    def __init__(self):
        self.level_idx    = 0
        self.lives        = PLAYER_LIVES
        self.total_coins  = 0
        self.state        = "play"   # play/dead/win/gameover/complete
        self.collected    = 0
        self._load()

    def _load(self):
        # каждый раз новая случайная карта
        new_random_level(self.level_idx)
        res = load_level(self.level_idx)
        (self.tiles, self.coins, self.enemies,
         self.flags, self.player, self.camera) = res
        self.collected = 0

    # ── обновление физики и логики ──────────────────────────
    def update(self):
        if self.state != "play":
            return

        p = self.player
        p.update(self.tiles)
        self.coins.update()
        self.flags.update()
        for en in self.enemies:
            en.update(self.tiles)
        self.camera.update(p.rect)

        # монеты
        got = pygame.sprite.spritecollide(p, self.coins, True)
        self.collected   += len(got)
        self.total_coins += len(got)

        # враги
        for en in list(self.enemies):
            if p.rect.colliderect(en.rect):
                # топнуть сверху?
                if p.vy > 0 and p.rect.bottom < en.rect.centery + s(10):
                    en.kill()
                    p.vy = JUMP_FORCE * 0.6
                else:
                    self.lives -= 1
                    self.state  = "dead"
                    return

        # флаг
        if pygame.sprite.spritecollide(p, self.flags, False):
            self.state = "win"
            return

        # упал вниз
        if p.rect.top > SH + TILE:
            self.lives -= 1
            self.state  = "dead"

    # ── реакция на «продолжить» ─────────────────────────────
    def advance(self):
        if self.state == "dead":
            if self.lives > 0:
                self._load()
                self.state = "play"
            else:
                self.state = "gameover"

        elif self.state == "win":
            self.level_idx += 1
            self._load()
            self.state = "play"

        elif self.state in ("gameover", "complete"):
            self.level_idx   = 0
            self.lives       = PLAYER_LIVES
            self.total_coins = 0
            self._load()
            self.state = "play"

    # ── рисование (без UI-слоя) ─────────────────────────────
    def draw(self, surf):
        cam = self.camera

        def blit(sprite):
            surf.blit(sprite.image, cam.apply(sprite.rect))

        for t in self.tiles:   blit(t)
        for c in self.coins:   blit(c)
        for f in self.flags:   blit(f)
        for e in self.enemies: blit(e)
        blit(self.player)
