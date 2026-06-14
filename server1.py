import socket, pickle, threading
import pygame, random, sys

# Cấu hình server
HOST = "192.168.1.21"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Server đang chờ client...")

conn, addr = server.accept()
print("Client kết nối từ", addr)

# Khởi tạo Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khủng long ăn táo - Server")
clock = pygame.time.Clock()

# Tải hình khủng long 4 hướng
dino_up = pygame.image.load("dino_up.png")
dino_down = pygame.image.load("dino_down.png")
dino_left = pygame.image.load("dino_left.png")
dino_right = pygame.image.load("dino_right.png")

# Tải hình táo và trap
apple_img = pygame.image.load("apple.png")
trap_img = pygame.image.load("trap.png")

# Kích thước gốc
dino_width, dino_height = dino_down.get_size()
apple_width, apple_height = apple_img.get_size()
trap_width, trap_height = trap_img.get_size()

font_small = pygame.font.Font("tahoma.ttf", 18)
font_big = pygame.font.Font("tahoma.ttf", 36)

# Trạng thái game
game_state = {
    "apple": (random.randint(50, 750), random.randint(50, 550)),
    "traps": [(random.randint(50, 750), random.randint(50, 550))],
    "players": {
        1: {"x": 100, "y": 100, "score": 0, "scale": 1.0, "img": dino_down},
        2: {"x": 600, "y": 400, "score": 0, "scale": 1.0, "img": dino_down}
    }
}

apples_per_stage = 10
max_stage = 10
apple_count = 0
stage = 1
start_time = pygame.time.get_ticks()
end_time = None
game_over = False
dead = False

# Nhận input từ client (Player 2)
def handle_client():
    global game_state
    while True:
        try:
            data = conn.recv(1024)
            if data:
                move = pickle.loads(data)
                p = game_state["players"][2]
                if move.get("left"):  p["x"] -= 5; p["img"] = dino_left
                if move.get("right"): p["x"] += 5; p["img"] = dino_right
                if move.get("up"):    p["y"] -= 5; p["img"] = dino_up
                if move.get("down"):  p["y"] += 5; p["img"] = dino_down
        except:
            break

threading.Thread(target=handle_client, daemon=True).start()

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input từ bàn phím cho Player 1
    keys = pygame.key.get_pressed()
    p1 = game_state["players"][1]
    if keys[pygame.K_LEFT]:  p1["x"] -= 5; p1["img"] = dino_left
    if keys[pygame.K_RIGHT]: p1["x"] += 5; p1["img"] = dino_right
    if keys[pygame.K_UP]:    p1["y"] -= 5; p1["img"] = dino_up
    if keys[pygame.K_DOWN]:  p1["y"] += 5; p1["img"] = dino_down

    # Vẽ táo
    screen.blit(apple_img, game_state["apple"])

    # Vẽ traps
    for tx, ty in game_state["traps"]:
        screen.blit(trap_img, (tx, ty))

    # Vẽ players
    for pid, p in game_state["players"].items():
        new_width = int(dino_width * p["scale"])
        new_height = int(dino_height * p["scale"])
        dino_scaled = pygame.transform.scale(p["img"], (new_width, new_height))
        screen.blit(dino_scaled, (p["x"], p["y"]))
        score_text = font_small.render(f"Player {pid} Score: {p['score']}", True, (0,0,0))
        screen.blit(score_text, (10, 10 + 20*pid))

    # Kiểm tra va chạm táo
    ax, ay = game_state["apple"]
    apple_rect = pygame.Rect(ax, ay, apple_width, apple_height)
    for pid, p in game_state["players"].items():
        dino_rect = pygame.Rect(p["x"], p["y"], int(dino_width*p["scale"]), int(dino_height*p["scale"]))
        if dino_rect.colliderect(apple_rect):
            p["score"] += 1
            p["scale"] *= 1.01
            game_state["apple"] = (random.randint(50, 750), random.randint(50, 550))
            game_state["traps"].append((random.randint(50, 750), random.randint(50, 550)))

    # Kiểm tra va chạm trap
    for pid, p in game_state["players"].items():
        dino_rect = pygame.Rect(p["x"], p["y"], int(dino_width*p["scale"]), int(dino_height*p["scale"]))
        for tx, ty in game_state["traps"]:
            trap_rect = pygame.Rect(tx, ty, trap_width, trap_height)
            if dino_rect.colliderect(trap_rect):
                p["score"] = -999

    pygame.display.flip()
    clock.tick(60)

    # Gửi trạng thái game cho client
    try:
        conn.sendall(pickle.dumps(game_state))
    except:
        pass

pygame.quit()
server.close()
sys.exit()
