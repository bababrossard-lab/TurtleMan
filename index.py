import pygame
import sys
import random
import math
import json
import os

pygame.init()

W, H       = 800, 600
CELL       = 40
COLS       = W // CELL
ROWS       = H // CELL
FPS        = 60
MOVE_DELAY = 175  # ms entre chaque déplacement de la tortue (vitesse réduite)

NAVY       = (4,  44,  83)
BLUE1      = (12, 68, 124)
BLUE2      = (24, 95, 165)
BLUE3      = (55, 138, 221)
WHITE      = (255, 255, 255)
GREEN      = (50,  200,  80)
DARK_GREEN = (20,  120,  40)
YELLOW     = (255, 230,  50)
ORANGE     = (255, 140,   0)
RED        = (220,  50,  50)
GREY       = (180, 180, 200)
BLACK      = (0,    0,    0)
PINK       = (255, 150, 180)
CORAL      = (255, 100,  80)
GOLD       = (255, 210,  90)
PLASTIC_COL     = (210, 230, 255)
PLASTIC_SCARED  = (100, 180, 100)
PLASTIC_OUTLINE = (150, 170, 200)

screen = pygame.display.set_mode((W, H))
pygame.display.set_caption("Tortue Marine - Stop a la pollution !")
clock  = pygame.time.Clock()

font_big   = pygame.font.SysFont("Arial", 44, bold=True)
font_med   = pygame.font.SysFont("Arial", 26, bold=True)
font_small = pygame.font.SysFont("Arial", 17)
font_tiny  = pygame.font.SysFont("Arial", 14)

# ── Sauvegarde locale (classement + comptes joueurs) ───────────────────────────
try:
    SAVE_DIR = os.path.dirname(os.path.abspath(__file__))
except NameError:
    # __file__ n'existe pas si le script est lancé depuis IDLE/un interpréteur interactif
    SAVE_DIR = os.getcwd()
SAVE_FILE = os.path.join(SAVE_DIR, "turtle_save.json")

def load_save_data():
    if os.path.exists(SAVE_FILE):
        try:
            with open(SAVE_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                data.setdefault("leaderboard", [])
                data.setdefault("players", {})
                return data
        except Exception:
            pass
    return {"leaderboard": [], "players": {}}

def save_save_data():
    try:
        with open(SAVE_FILE, "w", encoding="utf-8") as f:
            json.dump(SAVE_DATA, f, ensure_ascii=False, indent=2)
    except Exception:
        pass

SAVE_DATA = load_save_data()

def get_player(name):
    p = SAVE_DATA["players"].setdefault(name, {})
    p.setdefault("money", 0)
    p.setdefault("owned_skins", ["classique"])
    p.setdefault("equipped_skin", "classique")
    p.setdefault("best_score", 0)
    return p

def add_to_leaderboard(name, score):
    SAVE_DATA["leaderboard"].append({"name": name, "score": score})
    SAVE_DATA["leaderboard"].sort(key=lambda x: x["score"], reverse=True)
    SAVE_DATA["leaderboard"] = SAVE_DATA["leaderboard"][:10]
    save_save_data()

# ── Skins ───────────────────────────────────────────────────────────────────
SKINS = {
    "classique": {
        "label": "Caouanne (classique)", "price": 0,
        "shell_dark": (80, 60, 20), "shell_med": (120, 90, 30), "shell_light": (160, 130, 50),
        "skin": (100, 130, 80), "skin_light": (140, 170, 100),
    },
    "verte": {
        "label": "Tortue Verte", "price": 200,
        "shell_dark": (20, 70, 30), "shell_med": (40, 110, 50), "shell_light": (90, 170, 90),
        "skin": (60, 140, 90), "skin_light": (110, 190, 130),
    },
    "luth": {
        "label": "Tortue Luth", "price": 500,
        "shell_dark": (10, 10, 25), "shell_med": (25, 25, 55), "shell_light": (70, 70, 120),
        "skin": (30, 30, 60), "skin_light": (80, 90, 140),
    },
    "doree": {
        "label": "Tortue Dorée", "price": 1000,
        "shell_dark": (140, 100, 10), "shell_med": (200, 160, 30), "shell_light": (255, 220, 110),
        "skin": (210, 170, 60), "skin_light": (255, 220, 140),
    },
    "dauphin": {
        "label": "Dauphin (legendaire)", "price": 3000,
        "shell_dark": (60, 80, 100), "shell_med": (100, 130, 155), "shell_light": (190, 210, 225),
        "skin": (100, 130, 155), "skin_light": (190, 210, 225),
    },
}
SKIN_ORDER = ["classique", "verte", "luth", "doree", "dauphin"]

MAZE_LEVEL_1 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,2,2,1],
    [1,3,1,1,2,1,1,2,1,1,1,1,2,1,1,2,1,1,3,1],
    [1,2,1,0,2,2,2,2,2,0,0,2,2,2,2,2,0,1,2,1],
    [1,2,1,1,2,1,0,1,1,1,1,1,1,0,1,2,1,1,2,1],
    [1,2,2,2,2,1,2,2,2,0,0,2,2,2,1,2,2,2,2,1],
    [1,1,1,2,1,1,2,1,0,0,0,0,1,2,1,1,2,1,1,1],
    [2,2,2,2,2,2,3,1,0,0,0,0,1,2,2,2,2,2,2,2],
    [1,1,1,2,1,1,2,1,1,1,1,1,1,2,1,1,2,1,1,1],
    [1,2,2,2,2,1,2,2,2,0,0,2,2,2,1,2,2,2,2,1],
    [1,2,1,1,2,1,2,1,1,1,1,1,1,2,1,2,1,1,2,1],
    [1,3,1,0,2,2,2,2,2,0,0,2,2,2,2,2,0,1,3,1],
    [1,2,2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,2,2,1],
    [1,1,1,1,2,1,1,1,2,1,1,1,1,1,1,1,2,1,1,1],
    [1,2,2,3,2,2,1,2,2,2,2,2,2,1,2,2,2,2,2,1],
]

