
import sys
import pygame
from settings import SW, SH, FPS
from game    import GameSession
from assets  import init_assets
from ui      import (
    draw_background, draw_hud,
    draw_state_overlay, menu_screen,
)


def handle_advance_events(session, events):
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

    init_assets()

    menu_screen(screen, clock, FPS)

    session = GameSession()

    while True:
        clock.tick(FPS)
        events = pygame.event.get()

        for e in events:
            if e.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                pygame.quit(); sys.exit()

        session.update()

        if session.state != "play":
            prev = session.state
            handle_advance_events(session, events)
            if prev == "play" and session.state == "gameover":
                try:
                    from assets import sounds
                    sounds().play("gameover")
                except Exception:
                    pass

        screen.fill((92, 148, 252))
        draw_background(screen, session.camera.offset_x)
        session.draw(screen)
        draw_hud(screen, session.lives, session.total_coins,
                 session.level_idx)
        if session.state != "play":
            extra = ""
            if session.state == "win":
                extra = f"Монет: {session.collected}  —  SPACE далі"
            draw_state_overlay(screen, session.state, extra)

        pygame.display.flip()


if __name__ == "__main__":
    main()
