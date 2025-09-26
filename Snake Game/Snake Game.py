"""
Snake Game Upgrade
Enhanced version of the classic Snake game with improved visuals, gameplay features, and code organization.
"""

import tkinter
import random  

# Game configuration constants
ROWS = 25
COLS = 25
TILE_SIZE = 25

WINDOW_WIDTH = TILE_SIZE * COLS  # 25*25 = 625
WINDOW_HEIGHT = TILE_SIZE * ROWS  # 25*25 = 625

# Game colors
BACKGROUND_COLOR = "black"
SNAKE_HEAD_COLOR = "lime green"
SNAKE_BODY_COLOR = "green"
FOOD_COLOR = "red"
TEXT_COLOR = "white"
GAME_OVER_COLOR = "red"

class Tile:
    """
    Represents a single tile/position in the game grid.
    Used for snake segments and food items.
    """
    def __init__(self, x, y):
        self.x = x
        self.y = y

def create_window():
    """
    Creates and configures the main game window.
    Centers the window on the screen and sets up the canvas.
    """
    # Create main window
    window = tkinter.Tk()
    window.title("Snake Game")
    window.resizable(False, False)
    
    # Create canvas for drawing game elements
    canvas = tkinter.Canvas(window, bg=BACKGROUND_COLOR, width=WINDOW_WIDTH, 
                           height=WINDOW_HEIGHT, borderwidth=0, highlightthickness=0)
    canvas.pack()
    window.update()
    
    # Center the window on screen
    center_window(window)
    
    return window, canvas

def center_window(window):
    """
    Centers the game window on the screen.
    """
    window_width = window.winfo_width()
    window_height = window.winfo_height()
    screen_width = window.winfo_screenwidth()
    screen_height = window.winfo_screenheight()
    
    window_x = int((screen_width/2) - (window_width/2))
    window_y = int((screen_height/2) - (window_height/2))
    
    # Format: "(width)x(height)+(x)+(y)"
    window.geometry(f"{window_width}x{window_height}+{window_x}+{window_y}")

