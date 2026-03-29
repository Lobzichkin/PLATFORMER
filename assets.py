"""
assets.py — завантаження зображень та звуків.

Структура папок (створюється автоматично):
  assets/
    images/
      player/
        idle.png        — стоїть (або spritesheet_idle.png)
        walk_0.png      — крок 1
        walk_1.png      — крок 2
        walk_2.png      — крок 3
        walk_3.png      — крок 4
        jump.png        — стрибок
        dead.png        — смерть
      enemy/
        walk_0.png
        walk_1.png
      coin/
        spin_0.png … spin_3.png
      flag/
        wave_0.png … wave_3.png
      tiles/
        ground.png
        stone.png
      background/
        bg.png          — фонове зображення (опційно)
    sounds/
      jump.wav          — стрибок
      coin.wav          — збір монети
      enemy_stomp.wav   — вбивство ворога
      hurt.wav          — гравець отримав удар
      level_win.wav     — рівень пройдено
      gameover.wav      — кінець гри
      music.mp3         — фонова музика (опційно)

Якщо файл не знайдено — використовується піксельна графіка / порожній звук.
"""

import os
import pygame
from settings import TILE, PLAYER_W, PLAYER_H, ENEMY_W, ENEMY_H, COIN_W, COIN_H, FLAG_W, FLAG_H

ASSETS_DIR  = os.path.join(os.path.dirname(__file__), "assets")
IMAGES_DIR  = os.path.join(ASSETS_DIR, "images")
SOUNDS_DIR  = os.path.join(ASSETS_DIR, "sounds")

# ── Створюємо папки якщо не існують ──────────────────────
def _ensure_dirs():
    for d in [
        ASSETS_DIR, IMAGES_DIR, SOUNDS_DIR,
        os.path.join(IMAGES_DIR, "player"),
        os.path.join(IMAGES_DIR, "enemy"),
        os.path.join(IMAGES_DIR, "coin"),
        os.path.join(IMAGES_DIR, "flag"),
        os.path.join(IMAGES_DIR, "tiles"),
        os.path.join(IMAGES_DIR, "background"),
    ]:
        os.makedirs(d, exist_ok=True)

_ensure_dirs()


# ─────────────────────────────────────────────────────────
#  ЗОБРАЖЕННЯ
# ─────────────────────────────────────────────────────────

def _load_image(rel_path: str, size: tuple | None = None) -> pygame.Surface | None:
    """Завантажує зображення. Повертає None якщо файл не існує."""
    path = os.path.join(IMAGES_DIR, rel_path)
    if not os.path.isfile(path):
        return None
    try:
        img = pygame.image.load(path).convert_alpha()
        if size:
            img = pygame.transform.scale(img, size)
        return img
    except Exception as e:
        print(f"[assets] Помилка завантаження {rel_path}: {e}")
        return None


def _load_sequence(folder: str, prefix: str, count: int,
                   size: tuple | None = None) -> list[pygame.Surface | None]:
    """Завантажує серію зображень: prefix_0.png, prefix_1.png ..."""
    return [_load_image(f"{folder}/{prefix}_{i}.png", size) for i in range(count)]


# ── Гравець ──────────────────────────────────────────────
class PlayerImages:
    def __init__(self):
        sz = (PLAYER_W, PLAYER_H)
        self.idle  = _load_image("player/idle.png",  sz)
        self.walk  = _load_sequence("player", "walk", 4, sz)
        self.jump  = _load_image("player/jump.png",  sz)
        self.dead  = _load_image("player/dead.png",  sz)

    def has_any(self) -> bool:
        return any([
            self.idle,
            any(w for w in self.walk),
            self.jump,
            self.dead,
        ])

    def get_walk_frame(self, frame: int) -> pygame.Surface | None:
        imgs = [w for w in self.walk if w is not None]
        if not imgs:
            return self.idle
        return imgs[frame % len(imgs)]


# ── Ворог ─────────────────────────────────────────────────
class EnemyImages:
    def __init__(self):
        sz = (ENEMY_W, ENEMY_H)
        self.walk = _load_sequence("enemy", "walk", 2, sz)

    def has_any(self) -> bool:
        return any(w for w in self.walk)

    def get_walk_frame(self, frame: int) -> pygame.Surface | None:
        imgs = [w for w in self.walk if w is not None]
        if not imgs:
            return None
        return imgs[frame % len(imgs)]


# ── Монета ────────────────────────────────────────────────
class CoinImages:
    def __init__(self):
        sz = (COIN_W, COIN_H)
        self.spin = _load_sequence("coin", "spin", 4, sz)

    def has_any(self) -> bool:
        return any(s for s in self.spin)

    def get_frame(self, frame: int) -> pygame.Surface | None:
        imgs = [s for s in self.spin if s is not None]
        if not imgs:
            return None
        return imgs[frame % len(imgs)]


