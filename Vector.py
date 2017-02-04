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

    def absolute(self):
        return Vector(abs(self.x), abs(self.y))

    def is_zero(self):
        return self.x == 0 and self.y == 0

    def reverse_y(self):
        return Vector(self.x, -self.y)

    def reverse_x(self):
        return Vector(-self.x, self.y)
