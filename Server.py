import socket, pickle, random

HOST = "0.0.0.0"
PORT = 12345

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind((HOST, PORT))
server.listen(2)
print("Server đang chờ kết nối...")

clients = []
while len(clients) < 2:
    conn, addr = server.accept()
    print("Client kết nối từ", addr)
    clients.append(conn)

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

while True:
    # Nhận input từ client
    for i, conn in enumerate(clients, start=1):
        try:
            data = conn.recv(1024)
            if data:
                move = pickle.loads(data)
                if move.get("left"):  game_state["players"][i]["x"] -= 5
                if move.get("right"): game_state["players"][i]["x"] += 5
                if move.get("up"):    game_state["players"][i]["y"] -= 5
                if move.get("down"):  game_state["players"][i]["y"] += 5
        except:
            pass

    # Kiểm tra ăn táo
    ax, ay = game_state["apple"]
    for pid, p in game_state["players"].items():
        px, py = p["x"], p["y"]
        size = int(40 * p["scale"])
        player_rect = (px, py, size, size)
        apple_rect = (ax, ay, apple_size, apple_size)

        # kiểm tra va chạm
        if (px < ax + apple_size and px + size > ax and
            py < ay + apple_size and py + size > ay):
            p["score"] += 1
            p["scale"] *= 1.01  # tăng kích thước 1%
            # random táo mới
            game_state["apple"] = (random.randint(50, 750), random.randint(50, 550))
            # thêm trap mới
            game_state["traps"].append((random.randint(50, 750), random.randint(50, 550)))

    # Kiểm tra va chạm trap
    for pid, p in game_state["players"].items():
        px, py = p["x"], p["y"]
        size = int(40 * p["scale"])
        for tx, ty in game_state["traps"]:
            if (px < tx + trap_size and px + size > tx and
                py < ty + trap_size and py + size > ty):
                p["score"] = -999  # đánh dấu chết

    # Gửi trạng thái game cho cả 2 client
    for conn in clients:
        conn.sendall(pickle.dumps(game_state))
