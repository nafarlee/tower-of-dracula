class Vector(object):
    """Represents a 2D vector"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y

    def tuple(self):
        return (self.x, self.y)

    def add(self, other_vector):
        new_x = self.x + other_vector.x
        new_y = self.y + other_vector.y
        return Vector(new_x, new_y)

    def squared(self):
        return self.x^2 + self.y^2
