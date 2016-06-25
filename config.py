import json

def load():
    filename = "config.json"
    file_object = open(filename, "r")
    file_contents = file_object.read()

    return json.loads(file_contents)

def validate(config_dict):
    player = config_dict["player"]
    assert player == "Simon" or player == "Dracula", "invalid player configuration"
    multiplayer = config_dict["multiplayer"]
    assert isinstance(multiplayer, bool), "invalid multiplayer configuration"
    port = config_dict["port"]
    assert port > 0 and port < 65537, "invalid port configuration"

def get():
    config_dict = load()
    validate(config_dict)
    return config_dict
