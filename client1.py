import socket, pickle
import pygame, sys

HOST = "192.168.23.117"   # thay bằng IP của server
PORT = 12345

client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((HOST, PORT))
print("Đã kết nối tới server")

# Khởi tạo Pygame
pygame.init()
WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Khủng long ăn táo - Client")
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

running = True
while running:
    screen.fill((255, 255, 255))

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

    # Input từ bàn phím cho Player 2
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
    screen.blit(apple_img, (ax, ay))

    # Vẽ traps
    for tx, ty in game_state["traps"]:
        screen.blit(trap_img, (tx, ty))

    # Vẽ players
    for pid, p in game_state["players"].items():
        # chọn ảnh khủng long theo hướng hiện tại
        dino_img = p["img"]
        new_width = int(dino_width * p["scale"])
        new_height = int(dino_height * p["scale"])
        dino_scaled = pygame.transform.scale(dino_img, (new_width, new_height))
        screen.blit(dino_scaled, (p["x"], p["y"]))
        score_text = font_small.render(f"Player {pid} Score: {p['score']}", True, (0,0,0))
        screen.blit(score_text, (10, 10 + 20*pid))

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
client.close()
sys.exit()
