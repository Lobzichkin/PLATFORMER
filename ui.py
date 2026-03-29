import math
import pygame
from settings import (
    s, SW, SH, get_fonts,
    C_SKY_TOP, C_SKY_BOT, C_CLOUD, C_SUN,
    C_WHITE, C_DARK, C_GRAY,
    C_RED, C_YELLOW, C_ORANGE,
    BTN_LEFT_RECT, BTN_RIGHT_RECT, BTN_JUMP_RECT,
)

_fonts = None
def fonts():
    global _fonts
    if _fonts is None:
        _fonts = get_fonts()
    return _fonts


_bg_surf = None

def _make_bg():
    global _bg_surf
    _bg_surf = pygame.Surface((SW, SH))
    for y in range(SH):
        t = y / SH
        r = int(C_SKY_TOP[0] + (C_SKY_BOT[0] - C_SKY_TOP[0]) * t)
        g = int(C_SKY_TOP[1] + (C_SKY_BOT[1] - C_SKY_TOP[1]) * t)
        b = int(C_SKY_TOP[2] + (C_SKY_BOT[2] - C_SKY_TOP[2]) * t)
        pygame.draw.line(_bg_surf, (r, g, b), (0, y), (SW, y))
    pygame.draw.circle(_bg_surf, C_SUN, (SW - s(70), s(55)), s(28))
    pygame.draw.circle(_bg_surf, (255, 245, 150), (SW - s(70), s(55)), s(22))
    clouds = [(s(80), s(60)), (s(280), s(40)), (s(520), s(70)),
              (s(750), s(45)), (s(1000), s(60))]
    for cx, cy in clouds:
        for dx, dy, r in [( 0, 0, s(28)), (s(22), -s(10), s(20)),
                          (-s(18), -s(8), s(18)), (s(40), 0, s(22))]:
            pygame.draw.ellipse(_bg_surf, C_CLOUD,
                                (cx + dx - r, cy + dy - r//2, r*2, r))


def draw_background(surf, cam_offset_x=0):
    if _bg_surf is None:
        _make_bg()
    bx = -int(cam_offset_x * 0.3) % SW
    surf.blit(_bg_surf, (bx,    0))
    surf.blit(_bg_surf, (bx - SW, 0))


class TouchBtn:
    def __init__(self, rect, label, color):
        self.rect   = pygame.Rect(rect)
        self.label  = label
        self.color  = color
        self.active = False

    def handle(self, events):
        self.active = False
        for e in events:
            if e.type in (pygame.FINGERDOWN, pygame.FINGERMOTION):
                fx, fy = int(e.x * SW), int(e.y * SH)
                if self.rect.collidepoint(fx, fy):
                    self.active = True
            if e.type in (pygame.MOUSEBUTTONDOWN, pygame.MOUSEMOTION):
                if pygame.mouse.get_pressed()[0]:
                    if self.rect.collidepoint(pygame.mouse.get_pos()):
                        self.active = True

    def draw(self, surf):
        col = tuple(min(255, c + 55) for c in self.color) if self.active else self.color
        r   = self.rect
        pygame.draw.rect(surf, C_DARK,
                         (r.x + s(3), r.y + s(3), r.w, r.h),
                         border_radius=s(8))
        pygame.draw.rect(surf, col, r, border_radius=s(8))
        pygame.draw.rect(surf, C_WHITE, r, s(2), border_radius=s(8))
        txt = fonts()["med"].render(self.label, True, C_WHITE)
        surf.blit(txt, txt.get_rect(center=r.center))


btn_left  = TouchBtn(BTN_LEFT_RECT,  "◀", (50,  50, 170))
btn_right = TouchBtn(BTN_RIGHT_RECT, "▶", (50,  50, 170))
btn_jump  = TouchBtn(BTN_JUMP_RECT,  "▲", (50, 160,  50))


def update_touch(events):
    btn_left.handle(events)
    btn_right.handle(events)
    btn_jump.handle(events)
    direction = (1 if btn_right.active else 0) - (1 if btn_left.active else 0)
    return direction, btn_jump.active


def draw_touch_buttons(surf):
    btn_left.draw(surf)
    btn_right.draw(surf)
    btn_jump.draw(surf)


def draw_hud(surf, lives, total_coins, level_idx):
    bar = pygame.Surface((SW, s(30)), pygame.SRCALPHA)
    bar.fill((0, 0, 0, 80))
    surf.blit(bar, (0, 0))
    txt = fonts()["sm"].render(
        f"❤ {lives}   🪙 {total_coins}   Рівень {level_idx + 1}",
        True, C_WHITE)
    surf.blit(txt, (s(10), s(6)))


def draw_overlay(surf, title, subtitle, color):
    ov = pygame.Surface((SW, SH), pygame.SRCALPHA)
    ov.fill((0, 0, 0, 170))
    surf.blit(ov, (0, 0))
    box_w, box_h = s(480), s(140)
    box = pygame.Rect((SW - box_w)//2, (SH - box_h)//2, box_w, box_h)
    pygame.draw.rect(surf, C_DARK,  box, border_radius=s(16))
    pygame.draw.rect(surf, color,   box, s(4), border_radius=s(16))
    t1 = fonts()["big"].render(title,    True, color)
    t2 = fonts()["med"].render(subtitle, True, C_WHITE)
    surf.blit(t1, t1.get_rect(center=(SW//2, box.centery - s(24))))
    surf.blit(t2, t2.get_rect(center=(SW//2, box.centery + s(28))))


def menu_screen(surf, clock, fps):
    t = 0
    while True:
        t += 1
        draw_background(surf, t * 0.5)

        for col, off in [(C_DARK, s(4)), (C_YELLOW, 0)]:
            tx = fonts()["big"].render("ПЛАТФОРМЕР", True, col)
            surf.blit(tx, tx.get_rect(center=(SW//2 + off, SH//2 - s(60) + off)))

        if (t // 30) % 2 == 0:
            t2 = fonts()["med"].render("Натисни екран або ENTER", True, C_WHITE)
            surf.blit(t2, t2.get_rect(center=(SW//2, SH//2 + s(10))))

        t3 = fonts()["sm"].render(
            "← → рух   ↑ / SPACE стрибок   ESC вихід", True, C_WHITE)
        surf.blit(t3, t3.get_rect(center=(SW//2, SH//2 + s(60))))

        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT:
                pygame.quit(); raise SystemExit
            if e.type in (pygame.KEYDOWN, pygame.FINGERDOWN, pygame.MOUSEBUTTONDOWN):
                return
        clock.tick(fps)


OVERLAYS = {
    "dead":     ("ВИ ЗАГИНУЛИ",      "SPACE / tap — продовжити",     C_RED),
    "win":      ("РІВЕНЬ ПРОЙДЕНО!", "SPACE / tap — далі",           C_YELLOW),
    "gameover": ("ГРА ЗАКІНЧЕНА",    "SPACE / tap — почати знову",   C_GRAY),
    "complete": ("ВИ ПЕРЕМОГЛИ! 🎉", "SPACE / tap — у меню",        C_ORANGE),
}

def draw_state_overlay(surf, state, extra=""):
    if state not in OVERLAYS:
        return
    title, sub, color = OVERLAYS[state]
    draw_overlay(surf, title, extra or sub, color)
