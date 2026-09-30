"""
Paddle: a player's or the computer's mallet, confined to their own half
of the table.
"""


class Paddle:
    def __init__(self, x, y, radius, min_x, max_x, min_y, max_y):
        self.x = x
        self.y = y
        self.radius = radius
        self.min_x = min_x
        self.max_x = max_x
        self.min_y = min_y
        self.max_y = max_y

        # ADDED (Task 1): velocity tracking so collisions can use paddle motion
        self.prev_x = x
        self.prev_y = y
        self.vx = 0.0
        self.vy = 0.0

    def clamp(self):
        self.x = max(self.min_x, min(self.max_x, self.x))
        self.y = max(self.min_y, min(self.max_y, self.y))

    def move_by(self, dx, dy):
        self.x += dx
        self.y += dy
        self.clamp()

    def move_to(self, x, y):
        self.x = x
        self.y = y
        self.clamp()

    # ADDED (Task 1): call once per frame after all paddle movement is done
    def update_velocity(self):
        self.vx = self.x - self.prev_x
        self.vy = self.y - self.prev_y
        self.prev_x = self.x
        self.prev_y = self.y