import math
import random
import time

import pygame

from quests import QuestLog
from world import generate, solid, W, H, COLORS
from npc import Npc
import storage

pygame.init()
pygame.display.set_caption("Quester")

TILE = 14
VIEW_W, VIEW_H = 800, H * TILE
LEFT_W = 340
MARGIN = 14
WIN_W = LEFT_W + VIEW_W + MARGIN * 3
WIN_H = 690

screen = pygame.display.set_mode((WIN_W, WIN_H))
clock = pygame.time.Clock()

font = pygame.font.Font(None, 22)
font_small = pygame.font.Font(None, 18)
font_big = pygame.font.Font(None, 50)
font_title = pygame.font.Font(None, 34)

BG = (28, 24, 36)
PANEL = (40, 35, 51)
LINE = (65, 57, 77)
TEXT = (240, 235, 247)
MUTED = (165, 157, 179)
ACCENT = (240, 192, 80)
GREEN = (108, 192, 74)
SKY_TOP = (111, 177, 224)
SKY_BOT = (191, 225, 244)

TOOLS = [
    (1, "Dirt", (122, 74, 43)),
    (2, "Stone", (104, 109, 120)),
    (3, "Wood", (168, 116, 58)),
    (4, "Brick", (164, 67, 47)),
    (5, "Torch", (240, 160, 48)),
    (0, "Break", (201, 196, 211)),
]


def load_state():
    data = storage.load()
    if data:
        ql = QuestLog.from_dict(data["quests"])
        world = data["world"]
        npcs = [Npc.from_dict(n) for n in data.get("npcs", [])]
        pts = data.get("pts", 0)
        awarded = data.get("awarded", 0)
    else:
        ql = QuestLog()
        world = generate()
        npcs = []
        pts = 0
        awarded = 0
    return ql, world, npcs, pts, awarded


def save_state():
    storage.save({
        "quests": quest_log.to_dict(),
        "world": world,
        "npcs": [n.to_dict() for n in npcs],
        "pts": pts,
        "awarded": awarded,
    })


quest_log, world, npcs, pts, awarded = load_state()
camera_x = 0
tool = 1
status_msg = ""
input_text = ""
input_active = False


def is_solid(x, y):
    return solid(world, x, y)


def sync_level():
    global pts, awarded, status_msg
    lvl = quest_log.level()
    if lvl <= awarded:
        return
    gained = (lvl - awarded) * 5
    msg = f"Level {lvl}! +{gained} blocks to build with."
    for lv in range(awarded + 1, lvl + 1):
        if lv % 10 == 0:
            n = Npc(random.uniform(3, W - 4))
            npcs.append(n)
            msg = f"Level {lv}! {n.name} the {n.role} moved into your world."
    pts += gained
    awarded = lvl
    status_msg = msg


sync_level()

world_rect = pygame.Rect(LEFT_W + MARGIN * 2, 70, VIEW_W, VIEW_H)
max_camera = W - VIEW_W // TILE
input_rect = pygame.Rect(14, 132, 230, 28)
add_rect = pygame.Rect(250, 132, 76, 28)
preview_rect = pygame.Rect(14, 415, LEFT_W - 28, 26)


def draw_text(surf, text, pos, f=font, color=TEXT):
    surf.blit(f.render(text, True, color), pos)


