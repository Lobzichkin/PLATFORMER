import pygame
pygame.init()

# ── Экран ──────────────────────────────────────────────────
INFO = pygame.display.Info()
SW   = INFO.current_w
SH   = INFO.current_h

SCALE = SH / 480
def s(x): return int(x * SCALE)

# ── Тайл и физика ─────────────────────────────────────────
TILE          = s(32)
FPS           = 60
GRAVITY       = 0.55 * SCALE
JUMP_FORCE    = -13  * SCALE
PLAYER_SPEED  = 3.8  * SCALE
MAX_FALL      = 18   * SCALE

# ── Цвета (пиксель-палитра) ───────────────────────────────
C_SKY_TOP    = (92,  148, 252)
C_SKY_BOT    = (160, 210, 255)
C_CLOUD      = (240, 248, 255)
C_SUN        = (255, 230,  60)

C_GRASS_TOP  = ( 80, 180,  60)
C_GRASS_MID  = ( 56, 140,  40)
C_DIRT       = (140,  90,  40)
C_DIRT_DARK  = (100,  60,  20)
C_STONE      = (140, 140, 150)
C_STONE_DARK = ( 90,  90, 100)

C_COIN       = (255, 210,  30)
C_COIN_IN    = (200, 160,   0)
C_FLAG_POLE  = ( 60,  60,  60)
C_FLAG       = (255,  80,  30)

C_PLAYER_SKIN= (255, 198, 130)
C_PLAYER_CAP = (220,  40,  40)
C_PLAYER_EYE = ( 30,  30,  30)
C_PLAYER_BODY= ( 50, 110, 220)
C_PLAYER_LEG = ( 30,  30,  80)
C_PLAYER_SHOE= ( 20,  10,   0)

C_ENEMY_BODY = (220,  50,  50)
C_ENEMY_DARK = (160,  20,  20)
C_ENEMY_EYE  = (255, 255, 255)
C_ENEMY_PUP  = ( 10,  10,  10)
C_ENEMY_FEET = ( 80,  20,  20)

C_WHITE      = (255, 255, 255)
C_BLACK      = (  0,   0,   0)
C_DARK       = ( 25,  20,  30)
C_GRAY       = (140, 140, 140)
C_YELLOW     = (255, 220,  50)
C_RED        = (220,  40,  40)
C_ORANGE     = (255, 140,   0)

# ── Touch-кнопки ──────────────────────────────────────────
BW  = s(88)
BH  = s(52)
PAD = s(14)
BTN_LEFT_RECT  = (PAD,            SH - BH - PAD, BW, BH)
BTN_RIGHT_RECT = (PAD*2 + BW,     SH - BH - PAD, BW, BH)
BTN_JUMP_RECT  = (SW - BW - PAD,  SH - BH - PAD, BW, BH)

# ── Шрифты ───────────────────────────────────────────────
def get_fonts():
    return {
        "big": pygame.font.SysFont(None, int(SH * 0.08)),
        "med": pygame.font.SysFont(None, int(SH * 0.05)),
        "sm":  pygame.font.SysFont(None, int(SH * 0.035)),
    }

# ── Игровые константы ─────────────────────────────────────
PLAYER_LIVES = 3
NUM_LEVELS   = 3