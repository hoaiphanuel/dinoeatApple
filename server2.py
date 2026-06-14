import socket, pickle, random, threading, pygame

HOST, PORT = "0.0.0.0", 12345
server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Server đang chờ client...")
conn, addr = server.accept()
print("Client kết nối từ", addr)

WIDTH, HEIGHT = 800, 600
pygame.init()
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("tahoma.ttf", 18)

# Tải sprite khủng long và vật thể
dino_up = pygame.image.load("dino_up.png")
dino_down = pygame.image.load("dino_down.png")
dino_left = pygame.image.load("dino_left.png")
dino_right = pygame.image.load("dino_right.png")
apple_img = pygame.image.load("apple.png")
trap_img = pygame.image.load("trap.png")

sprites = {
    "up": dino_up,
    "down": dino_down,
    "left": dino_left,
    "right": dino_right
}

# Game state
game_state = {
    "apple": (random.randint(50, 750), random.randint(50, 550)),
    "traps": [],
    "players": {
        1: {"x": 100, "y": 100, "direction": "down", "score": 0, "scale": 1.0},
        2: {"x": 600, "y": 400, "direction": "up", "score": 0, "scale": 1.0}
    },
    "stage": 1,
    "apple_count": 0,
    "game_over": False,
    "dead": False,
    "start_time": pygame.time.get_ticks(),
    "end_time": None
}

apple_size = 30
trap_size = 40
apples_per_stage = 10
max_stage = 10

# Nhận input từ client
def handle_client():
    while True:
        try:
            data = conn.recv(1024)
            if data:
                move = pickle.loads(data)
                p = game_state["players"][2]
                if move.get("left"):  p["x"] -= 5; p["direction"]="left"
                if move.get("right"): p["x"] += 5; p["direction"]="right"
                if move.get("up"):    p["y"] -= 5; p["direction"]="up"
                if move.get("down"):  p["y"] += 5; p["direction"]="down"
        except:
            break

threading.Thread(target=handle_client, daemon=True).start()

running = True
while running:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input cho Player 1
    keys = pygame.key.get_pressed()
    p1 = game_state["players"][1]
    if keys[pygame.K_LEFT]:  p1["x"] -= 5; p1["direction"]="left"
    if keys[pygame.K_RIGHT]: p1["x"] += 5; p1["direction"]="right"
    if keys[pygame.K_UP]:    p1["y"] -= 5; p1["direction"]="up"
    if keys[pygame.K_DOWN]:  p1["y"] += 5; p1["direction"]="down"

    # Logic ăn táo
    ax, ay = game_state["apple"]
    for pid, p in game_state["players"].items():
        rect = pygame.Rect(p["x"], p["y"], int(40*p["scale"]), int(40*p["scale"]))
        apple_rect = pygame.Rect(ax, ay, apple_size, apple_size)
        if rect.colliderect(apple_rect):
            p["score"] += 1
            p["scale"] *= 1.01
            game_state["apple_count"] += 1
            game_state["apple"] = (random.randint(50, 750), random.randint(50, 550))
            if game_state["apple_count"] >= apples_per_stage:
                game_state["stage"] += 1
                game_state["apple_count"] = 0
                game_state["traps"].append((random.randint(50, 750), random.randint(50, 550)))
                if game_state["stage"] > max_stage:
                    game_state["game_over"] = True
                    game_state["end_time"] = pygame.time.get_ticks()

    # Logic trap
    for pid, p in game_state["players"].items():
        rect = pygame.Rect(p["x"], p["y"], int(40*p["scale"]), int(40*p["scale"]))
        for tx, ty in game_state["traps"]:
            trap_rect = pygame.Rect(tx, ty, trap_size, trap_size)
            if rect.colliderect(trap_rect):
                game_state["dead"] = True
                game_state["end_time"] = pygame.time.get_ticks()

    # Vẽ táo và trap
    screen.blit(apple_img, game_state["apple"])
    for tx, ty in game_state["traps"]:
        screen.blit(trap_img, (tx, ty))

    # Vẽ khủng long bằng sprite
    for pid, p in game_state["players"].items():
        dino_img = sprites.get(p["direction"], dino_down)
        size = int(40*p["scale"])
        dino_scaled = pygame.transform.scale(dino_img, (size, size))
        screen.blit(dino_scaled, (p["x"], p["y"]))
        score_text = font.render(f"Player {pid} Score: {p['score']}", True, (0,0,0))
        screen.blit(score_text, (10, 10 + 20*pid))

    pygame.display.flip()
    clock.tick(30)

    # Gửi state cho client
    try:
        conn.sendall(pickle.dumps(game_state))
    except:
        pass

pygame.quit()
server.close()
