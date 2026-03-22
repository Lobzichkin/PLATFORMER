"""
Утилиты для пиксельной отрисовки спрайтов.
Все функции рисуют на переданном Surface.
"""
import pygame
from settings import s, TILE
from settings import (
    C_GRASS_TOP, C_GRASS_MID, C_DIRT, C_DIRT_DARK,
    C_STONE, C_STONE_DARK,
    C_COIN, C_COIN_IN,
    C_FLAG_POLE, C_FLAG,
    C_PLAYER_SKIN, C_PLAYER_CAP, C_PLAYER_EYE,
    C_PLAYER_BODY, C_PLAYER_LEG, C_PLAYER_SHOE,
    C_ENEMY_BODY, C_ENEMY_DARK, C_ENEMY_EYE,
    C_ENEMY_PUP, C_ENEMY_FEET,
    C_WHITE, C_BLACK,
)


def _r(surf, color, x, y, w, h):
    """Shortcut: рисуем пиксельный прямоугольник."""
    pygame.draw.rect(surf, color, (x, y, w, h))


# ── ТАЙЛ ЗЕМЛИ ────────────────────────────────────────────
def draw_ground_tile(surf):
    """Трава + земля — пиксельный стиль."""
    W, H = surf.get_size()
    _r(surf, C_GRASS_TOP,  0,       0,      W, s(7))
    _r(surf, C_GRASS_MID,  0,       s(7),   W, s(5))
    _r(surf, C_DIRT,       0,       s(12),  W, H - s(12) - s(6))
    _r(surf, C_DIRT_DARK,  0,       H - s(6), W, s(6))
    # точки текстуры грунта
    for dy in range(s(14), H - s(8), s(8)):
        for dx in range(s(4), W - s(4), s(9)):
            _r(surf, C_DIRT_DARK, dx, dy, s(2), s(2))


