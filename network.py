import pickle

def send_world_report(world, socket):
    """send the pertinent world information to the second player"""
    world_report = {
        "Simon": world.simon.rect,
        "Health": world.simon.health,
        "MP": world.mp,
        "Time": world.time,
        "Enemies": [],
        "Winner": world.winner
    }

    for enemy in world.enemies:
        enemy_summary = (enemy.__name__, enemy.rect)
        world_report["Enemies"].append(enemy_summary)

    socket.sendall(pickle.dumps(world_report))

def receive_world_report(connection):
    """receive the pertinent world informtion from the first player"""
    data = connection.recv(1024)
    if not data:
        return None
    else:
        return pickle.loads(data)

def send_spawn_input(enemy_spawn_summary, socket):
    """send spawn inputs to the first player"""
    socket.sendall(pickle.dumps(enemy_spawn_summary))

def receive_spawn_input(connection):
    """recieve possible spawn inputs from the second player"""
    data = connection.recv(1024)
    if not data:
        return None
    else:
        return pickle.loads(data)