def initialize_game():
    """
    Initializes all game variables to their starting state.
    """
    global snake, food, velocityX, velocityY, snake_body, game_over, score
    
    # Snake starts in the middle of the grid
    snake = Tile(TILE_SIZE * (COLS // 2), TILE_SIZE * (ROWS // 2))
    
    # Place first food at random position
    food = Tile(
        random.randint(0, COLS-1) * TILE_SIZE,
        random.randint(0, ROWS-1) * TILE_SIZE
    )
    
    # Initial movement direction (stationary)
    velocityX = 0
    velocityY = 0
    
    # Snake body starts empty (just the head)
    snake_body = []
    
    # Game state
    game_over = False
    score = 0

def change_direction(e):
    """
    Handles keyboard input to change snake direction.
    Prevents 180-degree turns that would cause immediate collision.
    """
    global velocityX, velocityY, game_over
    
    # Ignore input if game is over
    if game_over:
        return
    
    # Map key presses to direction changes with collision prevention
    if e.keysym == "Up" and velocityY != 1:      # Can't turn up if moving down
        velocityX = 0
        velocityY = -1
    elif e.keysym == "Down" and velocityY != -1: # Can't turn down if moving up
        velocityX = 0
        velocityY = 1
    elif e.keysym == "Left" and velocityX != 1:  # Can't turn left if moving right
        velocityX = -1
        velocityY = 0
    elif e.keysym == "Right" and velocityX != -1: # Can't turn right if moving left
        velocityX = 1
        velocityY = 0
    elif e.keysym == "r" or e.keysym == "R":     # Restart game with 'R' key
        reset_game()

def reset_game():
    """
    Resets the game to its initial state after game over.
    """
    global game_over
    if game_over:
        initialize_game()

def wrap_around_walls():
    """
    Implements wrap-around behavior when snake hits walls.
    Snake will appear from the opposite side of the screen.
    """
    global snake
    
    # Wrap around horizontal boundaries
    if snake.x < 0:
        snake.x = WINDOW_WIDTH - TILE_SIZE  # Appear from right side
    elif snake.x >= WINDOW_WIDTH:
        snake.x = 0  # Appear from left side
    
    # Wrap around vertical boundaries
    if snake.y < 0:
        snake.y = WINDOW_HEIGHT - TILE_SIZE  # Appear from bottom
    elif snake.y >= WINDOW_HEIGHT:
        snake.y = 0  # Appear from top

def move():
    """
    Updates the game state by moving the snake and checking for collisions.
    Implements wrap-around wall behavior instead of game over on wall collision.
    """
    global snake, food, snake_body, game_over, score
    
    # Don't update if game is over
    if game_over:
        return
    
    # Check wall collisions and implement wrap-around
    wrap_around_walls()
    
    # Check self-collision (game over only on self-collision)
    for tile in snake_body:
        if snake.x == tile.x and snake.y == tile.y:
            game_over = True
            return
    
    # Check food collision
    if snake.x == food.x and snake.y == food.y:
        # Add new segment to snake body
        snake_body.append(Tile(food.x, food.y))
        
        # Generate new food at random position (avoiding snake body)
        while True:
            food.x = random.randint(0, COLS-1) * TILE_SIZE
            food.y = random.randint(0, ROWS-1) * TILE_SIZE
            
            # Ensure food doesn't spawn on snake
            food_on_snake = False
            if snake.x == food.x and snake.y == food.y:
                food_on_snake = True
            for tile in snake_body:
                if tile.x == food.x and tile.y == food.y:
                    food_on_snake = True
                    break
            
            if not food_on_snake:
                break
        
        score += 1
    
    # Update snake body positions (move each segment to position of previous segment)
    for i in range(len(snake_body)-1, -1, -1):
        tile = snake_body[i]
        if i == 0:  # First segment follows the head
            tile.x = snake.x
            tile.y = snake.y
        else:       # Other segments follow the previous segment
            prev_tile = snake_body[i-1]
            tile.x = prev_tile.x
            tile.y = prev_tile.y
    
    # Move snake head
    snake.x += velocityX * TILE_SIZE
    snake.y += velocityY * TILE_SIZE

def draw():
    """
    Draws all game elements on the canvas and schedules the next frame.
    """
    global snake, food, snake_body, game_over, score
    
    # Update game state
    move()
    
    # Clear canvas
    canvas.delete("all")
    
    # Draw grid (optional visual enhancement)
    draw_grid()
    
    # Draw food
    canvas.create_rectangle(food.x, food.y, food.x + TILE_SIZE, food.y + TILE_SIZE, 
                           fill=FOOD_COLOR, outline="dark red", width=2)
    
    # Draw snake body segments
    for i, tile in enumerate(snake_body):
        # Use slightly different color for body segments
        color = SNAKE_BODY_COLOR if i % 2 == 0 else "light green"
        canvas.create_rectangle(tile.x, tile.y, tile.x + TILE_SIZE, tile.y + TILE_SIZE, 
                               fill=color, outline="dark green", width=1)
    
    # Draw snake head (different color to distinguish from body)
    canvas.create_rectangle(snake.x, snake.y, snake.x + TILE_SIZE, snake.y + TILE_SIZE, 
                           fill=SNAKE_HEAD_COLOR, outline="dark green", width=2)
    
    # Draw game information
    if game_over:
        # Game over screen (only from self-collision now)
        canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 - 30, 
                          font="Arial 25 bold", text="GAME OVER", fill=GAME_OVER_COLOR)
        canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 10, 
                          font="Arial 18", text=f"Final Score: {score}", fill=TEXT_COLOR)
        canvas.create_text(WINDOW_WIDTH/2, WINDOW_HEIGHT/2 + 40, 
                          font="Arial 12", text="Press 'R' to Restart", fill=TEXT_COLOR)
    else:
        # In-game score display
        canvas.create_text(50, 15, font="Arial 12 bold", 
                          text=f"Score: {score}", fill=TEXT_COLOR)
        canvas.create_text(WINDOW_WIDTH - 50, 15, font="Arial 10", 
                          text=f"Length: {len(snake_body) + 1}", fill=TEXT_COLOR)
        
        # Display wrap-around feature indicator
        canvas.create_text(WINDOW_WIDTH/2, 15, font="Arial 8", 
                          text="Wrap-Around Walls: ON", fill="yellow")
    
    # Schedule next frame (adjust speed based on score for increasing difficulty)
    speed = max(50, 150 - min(score, 10) * 5)  # Speed increases with score, up to a limit
    window.after(speed, draw)

def draw_grid():
    """
    Draws a subtle grid on the game background for better visual reference.
    """
    for i in range(0, WINDOW_WIDTH, TILE_SIZE):
        canvas.create_line(i, 0, i, WINDOW_HEIGHT, fill="#111111", width=1)
    for i in range(0, WINDOW_HEIGHT, TILE_SIZE):
        canvas.create_line(0, i, WINDOW_WIDTH, i, fill="#111111", width=1)

# Initialize game
window, canvas = create_window()
initialize_game()

# Start game loop
draw()

# Bind keyboard events
window.bind("<KeyRelease>", change_direction)  # Direction changes
window.bind("<r>", change_direction)           # Restart game
window.bind("<R>", change_direction)           # Restart game (caps lock)

# Start the main event loop
window.mainloop()                