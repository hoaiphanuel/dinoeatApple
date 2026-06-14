import socket, pickle
import pygame

HOST = "127.0.0.1"   # IP của server
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Đã kết nối tới server")

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

    # Lấy input từ bàn phím
    keys = pygame.key.get_pressed()
    move = {
        "left": keys[pygame.K_LEFT],
        "right": keys[pygame.K_RIGHT],
        "up": keys[pygame.K_UP],
        "down": keys[pygame.K_DOWN]
    }
    client.sendall(pickle.dumps(move))

    # Nhận trạng thái game từ server
    data = client.recv(4096)
    if not data:
        break
    game_state = pickle.loads(data)

    # Vẽ táo
    ax, ay = game_state["apple"]
    pygame.draw.circle(screen, (255,0,0), (ax, ay), 10)

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

pygame.quit()
client.close()
