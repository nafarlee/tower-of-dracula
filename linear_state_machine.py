def end():
    pass

def create(transitions):
    count = 0
    key = 0
    while True:
        if count in transitions:
            key = count
            if transitions[key] == end:
                count = 0
                key = 0
            yield transitions[count]
        else:
            yield transitions[key]
        count += 1
