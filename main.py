import turtle
import random
import time

# --- Config ---
WIDTH, HEIGHT = 800, 600
BG_COLOR = "black"
DOT_COLOR = "cyan"
STEP_SIZE = 3            # pixels moved per animation step
FRAME_DELAY_MS = 16      # ms between frames (~60 FPS)
PAUSE_ON_TURN = 0.35     # seconds to pause when a new direction is chosen
MIN_DISTANCE = 100
MAX_DISTANCE = 600
EDGE_MARGIN = 20         # keep this far from edges before redirecting
REDIRECT_STEP = 150      # how far to move back toward center when near edge

# 1. Screen setup
screen = turtle.Screen()
screen.title("Random Moving Dot")
screen.bgcolor(BG_COLOR)
screen.setup(width=WIDTH, height=HEIGHT)
screen.tracer(0)  # we'll call update manually

# 2. Create the dot
dot = turtle.Turtle()
dot.hideturtle()
dot.shape("circle")
dot.color(DOT_COLOR)
dot.penup()
dot.speed(0)
dot.showturtle()

# Safe movement boundaries (centered coordinates)
max_x = screen.window_width() / 2 - EDGE_MARGIN
max_y = screen.window_height() / 2 - EDGE_MARGIN

# State variables for the animation loop
state = {
    "target_angle": None,        # degrees
    "remaining_distance": 0.0,   # pixels to travel before picking a new direction
    "paused_until": 0.0,         # time.time() until which we're paused
    "is_redirecting": False      # whether currently redirecting to center
}

def pick_new_direction_and_distance():
    """Return (angle_degrees, distance_pixels)."""
    angle = random.uniform(0, 360)
    distance = random.uniform(MIN_DISTANCE, MAX_DISTANCE)
    return angle, distance

def start_new_movement(angle_deg, distance, redirecting=False):
    """Initialize movement state for a new direction."""
    state["target_angle"] = angle_deg % 360
    state["remaining_distance"] = float(distance)
    state["paused_until"] = time.time() + PAUSE_ON_TURN
    state["is_redirecting"] = bool(redirecting)

def schedule_redirect_to_center(push_distance=REDIRECT_STEP):
    """Point toward center and set a short movement distance to move dot back in bounds."""
    x, y = dot.position()
    angle_to_center = dot.towards(0, 0)
    # If at center already, just pick a new direction
    if abs(x) < 1 and abs(y) < 1:
        a, d = pick_new_direction_and_distance()
        start_new_movement(a, d, redirecting=False)
    else:
        start_new_movement(angle_to_center, push_distance, redirecting=True)

def frame_step():
    """Called every FRAME_DELAY_MS milliseconds to advance animation."""
    now = time.time()

    # If paused (brief pause on each new direction), just update screen and reschedule
    if now < state["paused_until"]:
        screen.update()
        screen.ontimer(frame_step, FRAME_DELAY_MS)
        return

    # If no target, pick one
    if state["target_angle"] is None or state["remaining_distance"] <= 0:
        a, d = pick_new_direction_and_distance()
        start_new_movement(a, d)
        screen.update()
        screen.ontimer(frame_step, FRAME_DELAY_MS)
        return

    # Move one step toward the target, but don't exceed remaining_distance
    step = min(STEP_SIZE, state["remaining_distance"])
    dot.setheading(state["target_angle"])
    dot.forward(step)
    state["remaining_distance"] -= step

    x, y = dot.position()
    # If out of safe bounds (or very close), start redirect to center
    if abs(x) > max_x or abs(y) > max_y:
        schedule_redirect_to_center(push_distance=REDIRECT_STEP)

    screen.update()
    screen.ontimer(frame_step, FRAME_DELAY_MS)

# Initialize and start
initial_angle, initial_distance = pick_new_direction_and_distance()
start_new_movement(initial_angle, initial_distance)
frame_step()  # start the recurring loop

# Keep window open until closed by user
try:
    turtle.mainloop()
except turtle.Terminator:
    pass
