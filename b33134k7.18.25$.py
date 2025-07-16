import pygame
import os

# ==== CONFIG ====
WIN_W, WIN_H = 600, 400
FLOORS = 4
TILE_SIZE = 32

# --- Asset loader (replace these with NES PNGs as needed!) ---
def load_sprite(name, fallback_color):
    path = os.path.join("assets", name)
    try:
        img = pygame.image.load(path).convert_alpha()
        return pygame.transform.scale(img, (TILE_SIZE, TILE_SIZE))
    except:
        surf = pygame.Surface((TILE_SIZE, TILE_SIZE), pygame.SRCALPHA)
        surf.fill(fallback_color)
        return surf

# -- You can drop PNGs in ./assets: mario.png, goomba.png, block.png, etc. --
player_img = load_sprite("mario.png", (224, 32, 32))
goomba_img = load_sprite("goomba.png", (160, 80, 32))
block_img = load_sprite("block.png", (198, 142, 72))
floor_img = load_sprite("floor.png", (188, 188, 60))
door_img  = load_sprite("door.png",  (76,44,22))

# ==== INIT ====
pygame.init()
screen = pygame.display.set_mode((WIN_W, WIN_H))
pygame.display.set_caption("CatSama B3313 NES Tower")
clock = pygame.time.Clock()

# ==== ENGINE STATE ====
player = pygame.Rect(70, 320, TILE_SIZE, TILE_SIZE)
vy = 0
on_ground = False
floor = 0
warp_cooldown = 0

# --- Tower structure (simple platforms per floor, NES style) ---
platforms = [
    [pygame.Rect(0, 360, WIN_W, TILE_SIZE)],  # Floor 1 ground
    [pygame.Rect(0, 260, WIN_W, TILE_SIZE)],  # Floor 2
    [pygame.Rect(0, 160, WIN_W, TILE_SIZE)],  # Floor 3
    [pygame.Rect(120, 60, 360, TILE_SIZE)]    # Boss floor
]
doors = [
    pygame.Rect(WIN_W-40, 328, 36, 40),
    pygame.Rect(10, 228, 36, 40),
    pygame.Rect(WIN_W-40, 128, 36, 40),
    pygame.Rect(WIN_W//2-24, 40, 48, 44)
]

# --- Goomboss: use NES Goomba x3 on top floor ---
goomboss_pos = [(WIN_W//2-36, 20), (WIN_W//2, 20), (WIN_W//2+36, 20)]

# ==== MAIN LOOP ====
running = True
while running:
    for e in pygame.event.get():
        if e.type == pygame.QUIT:
            running = False

    keys = pygame.key.get_pressed()
    speed = 4

    if warp_cooldown == 0:
        if keys[pygame.K_LEFT]: player.x -= speed
        if keys[pygame.K_RIGHT]: player.x += speed
        if keys[pygame.K_SPACE] and on_ground:
            vy = -8
            on_ground = False

    # --- Gravity & Platform collision (NES logic: snap to top of tile) ---
    vy += 0.6
    player.y += vy
    on_ground = False
    for plat in platforms[floor]:
        if player.colliderect(plat) and vy >= 0:
            player.bottom = plat.top
            vy = 0
            on_ground = True

    # --- Keep in bounds ---
    player.x = max(0, min(WIN_W - TILE_SIZE, player.x))
    player.y = min(WIN_H-TILE_SIZE, player.y)

    # --- Door warp (like B3313) ---
    if warp_cooldown == 0 and player.colliderect(doors[floor]):
        warp_cooldown = 18
        floor = (floor + 1) % FLOORS
        if floor == FLOORS-1:
            player.x, player.y = WIN_W//2-16, 60+TILE_SIZE+4
        else:
            player.x, player.y = 70, platforms[floor][0].top-TILE_SIZE

    if warp_cooldown > 0:
        warp_cooldown -= 1

    # ==== DRAW ====
    screen.fill((92,148,252))  # NES Mario sky

    # Draw blocks (platforms)
    for plat in platforms[floor]:
        for x in range(plat.left, plat.right, TILE_SIZE):
            screen.blit(floor_img, (x, plat.top))

    # Door
    screen.blit(door_img, (doors[floor].x, doors[floor].y))

    # Player
    screen.blit(player_img, (player.x, player.y))

    # Goomboss: Boss floor = 3 stacked NES Goombas!
    if floor == FLOORS-1:
        for gx, gy in goomboss_pos:
            screen.blit(goomba_img, (gx, gy))
        font = pygame.font.SysFont("Arial", 26, True)
        label = font.render("GOOMBOSS", True, (180,30,30))
        screen.blit(label, (WIN_W//2-60, 16))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
