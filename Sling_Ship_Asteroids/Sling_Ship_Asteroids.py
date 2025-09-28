import pygame
import sys
import math
import random
from pygame import mixer

# Initialize pygame
pygame.init()
mixer.init()

# Screen dimensions
WIDTH, HEIGHT = 1000, 700
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Sling-Ship Asteroids")

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 50, 50)
GREEN = (50, 255, 50)
BLUE = (50, 100, 255)
YELLOW = (255, 255, 50)
PURPLE = (180, 70, 220)
ORANGE = (255, 150, 50)

# Game variables
clock = pygame.time.Clock()
FPS = 60
score = 0
lives = 3
level = 1
game_over = False
level_complete = False
asteroids_destroyed = 0
asteroids_to_destroy = 5  # Asteroids to destroy to complete level

# Create images programmatically to avoid file loading issues
def create_ship_image():
    surf = pygame.Surface((60, 60), pygame.SRCALPHA)
    # Ship body
    pygame.draw.polygon(surf, BLUE, [(30, 0), (0, 60), (60, 60)])
    # Ship cockpit
    pygame.draw.circle(surf, YELLOW, (30, 40), 15)
    # Ship details
    pygame.draw.polygon(surf, (30, 70, 200), [(30, 10), (20, 30), (40, 30)])
    return surf

