import turtle
import random
import time

BG_COLOR = "black"
DOT_COLOR = "cyan"
STEP_SIZE = 3
FRAME_DELAY_MS = 16
PAUSE_ON_TURN = 0.35
MIN_DISTANCE = 100
MAX_DISTANCE = 600
EDGE_MARGIN = 15
REDIRECT_STEP = 150

screen = turtle.Screen()
screen.title("Random Moving Dot")
screen.bgcolor(BG_COLOR)

root = screen.getcanvas().winfo_toplevel()
try:
    root.state("zoomed")
except Exception:
    try:
        root.attributes("-zoomed", True)
    except Exception:
        screen.setup(width=1.0, height=1.0)

screen.tracer(0)

dot = turtle.Turtle()
dot.hideturtle()
dot.shape("circle")
dot.color(DOT_COLOR)
dot.penup()
dot.speed(0)
dot.showturtle()

max_x = 0
max_y = 0


def update_bounds(event=None):
    """Recalculate safe movement bounds based on current window size."""
    global max_x, max_y
    max_x = screen.window_width() / 2 - EDGE_MARGIN
    max_y = screen.window_height() / 2 - EDGE_MARGIN


# Ensure bounds are set initially and update on window resize/move events
update_bounds()
try:
    root.bind("<Configure>", update_bounds)
except Exception:
    pass

state = {
    "target_angle": None,
    "remaining_distance": 0.0,
    "paused_until": 0.0,
    "is_redirecting": False
}


def pick_new_direction_and_distance():
    """Return a random movement angle (degrees) and distance (pixels)."""
    angle = random.uniform(0, 360)
    distance = random.uniform(MIN_DISTANCE, MAX_DISTANCE)
    return angle, distance


def start_new_movement(angle_deg, distance, redirecting=False):
    """Initialize movement state with a target angle, distance, and optional redirect flag."""
    state["target_angle"] = angle_deg % 360
    state["remaining_distance"] = float(distance)
    state["paused_until"] = time.time() + PAUSE_ON_TURN
    state["is_redirecting"] = bool(redirecting)


def schedule_redirect_to_center(push_distance=REDIRECT_STEP):
    """Redirect the dot toward the screen center for a short distance."""
    x, y = dot.position()
    angle_to_center = dot.towards(0, 0)
    if abs(x) < 1 and abs(y) < 1:
        a, d = pick_new_direction_and_distance()
        start_new_movement(a, d, redirecting=False)
    else:
        start_new_movement(angle_to_center, push_distance, redirecting=True)


def frame_step():
    """Advance the animation by one frame and schedule the next frame."""
    now = time.time()

    if now < state["paused_until"]:
        screen.update()
        screen.ontimer(frame_step, FRAME_DELAY_MS)
        return

    if state["target_angle"] is None or state["remaining_distance"] <= 0:
        a, d = pick_new_direction_and_distance()
        start_new_movement(a, d)
        screen.update()
        screen.ontimer(frame_step, FRAME_DELAY_MS)
        return

    step = min(STEP_SIZE, state["remaining_distance"])
    dot.setheading(state["target_angle"])
    dot.forward(step)
    state["remaining_distance"] -= step

    x, y = dot.position()
    if abs(x) > max_x or abs(y) > max_y:
        schedule_redirect_to_center(push_distance=REDIRECT_STEP)

    screen.update()
    screen.ontimer(frame_step, FRAME_DELAY_MS)


initial_angle, initial_distance = pick_new_direction_and_distance()
start_new_movement(initial_angle, initial_distance)
frame_step()

try:
    turtle.mainloop()
except turtle.Terminator:
    pass
