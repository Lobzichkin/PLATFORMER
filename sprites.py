import pygame
from settings import (
    s, TILE, GRAVITY, JUMP_FORCE, PLAYER_SPEED, MAX_FALL, SH,
)
from draw_utils import (
    draw_ground_tile, draw_stone_tile,
    draw_coin, draw_flag, draw_player, draw_enemy,
    COIN_W, COIN_H, FLAG_W, FLAG_H,
    PLAYER_W, PLAYER_H, ENEMY_W, ENEMY_H,
)


def _collide_x(rect, tiles):
    """Разрешить коллизии по X. Возвращает True если заблокирован."""
    blocked = False
    for t in tiles:
        if rect.colliderect(t.rect):
            if rect.centerx > t.rect.centerx:
                rect.left = t.rect.right
            else:
                rect.right = t.rect.left
            blocked = True
    return blocked


def _collide_y(rect, vy, tiles):
    """Разрешить коллизии по Y. Возвращает (on_ground, hit_ceil)."""
    on_ground = False
    hit_ceil  = False
    for t in tiles:
        if rect.colliderect(t.rect):
            if vy >= 0:
                rect.bottom = t.rect.top
                on_ground   = True
            else:
                rect.top  = t.rect.bottom
                hit_ceil  = True
    return on_ground, hit_ceil


# ──────────────────────────────────────────────────────────
class Tile(pygame.sprite.Sprite):
    def __init__(self, x, y, kind='ground'):
        super().__init__()
        self.image = pygame.Surface((TILE, TILE), pygame.SRCALPHA)
        if kind == 'ground':
            draw_ground_tile(self.image)
        else:
            draw_stone_tile(self.image)
        self.rect = self.image.get_rect(topleft=(x, y))


# ──────────────────────────────────────────────────────────
class Coin(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.base_y = y + TILE // 2
        self.frame  = 0
        self.anim_t = 0
        self.image  = pygame.Surface((COIN_W, COIN_H), pygame.SRCALPHA)
        self._refresh()
        self.rect = self.image.get_rect(center=(x + TILE // 2, self.base_y))

    def _refresh(self):
        draw_coin(self.image, self.frame)

    def update(self):
        import math
        self.anim_t += 1
        if self.anim_t % 8 == 0:
            self.frame = (self.frame + 1) % 4
            self._refresh()
        self.rect.centery = self.base_y + int(s(4) * math.sin(self.anim_t * 0.08))


# ──────────────────────────────────────────────────────────
class Flag(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.frame  = 0
        self.anim_t = 0
        self.image  = pygame.Surface((FLAG_W, FLAG_H), pygame.SRCALPHA)
        draw_flag(self.image, 0)
        self.rect = self.image.get_rect(bottomleft=(x, y + TILE))

    def update(self):
        self.anim_t += 1
        if self.anim_t % 10 == 0:
            self.frame = (self.frame + 1) % 4
            self.image.fill((0, 0, 0, 0))
            draw_flag(self.image, self.frame)


# ──────────────────────────────────────────────────────────
class Enemy(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image      = pygame.Surface((ENEMY_W, ENEMY_H), pygame.SRCALPHA)
        self.walk_frame = 0
        self.anim_t     = 0
        draw_enemy(self.image, 0)
        self.rect = self.image.get_rect(bottomleft=(x, y + TILE))
        self.fx   = float(self.rect.x)
        self.fy   = float(self.rect.y)
        self.vx   = float(s(2))
        self.vy   = 0.0
        self.on_ground = False

    def _refresh(self):
        self.image.fill((0, 0, 0, 0))
        draw_enemy(self.image, self.walk_frame)

    def update(self, tiles):
        self.anim_t += 1
        if self.anim_t % 12 == 0:
            self.walk_frame = (self.walk_frame + 1) % 2
            self._refresh()

        self.vy = min(self.vy + GRAVITY, MAX_FALL)

        # X
        self.fx    += self.vx
        self.rect.x = round(self.fx)
        if _collide_x(self.rect, tiles):
            self.fx  = float(self.rect.x)
            self.vx  = -self.vx

        # Y
        self.fy    += self.vy
        self.rect.y = round(self.fy)
        on_ground, hit_ceil = _collide_y(self.rect, self.vy, tiles)
        self.on_ground = on_ground
        if on_ground or hit_ceil:
            self.vy = 0.0
            self.fy = float(self.rect.y)

        # разворот на краю
        if self.on_ground:
            check = pygame.Rect(
                self.rect.left + int(self.vx),
                self.rect.bottom + 2,
                self.rect.width, 4
            )
            if not any(check.colliderect(t.rect) for t in tiles):
                self.vx = -self.vx


# ──────────────────────────────────────────────────────────
class Player(pygame.sprite.Sprite):
    def __init__(self, x, y):
        super().__init__()
        self.image = pygame.Surface((PLAYER_W, PLAYER_H), pygame.SRCALPHA)
        self.rect  = self.image.get_rect(topleft=(x, y))
        self.fx    = float(x)
        self.fy    = float(y)
        self.vx    = 0.0
        self.vy    = 0.0
        self.on_ground   = False
        self.facing      = 1
        self.walk_frame  = 0
        self.anim_t      = 0
        self._touch_dir  = 0
        self._touch_jump = False
        self._refresh()

    def _refresh(self, walking=False):
        draw_player(self.image, self.walk_frame if walking else 0, self.facing)

    def update(self, tiles):
        keys = pygame.key.get_pressed()
        kb   = int(keys[pygame.K_RIGHT]) - int(keys[pygame.K_LEFT])
        move = self._touch_dir if self._touch_dir != 0 else kb
        jump = keys[pygame.K_SPACE] or keys[pygame.K_UP] or self._touch_jump

        # анимация
        if move != 0:
            self.facing  = move
            self.anim_t += 1
            if self.anim_t % 7 == 0:
                self.walk_frame = (self.walk_frame + 1) % 4
            self._refresh(walking=True)
        else:
            self.anim_t = 0
            self._refresh(walking=False)

        self.vx = float(move * PLAYER_SPEED)
        if jump and self.on_ground:
            self.vy = float(JUMP_FORCE)
        self.vy = min(self.vy + GRAVITY, MAX_FALL)

        # X
        self.fx    += self.vx
        self.rect.x = round(self.fx)
        if _collide_x(self.rect, tiles):
            self.fx = float(self.rect.x)
            self.vx = 0.0

        # Y
        self.fy    += self.vy
        self.rect.y = round(self.fy)
        on_ground, hit_ceil = _collide_y(self.rect, self.vy, tiles)
        self.on_ground = on_ground
        if on_ground or hit_ceil:
            self.vy = 0.0
            self.fy = float(self.rect.y)
