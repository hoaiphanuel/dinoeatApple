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

# Nhập tên người chơi
player1_name = input("Nhập tên Player 1: ")
player2_name = input("Nhập tên Player 2: ")

# Tải sprite
dino1_up = pygame.image.load("dino_green_up.png")
dino1_down = pygame.image.load("dino_green_down.png")
dino1_left = pygame.image.load("dino_green_left.png")
dino1_right = pygame.image.load("dino_green_right.png")

dino2_up = pygame.image.load("dino_red_up.png")
dino2_down = pygame.image.load("dino_red_down.png")
dino2_left = pygame.image.load("dino_red_left.png")
dino2_right = pygame.image.load("dino_red_right.png")

apple_img = pygame.image.load("apple.png")
trap_img = pygame.image.load("trap.png")

sprites = {
    1: {"up": dino1_up, "down": dino1_down, "left": dino1_left, "right": dino1_right},
    2: {"up": dino2_up, "down": dino2_down, "left": dino2_left, "right": dino2_right}
}

apple_size = 30
trap_size = 40
apples_per_stage = 10
max_stage = 10

def get_random_position(obj_width, obj_height, existing_rects):
    while True:
        x = random.randint(0, WIDTH - obj_width)
        y = random.randint(0, HEIGHT - obj_height)
        new_rect = pygame.Rect(x, y, obj_width, obj_height)
        if not any(new_rect.colliderect(rect) for rect in existing_rects):
            return x, y

def reset_game():
    dino1_rect = pygame.Rect(100, 100, 40, 40)
    dino2_rect = pygame.Rect(600, 400, 40, 40)
    apple_x, apple_y = get_random_position(apple_size, apple_size, [dino1_rect, dino2_rect])
    return {
        "apple": (apple_x, apple_y),
        "traps": [],
        "players": {
            1: {"x": 100, "y": 100, "direction": "down", "score": 0, "scale": 1.0, "name": player1_name},
            2: {"x": 600, "y": 400, "direction": "up", "score": 0, "scale": 1.0, "name": player2_name}
        },
        "stage": 1,
        "apple_count": 0,
        "game_over": False,
        "dead": False,
        "dead_player": None,
        "start_time": pygame.time.get_ticks(),
        "end_time": None
    }

game_state = reset_game()

def handle_client():
    global game_state
    while True:
        try:
            data = conn.recv(1024)
            if data:
                move = pickle.loads(data)
                if move.get("reset"):
                    game_state = reset_game()
                    continue
                p = game_state["players"][2]
                size = int(40 * p["scale"])
                if move.get("left") and p["x"] > -(size//2):
                    p["x"] -= 5; p["direction"]="left"
                if move.get("right") and p["x"] < WIDTH - size//2:
                    p["x"] += 5; p["direction"]="right"
                if move.get("up") and p["y"] > -(size//2):
                    p["y"] -= 5; p["direction"]="up"
                if move.get("down") and p["y"] < HEIGHT - size//2:
                    p["y"] += 5; p["direction"]="down"
        except:
            break

threading.Thread(target=handle_client, daemon=True).start()

running = True
while running:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input Player 1
    if not game_state["game_over"] and not game_state["dead"]:
        p1 = game_state["players"][1]
        size = int(40 * p1["scale"])
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and p1["x"] > -(size//2):
            p1["x"] -= 5; p1["direction"]="left"
        if keys[pygame.K_RIGHT] and p1["x"] < WIDTH - size//2:
            p1["x"] += 5; p1["direction"]="right"
        if keys[pygame.K_UP] and p1["y"] > -(size//2):
            p1["y"] -= 5; p1["direction"]="up"
        if keys[pygame.K_DOWN] and p1["y"] < HEIGHT - size//2:
            p1["y"] += 5; p1["direction"]="down"

    # Ăn táo
    ax, ay = game_state["apple"]
    for pid, p in game_state["players"].items():
        rect = pygame.Rect(p["x"], p["y"], int(40*p["scale"]), int(40*p["scale"]))
        apple_rect = pygame.Rect(ax, ay, apple_size, apple_size)
        if rect.colliderect(apple_rect) and not game_state["game_over"] and not game_state["dead"]:
            p["score"] += 1
            p["scale"] *= 1.01
            game_state["apple_count"] += 1
            existing = [pygame.Rect(pp["x"], pp["y"], int(40*pp["scale"]), int(40*pp["scale"])) for pp in game_state["players"].values()]
            existing += [pygame.Rect(tx, ty, trap_size, trap_size) for tx, ty in game_state["traps"]]
            apple_x, apple_y = get_random_position(apple_size, apple_size, existing)
            game_state["apple"] = (apple_x, apple_y)
            if game_state["apple_count"] >= apples_per_stage:
                game_state["stage"] += 1
                game_state["apple_count"] = 0
                existing.append(pygame.Rect(apple_x, apple_y, apple_size, apple_size))
                trap_x, trap_y = get_random_position(trap_size, trap_size, existing)
                game_state["traps"].append((trap_x, trap_y))
                if game_state["stage"] > max_stage:
                    game_state["game_over"] = True
                    game_state["end_time"] = pygame.time.get_ticks()

    # Trap
    for pid, p in game_state["players"].items():
        rect = pygame.Rect(p["x"], p["y"], int(40*p["scale"]), int(40*p["scale"]))
        for tx, ty in game_state["traps"]:
            trap_rect = pygame.Rect(tx, ty, trap_size, trap_size)
            if rect.colliderect(trap_rect) and not game_state["game_over"] and not game_state["dead"]:
                game_state["dead"] = True
                game_state["dead_player"] = pid
                game_state["end_time"] = pygame.time.get_ticks()

    # Vẽ táo, trap
    screen.blit(apple_img, game_state["apple"])
    for tx, ty in game_state["traps"]:
        screen.blit(trap_img, (tx, ty))

    # Vẽ khủng long + điểm
    for pid, p in game_state["players"].items():
        dino_img = sprites[pid].get(p["direction"], sprites[pid]["down"])
        size = int(40*p["scale"])
        dino_scaled = pygame.transform.scale(dino_img, (size, size))
        screen.blit(dino_scaled, (p["x"], p["y"]))
        score_text = font.render(f"{p['name']} Score: {p['score']}", True, (0,0,0))
        screen.blit(score_text, (10, 10 + 20*pid))

    # Đồng hồ
    if not game_state["end_time"]:
        current_time = (pygame.time.get_ticks() - game_state["start_time"]) / 1000
    else:
        current_time = (game_state["end_time"] - game_state["start_time"]) / 1000
    timer_text = font.render(f"Time: {current_time:.2f}s", True, (0,0,0))
    screen.blit(timer_text, (WIDTH-250, 40))

    # Thông báo kết thúc
    if game_state["game_over"]:
        msg = font.render("Hoàn thành tất cả stage!", True, (0, 128, 0))
        screen.blit(msg, (WIDTH // 2 - 150, HEIGHT // 2))
    elif game_state["dead"]:
        pid = game_state.get("dead_player")
        if pid:
            name = game_state["players"][pid]["name"]
            msg = font.render(f"{name} đã chết!", True, (255, 0, 0))
            screen.blit(msg, (WIDTH // 2 - 120, HEIGHT // 2))

    pygame.display.flip()
    clock.tick(30)

    # Gửi state cho client
    try:
        conn.sendall(pickle.dumps(game_state))
    except:
        pass

pygame.quit()
server.close()
