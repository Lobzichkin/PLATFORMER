"""
Процедурная генерация уровней.
Каждый вызов get_level_map(idx) возвращает уникальную карту,
сложность растёт с номером уровня.
"""
import random

# Размеры карты (в тайлах)
ROWS = 11        # строк (последняя — земля)
MIN_COLS = 55    # минимальная ширина
MAX_COLS = 80    # максимальная ширина


def generate_level(seed: int, difficulty: int) -> list[str]:
    """
    seed       — зерно для воспроизводимости конкретного уровня
    difficulty — 0..N, влияет на количество врагов и ям
    """
    rng  = random.Random(seed)
    cols = rng.randint(MIN_COLS, MAX_COLS)
    diff = min(difficulty, 10)   # капуем сложность

    # ── Параметры сложности ──────────────────────────────
    gap_chance    = 0.06 + diff * 0.012   # вероятность ямы в земле
    plat_count    = rng.randint(6, 10 + diff)
    enemy_count   = rng.randint(diff, 3 + diff * 2)
    coin_count    = rng.randint(5, 12)

    # ── Сетка: rows × cols  (всё — пробелы) ─────────────
    grid = [[' '] * cols for _ in range(ROWS)]

    # ── Земля (последняя строка) с ямами ─────────────────
    ground_row = ROWS - 1
    # первые 3 и последние 3 колонки всегда земля (старт/финиш)
    for c in range(cols):
        if c < 3 or c >= cols - 3:
            grid[ground_row][c] = 'G'
        elif rng.random() > gap_chance:
            grid[ground_row][c] = 'G'
        # иначе — яма (пробел)

    # ── Платформы ─────────────────────────────────────────
    platforms = []   # список (row, col_start, length)
    attempts  = 0
    placed    = 0
    while placed < plat_count and attempts < 200:
        attempts += 1
        length  = rng.randint(3, 8)
        row     = rng.randint(ROWS - 5, ROWS - 3)   # строки 6-8
        col     = rng.randint(3, cols - length - 3)

        # проверяем что не перекрываем другую платформу
        overlap = any(
            r == row and not (col + length <= cs or col >= cs + ln)
            for r, cs, ln in platforms
        )
        if overlap:
            continue

        for c in range(col, col + length):
            grid[row][c] = '#'
        platforms.append((row, col, length))
        placed += 1

    # ── Враги на платформах и земле ───────────────────────
    enemy_spots = []
    # на земле
    for c in range(5, cols - 5):
        if grid[ground_row][c] == 'G' and grid[ground_row - 1][c] == ' ':
            enemy_spots.append((ground_row - 1, c))
    # на платформах
    for row, cs, ln in platforms:
        if ln >= 2:
            for c in range(cs, cs + ln):
                if grid[row - 1][c] == ' ':
                    enemy_spots.append((row - 1, c))

    rng.shuffle(enemy_spots)
    for i in range(min(enemy_count, len(enemy_spots))):
        r, c = enemy_spots[i]
        grid[r][c] = 'E'

    # ── Монеты над платформами и землёй ───────────────────
    coin_spots = []
    for row, cs, ln in platforms:
        for c in range(cs, cs + ln):
            if grid[row - 1][c] == ' ':
                coin_spots.append((row - 1, c))
    # монеты над землёй (где нет врагов)
    for c in range(3, cols - 3):
        if grid[ground_row][c] == 'G' and grid[ground_row - 1][c] == ' ':
            coin_spots.append((ground_row - 1, c))

    rng.shuffle(coin_spots)
    placed_coins = 0
    for r, c in coin_spots:
        if grid[r][c] == ' ':
            grid[r][c] = 'C'
            placed_coins += 1
            if placed_coins >= coin_count:
                break

    # ── Флаг — правый край, на самой высокой платформе ───
    # ищем платформу ближайшую к правому краю
    right_plats = sorted(platforms, key=lambda p: -(p[1] + p[2]))
    if right_plats:
        fr, fc, fl = right_plats[0]
        flag_c = fc + fl - 1
        flag_r = fr - 1
        # убедимся что выше флага пусто
        for rr in range(max(0, flag_r - 2), flag_r + 1):
            grid[rr][flag_c] = ' '
        grid[flag_r][flag_c] = 'F'
    else:
        # fallback — правый верхний угол
        grid[1][cols - 4] = 'F'

    # ── Конвертируем в список строк ───────────────────────
    return [''.join(row) for row in grid]


# ── Кэш чтобы не перегенерировать при каждом вызове ──────
_cache: dict[int, list[str]] = {}


def get_level_map(idx: int) -> list[str]:
    """Возвращает карту уровня. Одинаковый idx → одинаковая карта."""
    if idx not in _cache:
        # seed зависит от номера уровня — каждый уровень уникален,
        # но воспроизводим в рамках одного запуска
        seed = idx * 31337 + 42
        diff = idx          # сложность = номер уровня
        _cache[idx] = generate_level(seed, diff)
    return _cache[idx]


def new_random_level(idx: int) -> list[str]:
    """Генерирует новую случайную карту для idx (игнорирует кэш)."""
    import time
    seed = int(time.time() * 1000) ^ (idx * 999)
    diff = idx
    result = generate_level(seed, diff)
    _cache[idx] = result
    return result


def level_pixel_width(idx: int) -> int:
    from settings import TILE
    return max(len(r) for r in get_level_map(idx)) * TILE


def count_coins(idx: int) -> int:
    return sum(row.count('C') for row in get_level_map(idx))
