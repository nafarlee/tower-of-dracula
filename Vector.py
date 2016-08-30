class Vector(object):
    """Represents a 2D vector"""

    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
    
    def tuple(self):
        return (self.x, self.y)