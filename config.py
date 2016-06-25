import json

def get():
    filename = "config.json"
    file_object = open(filename, "r")
    file_contents = file_object.read()

    return json.loads(file_contents)
