"""
collisions: puck-vs-paddle collision handling.
"""

import math  # ADDED (Task 1)

MAX_PUCK_SPEED = 14.0  # ADDED (Task 1): keeps per-frame movement below combined radii (no tunneling)


def handle_paddle_collision(puck, paddle, min_y=None, max_y=None):
    """
    If the puck overlaps the paddle, push it out and bounce it off.
    min_y / max_y (optional) are the limits for the puck's centre so it
    can be slid sideways instead of being pushed into a top/bottom wall.
    Returns True if a collision was handled this frame.
    """
    dx = puck.x - paddle.x
    dy = puck.y - paddle.y
    distance = math.hypot(dx, dy)  # CHANGED (Task 1)
    min_dist = puck.radius + paddle.radius

    if distance >= min_dist:
        return False

    # ADDED (Task 1): collision normal, pointing from paddle centre to puck centre
    if distance > 1e-6:
        nx, ny = dx / distance, dy / distance
    else:
        speed = math.hypot(puck.vx, puck.vy)
        if speed > 1e-6:
            nx, ny = -puck.vx / speed, -puck.vy / speed
        else:
            nx, ny = 0.0, -1.0

    # ADDED (Task 1): positional correction - move puck fully out of the paddle
    puck.x = paddle.x + nx * min_dist
    puck.y = paddle.y + ny * min_dist

    # ADDED (Task 1): if that pushed the puck into a top/bottom wall, slide it
    # along the paddle's edge instead so it can't get pinned and vibrate
    if min_y is not None and max_y is not None:
        clamped_y = max(min_y, min(max_y, puck.y))
        if clamped_y != puck.y:
            puck.y = clamped_y
            dy = puck.y - paddle.y
            side = 1.0 if puck.x >= paddle.x else -1.0
            puck.x = paddle.x + side * math.sqrt(max(min_dist ** 2 - dy ** 2, 0.0))
            nx = (puck.x - paddle.x) / min_dist
            ny = dy / min_dist

    # ADDED (Task 1): reflect velocity about the normal, relative to the moving paddle.
    # Only when approaching (vn < 0); if already separating, leave velocity alone.
    rvx = puck.vx - paddle.vx
    rvy = puck.vy - paddle.vy
    vn = rvx * nx + rvy * ny
    if vn < 0:
        rvx -= 2 * vn * nx
        rvy -= 2 * vn * ny
        puck.vx = rvx + paddle.vx
        puck.vy = rvy + paddle.vy

    # ADDED (Task 1): speed cap
    speed = math.hypot(puck.vx, puck.vy)
    if speed > MAX_PUCK_SPEED:
        scale = MAX_PUCK_SPEED / speed
        puck.vx *= scale
        puck.vy *= scale

    return True