MAZE_LEVEL_2 = [
    [1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1,1],
    [1,2,2,1,2,2,2,2,1,2,2,2,2,2,2,1,2,2,2,1],
    [1,2,2,1,2,1,1,2,1,2,1,2,1,1,2,1,2,2,3,1],
    [1,2,2,2,2,1,2,2,2,2,2,2,2,2,2,2,2,2,2,1],
    [1,1,2,1,1,1,2,1,1,0,0,1,1,2,1,1,1,2,1,1],
    [1,3,2,2,2,1,2,1,0,0,0,0,1,2,1,2,2,2,3,1],
    [1,1,1,2,2,1,2,1,0,0,0,0,1,2,1,2,2,1,1,1],
    [2,2,2,2,2,2,2,1,0,0,0,0,1,2,2,2,2,2,2,2],
    [1,1,1,2,1,2,2,1,1,1,1,1,1,2,1,1,2,1,2,1],
    [1,2,2,2,1,2,2,2,2,2,2,2,2,2,1,2,2,2,2,1],
    [1,2,1,2,1,1,2,1,1,2,1,1,2,1,1,2,1,2,1,1],
    [1,2,1,2,2,2,2,1,2,2,2,1,2,2,2,2,1,2,1,1],
    [1,3,1,1,1,2,1,1,2,1,2,1,1,2,1,1,1,2,3,1],
    [1,2,1,1,2,2,2,1,2,1,2,1,2,2,2,1,1,1,2,1],
    [1,2,2,2,2,1,2,3,2,2,2,2,2,1,2,2,2,2,2,1],
]

LEVELS = [
    {
        'name':       'Récif de pierre',
        'maze':       MAZE_LEVEL_1,
        'wall_main':  (12, 68, 124),
        'wall_edge':  (24, 95, 165),
        'wall_dot':   (55, 138, 221),
        'bg_top':     (4,  44,  83),
        'bg_bottom':  (24, 95, 165),
    },
    {
        'name':       'Récif de corail',
        'maze':       MAZE_LEVEL_2,
        'wall_main':  (200, 70,  60),
        'wall_edge':  (255, 120, 90),
        'wall_dot':   (255, 190, 160),
        'bg_top':     (50,  10,  35),
        'bg_bottom':  (120, 35,  55),
    },
]
TUNNEL_ROW = 7


