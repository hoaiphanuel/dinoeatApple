import socket, pickle, pygame, threading

HOST, PORT = "192.168.1.21", 12345  # IP server
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Đã kết nối tới server")

game_state = {}

# Thread nhận dữ liệu từ server
def receive_data():
    global game_state
    while True:
        try:
            data = client.recv(8192)
            if not data:
                break
            game_state = pickle.loads(data)
        except:
            break

threading.Thread(target=receive_data, daemon=True).start()

pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("tahoma.ttf", 18)

# Tải sprite khủng long xanh (Player 1) và đỏ (Player 2)
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

running = True
while running:
    screen.fill((255,255,255))
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input Player 2
    keys = pygame.key.get_pressed()
    move = {
        "left": keys[pygame.K_LEFT],
        "right": keys[pygame.K_RIGHT],
        "up": keys[pygame.K_UP],
        "down": keys[pygame.K_DOWN]
    }
    try:
        client.sendall(pickle.dumps(move))
    except:
        running = False

    # Vẽ game theo state
    if game_state:
        # Táo
        ax, ay = game_state["apple"]
        screen.blit(apple_img, (ax, ay))

        # Traps
        for tx, ty in game_state["traps"]:
            screen.blit(trap_img, (tx, ty))

        # Khủng long
        for pid, p in game_state["players"].items():
            dino_img = sprites[pid].get(p["direction"], sprites[pid]["down"])
            size = int(40 * p["scale"])
            dino_scaled = pygame.transform.scale(dino_img, (size, size))
            screen.blit(dino_scaled, (p["x"], p["y"]))

            score_text = font.render(f"Player {pid} Score: {p['score']}", True, (0,0,0))
            screen.blit(score_text, (10, 10 + 20*pid))

        # Stage và thời gian
        stage_text = font.render(f"Stage: {game_state['stage']}", True, (0,0,0))
        screen.blit(stage_text, (WIDTH-150, 10))

        if not game_state["end_time"]:
            current_time = (pygame.time.get_ticks() - game_state["start_time"]) / 1000
        else:
            current_time = (game_state["end_time"] - game_state["start_time"]) / 1000
        timer_text = font.render(f"Time: {current_time:.2f}s", True, (0,0,0))
        screen.blit(timer_text, (WIDTH-250, 40))

        # Thông báo thắng/thua
        if game_state["game_over"]:
            msg = font.render("Hoàn thành tất cả stage!", True, (0,128,0))
            screen.blit(msg, (WIDTH//2 - 150, HEIGHT//2))
        elif game_state["dead"]:
            msg = font.render("Bạn đã chết!", True, (255,0,0))
            screen.blit(msg, (WIDTH//2 - 100, HEIGHT//2))

    pygame.display.flip()
    clock.tick(30)

pygame.quit()
client.close()
