import socket, pickle, random, threading
import pygame

HOST = "0.0.0.0"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(1)
print("Server đang chờ client...")

conn, addr = server.accept()
print("Client kết nối từ", addr)

# Trạng thái game
game_state = {
    "apple": (random.randint(50, 750), random.randint(50, 550)),
    "traps": [(random.randint(50, 750), random.randint(50, 550))],
    "players": {
        1: {"x": 100, "y": 100, "score": 0, "scale": 1.0, "color": "green"},
        2: {"x": 600, "y": 400, "score": 0, "scale": 1.0, "color": "red"}
    }
}

apple_size = 20
trap_size = 30

# Hàm nhận input từ client
def handle_client():
    global game_state
    while True:
        try:
            data = conn.recv(1024)
            if data:
                move = pickle.loads(data)
                p = game_state["players"][2]
                if move.get("left"):  p["x"] -= 5
                if move.get("right"): p["x"] += 5
                if move.get("up"):    p["y"] -= 5
                if move.get("down"):  p["y"] += 5
        except:
            break

threading.Thread(target=handle_client, daemon=True).start()

# Pygame cho server (Player 1)
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
font = pygame.font.Font("tahoma.ttf", 18)

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input từ bàn phím cho Player 1
    keys = pygame.key.get_pressed()
    p1 = game_state["players"][1]
    if keys[pygame.K_LEFT]:  p1["x"] -= 5
    if keys[pygame.K_RIGHT]: p1["x"] += 5
    if keys[pygame.K_UP]:    p1["y"] -= 5
    if keys[pygame.K_DOWN]:  p1["y"] += 5

    # Logic ăn táo
    ax, ay = game_state["apple"]
    for pid, p in game_state["players"].items():
        px, py = p["x"], p["y"]
        size = int(40 * p["scale"])
        if (px < ax + apple_size and px + size > ax and
            py < ay + apple_size and py + size > ay):
            p["score"] += 1
            p["scale"] *= 1.01
            game_state["apple"] = (random.randint(50, 750), random.randint(50, 550))
            game_state["traps"].append((random.randint(50, 750), random.randint(50, 550)))

    # Logic trap
    for pid, p in game_state["players"].items():
        px, py = p["x"], p["y"]
        size = int(40 * p["scale"])
        for tx, ty in game_state["traps"]:
            if (px < tx + trap_size and px + size > tx and
                py < ty + trap_size and py + size > ty):
                p["score"] = -999

    # Vẽ táo
    pygame.draw.circle(screen, (255,0,0), game_state["apple"], 10)

    # Vẽ traps
    for tx, ty in game_state["traps"]:
        pygame.draw.rect(screen, (100,100,100), (tx, ty, 30, 30))

    # Vẽ players
    for pid, p in game_state["players"].items():
        color = (0,255,0) if p["color"]=="green" else (255,0,0)
        size = int(40 * p["scale"])
        pygame.draw.rect(screen, color, (p["x"], p["y"], size, size))
        score_text = font.render(f"Player {pid} Score: {p['score']}", True, (0,0,0))
        screen.blit(score_text, (10, 10 + 20*pid))

    pygame.display.flip()
    clock.tick(30)

    # Gửi trạng thái game cho client
    try:
        conn.sendall(pickle.dumps(game_state))
    except:
        pass

pygame.quit()
server.close()