# ── Bulle ─────────────────────────────────────────────────────────────────────
class Bubble:
    def __init__(self):
        self.reset(random.randint(0, W), random.randint(0, H))
    def reset(self, x=None, y=None):
        self.x     = x if x is not None else random.randint(0, W)
        self.y     = y if y is not None else H + 5
        self.r     = random.randint(2, 8)
        self.spd   = random.uniform(0.4, 1.2)
        self.alpha = random.randint(40, 110)
    def update(self):
        self.y -= self.spd
        if self.y < -10:
            self.reset()
    def draw(self, surf):
        s = pygame.Surface((self.r*2+2, self.r*2+2), pygame.SRCALPHA)
        pygame.draw.circle(s, (200,230,255,self.alpha), (self.r+1,self.r+1), self.r)
        pygame.draw.circle(s, (255,255,255,70), (self.r,self.r), max(1,self.r//3))
        surf.blit(s, (int(self.x-self.r), int(self.y-self.r)))

bubbles = [Bubble() for _ in range(30)]

# ── Tortue réaliste ───────────────────────────────────────────────────────────
def draw_turtle(surf, cx, cy, direction, frame, skin_id="classique"):
    """Tortue marine réaliste orientée selon la direction."""
    skin = SKINS.get(skin_id, SKINS["classique"])
    t = frame * 0.08
    flipper_wave = math.sin(t) * 12

    C_SHELL_DARK  = skin["shell_dark"]
    C_SHELL_MED   = skin["shell_med"]
    C_SHELL_LIGHT = skin["shell_light"]
    C_SKIN        = skin["skin"]
    C_SKIN_LIGHT  = skin["skin_light"]
    C_PLASTRON    = (200, 185, 130)
    C_EYE         = (20,  20,  20)
    C_EYE_SHINE   = (255, 255, 255)
    C_SCALE       = (70,  100, 55)

    angle_map = {(1,0): 0, (-1,0): 180, (0,-1): 90, (0,1): 270}
    angle = angle_map.get(direction, 0)

    SIZE = 48
    tmp = pygame.Surface((SIZE*2, SIZE*2), pygame.SRCALPHA)
    ox, oy = SIZE, SIZE

    tail_pts = [
        (ox - 7,  oy),
        (ox - 18, oy - 3),
        (ox - 20, oy),
        (ox - 18, oy + 3),
    ]
    pygame.draw.polygon(tmp, C_SKIN, tail_pts)

    pygame.draw.ellipse(tmp, C_PLASTRON, (ox-12, oy-9, 24, 18))

    shell_rect = pygame.Rect(ox-13, oy-10, 26, 20)
    pygame.draw.ellipse(tmp, C_SHELL_MED, shell_rect)

    vert_pts = [
        (ox,    oy-10),
        (ox+4,  oy-7),
        (ox+3,  oy+8),
        (ox,    oy+10),
        (ox-3,  oy+8),
        (ox-4,  oy-7),
    ]
    pygame.draw.polygon(tmp, C_SHELL_DARK, vert_pts)
    pygame.draw.polygon(tmp, C_SHELL_LIGHT, vert_pts, 1)

    for i, (dy_off, w, h) in enumerate([(-7, 7, 6), (0, 8, 6), (6, 6, 5)]):
        for side in [-1, 1]:
            rx = ox + side * 7
            ry = oy + dy_off
            pts = [
                (rx,         ry - h//2),
                (rx + side*w, ry - h//3),
                (rx + side*w, ry + h//3),
                (rx,         ry + h//2),
            ]
            pygame.draw.polygon(tmp, C_SHELL_DARK, pts)
            pygame.draw.polygon(tmp, C_SHELL_LIGHT, pts, 1)

    pygame.draw.ellipse(tmp, C_SHELL_DARK, shell_rect, 2)

    for side in [-1, 1]:
        fa = math.radians(flipper_wave * side)
        base_x = ox + side * 10
        base_y = oy - 4
        tip_x  = ox + side * (22 + math.cos(fa) * 4)
        tip_y  = oy - 8 + math.sin(fa) * 8
        pts = [
            (base_x,          base_y),
            (base_x + side*2, base_y + 5),
            (tip_x,           tip_y + 6),
            (tip_x + side*4,  tip_y + 2),
            (tip_x,           tip_y - 2),
            (base_x + side*2, base_y - 4),
        ]
        pygame.draw.polygon(tmp, C_SKIN, pts)
        pygame.draw.ellipse(tmp, C_SCALE,
                            (base_x + side*4 - 3, base_y - 2, 6, 4))
        pygame.draw.polygon(tmp, C_SKIN_LIGHT, pts, 1)

    for side in [-1, 1]:
        fb = math.radians(-flipper_wave * side * 0.5)
        bx = ox - 8 + side * 9
        by = oy + 4
        pts = [
            (bx,          by),
            (bx + side*2, by + 4),
            (bx + side*(12 + math.cos(fb)*2), by + 5 + math.sin(fb)*4),
            (bx + side*12, by),
            (bx + side*8,  by - 3),
        ]
        pygame.draw.polygon(tmp, C_SKIN, pts)
        pygame.draw.polygon(tmp, C_SKIN_LIGHT, pts, 1)

    hx, hy = ox + 15, oy
    pygame.draw.ellipse(tmp, C_SKIN, (hx - 4, hy - 4, 8, 8))
    pygame.draw.ellipse(tmp, C_SKIN,       (hx + 2, hy - 7, 16, 14))
    pygame.draw.ellipse(tmp, C_SKIN_LIGHT, (hx + 3, hy - 6, 14, 12))
    pygame.draw.ellipse(tmp, C_SHELL_MED, (hx + 3, hy - 6, 10, 7))
    pygame.draw.circle(tmp, C_SHELL_DARK, (hx + 16, hy - 2), 2)
    pygame.draw.circle(tmp, C_SHELL_DARK, (hx + 16, hy + 2), 2)
    pygame.draw.circle(tmp, C_EYE,       (hx + 7,  hy - 3), 3)
    pygame.draw.circle(tmp, (60,80,40),   (hx + 7,  hy - 3), 2)
    pygame.draw.circle(tmp, C_EYE_SHINE, (hx + 8,  hy - 4), 1)
    pygame.draw.line(tmp, C_SHELL_DARK, (hx + 10, hy + 3), (hx + 17, hy + 2), 1)

    rotated = pygame.transform.rotate(tmp, angle)
    rx = cx - rotated.get_width()  // 2
    ry = cy - rotated.get_height() // 2
    surf.blit(rotated, (rx, ry))

# ── Dauphin (skin légendaire, forme totalement différente) ────────────────────
def draw_dolphin(surf, cx, cy, direction, frame):
    t = frame * 0.1

    C_BODY_DARK  = (55, 75, 95)
    C_BODY_MED   = (100, 130, 155)
    C_BODY_LIGHT = (190, 210, 225)
    C_BELLY      = (230, 240, 245)
    C_EYE        = (20, 20, 20)

    angle_map = {(1,0): 0, (-1,0): 180, (0,-1): 90, (0,1): 270}
    angle = angle_map.get(direction, 0)

    SIZE = 48
    tmp = pygame.Surface((SIZE*2, SIZE*2), pygame.SRCALPHA)
    ox, oy = SIZE, SIZE

    tail_wag = math.sin(t * 1.6) * 7
    tail_pts = [
        (ox-14, oy),
        (ox-26, oy-9+tail_wag*0.3),
        (ox-31, oy-2+tail_wag),
        (ox-21, oy),
        (ox-31, oy+2-tail_wag),
        (ox-26, oy+9-tail_wag*0.3),
    ]
    pygame.draw.polygon(tmp, C_BODY_DARK, tail_pts)
    pygame.draw.line(tmp, C_BODY_DARK, (ox-14,oy), (ox-2,oy), 4)

    body_rect = pygame.Rect(ox-16, oy-9, 32, 17)
    pygame.draw.ellipse(tmp, C_BODY_DARK, body_rect)
    belly_rect = pygame.Rect(ox-13, oy-1, 27, 9)
    pygame.draw.ellipse(tmp, C_BELLY, belly_rect)

    dfin = [(ox-1, oy-9), (ox+3, oy-23), (ox+9, oy-8)]
    pygame.draw.polygon(tmp, C_BODY_DARK, dfin)

    pfin_wag = math.sin(t*2.2) * 5
    pfin = [(ox+3, oy+3), (ox-3+pfin_wag*0.3, oy+17+pfin_wag), (ox+7, oy+9)]
    pygame.draw.polygon(tmp, C_BODY_MED, pfin)

    head_rect = pygame.Rect(ox+10, oy-6, 15, 12)
    pygame.draw.ellipse(tmp, C_BODY_MED, head_rect)
    beak = [(ox+22, oy-3), (ox+34, oy-1), (ox+34, oy+2), (ox+22, oy+4)]
    pygame.draw.polygon(tmp, C_BODY_MED, beak)
    pygame.draw.ellipse(tmp, C_BODY_LIGHT, (ox+11, oy-6, 9, 6))

    pygame.draw.circle(tmp, C_EYE, (ox+17, oy-2), 2)
    pygame.draw.circle(tmp, WHITE, (ox+18, oy-3), 1)
    pygame.draw.line(tmp, C_BODY_DARK, (ox+22, oy+3), (ox+33, oy+1), 1)

    rotated = pygame.transform.rotate(tmp, angle)
    rx = cx - rotated.get_width()  // 2
    ry = cy - rotated.get_height() // 2
    surf.blit(rotated, (rx, ry))

def draw_character(surf, cx, cy, direction, frame, skin_id="classique"):
    """Dispatche vers la bonne forme (tortue ou dauphin) selon le skin équipé."""
    if skin_id == "dauphin":
        draw_dolphin(surf, cx, cy, direction, frame)
    else:
        draw_turtle(surf, cx, cy, direction, frame, skin_id=skin_id)
def draw_plastic_bag(surf, cx, cy, frame, scared=False, dissolve=1.0):
    t    = frame * 0.07
    cy2  = cy

    col     = PLASTIC_SCARED if scared else PLASTIC_COL
    outline = (80,160,80) if scared else PLASTIC_OUTLINE
    alpha   = int(255 * dissolve)

    sac = pygame.Surface((38, 44), pygame.SRCALPHA)
    body_pts = [(4,14),(34,14),(30,38),(8,38)]
    pygame.draw.polygon(sac, (*col, alpha),     body_pts)
    pygame.draw.polygon(sac, (*outline, alpha), body_pts, 2)
    pygame.draw.arc(sac, (*outline, alpha), pygame.Rect(6,  4, 10, 16), 0, math.pi, 2)
    pygame.draw.arc(sac, (*outline, alpha), pygame.Rect(22, 4, 10, 16), 0, math.pi, 2)
    for px2 in [12, 19, 26]:
        pygame.draw.line(sac, (*outline, max(0, alpha-80)), (px2,16),(px2-1,36), 1)
    pygame.draw.line(sac, (255,255,255, max(0, alpha//2)), (10,18),(8,34), 2)
    if scared:
        br = int(3 + math.sin(t*2)*2)
        pygame.draw.circle(sac, (100,220,100, max(0,alpha-100)), (34,10), br)
    surf.blit(sac, (cx - 19, cy2 - 22))
    if not scared and dissolve > 0.7:
        lbl = pygame.font.SysFont("Arial", 7).render("plastique", True, (*PLASTIC_OUTLINE, alpha))
        surf.blit(lbl, (cx - lbl.get_width()//2, cy2 + 2))

# ── Méduse ──────────────────────────────────────────────────────────────────
def draw_jellyfish(surf, cx, cy, frame, dissolve=1.0):
    t     = frame * 0.1
    alpha = int(230 * dissolve)

    C_BELL       = (220, 130, 200)
    C_BELL_LIGHT = (255, 190, 235)
    C_TENTACLE   = (200, 110, 180)

    jf = pygame.Surface((40, 50), pygame.SRCALPHA)
    jx, jy = 20, 16

    for i in range(5):
        base_x = jx - 12 + i*6
        pts = [(base_x, jy + 6)]
        for s in range(1, 6):
            wave = math.sin(t + i + s*0.8) * 3
            pts.append((base_x + wave, jy + 6 + s*5))
        if len(pts) > 1:
            pygame.draw.lines(jf, (*C_TENTACLE, max(0,alpha-40)), False, pts, 2)

    pygame.draw.ellipse(jf, (*C_BELL, alpha), (jx-14, jy-12, 28, 22))
    pygame.draw.ellipse(jf, (*C_BELL_LIGHT, max(0,alpha-30)), (jx-10, jy-10, 14, 10))
    for i in range(6):
        bx = jx - 12 + i*5
        bob = math.sin(t*1.5 + i) * 2
        pygame.draw.circle(jf, (*C_BELL, alpha), (bx, jy+8+int(bob)), 3)

    surf.blit(jf, (cx - 20, cy - 16))

# ── Poisson ───────────────────────────────────────────────────────────────────
def draw_fish(surf, cx, cy, frame):
    bob = math.sin(frame * 0.1 + cx) * 2
    cy2 = int(cy + bob)
    pygame.draw.ellipse(surf, YELLOW,  (cx-7, cy2-5, 14, 10))
    pygame.draw.polygon(surf, ORANGE,  [(cx-7,cy2),(cx-14,cy2-5),(cx-14,cy2+5)])
    pygame.draw.circle(surf, BLACK,    (cx+3, cy2-1), 2)
    pygame.draw.circle(surf, WHITE,    (cx+4, cy2-2), 1)

# ── Étoile de mer ─────────────────────────────────────────────────────────────
def draw_starfish(surf, cx, cy, frame):
    ao   = frame * 0.03
    r_o, r_i = 11, 4
    pts  = []
    for i in range(10):
        angle = math.pi/2 + i*math.pi/5 + ao
        r     = r_o if i%2==0 else r_i
        pts.append((cx + r*math.cos(angle), cy + r*math.sin(angle)))
    pygame.draw.polygon(surf, CORAL, pts)
    pygame.draw.circle(surf, PINK,  (cx, cy), 3)

# ── Position pixel interpolée ─────────────────────────────────────────────────
def grid_to_px(gx, gy):
    return gx * CELL + CELL // 2, gy * CELL + CELL // 2

# ── Jeu ───────────────────────────────────────────────────────────────────────
class Game:
    def __init__(self, level_idx=0, player_name="Joueur"):
        self.level_idx   = level_idx
        self.player_name = player_name
        self.player      = get_player(player_name)
        self.loop_count  = 0
        self.game_over_recorded = False
        self.reset(keep_score=False)

    def reset(self, keep_score=True):
        prev_score = self.score if (keep_score and hasattr(self, 'score')) else 0
        prev_lives = self.lives if (keep_score and hasattr(self, 'lives')) else 3

        level = LEVELS[self.level_idx]
        maze  = level['maze']

        self.grid = []
        for r in range(ROWS):
            row = []
            for c in range(COLS):
                row.append(maze[r % len(maze)][c % len(maze[0])])
            self.grid.append(row)

        self.px, self.py       = 1, 1
        self.dx, self.dy       = 1, 0
        self.next_dx, self.next_dy = 1, 0

        self.rx, self.ry = float(grid_to_px(self.px, self.py)[0]), \
                           float(grid_to_px(self.px, self.py)[1])

        self.score              = prev_score
        self.lives              = prev_lives
        self.frame               = 0
        self.move_acc            = 0
        self.eco_active          = False
        self.eco_timer           = 0
        self.state               = 'playing'
        self.flash_timer         = 0
        self.invincible_timer    = 0
        self.particles           = []
        self.msg                 = ''
        self.msg_timer           = 0
        self.level_transition    = 0

        # La vitesse des sacs augmente légèrement à chaque boucle complète (niveau 2 -> niveau 1)
        BAG_SPEED  = max(180, 280 - self.loop_count * 15)
        CAGE_SPAWN = (9, 7)
        self.bags = [
            {'gx':9,  'gy':7,  'dx':1,  'dy':0,
             'rx': float(grid_to_px(9,7)[0]),  'ry': float(grid_to_px(9,7)[1]),
             'acc':0, 'dissolve':1.0, 'is_jellyfish':False, 'caged_timer':0},
            {'gx':10, 'gy':6,  'dx':0,  'dy':1,
             'rx': float(grid_to_px(10,6)[0]), 'ry': float(grid_to_px(10,6)[1]),
             'acc':random.randint(0,60), 'dissolve':1.0, 'is_jellyfish':False, 'caged_timer':0},
            {'gx':11, 'gy':8,  'dx':-1, 'dy':0,
             'rx': float(grid_to_px(11,8)[0]), 'ry': float(grid_to_px(11,8)[1]),
             'acc':random.randint(0,60), 'dissolve':1.0, 'is_jellyfish':False, 'caged_timer':0},
        ]
        self.BAG_SPEED  = BAG_SPEED
        self.CAGE_SPAWN = CAGE_SPAWN

        self.total_fish = sum(1 for r in self.grid for c in r if c == 2)

    # ── Helpers ───────────────────────────────────────────────────────────────
    def passable(self, gx, gy):
        if gy < 0 or gy >= ROWS:
            return False
        if gx < 0 or gx >= COLS:
            return gy == TUNNEL_ROW
        return self.grid[gy][gx] != 1

    def passable_turtle(self, gx, gy):
        if not self.passable(gx, gy):
            return False
        cage_gx, cage_gy = self.CAGE_SPAWN
        if cage_gy-1 <= gy <= cage_gy and cage_gx-1 <= gx <= cage_gx+2:
            return False
        return True

    def show_msg(self, text):
        self.msg, self.msg_timer = text, 90

    def next_level(self):
        self.level_idx += 1
        if self.level_idx >= len(LEVELS):
            self.level_idx = 0
            self.loop_count += 1
            self.show_msg("Nouveau tour, ca accelere !")
        self.reset(keep_score=True)

    def add_particles(self, cx, cy, color, n=10):
        for _ in range(n):
            a   = random.uniform(0, 2*math.pi)
            spd = random.uniform(1, 4)
            self.particles.append({
                'x':cx,'y':cy,
                'vx':math.cos(a)*spd,'vy':math.sin(a)*spd,
                'life':35,'color':color
            })

    # ── Déplacement tortue ────────────────────────────────────────────────────
    def move_turtle(self):
        nx, ny = self.px+self.next_dx, self.py+self.next_dy
        if self.passable_turtle(nx, ny):
            self.dx, self.dy = self.next_dx, self.next_dy
        nx, ny = self.px+self.dx, self.py+self.dy
        if self.passable_turtle(nx, ny):
            wrapped = nx < 0 or nx >= COLS
            self.px, self.py = nx % COLS if self.py == TUNNEL_ROW else nx, ny
            if wrapped and self.py == TUNNEL_ROW:
                self.rx = float(grid_to_px(self.px, self.py)[0])

    # ── Collecte ──────────────────────────────────────────────────────────────
    def collect(self):
        cell = self.grid[self.py][self.px]
        cx, cy = grid_to_px(self.px, self.py)
        if cell == 2:
            self.grid[self.py][self.px] = 0
            self.score      += 10
            self.total_fish -= 1
            self.add_particles(cx, cy, YELLOW, 8)
            if self.total_fish <= 0:
                # Le niveau est terminé : on boucle (niveau 2 -> niveau 1) tant qu'il reste des vies
                self.state = 'level_complete'
        elif cell == 3:
            self.grid[self.py][self.px] = 0
            self.score      += 50
            self.eco_active  = True
            self.eco_timer   = 300
            for bag in self.bags:
                bag['is_jellyfish'] = True
            self.add_particles(cx, cy, CORAL, 16)
            self.show_msg("Les sacs deviennent des meduses !")

    # ── Déplacement sac (chaque case, style Pac-Man) ─────────────────────────
    def choose_bag_dir(self, bag):
        dirs = [(1,0),(-1,0),(0,1),(0,-1)]
        random.shuffle(dirs)
        gx, gy = bag['gx'], bag['gy']

        if self.eco_active:
            best, best_d = None, -1
            for dx, dy in dirs:
                nx, ny = gx+dx, gy+dy
                if self.passable(nx, ny):
                    d = (nx-self.px)**2 + (ny-self.py)**2
                    if d > best_d:
                        best_d, best = d, (dx, dy)
        else:
            best, best_d = None, 9999
            for dx, dy in dirs:
                nx, ny = gx+dx, gy+dy
                if self.passable(nx, ny):
                    noise = random.uniform(0, 1.8)
                    d = abs(nx-self.px) + abs(ny-self.py) + noise
                    if d < best_d:
                        best_d, best = d, (dx, dy)

        return best if best else (bag['dx'], bag['dy'])

    def update_bag(self, bag, dt):
        if bag['caged_timer'] > 0:
            bag['caged_timer'] -= dt
            return

        bag['acc'] += dt
        speed = self.BAG_SPEED * (1.4 if self.eco_active else 1.0)

        tx, ty = grid_to_px(bag['gx'], bag['gy'])
        bag['rx'] += (tx - bag['rx']) * min(1.0, dt / max(1, speed - bag['acc'] + dt))
        bag['ry'] += (ty - bag['ry']) * min(1.0, dt / max(1, speed - bag['acc'] + dt))

        if bag['acc'] >= speed:
            bag['acc'] -= speed
            nx, ny = bag['gx'] + bag['dx'], bag['gy'] + bag['dy']
            if not self.passable(nx, ny):
                dx, dy = self.choose_bag_dir(bag)
                bag['dx'], bag['dy'] = dx, dy
                nx, ny = bag['gx'] + dx, bag['gy'] + dy
            if nx < 0 or nx >= COLS:
                nx %= COLS
                bag['rx'] = float(grid_to_px(nx, ny)[0])
            bag['gx'], bag['gy'] = nx, ny % ROWS
            dx, dy = self.choose_bag_dir(bag)
            bag['dx'], bag['dy'] = dx, dy

    # ── Collision ─────────────────────────────────────────────────────────────
    def check_collision(self):
        if self.invincible_timer > 0:
            return
        cx, cy = grid_to_px(self.px, self.py)
        for bag in self.bags:
            if bag['gx'] == self.px and bag['gy'] == self.py:
                if self.eco_active:
                    self.score += 300
                    self.add_particles(cx, cy, GREEN, 20)
                    bag['gx'], bag['gy'] = self.CAGE_SPAWN
                    bag['rx'], bag['ry'] = grid_to_px(*self.CAGE_SPAWN)
                    bag['is_jellyfish'] = False
                    bag['caged_timer']  = 420
                    self.show_msg("+300 Méduse recyclée !")
                else:
                    self.lives    -= 1
                    self.flash_timer = 70
                    self.invincible_timer = 90
                    self.add_particles(cx, cy, (200,200,255), 18)
                    self.show_msg("La tortue est piégée !")
                    if self.lives <= 0:
                        self.state = 'gameover'
                    else:
                        self.px, self.py = 1, 1
                        self.rx, self.ry = grid_to_px(1, 1)
                        self.dx, self.dy = 1, 0

    # ── Update ────────────────────────────────────────────────────────────────
    def update(self, dt):
        if self.state == 'gameover' and not self.game_over_recorded:
            self.game_over_recorded = True
            add_to_leaderboard(self.player_name, self.score)
            earned = self.score // 5   # 1 coquillage tous les 5 points (plus dur d'acheter des skins)
            self.player['money']      += earned
            self.player['best_score']  = max(self.player['best_score'], self.score)
            save_save_data()

        if self.state != 'playing':
            return

        self.frame += 1
        for b in bubbles:
            b.update()

        for p in self.particles:
            p['x'] += p['vx']; p['y'] += p['vy']; p['life'] -= 1
        self.particles = [p for p in self.particles if p['life'] > 0]

        if self.flash_timer > 0:
            self.flash_timer -= 1
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
        if self.msg_timer > 0:
            self.msg_timer -= 1

        if self.eco_active:
            self.eco_timer -= 1
            ratio = self.eco_timer / 300
            for bag in self.bags:
                bag['dissolve'] = max(0.3, ratio)
            if self.eco_timer <= 0:
                self.eco_active = False
                for bag in self.bags:
                    bag['dissolve']     = 1.0
                    bag['is_jellyfish'] = False

        self.move_acc += dt
        if self.move_acc >= MOVE_DELAY:
            self.move_acc -= MOVE_DELAY
            self.move_turtle()
            self.collect()
            self.check_collision()

        tx, ty = grid_to_px(self.px, self.py)
        lerp = 0.35
        self.rx += (tx - self.rx) * lerp
        self.ry += (ty - self.ry) * lerp

        for bag in self.bags:
            self.update_bag(bag, dt)

    # ── Dessin ────────────────────────────────────────────────────────────────
    def draw(self):
        level = LEVELS[self.level_idx]
        bg_top, bg_bottom = level['bg_top'], level['bg_bottom']
        wall_main, wall_edge, wall_dot = level['wall_main'], level['wall_edge'], level['wall_dot']

        for y in range(0, H, 4):
            t = y/H
            r = int(bg_top[0]+(bg_bottom[0]-bg_top[0])*t)
            g = int(bg_top[1]+(bg_bottom[1]-bg_top[1])*t)
            b = int(bg_top[2]+(bg_bottom[2]-bg_top[2])*t)
            pygame.draw.rect(screen, (r,g,b), (0,y,W,4))

        for b in bubbles:
            b.draw(screen)

        for gy in range(ROWS):
            for gx in range(COLS):
                cx = gx*CELL+CELL//2
                cy = gy*CELL+CELL//2
                cell = self.grid[gy][gx]
                if cell == 1:
                    rect = pygame.Rect(gx*CELL+1, gy*CELL+1, CELL-2, CELL-2)
                    pygame.draw.rect(screen, wall_main, rect, border_radius=6)
                    pygame.draw.rect(screen, wall_edge, rect, width=1, border_radius=6)
                    pygame.draw.circle(screen, wall_dot, (cx,cy), 4)
                    pygame.draw.circle(screen, wall_dot, (cx-8,cy-8), 3)
                    pygame.draw.circle(screen, wall_dot, (cx+8,cy+8), 3)
                elif cell == 2:
                    draw_fish(screen, cx, cy, self.frame)
                elif cell == 3:
                    draw_starfish(screen, cx, cy, self.frame)

        gate_gx, gate_gy = self.CAGE_SPAWN
        gate_x = gate_gx * CELL
        gate_y = (gate_gy - 1) * CELL + CELL - 4
        pygame.draw.rect(screen, wall_edge, (gate_x, gate_y, CELL*2, 5), border_radius=2)
        for i in range(5):
            bx = gate_x + 4 + i*((CELL*2-8)//4)
            pygame.draw.rect(screen, wall_main, (bx, gate_y-2, 3, 9))

        for p in self.particles:
            alpha = int(255 * p['life']/35)
            s = pygame.Surface((6,6), pygame.SRCALPHA)
            pygame.draw.circle(s, (*p['color'], alpha), (3,3), 3)
            screen.blit(s, (int(p['x'])-3, int(p['y'])-3))

        for bag in self.bags:
            if bag['is_jellyfish']:
                draw_jellyfish(screen, int(bag['rx']), int(bag['ry']),
                               self.frame, dissolve=bag['dissolve'])
            else:
                draw_plastic_bag(screen, int(bag['rx']), int(bag['ry']),
                                 self.frame, scared=self.eco_active,
                                 dissolve=bag['dissolve'])

        turtle_visible = self.flash_timer == 0 or self.flash_timer % 10 < 7
        if self.invincible_timer > 0:
            turtle_visible = (self.invincible_timer // 6) % 2 == 0
        if turtle_visible:
            draw_character(screen, int(self.rx), int(self.ry),
                        (self.dx, self.dy), self.frame,
                        skin_id=self.player.get('equipped_skin', 'classique'))

        self._draw_hud()

        if self.msg_timer > 0:
            t = font_small.render(self.msg, True, WHITE)
            s = pygame.Surface((t.get_width()+8, t.get_height()+4), pygame.SRCALPHA)
            pygame.draw.rect(s, (0,0,40,200), s.get_rect(), border_radius=6)
            s.blit(t, (4,2))
            screen.blit(s, (W//2-s.get_width()//2, H//2-60))

        if self.flash_timer > 0 and self.flash_timer % 10 < 5:
            ov = pygame.Surface((W,H), pygame.SRCALPHA)
            ov.fill((220,50,50,55))
            screen.blit(ov, (0,0))

        if self.state == 'gameover':
            self._overlay("GAME OVER", f"Score : {self.score}   +{self.score // 5} coquillages",
                          "La pollution a eu raison de la tortue…", RED)
        elif self.state == 'level_complete':
            next_name = LEVELS[(self.level_idx + 1) % len(LEVELS)]['name']
            self._overlay("NIVEAU TERMINE !", f"Score : {self.score}",
                          f"Niveau suivant : {next_name}", YELLOW,
                          button_text="ENTRÉE = continuer  |  ECHAP = quitter")

    def _draw_hud(self):
        t = font_med.render(f"Score : {self.score}", True, WHITE)
        screen.blit(t, (10,10))
        lvl_t = font_small.render(f"Niveau {self.level_idx+1} — {LEVELS[self.level_idx]['name']}", True, GREY)
        screen.blit(lvl_t, (10, 40))
        name_t = font_small.render(f"{self.player_name}   |   Coquillages : {self.player['money']}", True, GOLD)
        screen.blit(name_t, (10, 62))
        for i in range(self.lives):
            lx = W-40-i*35
            pygame.draw.circle(screen, GREEN, (lx, 22), 10)
            pygame.draw.circle(screen, DARK_GREEN, (lx, 22), 7)
        if self.eco_active:
            pct = self.eco_timer/300
            pygame.draw.rect(screen, (80,200,80),
                             (W//2-80, 8, int(160*pct), 12), border_radius=6)
            pygame.draw.rect(screen, WHITE,
                             (W//2-80, 8, 160, 12), width=1, border_radius=6)
            t = font_small.render("Eco-bouclier actif - sacs en dissolution !", True, (80,220,80))
            screen.blit(t, (W//2-t.get_width()//2, 22))
        t = font_small.render(f"Poissons restants : {self.total_fish}", True, YELLOW)
        screen.blit(t, (10, H-24))
        t2 = font_small.render("Évite les sacs plastiques — ils piègent les tortues !", True, PLASTIC_COL)
        screen.blit(t2, (W//2-t2.get_width()//2, H-24))

    def _overlay(self, title, sub, details, color, button_text="ENTRÉE = rejouer  |  ECHAP = quitter"):
        ov = pygame.Surface((W,H), pygame.SRCALPHA)
        ov.fill((0,0,40,185))
        screen.blit(ov, (0,0))
        t1 = font_big.render(title,   True, color)
        t2 = font_med.render(sub,     True, WHITE)
        t3 = font_small.render(details, True, GREY)
        t4 = font_small.render(button_text, True, GREY)
        screen.blit(t1, (W//2-t1.get_width()//2, H//2-80))
        screen.blit(t2, (W//2-t2.get_width()//2, H//2-20))
        screen.blit(t3, (W//2-t3.get_width()//2, H//2+20))
        screen.blit(t4, (W//2-t4.get_width()//2, H//2+60))


# ── Écran saisie du prénom ──────────────────────────────────────────────────
def draw_name_input(frame, name_buffer):
    screen.fill(NAVY)
    for b in bubbles:
        b.draw(screen); b.update()
    t1 = font_big.render("TORTUE MARINE", True, (100,220,255))
    screen.blit(t1, (W//2-t1.get_width()//2, 120))
    t2 = font_med.render("Quel est ton prénom ?", True, WHITE)
    screen.blit(t2, (W//2-t2.get_width()//2, 210))

    box = pygame.Rect(W//2-160, 260, 320, 50)
    pygame.draw.rect(screen, BLUE1, box, border_radius=10)
    pygame.draw.rect(screen, BLUE3, box, width=2, border_radius=10)
    show_cursor = (frame // 30) % 2 == 0
    txt = name_buffer + ("|" if show_cursor else "")
    t3 = font_med.render(txt if txt else " ", True, WHITE)
    screen.blit(t3, (box.x+14, box.y+10))

    hint = font_small.render("Tape ton prénom puis appuie sur ENTRÉE (15 caractères max)", True, GREY)
    screen.blit(hint, (W//2-hint.get_width()//2, 330))
    pygame.display.flip()


# ── Écran titre ───────────────────────────────────────────────────────────────
def draw_start(frame, player_name, player):
    screen.fill(NAVY)
    for b in bubbles:
        b.draw(screen); b.update()
    t1 = font_big.render("TORTUE MARINE", True, (100,220,255))
    screen.blit(t1, (W//2-t1.get_width()//2, 55))
    t2 = font_med.render("Stop à la pollution plastique !", True, WHITE)
    screen.blit(t2, (W//2-t2.get_width()//2, 118))

    welcome = font_small.render(f"Salut {player_name} !   Coquillages : {player['money']}   -   meilleur score : {player['best_score']}", True, GOLD)
    screen.blit(welcome, (W//2-welcome.get_width()//2, 155))

    draw_character(screen, W//2, 220, (1,0), frame, skin_id=player.get('equipped_skin','classique'))
    draw_plastic_bag(screen, W//2-90, 220, frame)
    arrow = font_small.render("<- evite ca !", True, PLASTIC_COL)
    screen.blit(arrow, (W//2-90-arrow.get_width()-8, 228))
    draw_starfish(screen, W//2+90, 220, frame)
    arrow2 = font_small.render("prends ca ! ->", True, CORAL)
    screen.blit(arrow2, (W//2+102, 228))

    lines = [
        ("Flèches / ZQSD pour te déplacer",       WHITE,  280),
        ("Poisson = +10 pts", YELLOW, 308),
        ("Etoile de mer = Eco-bouclier 5 sec (+50 pts)", CORAL, 332),
        ("Sac plastique = perd une vie !", PLASTIC_COL, 356),
        ("Sac dissous pendant l'eco-bouclier = +300 pts", (100,220,100), 380),
    ]
    for text, col, y in lines:
        t = font_small.render(text, True, col)
        screen.blit(t, (W//2-t.get_width()//2, y))

    t5 = font_med.render("ENTRÉE = plonger !", True, YELLOW)
    screen.blit(t5, (W//2-t5.get_width()//2, 430))
    t6 = font_small.render("B = boutique de skins   |   C = classement   |   N = changer de prénom   |   ECHAP = quitter", True, GREY)
    screen.blit(t6, (W//2-t6.get_width()//2, 470))
    pygame.display.flip()


# ── Écran classement ─────────────────────────────────────────────────────────
def draw_leaderboard(frame):
    screen.fill(NAVY)
    for b in bubbles:
        b.draw(screen); b.update()
    t1 = font_big.render("CLASSEMENT", True, GOLD)
    screen.blit(t1, (W//2-t1.get_width()//2, 40))

    board = SAVE_DATA.get("leaderboard", [])
    if not board:
        t = font_small.render("Aucun score enregistré pour le moment. Joue une partie !", True, GREY)
        screen.blit(t, (W//2-t.get_width()//2, 150))
    else:
        for i, entry in enumerate(board[:10]):
            y = 120 + i*38
            rank_col = GOLD if i == 0 else (WHITE if i > 2 else CORAL)
            t = font_med.render(f"{i+1}.  {entry['name']}", True, rank_col)
            s = font_med.render(f"{entry['score']} pts", True, rank_col)
            screen.blit(t, (W//2-260, y))
            screen.blit(s, (W//2+140, y))

    t2 = font_small.render("ECHAP = retour au menu", True, GREY)
    screen.blit(t2, (W//2-t2.get_width()//2, H-40))
    pygame.display.flip()


# ── Écran boutique de skins ──────────────────────────────────────────────────
def draw_shop(frame, player, shop_index):
    screen.fill(NAVY)
    for b in bubbles:
        b.draw(screen); b.update()
    t1 = font_big.render("BOUTIQUE DE SKINS", True, (100,220,255))
    screen.blit(t1, (W//2-t1.get_width()//2, 30))
    money_t = font_med.render(f"Coquillages : {player['money']}", True, GOLD)
    screen.blit(money_t, (W//2-money_t.get_width()//2, 78))

    n = len(SKIN_ORDER)
    card_w, card_h, gap = 138, 210, 12
    total_w = n*card_w + (n-1)*gap
    start_x = W//2 - total_w//2
    y = 150

    for i, skin_id in enumerate(SKIN_ORDER):
        skin  = SKINS[skin_id]
        x = start_x + i*(card_w+gap)
        rect = pygame.Rect(x, y, card_w, card_h)
        owned    = skin_id in player['owned_skins']
        equipped = player['equipped_skin'] == skin_id
        selected = i == shop_index

        bg = BLUE2 if selected else BLUE1
        pygame.draw.rect(screen, bg, rect, border_radius=12)
        border_col = YELLOW if selected else BLUE3
        pygame.draw.rect(screen, border_col, rect, width=3 if selected else 1, border_radius=12)

        draw_character(screen, x+card_w//2, y+55, (1,0), frame, skin_id=skin_id)

        name_t = font_small.render(skin['label'], True, WHITE)
        screen.blit(name_t, (x+card_w//2-name_t.get_width()//2, y+95))

        if equipped:
            tag = font_small.render("Equipee", True, GREEN)
            screen.blit(tag, (x+card_w//2-tag.get_width()//2, y+122))
        elif owned:
            tag = font_small.render("Possedee", True, GREY)
            screen.blit(tag, (x+card_w//2-tag.get_width()//2, y+122))
        else:
            price_col = GOLD if player['money'] >= skin['price'] else RED
            tag = font_small.render(f"{skin['price']} co", True, price_col)
            screen.blit(tag, (x+card_w//2-tag.get_width()//2, y+122))

    action = "ENTRÉE = équiper"
    sel_id = SKIN_ORDER[shop_index]
    if sel_id not in player['owned_skins']:
        action = "ENTRÉE = acheter" if player['money'] >= SKINS[sel_id]['price'] else "Pas assez de coquillages"
    t2 = font_small.render(f"<- -> naviguer   |   {action}   |   ECHAP = retour", True, GREY)
    screen.blit(t2, (W//2-t2.get_width()//2, H-40))
    pygame.display.flip()


# ── Boucle principale ─────────────────────────────────────────────────────────
def main():
    state       = 'name_input'
    frame       = 0
    name_buffer = ""
    player_name = None
    game        = None
    shop_index  = 0

    while True:
        dt = clock.tick(FPS)
        dt = min(dt, 50)
        frame += 1

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()

            # ── Saisie du prénom ──────────────────────────────────────────
            if state == 'name_input':
                if event.type == pygame.TEXTINPUT:
                    if len(name_buffer) < 15:
                        name_buffer += event.text
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_BACKSPACE:
                        name_buffer = name_buffer[:-1]
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        clean = name_buffer.strip()
                        if clean:
                            player_name = clean
                            game = Game(player_name=player_name)
                            state = 'menu'
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

            # ── Menu principal ────────────────────────────────────────────
            elif state == 'menu':
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        game = Game(player_name=player_name)
                        state = 'game'
                    elif event.key == pygame.K_b:
                        shop_index = 0
                        state = 'shop'
                    elif event.key == pygame.K_c:
                        state = 'leaderboard'
                    elif event.key == pygame.K_n:
                        name_buffer = ""
                        state = 'name_input'
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

            # ── Classement ────────────────────────────────────────────────
            elif state == 'leaderboard':
                if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                    state = 'menu'

            # ── Boutique ──────────────────────────────────────────────────
            elif state == 'shop':
                if event.type == pygame.KEYDOWN:
                    player = get_player(player_name)
                    if event.key == pygame.K_RIGHT:
                        shop_index = (shop_index + 1) % len(SKIN_ORDER)
                    elif event.key == pygame.K_LEFT:
                        shop_index = (shop_index - 1) % len(SKIN_ORDER)
                    elif event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                        sel_id = SKIN_ORDER[shop_index]
                        if sel_id in player['owned_skins']:
                            player['equipped_skin'] = sel_id
                        elif player['money'] >= SKINS[sel_id]['price']:
                            player['money'] -= SKINS[sel_id]['price']
                            player['owned_skins'].append(sel_id)
                            player['equipped_skin'] = sel_id
                        save_save_data()
                    elif event.key == pygame.K_ESCAPE:
                        state = 'menu'

            # ── Partie en cours ───────────────────────────────────────────
            elif state == 'game':
                if event.type == pygame.KEYDOWN:
                    if event.key in (pygame.K_RIGHT, pygame.K_d):
                        game.next_dx, game.next_dy = 1, 0
                    elif event.key in (pygame.K_LEFT, pygame.K_q, pygame.K_a):
                        game.next_dx, game.next_dy = -1, 0
                    elif event.key in (pygame.K_UP, pygame.K_z, pygame.K_w):
                        game.next_dx, game.next_dy = 0, -1
                    elif event.key in (pygame.K_DOWN, pygame.K_s):
                        game.next_dx, game.next_dy = 0, 1
                    elif event.key == pygame.K_ESCAPE:
                        pygame.quit(); sys.exit()

                    if game.state == 'gameover':
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            state = 'menu'
                    elif game.state == 'level_complete':
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            game.next_level()

        if state == 'name_input':
            draw_name_input(frame, name_buffer)
        elif state == 'menu':
            draw_start(frame, player_name, get_player(player_name))
        elif state == 'leaderboard':
            draw_leaderboard(frame)
        elif state == 'shop':
            draw_shop(frame, get_player(player_name), shop_index)
        elif state == 'game':
            game.update(dt)
            game.draw()
            pygame.display.flip()

if __name__ == '__main__':
    main()