# ── Прапор ────────────────────────────────────────────────
class FlagImages:
    def __init__(self):
        sz = (FLAG_W, FLAG_H)
        self.wave = _load_sequence("flag", "wave", 4, sz)

    def has_any(self) -> bool:
        return any(w for w in self.wave)

    def get_frame(self, frame: int) -> pygame.Surface | None:
        imgs = [w for w in self.wave if w is not None]
        if not imgs:
            return None
        return imgs[frame % len(imgs)]


# ── Тайли ─────────────────────────────────────────────────
class TileImages:
    def __init__(self):
        sz = (TILE, TILE)
        self.ground = _load_image("tiles/ground.png", sz)
        self.stone  = _load_image("tiles/stone.png",  sz)


# ── Фон ───────────────────────────────────────────────────
class BackgroundImage:
    def __init__(self):
        from settings import SW, SH
        self.bg = _load_image("background/bg.png", (SW, SH))

    def has_any(self) -> bool:
        return self.bg is not None


# ─────────────────────────────────────────────────────────
#  ЗВУКИ
# ─────────────────────────────────────────────────────────

class SoundManager:
    def __init__(self):
        self._sounds: dict[str, pygame.mixer.Sound | None] = {}
        self._music_playing = False

        if not pygame.mixer.get_init():
            try:
                pygame.mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
            except Exception as e:
                print(f"[assets] Звук недоступний: {e}")
                return

        sound_files = {
            "jump":         "jump.wav",
            "coin":         "coin.wav",
            "enemy_stomp":  "enemy_stomp.wav",
            "hurt":         "hurt.wav",
            "level_win":    "level_win.wav",
            "gameover":     "gameover.wav",
        }
        for key, fname in sound_files.items():
            path = os.path.join(SOUNDS_DIR, fname)
            if os.path.isfile(path):
                try:
                    self._sounds[key] = pygame.mixer.Sound(path)
                    print(f"[assets] Звук завантажено: {fname}")
                except Exception as e:
                    print(f"[assets] Помилка звуку {fname}: {e}")
                    self._sounds[key] = None
            else:
                self._sounds[key] = None

        # Фонова музика
        music_path = os.path.join(SOUNDS_DIR, "music.mp3")
        if not os.path.isfile(music_path):
            music_path = os.path.join(SOUNDS_DIR, "music.wav")
        if os.path.isfile(music_path):
            try:
                pygame.mixer.music.load(music_path)
                pygame.mixer.music.set_volume(0.4)
                pygame.mixer.music.play(-1)  # -1 = петля
                self._music_playing = True
                print("[assets] Музика запущена")
            except Exception as e:
                print(f"[assets] Помилка музики: {e}")

    def play(self, name: str, volume: float = 1.0):
        snd = self._sounds.get(name)
        if snd:
            snd.set_volume(volume)
            snd.play()

    def stop_music(self):
        if self._music_playing:
            pygame.mixer.music.stop()

    def set_music_volume(self, vol: float):
        if self._music_playing:
            pygame.mixer.music.set_volume(vol)


# ─────────────────────────────────────────────────────────
#  ГЛОБАЛЬНИЙ МЕНЕДЖЕР (ініціалізується один раз)
# ─────────────────────────────────────────────────────────

_images_player     : PlayerImages     | None = None
_images_enemy      : EnemyImages      | None = None
_images_coin       : CoinImages       | None = None
_images_flag       : FlagImages       | None = None
_images_tiles      : TileImages       | None = None
_images_background : BackgroundImage  | None = None
_sound_manager     : SoundManager     | None = None


def init_assets():
    """Викликати один раз після pygame.init()."""
    global _images_player, _images_enemy, _images_coin
    global _images_flag, _images_tiles, _images_background, _sound_manager

    _images_player     = PlayerImages()
    _images_enemy      = EnemyImages()
    _images_coin       = CoinImages()
    _images_flag       = FlagImages()
    _images_tiles      = TileImages()
    _images_background = BackgroundImage()
    _sound_manager     = SoundManager()

    print("[assets] Ініціалізація завершена")
    if _images_player.has_any():
        print("[assets] Знайдено зображення гравця ✓")
    else:
        print("[assets] Зображення гравця не знайдено — використовується піксельна графіка")
    if _images_enemy.has_any():
        print("[assets] Знайдено зображення ворога ✓")
    if _images_coin.has_any():
        print("[assets] Знайдено зображення монети ✓")


def player_images()     -> PlayerImages:     return _images_player
def enemy_images()      -> EnemyImages:      return _images_enemy
def coin_images()       -> CoinImages:       return _images_coin
def flag_images()       -> FlagImages:       return _images_flag
def tile_images()       -> TileImages:       return _images_tiles
def background_image()  -> BackgroundImage:  return _images_background
def sounds()            -> SoundManager:     return _sound_manager