def button(surf, rect, label, active=False, f=font_small):
    pygame.draw.rect(surf, ACCENT if active else PANEL, rect)
    pygame.draw.rect(surf, LINE, rect, 2)
    tw, th = f.size(label)
    surf.blit(f.render(label, True, (30, 24, 18) if active else TEXT),
              (rect.x + (rect.w - tw) // 2, rect.y + (rect.h - th) // 2))


running = True
quest_rows = []
tool_rows = []

while running:
    dt = clock.tick(60) / 1000
    t = time.time()

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if input_active:
                if event.key == pygame.K_RETURN:
                    quest_log.add(input_text)
                    input_text = ""
                    save_state()
                elif event.key == pygame.K_BACKSPACE:
                    input_text = input_text[:-1]
                elif event.key == pygame.K_ESCAPE:
                    input_active = False
                elif event.unicode.isprintable() and len(input_text) < 80:
                    input_text += event.unicode
            else:
                if event.key == pygame.K_LEFT:
                    camera_x = max(0, camera_x - 1)
                elif event.key == pygame.K_RIGHT:
                    camera_x = min(max_camera, camera_x + 1)
                elif pygame.K_1 <= event.key <= pygame.K_5:
                    idx = event.key - pygame.K_1
                    if idx < len(TOOLS):
                        tool = TOOLS[idx][0]

        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            mx, my = event.pos
            if input_rect.collidepoint(mx, my):
                input_active = True
            elif add_rect.collidepoint(mx, my):
                quest_log.add(input_text)
                input_text = ""
                save_state()
            else:
                input_active = False
                for c_rect, d_rect, q in quest_rows:
                    if c_rect and c_rect.collidepoint(mx, my):
                        quest_log.complete(q)
                        sync_level()
                        save_state()
                    elif d_rect and d_rect.collidepoint(mx, my):
                        quest_log.remove(q)
                        save_state()
                for rect, tid in tool_rows:
                    if rect.collidepoint(mx, my):
                        tool = tid
                if preview_rect.collidepoint(mx, my):
                    quest_log.bonus += 10
                    sync_level()
                    save_state()
                if world_rect.collidepoint(mx, my) and quest_log.level() >= 1:
                    wx = camera_x + (mx - world_rect.x) // TILE
                    wy = (my - world_rect.y) // TILE
                    clicked_npc = None
                    for n in npcs:
                        sx = world_rect.x + (n.x - camera_x) * TILE
                        sy = world_rect.y + (H - 1 - n.y) * TILE + TILE
                        if sx - 10 < mx < sx + 10 and sy - 40 < my < sy + 5:
                            clicked_npc = n
                            break
                    if clicked_npc:
                        clicked_npc.speak()
                    elif 0 <= wx < W and 0 <= wy < H:
                        cur = world[wy][wx]
                        if tool == 0:
                            if cur:
                                if cur >= 10:
                                    pts += 1
                                world[wy][wx] = 0
                                save_state()
                        elif not cur:
                            if pts < 1:
                                status_msg = "Out of blocks. Complete a quest to earn 5 more."
                            else:
                                pts -= 1
                                world[wy][wx] = tool + 10
                                save_state()

    if quest_log.level() >= 1:
        for n in npcs:
            n.update(dt, is_solid, W, H)

    # ---------------- draw ----------------
    screen.fill(BG)

    # left panel
    pygame.draw.rect(screen, PANEL, (0, 0, LEFT_W, WIN_H))
    draw_text(screen, "Quester", (14, 10), font_title, ACCENT)
    draw_text(screen, "Finish quests. Level up. Build a world.", (14, 46), font_small, MUTED)

    lvl = quest_log.level()
    draw_text(screen, str(lvl), (14, 64), font_big, ACCENT)
    lw, _ = font_big.size(str(lvl))
    draw_text(screen, "level", (14 + lw + 8, 86), font_small, MUTED)

    bar_rect = pygame.Rect(14, 108, LEFT_W - 28, 10)
    pygame.draw.rect(screen, LINE, bar_rect, 2)
    fill_w = int((bar_rect.w - 4) * ((lvl % 10) / 10))
    pygame.draw.rect(screen, GREEN, (bar_rect.x + 2, bar_rect.y + 2, fill_w, bar_rect.h - 4))
    draw_text(screen, f"{10 - lvl % 10} level(s) to next villager", (14, 122), font_small, MUTED)

    pygame.draw.rect(screen, BG, input_rect)
    pygame.draw.rect(screen, ACCENT if input_active else LINE, input_rect, 2)
    placeholder = "Type a quest, press Enter"
    shown = input_text if (input_text or input_active) else placeholder
    draw_text(screen, shown[:32], (input_rect.x + 6, input_rect.y + 6), font_small,
              TEXT if input_text else MUTED)
    button(screen, add_rect, "Add")

    quest_rows = []
    qy = 172
    for q in sorted(quest_log.quests, key=lambda q: q.done):
        if qy > 400:
            break
        color = MUTED if q.done else TEXT
        label = ("[x] " if q.done else "[ ] ") + q.text
        draw_text(screen, label[:34], (14, qy), font_small, color)
        c_rect = d_rect = None
        if not q.done:
            c_rect = pygame.Rect(LEFT_W - 96, qy - 2, 50, 22)
            d_rect = pygame.Rect(LEFT_W - 40, qy - 2, 22, 22)
            button(screen, c_rect, "Done")
            button(screen, d_rect, "X")
        quest_rows.append((c_rect, d_rect, q))
        qy += 26
    if not quest_log.quests:
        draw_text(screen, "No quests yet. Add one above.", (14, qy), font_small, MUTED)

    button(screen, preview_rect, "Preview: +10 levels")

    draw_text(screen, "Villagers", (14, 455), font, ACCENT)
    ry = 480
    if not npcs:
        draw_text(screen, "No one lives here yet.", (14, ry), font_small, MUTED)
    for n in npcs:
        if ry > WIN_H - 20:
            break
        pygame.draw.rect(screen, n.shirt, (14, ry + 2, 12, 12))
        draw_text(screen, f"{n.name} the {n.role}", (32, ry), font_small, TEXT)
        ry += 20

    # world panel
    if lvl < 1:
        pygame.draw.rect(screen, (20, 16, 30), world_rect)
        msg = "Complete your first quest to unlock your world."
        words, line, lines = msg.split(), "", []
        for w_ in words:
            test = (line + " " + w_).strip()
            if font.size(test)[0] > world_rect.w - 40:
                lines.append(line)
                line = w_
            else:
                line = test
        lines.append(line)
        for i, ln in enumerate(lines):
            tw, _ = font.size(ln)
            draw_text(screen, ln, (world_rect.centerx - tw // 2, world_rect.centery - 20 + i * 24), font, TEXT)
    else:
        for yy in range(world_rect.h):
            ratio = yy / world_rect.h
            col = tuple(int(SKY_TOP[i] + (SKY_BOT[i] - SKY_TOP[i]) * ratio) for i in range(3))
            pygame.draw.line(screen, col, (world_rect.x, world_rect.y + yy), (world_rect.right, world_rect.y + yy))

        cam_tile = int(camera_x)
        visible = VIEW_W // TILE + 2
        for ty in range(H):
            for tx in range(cam_tile, min(W, cam_tile + visible)):
                v = world[ty][tx]
                if not v:
                    continue
                b = v % 10
                sx = world_rect.x + (tx - camera_x) * TILE
                sy = world_rect.y + ty * TILE
                if b == 5:
                    pygame.draw.rect(screen, (107, 74, 43), (sx + 6, sy + 6, 2, 8))
                    flick = 2 if int(t * 8) % 2 == 0 else 0
                    pygame.draw.circle(screen, (255, 140, 26), (sx + 7, sy + 4 - flick), 4)
                    pygame.draw.circle(screen, (255, 220, 140), (sx + 7, sy + 3 - flick), 2)
                else:
                    base = COLORS.get(b, (120, 120, 120))
                    rnd = ((tx * 73856093) ^ (ty * 19349663)) & 0xFF
                    shade = (rnd % 12) - 6
                    col = tuple(max(0, min(255, c + shade)) for c in base)
                    pygame.draw.rect(screen, col, (sx, sy, TILE, TILE))
                    pygame.draw.rect(screen, (25, 20, 30), (sx, sy, TILE, TILE), 1)
                    if b == 1 and (ty == 0 or world[ty - 1][tx] % 10 not in (1, 2, 3, 4, 7)):
                        pygame.draw.rect(screen, (95, 168, 58), (sx, sy, TILE, 3))

        for n in npcs:
            sx = world_rect.x + (n.x - camera_x) * TILE
            sy = world_rect.y + (H - 1 - n.y) * TILE + TILE
            bob = math.sin(t * 8) * 2 if n.vx else 0
            pygame.draw.rect(screen, (58, 51, 80), (sx - 4, sy - 16 + bob, 8, 8))
            pygame.draw.rect(screen, n.shirt, (sx - 5, sy - 24 + bob, 10, 8))
            pygame.draw.rect(screen, n.skin, (sx - 4, sy - 32 + bob, 8, 8))
            pygame.draw.rect(screen, n.hair, (sx - 5, sy - 34 + bob, 10, 3))
            tw, _ = font_small.size(n.name)
            draw_text(screen, n.name, (sx - tw // 2, sy - 48 + bob), font_small, TEXT)
            if n.say and t < n.say_until:
                bw = min(220, font_small.size(n.say)[0] + 16)
                bx = max(world_rect.x, min(world_rect.right - bw, sx - bw // 2))
                pygame.draw.rect(screen, (255, 255, 255), (bx, sy - 74 + bob, bw, 22))
                pygame.draw.rect(screen, LINE, (bx, sy - 74 + bob, bw, 22), 2)
                draw_text(screen, n.say[:40], (bx + 8, sy - 69 + bob), font_small, (36, 31, 46))

    tool_rows = []
    tx0, ty0 = world_rect.x, world_rect.bottom + 10
    for i, (tid, label, color) in enumerate(TOOLS):
        rect = pygame.Rect(tx0 + i * 108, ty0, 100, 30)
        pygame.draw.rect(screen, color, (rect.x + 4, rect.y + 8, 14, 14))
        button(screen, rect, label, active=(tool == tid))
        tool_rows.append((rect, tid))
    draw_text(screen, f"{pts} blocks left", (tx0 + len(TOOLS) * 108 + 10, ty0 + 6), font_small, ACCENT)

    draw_text(screen, status_msg, (tx0, ty0 + 40), font_small, MUTED)
    draw_text(screen, "Arrows: scroll  |  1-5: pick tool  |  Click: build / break / talk",
              (tx0, ty0 + 62), font_small, MUTED)

    pygame.display.flip()

pygame.quit()