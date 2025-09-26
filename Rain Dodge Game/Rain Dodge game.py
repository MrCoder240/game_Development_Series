import pygame
import time
import random
pygame.font.init() # Initialize the font module

WIDTH, HEIGHT = 1000, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Rain Dodge") # Set the window title


BG = pygame.Surface((WIDTH, HEIGHT))
BG.fill((0, 0, 0))                         # Black background

PLAYER_WIDTH = 40        
PLAYER_HEIGHT = 60

PLAYER_VEL = 5
STAR_WIDTH = 10
STAR_HEIGHT = 20
STAR_VEL = 3

FONT = pygame.font.SysFont("comicsans", 30)  # Use a common font available on most systems


def draw(player, elapsed_time, stars): # Draw the game window
    WIN.blit(BG, (0, 0))                        # Draw the background

    time_text = FONT.render(f"Time: {round(elapsed_time)}s", 1, "white")       # Render the time text
    WIN.blit(time_text, (10, 10))                                              # Draw the time text

    pygame.draw.rect(WIN, "red", player)                                       # Draw the player

    for star in stars:                           # Draw the stars
        pygame.draw.rect(WIN, "white", star)           # Draw each star

    pygame.display.update()                             # Update the display


def main():               
    run = True                            # Main game loop

    player = pygame.Rect(200, HEIGHT - PLAYER_HEIGHT, PLAYER_WIDTH, PLAYER_HEIGHT)      
    clock = pygame.time.Clock()                                     # Clock to control frame rate
    start_time = time.time()                                        # Record the start time
    elapsed_time = 0

    star_add_increment = 2000   # Initial time interval to add stars (in milliseconds)
    star_count = 0            # Counter to track time for adding stars

    stars = []         # List to hold star rectangles
    hit = False               # Flag to indicate if the player has been hit

    while run:
        star_count += clock.tick(60)                          # Maintain 60 FPS and get the time since last tick
        elapsed_time = time.time() - start_time

        if star_count > star_add_increment:                  # Time to add new stars
            for _ in range(3):
                star_x = random.randint(0, WIDTH - STAR_WIDTH)
                star = pygame.Rect(star_x, -STAR_HEIGHT, STAR_WIDTH, STAR_HEIGHT) # Create a new star rectangle
                stars.append(star)

            star_add_increment = max(200, star_add_increment - 50)   # Decrease interval to increase difficulty
            star_count = 0

        for event in pygame.event.get():      # Event handling
            if event.type == pygame.QUIT:                                      # If the window is closed
                run = False
                break                         # Exit the game loop
                                                                    
        keys = pygame.key.get_pressed()                                 # Get the current state of all keys
        if keys[pygame.K_LEFT] and player.x - PLAYER_VEL >= 0:
            player.x -= PLAYER_VEL
        if keys[pygame.K_RIGHT] and player.x + PLAYER_VEL + player.width <= WIDTH:
            player.x += PLAYER_VEL

        for star in stars[:]:                        # Update star positions and check for collisions
            star.y += STAR_VEL
            if star.y > HEIGHT:
                stars.remove(star)                   # Remove stars that have moved off the screen
            elif star.y + star.height >= player.y and star.colliderect(player):                              # Check for collision with player
                stars.remove(star)
                hit = True
                break

        if hit:                                                                         # If the player has been hit
            lost_text = FONT.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()
            pygame.time.delay(4000)
            break

        draw(player, elapsed_time, stars)                      # Draw everything    

    pygame.quit()                # Quit pygame


if __name__ == "__main__":
    main()