# ── ТАЙЛ КАМНЯ ────────────────────────────────────────────
def draw_stone_tile(surf):
    W, H = surf.get_size()
    _r(surf, C_STONE,      0, 0, W, H)
    _r(surf, C_STONE_DARK, 0, 0, W, s(3))          # верхняя линия
    _r(surf, C_STONE_DARK, 0, 0, s(3), H)          # левая линия
    _r(surf, C_WHITE,      s(3), s(3), W-s(6), s(2))  # блик
    # крестообразный шов
    _r(surf, C_STONE_DARK, W//2 - s(1), 0,   s(2), H)
    _r(surf, C_STONE_DARK, 0,  H//2 - s(1), W,     s(2))


# ── МОНЕТА ────────────────────────────────────────────────
COIN_W = s(14)
COIN_H = s(14)

def draw_coin(surf, frame: int):
    """frame 0-3 — анимация вращения."""
    surf.fill((0, 0, 0, 0))
    W, H = COIN_W, COIN_H
    cx, cy = W // 2, H // 2
    # ширина монеты меняется по фазе (имитация вращения)
    phases = [W, W * 3 // 4, W // 5, W * 3 // 4]
    pw = max(2, phases[frame % 4])
    pygame.draw.ellipse(surf, C_COIN,    (cx - pw//2, cy - H//2 + s(1), pw, H - s(2)))
    pygame.draw.ellipse(surf, C_COIN_IN, (cx - pw//4, cy - H//4,        pw//2, H//2))
    # блик
    if pw > s(4):
        _r(surf, C_WHITE, cx - pw//2 + s(1), cy - H//2 + s(2), s(2), s(3))


# ── ФЛАГ ──────────────────────────────────────────────────
FLAG_W = s(24)
FLAG_H = s(52)

def draw_flag(surf, wave: int):
    surf.fill((0, 0, 0, 0))
    # шест
    _r(surf, C_FLAG_POLE, FLAG_W//2 - s(2), 0, s(4), FLAG_H)
    # флажок (3 горизонтальные полосы — «волна»)
    offsets = [0, s(2), s(1), -s(1)][wave % 4]
    pts = [
        (FLAG_W//2 + s(2),         s(4)),
        (FLAG_W//2 + s(2),         s(22)),
        (FLAG_W - s(2) + offsets,  s(13)),
    ]
    pygame.draw.polygon(surf, C_FLAG, pts)
    pygame.draw.polygon(surf, (200, 50, 0), pts, s(1))


# ── ИГРОК ─────────────────────────────────────────────────
PLAYER_W = s(26)
PLAYER_H = s(38)

def draw_player(surf, walk_frame: int, facing: int):
    """facing: 1 = вправо, -1 = влево."""
    surf.fill((0, 0, 0, 0))
    W, H = PLAYER_W, PLAYER_H

    # ── голова ──
    head_x = W // 2 - s(9)
    _r(surf, C_PLAYER_SKIN, head_x,        s(4),  s(18), s(16))
    # кепка
    _r(surf, C_PLAYER_CAP,  head_x - s(2), s(2),  s(22), s(8))
    _r(surf, C_PLAYER_CAP,  head_x,        0,     s(14), s(4))
    # козырёк
    _r(surf, C_PLAYER_CAP,  head_x + s(14), s(6), s(6),  s(3))
    # глаза
    eye_x = head_x + (s(11) if facing >= 0 else s(3))
    _r(surf, C_PLAYER_EYE, eye_x, s(10), s(4), s(4))
    # ус
    mus_x = head_x + (s(7) if facing >= 0 else s(2))
    _r(surf, C_BLACK, mus_x, s(15), s(8), s(2))

    # ── тело ──
    _r(surf, C_PLAYER_BODY, W//2 - s(9), s(20), s(18), s(12))
    # ремень/пуговица
    _r(surf, C_BLACK, W//2 - s(2), s(28), s(4), s(2))

    # ── ноги (анимация) ──
    leg_frames = [(0, 0), (s(3), -s(3)), (-s(3), s(3)), (0, 0)]
    loff, roff = leg_frames[walk_frame % 4]
    # левая нога
    _r(surf, C_PLAYER_LEG,  W//2 - s(9), s(32) + loff, s(8),  s(6))
    _r(surf, C_PLAYER_SHOE, W//2 - s(9), s(38) + loff, s(9),  s(3))
    # правая нога
    _r(surf, C_PLAYER_LEG,  W//2 + s(1), s(32) + roff, s(8),  s(6))
    _r(surf, C_PLAYER_SHOE, W//2 + s(1), s(38) + roff, s(9),  s(3))

    if facing == -1:
        # зеркалим по горизонтали
        flipped = pygame.transform.flip(surf.copy(), True, False)
        surf.blit(flipped, (0, 0))


# ── ВРАГ ──────────────────────────────────────────────────
ENEMY_W = s(28)
ENEMY_H = s(26)

def draw_enemy(surf, walk_frame: int):
    surf.fill((0, 0, 0, 0))
    W, H = ENEMY_W, ENEMY_H

    # тело — трапеция (гриб-стиль)
    body_pts = [
        (s(2),  H),
        (W-s(2), H),
        (W,      H//2),
        (0,      H//2),
    ]
    pygame.draw.polygon(surf, C_ENEMY_DARK, body_pts)
    _r(surf, C_ENEMY_BODY, s(2), H//2, W - s(4), H//2 - s(2))

    # голова — большой полукруг сверху
    pygame.draw.ellipse(surf, C_ENEMY_BODY, (0, 0, W, H))
    # тёмная нижняя часть головы
    _r(surf, C_ENEMY_DARK, 0, H//2, W, s(4))

    # глаза
    for ex in (W//2 - s(8), W//2 + s(2)):
        pygame.draw.ellipse(surf, C_ENEMY_EYE, (ex, s(6), s(8), s(8)))
        pygame.draw.ellipse(surf, C_ENEMY_PUP, (ex+s(2), s(8), s(4), s(4)))

    # ножки
    foot_frames = [(0, s(3)), (s(3), 0)]
    fl, fr = foot_frames[walk_frame % 2]
    _r(surf, C_ENEMY_FEET, W//2 - s(9), H - s(2) + fl, s(8), s(4))
    _r(surf, C_ENEMY_FEET, W//2 + s(1), H - s(2) + fr, s(8), s(4))
