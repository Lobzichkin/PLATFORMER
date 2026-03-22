"""
ПЛАТФОРМЕР — точка входа
Структура проекта:
  main.py        — запуск, главный цикл
  game.py        — GameSession: логика, загрузка уровней, рисование мира
  sprites.py     — Tile, Coin, Flag, Enemy, Player
  draw_utils.py  — пиксельная отрисовка спрайтов
  camera.py      — Camera (горизонтальный скроллинг)
  ui.py          — HUD, touch-кнопки, оверлеи, меню, фон
  levels.py      — карты уровней
  settings.py    — константы, цвета, шрифты
"""

import sys
import pygame
from settings import SW, SH, FPS
from game    import GameSession
from ui      import (
    draw_background, draw_hud,
    draw_state_overlay, menu_screen,
)


def handle_advance_events(session, events):
    """Обрабатывает нажатия для продолжения на экранах оверлея."""
    for e in events:
        if e.type == pygame.KEYDOWN:
            if e.key in (pygame.K_SPACE, pygame.K_RETURN):
                session.advance()
                return
        if e.type in (pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
            session.advance()
            return


def main():
    screen = pygame.display.set_mode((SW, SH), pygame.FULLSCREEN)
    pygame.display.set_caption("Платформер")
    clock  = pygame.time.Clock()

    menu_screen(screen, clock, FPS)

    session = GameSession()

    while True:
        clock.tick(FPS)
        events = pygame.event.get()

        # ── системные события ──
        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        # ── логика ──
        session.update()

        # ── продолжение при оверлеях ──
        if session.state != "play":
            handle_advance_events(session, events)

        # ── рисование ──
        screen.fill((92, 148, 252))          # очищаем экран каждый кадр
        draw_background(screen, session.camera.offset_x)
        session.draw(screen)
        draw_hud(screen, session.lives, session.total_coins,
                 session.level_idx)
        if session.state != "play":
            extra = ""
            if session.state == "win":
                extra = f"Монет: {session.collected}  —  SPACE продолжить"
            draw_state_overlay(screen, session.state, extra)

        pygame.display.flip()


if __name__ == "__main__":
    main()