def create_asteroid_image(size):
    surf = pygame.Surface((size, size), pygame.SRCALPHA)
    # Create rocky asteroid appearance
    pygame.draw.circle(surf, (150, 150, 150), (size//2, size//2), size//2)
    
    # Add crater details
    for _ in range(size//10):
        x = random.randint(size//4, 3*size//4)
        y = random.randint(size//4, 3*size//4)
        crater_size = random.randint(2, size//8)
        brightness = random.randint(100, 140)
        pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), crater_size)
    
    return surf

def create_projectile_image():
    surf = pygame.Surface((20, 20), pygame.SRCALPHA)
    # Projectile with glow effect
    pygame.draw.circle(surf, YELLOW, (10, 10), 8)
    pygame.draw.circle(surf, ORANGE, (10, 10), 5)
    return surf

def create_background_image():
    surf = pygame.Surface((WIDTH, HEIGHT))
    surf.fill(BLACK)
    
    # Create starfield
    for _ in range(200):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        size = random.randint(1, 3)
        brightness = random.randint(150, 255)
        pygame.draw.circle(surf, (brightness, brightness, brightness), (x, y), size)
    
    # Add some nebulae
    for _ in range(5):
        x = random.randint(0, WIDTH)
        y = random.randint(0, HEIGHT)
        radius = random.randint(50, 200)
        color = random.choice([(50, 50, 100), (100, 50, 100), (50, 100, 100)])
        for r in range(radius, 0, -10):
            alpha = max(0, 50 - r//4)
            s = pygame.Surface((r*2, r*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (*color, alpha), (r, r), r)
            surf.blit(s, (x-r, y-r))
    
    return surf

# Create game assets
ship_img = create_ship_image()
asteroid_imgs = [
    create_asteroid_image(80),
    create_asteroid_image(70),
    create_asteroid_image(60)
]
projectile_img = create_projectile_image()
background_img = create_background_image()

# Create simple sound effects programmatically
def create_beep_sound(frequency=440, duration=100):
    sample_rate = 44100
    n_samples = int(round(duration * 0.001 * sample_rate))
    buf = numpy.zeros((n_samples, 2), dtype=numpy.int16)
    max_sample = 2**(16 - 1) - 1
    
    for s in range(n_samples):
        t = float(s) / sample_rate
        buf[s][0] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
        buf[s][1] = int(round(max_sample * math.sin(2 * math.pi * frequency * t)))
    
    return pygame.sndarray.make_sound(buf)

# Try to create sounds, fallback to silent sounds if numpy not available
try:
    import numpy
    shoot_sound = create_beep_sound(800, 50)
    explosion_sound = create_beep_sound(200, 200)
    level_up_sound = create_beep_sound(1000, 300)
except:
    # Create silent sounds as fallback
    shoot_sound = mixer.Sound(buffer=bytearray())
    explosion_sound = mixer.Sound(buffer=bytearray())
    level_up_sound = mixer.Sound(buffer=bytearray())

# Fonts
try:
    font_large = pygame.font.SysFont("arial", 48, bold=True)
    font_medium = pygame.font.SysFont("arial", 36)
    font_small = pygame.font.SysFont("arial", 24)
except:
    # Fallback fonts
    font_large = pygame.font.Font(None, 48)
    font_medium = pygame.font.Font(None, 36)
    font_small = pygame.font.Font(None, 24)

class Player:
    def __init__(self):
        self.x = WIDTH // 2
        self.y = HEIGHT // 2
        self.radius = 30
        self.angle = 0
        self.dragging = False
        self.drag_start = (0, 0)
        self.drag_end = (0, 0)
        self.power = 0
        self.max_power = 200
        
    def update(self, mouse_pos, mouse_click, mouse_release):
        # Calculate angle to mouse position
        dx = mouse_pos[0] - self.x
        dy = mouse_pos[1] - self.y
        self.angle = math.atan2(dy, dx)
        
        # Handle dragging for aiming and power
        if mouse_click and not self.dragging:
            self.dragging = True
            self.drag_start = mouse_pos
        elif self.dragging:
            self.drag_end = mouse_pos
            dx = self.drag_start[0] - self.drag_end[0]
            dy = self.drag_start[1] - self.drag_end[1]
            self.power = min(math.sqrt(dx*dx + dy*dy), self.max_power)
            
        if mouse_release and self.dragging:
            self.dragging = False
            return True  # Fire projectile
        return False
    
    def draw(self, screen):
        # Draw ship
        rotated_ship = pygame.transform.rotate(ship_img, math.degrees(-self.angle) - 90)
        ship_rect = rotated_ship.get_rect(center=(self.x, self.y))
        screen.blit(rotated_ship, ship_rect)
        
        # Draw aiming line when dragging
        if self.dragging:
            # Calculate direction vector
            dx = math.cos(self.angle) * self.power
            dy = math.sin(self.angle) * self.power
            
            # Draw line from ship to drag end
            pygame.draw.line(screen, RED, (self.x, self.y), 
                            (self.x + dx, self.y + dy), 3)
            
            # Draw power indicator
            power_percent = self.power / self.max_power
            color = GREEN if power_percent < 0.7 else YELLOW if power_percent < 0.9 else RED
            pygame.draw.rect(screen, color, (20, HEIGHT - 40, power_percent * 200, 20))
            pygame.draw.rect(screen, WHITE, (20, HEIGHT - 40, 200, 20), 2)

class Projectile:
    def __init__(self, x, y, angle, power):
        self.x = x
        self.y = y
        self.radius = 10
        self.speed = power * 0.1 + 5  # Base speed plus power factor
        self.vx = math.cos(angle) * self.speed
        self.vy = math.sin(angle) * self.speed
        self.lifetime = 120  # Frames until projectile disappears
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.lifetime -= 1
        
        # Bounce off walls
        if self.x < self.radius or self.x > WIDTH - self.radius:
            self.vx *= -1
        if self.y < self.radius or self.y > HEIGHT - self.radius:
            self.vy *= -1
            
        return self.lifetime <= 0 or self.x < 0 or self.x > WIDTH or self.y < 0 or self.y > HEIGHT
    
    def draw(self, screen):
        # Draw projectile with glow effect
        pygame.draw.circle(screen, YELLOW, (int(self.x), int(self.y)), self.radius)
        pygame.draw.circle(screen, ORANGE, (int(self.x), int(self.y)), self.radius - 3)

class Asteroid:
    def __init__(self, size=3):
        self.size = size  # 3=large, 2=medium, 1=small
        self.radius = size * 15 + 10  # Radius based on size
        
        # Spawn from edges
        side = random.randint(0, 3)
        if side == 0:  # Top
            self.x = random.randint(0, WIDTH)
            self.y = -self.radius
        elif side == 1:  # Right
            self.x = WIDTH + self.radius
            self.y = random.randint(0, HEIGHT)
        elif side == 2:  # Bottom
            self.x = random.randint(0, WIDTH)
            self.y = HEIGHT + self.radius
        else:  # Left
            self.x = -self.radius
            self.y = random.randint(0, HEIGHT)
            
        # Move toward center with some randomness
        dx = WIDTH/2 - self.x + random.uniform(-100, 100)
        dy = HEIGHT/2 - self.y + random.uniform(-100, 100)
        dist = math.sqrt(dx*dx + dy*dy)
        speed = random.uniform(1.0, 3.0) / size  # Smaller asteroids are faster
        self.vx = (dx / dist) * speed
        self.vy = (dy / dist) * speed
        
        # Rotation
        self.rotation = 0
        self.rotation_speed = random.uniform(-0.05, 0.05)
        self.img = random.choice(asteroid_imgs)
        
    def update(self):
        self.x += self.vx
        self.y += self.vy
        self.rotation += self.rotation_speed
        
        # Wrap around screen edges
        if self.x < -self.radius:
            self.x = WIDTH + self.radius
        elif self.x > WIDTH + self.radius:
            self.x = -self.radius
        if self.y < -self.radius:
            self.y = HEIGHT + self.radius
        elif self.y > HEIGHT + self.radius:
            self.y = -self.radius
            
    def draw(self, screen):
        # Draw rotating asteroid
        rotated_asteroid = pygame.transform.rotate(self.img, math.degrees(self.rotation))
        rect = rotated_asteroid.get_rect(center=(int(self.x), int(self.y)))
        screen.blit(rotated_asteroid, rect)
        
    def split(self):
        # Create smaller asteroids when hit
        if self.size > 1:
            return [Asteroid(self.size - 1) for _ in range(2)]
        return []

class Explosion:
    def __init__(self, x, y, size):
        self.x = x
        self.y = y
        self.size = size
        self.radius = size * 10
        self.particles = []
        self.lifetime = 20
        
        # Create explosion particles
        for _ in range(size * 10):
            angle = random.uniform(0, math.pi * 2)
            speed = random.uniform(1, 5)
            lifetime = random.randint(10, 30)
            self.particles.append({
                'x': x,
                'y': y,
                'vx': math.cos(angle) * speed,
                'vy': math.sin(angle) * speed,
                'lifetime': lifetime,
                'size': random.randint(2, 5)
            })
    
    def update(self):
        self.lifetime -= 1
        for p in self.particles:
            p['x'] += p['vx']
            p['y'] += p['vy']
            p['lifetime'] -= 1
            
        # Remove dead particles
        self.particles = [p for p in self.particles if p['lifetime'] > 0]
        
        return self.lifetime <= 0 and len(self.particles) == 0
    
    def draw(self, screen):
        for p in self.particles:
            alpha = min(255, p['lifetime'] * 25)
            color = (255, random.randint(100, 200), 50, alpha)
            pygame.draw.circle(screen, color, (int(p['x']), int(p['y'])), p['size'])

class Star:
    def __init__(self):
        self.x = random.randint(0, WIDTH)
        self.y = random.randint(0, HEIGHT)
        self.size = random.uniform(0.1, 2.0)
        self.speed = random.uniform(0.1, 0.5)
        self.brightness = random.randint(100, 255)
        
    def update(self):
        self.y += self.speed
        if self.y > HEIGHT:
            self.y = 0
            self.x = random.randint(0, WIDTH)
            
    def draw(self, screen):
        color = (self.brightness, self.brightness, self.brightness)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), self.size)

def check_collision(obj1, obj2):
    # Simple circle-based collision detection
    dx = obj1.x - obj2.x
    dy = obj1.y - obj2.y
    distance = math.sqrt(dx*dx + dy*dy)
    return distance < (obj1.radius + obj2.radius)

def spawn_asteroids(count, size=3):
    return [Asteroid(size) for _ in range(count)]

def draw_text(screen, text, font, color, x, y, align="center"):
    text_surface = font.render(text, True, color)
    text_rect = text_surface.get_rect()
    
    if align == "center":
        text_rect.center = (x, y)
    elif align == "left":
        text_rect.midleft = (x, y)
    else:  # right
        text_rect.midright = (x, y)
        
    screen.blit(text_surface, text_rect)
    return text_rect

def main():
    global score, lives, level, game_over, level_complete, asteroids_destroyed, asteroids_to_destroy
    
    # Game objects
    player = Player()
    projectiles = []
    asteroids = spawn_asteroids(3 + level, 3)  # More asteroids at higher levels
    explosions = []
    stars = [Star() for _ in range(100)]
    
    # Game loop
    running = True
    mouse_click = False
    mouse_release = False
    
    while running:
        # Event handling
        mouse_click = False
        mouse_release = False
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    running = False
                elif event.key == pygame.K_r and game_over:
                    # Reset game
                    score = 0
                    lives = 3
                    level = 1
                    game_over = False
                    level_complete = False
                    asteroids_destroyed = 0
                    asteroids_to_destroy = 5
                    asteroids = spawn_asteroids(3 + level, 3)
                    projectiles = []
                    explosions = []
                elif event.key == pygame.K_SPACE and level_complete:
                    # Start next level
                    level += 1
                    asteroids_to_destroy = 5 + level * 2
                    asteroids_destroyed = 0
                    level_complete = False
                    asteroids = spawn_asteroids(3 + level, 3)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:  # Left mouse button
                    mouse_click = True
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1:  # Left mouse button
                    mouse_release = True
        
        # Get mouse position
        mouse_pos = pygame.mouse.get_pos()
        
        # Update game state if not game over
        if not game_over and not level_complete:
            # Update player and check for projectile firing
            if player.update(mouse_pos, mouse_click, mouse_release):
                # Fire projectile
                projectiles.append(Projectile(player.x, player.y, player.angle, player.power))
                try:
                    shoot_sound.play()
                except:
                    pass  # Sound might not be available
            
            # Update projectiles
            projectiles_to_remove = []
            for p in projectiles:
                if p.update():
                    projectiles_to_remove.append(p)
            
            for p in projectiles_to_remove:
                if p in projectiles:
                    projectiles.remove(p)
            
            # Update asteroids
            for asteroid in asteroids:
                asteroid.update()
                
                # Check collision with player
                if check_collision(asteroid, player):
                    lives -= 1
                    explosions.append(Explosion(player.x, player.y, 3))
                    try:
                        explosion_sound.play()
                    except:
                        pass
                    
                    # Remove the asteroid that hit the player
                    if asteroid in asteroids:
                        asteroids.remove(asteroid)
                    
                    if lives <= 0:
                        game_over = True
            
            # Check collisions between projectiles and asteroids
            projectiles_to_remove = []
            asteroids_to_remove = []
            new_asteroids = []
            
            for projectile in projectiles:
                for asteroid in asteroids:
                    if check_collision(projectile, asteroid):
                        projectiles_to_remove.append(projectile)
                        asteroids_to_remove.append(asteroid)
                        
                        # Create explosion
                        explosions.append(Explosion(asteroid.x, asteroid.y, asteroid.size))
                        try:
                            explosion_sound.play()
                        except:
                            pass
                        
                        # Split asteroid if it's large enough
                        new_asteroids.extend(asteroid.split())
                        
                        # Update score
                        score += asteroid.size * 100
                        asteroids_destroyed += 1
                        
                        # Check if level is complete
                        if asteroids_destroyed >= asteroids_to_destroy:
                            level_complete = True
                            try:
                                level_up_sound.play()
                            except:
                                pass
                        
                        break
            
            # Remove collided objects
            for p in projectiles_to_remove:
                if p in projectiles:
                    projectiles.remove(p)
            
            for a in asteroids_to_remove:
                if a in asteroids:
                    asteroids.remove(a)
            
            # Add new asteroids from splits
            asteroids.extend(new_asteroids)
            
            # Update explosions
            explosions_to_remove = []
            for e in explosions:
                if e.update():
                    explosions_to_remove.append(e)
            
            for e in explosions_to_remove:
                if e in explosions:
                    explosions.remove(e)
            
            # Update stars for parallax background
            for star in stars:
                star.update()
        
        # Draw everything
        screen.blit(background_img, (0, 0))
        
        # Draw stars
        for star in stars:
            star.draw(screen)
        
        # Draw game objects
        for asteroid in asteroids:
            asteroid.draw(screen)
            
        for projectile in projectiles:
            projectile.draw(screen)
            
        for explosion in explosions:
            explosion.draw(screen)
            
        player.draw(screen)
        
        # Draw UI
        # Score and lives
        draw_text(screen, f"Score: {score}", font_small, WHITE, 20, 20, "left")
        draw_text(screen, f"Lives: {lives}", font_small, WHITE, WIDTH - 20, 20, "right")
        draw_text(screen, f"Level: {level}", font_small, WHITE, WIDTH // 2, 20, "center")
        
        # Asteroids destroyed progress
        progress_text = f"Asteroids: {asteroids_destroyed}/{asteroids_to_destroy}"
        draw_text(screen, progress_text, font_small, WHITE, WIDTH // 2, 60, "center")
        
        # Game over screen
        if game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "GAME OVER", font_large, RED, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, f"Final Score: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(screen, "Press R to Restart", font_medium, GREEN, WIDTH // 2, HEIGHT // 2 + 80)
        
        # Level complete screen
        if level_complete:
            overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            draw_text(screen, "LEVEL COMPLETE!", font_large, GREEN, WIDTH // 2, HEIGHT // 2 - 50)
            draw_text(screen, f"Score: {score}", font_medium, WHITE, WIDTH // 2, HEIGHT // 2 + 20)
            draw_text(screen, "Press SPACE for Next Level", font_medium, YELLOW, WIDTH // 2, HEIGHT // 2 + 80)
        
        # Instructions
        if not game_over and not level_complete and len(projectiles) == 0 and not player.dragging:
            draw_text(screen, "Click and drag to aim, release to fire", font_small, YELLOW, WIDTH // 2, HEIGHT - 40)
        
        # Update display
        pygame.display.flip()
        
        # Control frame rate
        clock.tick(FPS)
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()