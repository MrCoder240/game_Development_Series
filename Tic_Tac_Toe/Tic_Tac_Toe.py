
"""
Advanced Tic Tac Toe — Modern Animated Menu with Minecraft-style Pixel Font
- Vibrant multi-color gradient background
- Animated buttons (slide-in, hover pulse, glow)
- Minecraft-like pixel font for title & buttons
- Looping background music loaded from MP3
- Click/win/lose remain WAV
- Robust fallback handling and detailed inline comments
"""

import pygame
import sys
import random
import math
from pygame import mixer

# ----------------------------
# Initialization
# ----------------------------
pygame.init()
# Initialize mixer: best-effort; protect against initialization errors
try:
    mixer.init(frequency=44100, size=-16, channels=2, buffer=512)
except Exception as e:
    print("Warning: pygame.mixer failed to initialize:", e)

# ----------------------------
# Configuration & Constants
# ----------------------------
WIDTH, HEIGHT = 900, 650
BOARD_SIZE = 450
CELL_SIZE = BOARD_SIZE // 3
FPS = 60

# Files (edit names if you have different)
FONT_FILE = "minecraft.ttf"   # <-- Put your Minecraft-like pixel font here
BG_MUSIC_FILE = "bg_music.mp3" # <-- Background music (MP3, loops)
SOUND_FILES = {
    "click": "click.wav",
    "win": "win.wav",
    "lose": "lose.wav",
}

# Colors (RGB)
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
BLUE = (30, 144, 255)
RED = (220, 20, 60)
GREEN = (34, 139, 34)
GRAY = (200, 200, 200)
LIGHT_GRAY = (240, 240, 240)

# Game states
MAIN_MENU = 0
GAME_MODE_SELECT = 1
DIFFICULTY_SELECT = 2
IN_GAME = 3
GAME_OVER = 4

# Pygame setup
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Tic Tac Toe ")
clock = pygame.time.Clock()

# ----------------------------
# Font loading (Minecraft-like pixel font with graceful fallback)
# ----------------------------
def load_font(path, size, fallback_name="arial", bold=False):
    """
    Try to load a TTF from path. If not found or fails, fallback to a system font.
    Returns a pygame.font.Font instance.
    """
    try:
        font = pygame.font.Font(path, size)
        return font
    except Exception:
        print(f"Note: Could not load font '{path}'. Falling back to system font '{fallback_name}'.")
        return pygame.font.SysFont(fallback_name, size, bold=bold)

# Sizes chosen: Title big, buttons medium, game text medium
title_font = load_font(FONT_FILE, 72, fallback_name="arial", bold=True)
button_font = load_font(FONT_FILE, 30, fallback_name="arial", bold=True)
game_font = load_font(FONT_FILE, 32, fallback_name="arial", bold=True)
info_font = load_font(FONT_FILE, 20, fallback_name="arial")

# ----------------------------
# Sound manager (SFX + MP3 background)
# ----------------------------
class SoundManager:
    """
    Handles loading SFX (wav) and background music (mp3).
    - SFX: loaded as Sound objects with silent fallbacks
    - Background music: uses pygame.mixer.music, loops infinitely
    """
    def __init__(self):
        self.sounds = {}
        self.bg_loaded = False
        self.load_sfx()
        self.load_background_music(BG_MUSIC_FILE)

    def load_sfx(self):
        """Load WAV sound effects; if missing, use a silent fallback or None."""
        for key, filename in SOUND_FILES.items():
            try:
                self.sounds[key] = mixer.Sound(filename)
            except Exception as e:
                print(f"Note: Could not load SFX '{filename}' for '{key}': {e}. Using silent fallback.")
                # Best-effort silent fallback: small buffer; if that fails set None
                try:
                    self.sounds[key] = mixer.Sound(buffer=bytearray([0]*8))
                except Exception:
                    self.sounds[key] = None

    def load_background_music(self, filename):
        """Load MP3 background music via mixer.music; mark whether loaded."""
        try:
            mixer.music.load(filename)
            self.bg_loaded = True
        except Exception as e:
            print(f"Note: Could not load background music '{filename}': {e}. Background music disabled.")
            self.bg_loaded = False

    def play(self, key):
        """Play a sound effect safely (if available)."""
        try:
            s = self.sounds.get(key)
            if s:
                s.play()
        except Exception as e:
            print(f"Warning: Error playing sound '{key}': {e}")

    def start_background_music(self, loops=-1, fade_ms=800):
        """Start background music loop (infinite by default)."""
        if self.bg_loaded:
            try:
                mixer.music.set_volume(0.45)
                mixer.music.play(loops=loops, fade_ms=fade_ms)
            except Exception as e:
                print("Warning: Could not start background music:", e)

    def stop_background_music(self, fade_ms=400):
        """Fade out/stop background music."""
        if self.bg_loaded:
            try:
                mixer.music.fadeout(fade_ms)
            except Exception:
                try:
                    mixer.music.stop()
                except Exception:
                    pass

# Create a global SoundManager
sound_manager = SoundManager()

# ----------------------------
# Gradient & visual helpers
# ----------------------------
def draw_multi_gradient(surface, colors, vertical=True):
    """
    Draws a multi-stop linear gradient across surface.
    - colors: list of RGB tuples from start to end
    - vertical: True => top->bottom; False => left->right
    """
    w, h = surface.get_size()
    n = len(colors) - 1
    if n <= 0:
        surface.fill(colors[0] if colors else (0,0,0))
        return

    if vertical:
        seg = h // n
        for i in range(n):
            c1 = colors[i]
            c2 = colors[i+1]
            for y in range(seg):
                t = y / max(seg-1, 1)
                r = int(c1[0] + (c2[0]-c1[0])*t)
                g = int(c1[1] + (c2[1]-c1[1])*t)
                b = int(c1[2] + (c2[2]-c1[2])*t)
                yy = i*seg + y
                if yy < h:
                    pygame.draw.line(surface, (r,g,b), (0,yy), (w,yy))
        # fill rest
        last = colors[-1]
        for yy in range(n*seg, h):
            pygame.draw.line(surface, last, (0,yy), (w,yy))
    else:
        seg = w // n
        for i in range(n):
            c1 = colors[i]
            c2 = colors[i+1]
            for x in range(seg):
                t = x / max(seg-1, 1)
                r = int(c1[0] + (c2[0]-c1[0])*t)
                g = int(c1[1] + (c2[1]-c1[1])*t)
                b = int(c1[2] + (c2[2]-c1[2])*t)
                xx = i*seg + x
                if xx < w:
                    pygame.draw.line(surface, (r,g,b), (xx,0), (xx,h))
        last = colors[-1]
        for xx in range(n*seg, w):
            pygame.draw.line(surface, last, (xx,0), (xx,h))

# ----------------------------
# Animated Button Class
# ----------------------------
class Button:
    """
    Animated button with:
    - Slide-in entrance (staggered)
    - Hover pulse (sine-based scaling)
    - Glow while hovered
    - Click handling that triggers click sound
    """
    def __init__(self, x, y, w, h, text, color, hover_color, text_color=WHITE, slide_in_from=-400, delay_ms=0):
        self.target_rect = pygame.Rect(x, y, w, h)
        # Start off-screen (for slide-in)
        self.rect = pygame.Rect(x + slide_in_from, y, w, h)
        self.text = text
        self.color = color
        self.hover_color = hover_color
        self.text_color = text_color
        self.is_hovered = False
        self.slide_start_time = pygame.time.get_ticks() + delay_ms
        self.slide_duration = 600  # ms
        self.scale = 1.0
        self.pulse_amp = 0.045
        self.pulse_speed = 5.5
        self.border_thickness = 3

    def update(self, mouse_pos):
        """Update slide-in animation & hover status."""
        now = pygame.time.get_ticks()
        if now >= self.slide_start_time:
            t = min(1.0, (now - self.slide_start_time) / self.slide_duration)
            # ease-out cubic
            t_e = 1 - pow(1 - t, 3)
            start_x = self.target_rect.x - (self.target_rect.width + 60)
            self.rect.x = int(start_x + (self.target_rect.x - start_x) * t_e)

        self.is_hovered = self.rect.collidepoint(mouse_pos)
        if self.is_hovered:
            pulse = 1.0 + self.pulse_amp * math.sin(pygame.time.get_ticks() / 1000.0 * self.pulse_speed * 2 * math.pi)
            # smooth interpolation
            self.scale += (pulse - self.scale) * 0.25
        else:
            self.scale += (1.0 - self.scale) * 0.2

    def draw(self, surf):
        """Draw button (scaled) and text using pixel button_font."""
        base = self.hover_color if self.is_hovered else self.color
        border = (max(0, base[0]-30), max(0, base[1]-30), max(0, base[2]-30))

        w = int(self.rect.width * self.scale)
        h = int(self.rect.height * self.scale)
        draw_rect = pygame.Rect(0,0,w,h)
        draw_rect.center = self.rect.center

        # Glow effect
        if self.is_hovered:
            glow = pygame.Surface((w+24, h+24), pygame.SRCALPHA)
            pygame.draw.ellipse(glow, (base[0], base[1], base[2], 40), glow.get_rect())
            glow_pos = glow.get_rect(center=self.rect.center)
            surf.blit(glow, glow_pos)

        pygame.draw.rect(surf, base, draw_rect, border_radius=10)
        pygame.draw.rect(surf, border, draw_rect, self.border_thickness, border_radius=10)

        # Render text using pixel font (button_font)
        text_surf = button_font.render(self.text, True, self.text_color)
        text_rect = text_surf.get_rect(center=draw_rect.center)
        surf.blit(text_surf, text_rect)

    def is_clicked(self, pos, event):
        """Return True when left-mouse clicked inside current rect; play click SFX."""
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if self.rect.collidepoint(pos):
                sound_manager.play('click')
                return True
        return False

# ----------------------------
# TicTacToe Main Class
# ----------------------------
class TicTacToe:
    def __init__(self):
        # Game data
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.game_state = MAIN_MENU
        self.game_mode = None     # 'single' | 'multi'
        self.difficulty = None    # 'easy' | 'medium' | 'hard'
        self.winner = None
        self.game_over = False

        # UI Buttons (staggered slide-in)
        self.buttons = self.create_buttons()

        # Menu animation time (for title fade)
        self.menu_start_time = pygame.time.get_ticks()

        # Start background music (loop)
        sound_manager.start_background_music(loops=-1)

    def create_buttons(self):
        """Create and return a dict of UI Buttons used through the game."""
        mid_x = WIDTH // 2
        btns = {}
        # Main menu
        btns['start'] = Button(mid_x-120, HEIGHT//2 + 12, 240, 56, "START GAME", (45,120,230), (30,90,210), WHITE, slide_in_from=-520, delay_ms=0)
        btns['quit']  = Button(mid_x-120, HEIGHT//2 + 92, 240, 56, "QUIT", (200,70,70), (220,40,40), WHITE, slide_in_from=-520, delay_ms=120)

        # Mode select
        btns['single'] = Button(mid_x-170, HEIGHT//2 - 40, 340, 56, "SINGLE PLAYER", (45,120,230), (30,90,210), WHITE, slide_in_from=-600, delay_ms=0)
        btns['multi']  = Button(mid_x-170, HEIGHT//2 + 40, 340, 56, "MULTIPLAYER", (50,200,120), (40,170,100), WHITE, slide_in_from=-600, delay_ms=120)
        btns['back_mode'] = Button(mid_x-170, HEIGHT//2 + 140, 340, 52, "BACK", GRAY, LIGHT_GRAY, BLACK, slide_in_from=-600, delay_ms=240)

        # Difficulty select
        btns['easy'] = Button(mid_x-170, HEIGHT//2 - 80, 340, 56, "EASY", (120,200,140), (100,180,120), BLACK, slide_in_from=-600, delay_ms=0)
        btns['medium'] = Button(mid_x-170, HEIGHT//2, 340, 56, "MEDIUM", (255,165,0), (255,140,0), BLACK, slide_in_from=-600, delay_ms=90)
        btns['hard'] = Button(mid_x-170, HEIGHT//2 + 80, 340, 56, "HARD", (220,90,90), (200,60,60), WHITE, slide_in_from=-600, delay_ms=180)
        btns['back_diff'] = Button(mid_x-170, HEIGHT//2 + 160, 340, 52, "BACK", GRAY, LIGHT_GRAY, BLACK, slide_in_from=-600, delay_ms=270)

        # Game over buttons
        btns['play_again'] = Button(mid_x-170, HEIGHT//2 + 40, 340, 56, "PLAY AGAIN", (45,120,230), (30,90,210), WHITE, slide_in_from=-420, delay_ms=0)
        btns['main_menu'] = Button(mid_x-170, HEIGHT//2 + 110, 340, 52, "MAIN MENU", GRAY, LIGHT_GRAY, BLACK, slide_in_from=-420, delay_ms=90)

        return btns

    # ------------------------
    # Game logic
    # ------------------------
    def reset_game(self):
        """Reset board for new match."""
        self.board = [['' for _ in range(3)] for _ in range(3)]
        self.current_player = 'X'
        self.winner = None
        self.game_over = False

    def check_winner(self):
        """Return 'X'/'O' if winner, 'Draw' if draw, else None."""
        # rows
        for row in self.board:
            if row[0] != '' and row[0] == row[1] == row[2]:
                return row[0]
        # cols
        for c in range(3):
            if self.board[0][c] != '' and self.board[0][c] == self.board[1][c] == self.board[2][c]:
                return self.board[0][c]
        # diagonals
        if self.board[0][0] != '' and self.board[0][0] == self.board[1][1] == self.board[2][2]:
            return self.board[0][0]
        if self.board[0][2] != '' and self.board[0][2] == self.board[1][1] == self.board[2][0]:
            return self.board[0][2]
        # draw
        if all(cell != '' for row in self.board for cell in row):
            return 'Draw'
        return None

    def make_move(self, row, col):
        """Place mark if possible, play click SFX, check for winner, handle turn changes."""
        if self.board[row][col] == '' and not self.game_over:
            self.board[row][col] = self.current_player
            sound_manager.play('click')

            result = self.check_winner()
            if result:
                self.game_over = True
                # winner variable kept as actual mark for display; None for draw
                self.winner = result if result != 'Draw' else None
                # sound: play win/lose accordingly; no draw sound
                if self.game_mode == 'single':
                    if result == 'X':
                        sound_manager.play('win')
                    elif result == 'O':
                        sound_manager.play('lose')
                else:
                    if result != 'Draw':
                        sound_manager.play('win')
            else:
                # switch player and, if AI turn, schedule AI via timed event
                self.current_player = 'O' if self.current_player == 'X' else 'X'
                if self.game_mode == 'single' and self.current_player == 'O' and not self.game_over:
                    # Schedule a one-shot timer (simulate AI thinking)
                    pygame.time.set_timer(pygame.USEREVENT + 1, 320, loops=1)

    # ------------------------
    # AI strategies
    # ------------------------
    def computer_move_easy(self):
        empty = [(r,c) for r in range(3) for c in range(3) if self.board[r][c] == '']
        if empty:
            r,c = random.choice(empty)
            self.make_move(r,c)

    def computer_move_medium(self):
        # try win, then block, else random
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.board[r][c] = 'O'
                    if self.check_winner() == 'O':
                        self.board[r][c] = ''
                        self.make_move(r,c)
                        return
                    self.board[r][c] = ''
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.board[r][c] = 'X'
                    if self.check_winner() == 'X':
                        self.board[r][c] = ''
                        self.make_move(r,c)
                        return
                    self.board[r][c] = ''
        self.computer_move_easy()

    def computer_move_hard(self):
        best_score = float('-inf')
        best_move = None
        for r in range(3):
            for c in range(3):
                if self.board[r][c] == '':
                    self.board[r][c] = 'O'
                    score = self.minimax(0, False)
                    self.board[r][c] = ''
                    if score > best_score:
                        best_score = score
                        best_move = (r,c)
        if best_move:
            self.make_move(best_move[0], best_move[1])

    def minimax(self, depth, is_maximizing):
        res = self.check_winner()
        if res == 'O':
            return 10 - depth
        elif res == 'X':
            return depth - 10
        elif res == 'Draw':
            return 0

        if is_maximizing:
            best = float('-inf')
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        self.board[r][c] = 'O'
                        val = self.minimax(depth+1, False)
                        self.board[r][c] = ''
                        best = max(best, val)
            return best
        else:
            best = float('inf')
            for r in range(3):
                for c in range(3):
                    if self.board[r][c] == '':
                        self.board[r][c] = 'X'
                        val = self.minimax(depth+1, True)
                        self.board[r][c] = ''
                        best = min(best, val)
            return best

    # ------------------------
    # Input handling & drawing
    # ------------------------
    def handle_click(self, pos):
        """Map mouse pos to board cell and attempt move if allowed."""
        board_rect = pygame.Rect((WIDTH - BOARD_SIZE)//2, (HEIGHT - BOARD_SIZE)//2 + 20, BOARD_SIZE, BOARD_SIZE)
        if board_rect.collidepoint(pos) and not self.game_over:
            rel_x = pos[0] - board_rect.left
            rel_y = pos[1] - board_rect.top
            col = int(rel_x // CELL_SIZE)
            row = int(rel_y // CELL_SIZE)
            if self.game_mode == 'single' and self.current_player == 'O':
                return
            self.make_move(row, col)

    def draw_board(self):
        """Render board, grid lines, pieces and HUD info."""
        board_rect = pygame.Rect((WIDTH - BOARD_SIZE)//2, (HEIGHT - BOARD_SIZE)//2 + 20, BOARD_SIZE, BOARD_SIZE)
        pygame.draw.rect(screen, LIGHT_GRAY, board_rect, border_radius=12)
        pygame.draw.rect(screen, BLACK, board_rect, 3, border_radius=12)

        for i in range(1,3):
            pygame.draw.line(screen, BLACK,
                             (board_rect.left + i*CELL_SIZE, board_rect.top),
                             (board_rect.left + i*CELL_SIZE, board_rect.bottom), 4)
            pygame.draw.line(screen, BLACK,
                             (board_rect.left, board_rect.top + i*CELL_SIZE),
                             (board_rect.right, board_rect.top + i*CELL_SIZE), 4)

        for r in range(3):
            for c in range(3):
                val = self.board[r][c]
                cell_rect = pygame.Rect(board_rect.left + c*CELL_SIZE + 10,
                                        board_rect.top + r*CELL_SIZE + 10,
                                        CELL_SIZE - 20, CELL_SIZE - 20)
                if val == 'X':
                    pygame.draw.line(screen, BLUE, (cell_rect.left, cell_rect.top), (cell_rect.right, cell_rect.bottom), 10)
                    pygame.draw.line(screen, BLUE, (cell_rect.right, cell_rect.top), (cell_rect.left, cell_rect.bottom), 10)
                elif val == 'O':
                    pygame.draw.circle(screen, RED, cell_rect.center, CELL_SIZE//2 - 18, 10)

        # HUD
        player_s = game_font.render(f"Player: {self.current_player}", True, BLUE if self.current_player=='X' else RED)
        screen.blit(player_s, (20, 20))
        mode_text = f"Mode: {self.game_mode.upper() if self.game_mode else 'N/A'}"
        if self.game_mode == 'single' and self.difficulty:
            mode_text += f"  |  Difficulty: {self.difficulty.upper()}"
        mode_s = info_font.render(mode_text, True, BLACK)
        screen.blit(mode_s, (20, 62))

    # ------------------------
    # UI screens: menu, mode select, difficulty, game over
    # ------------------------
    def draw_main_menu(self, mouse_pos):
        """Draw animated multi-color gradient background, pixel title & animated buttons."""
        gradient = pygame.Surface((WIDTH, HEIGHT))
        palette = [(255, 60, 120), (255,165,0), (255,235,59), (60,180,255), (120,60,255)]
        draw_multi_gradient(gradient, palette, vertical=False)

        # Moving radial overlay for subtle motion
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        t = pygame.time.get_ticks() / 1000.0
        cx = int(WIDTH/2 + math.sin(t * 0.6) * 120)
        cy = int(HEIGHT/2 + math.cos(t * 0.5) * 60)
        pygame.draw.circle(overlay, (255,255,255,28), (cx,cy), 300)
        gradient.blit(overlay, (0,0), special_flags=pygame.BLEND_RGBA_ADD)
        screen.blit(gradient, (0,0))

        # Title with Minecraft-like pixel font & glow pulse
        elapsed = pygame.time.get_ticks() - self.menu_start_time
        fade = min(255, int(255 * (elapsed / 700.0)))
        bob = math.sin(pygame.time.get_ticks() / 900.0) * 5
        title_surf = title_font.render("TIC TAC TOE", True, (255,255,255))
        title_surf.set_alpha(fade)
        title_rect = title_surf.get_rect(center=(WIDTH//2, HEIGHT//6 + bob))
        # Shadow for depth
        shadow = title_font.render("TIC TAC TOE", True, (0,0,0))
        shadow.set_alpha(max(0, fade-60))
        shadow_rect = shadow.get_rect(center=(title_rect.centerx + 6, title_rect.centery + 6))
        screen.blit(shadow, shadow_rect)
        screen.blit(title_surf, title_rect)

        # Decorative translucent card for contrast
        card_rect = pygame.Rect(WIDTH//2 - 260, HEIGHT//2 - 120, 520, 320)
        card_surf = pygame.Surface(card_rect.size, pygame.SRCALPHA)
        pygame.draw.rect(card_surf, (255,255,255,200), card_surf.get_rect(), border_radius=18)
        pygame.draw.rect(card_surf, (0,0,0,40), card_surf.get_rect(), 3, border_radius=18)
        screen.blit(card_surf, card_rect.topleft)

        # Buttons
        for key in ['start','quit']:
            btn = self.buttons[key]
            btn.update(mouse_pos)
            btn.draw(screen)

    def draw_game_mode_select(self, mouse_pos):
        surface = pygame.Surface((WIDTH, HEIGHT))
        draw_multi_gradient(surface, [(40,160,255),(100,200,180),(220,120,255)], vertical=False)
        screen.blit(surface,(0,0))
        title = title_font.render("SELECT MODE", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//6)))
        box = pygame.Rect(WIDTH//2 - 380//2, HEIGHT//2 - 160//2, 380, 260)
        pygame.draw.rect(screen, (255,255,255,200), box, border_radius=16)
        pygame.draw.rect(screen, BLACK, box, 2, border_radius=16)
        for key in ['single','multi','back_mode']:
            btn = self.buttons[key]
            btn.update(mouse_pos)
            btn.draw(screen)

    def draw_difficulty_select(self, mouse_pos):
        surface = pygame.Surface((WIDTH, HEIGHT))
        draw_multi_gradient(surface, [(255,140,0),(255,60,120),(120,60,255)], vertical=False)
        screen.blit(surface,(0,0))
        title = title_font.render("DIFFICULTY", True, WHITE)
        screen.blit(title, title.get_rect(center=(WIDTH//2, HEIGHT//6)))
        box = pygame.Rect(WIDTH//2 - 420//2, HEIGHT//2 - 180//2, 420, 320)
        pygame.draw.rect(screen, (255,255,255,200), box, border_radius=16)
        pygame.draw.rect(screen, BLACK, box, 2, border_radius=16)
        for key in ['easy','medium','hard','back_diff']:
            btn = self.buttons[key]
            btn.update(mouse_pos)
            btn.draw(screen)

    def draw_game_over(self, mouse_pos):
        # draw board underneath then overlay
        self.draw_board()
        overlay = pygame.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        overlay.fill((0,0,0,160))
        screen.blit(overlay,(0,0))
        box = pygame.Rect(WIDTH//2 - 300, HEIGHT//3 - 60, 600, 320)
        pygame.draw.rect(screen, WHITE, box, border_radius=16)
        pygame.draw.rect(screen, BLACK, box, 2, border_radius=16)
        if self.winner:
            if self.game_mode == 'single' and self.winner == 'O':
                msg = "COMPUTER WINS!"
                color = RED
            elif self.game_mode == 'single' and self.winner == 'X':
                msg = "YOU WIN!"
                color = GREEN
            else:
                msg = f"PLAYER {self.winner} WINS!"
                color = BLUE if self.winner == 'X' else RED
        else:
            msg = "DRAW GAME!"
            color = BLACK
        msg_surf = title_font.render(msg, True, color)
        screen.blit(msg_surf, msg_surf.get_rect(center=(WIDTH//2, box.top + 80)))
        for key in ['play_again','main_menu']:
            btn = self.buttons[key]
            btn.update(mouse_pos)
            btn.draw(screen)

    # ------------------------
    # Main loop
    # ------------------------
    def run(self):
        running = True
        while running:
            mouse_pos = pygame.mouse.get_pos()
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False

                # AI timer event: triggered after short delay to simulate thinking
                if event.type == pygame.USEREVENT + 1:
                    if self.difficulty == 'easy':
                        self.computer_move_easy()
                    elif self.difficulty == 'medium':
                        self.computer_move_medium()
                    elif self.difficulty == 'hard':
                        self.computer_move_hard()

                # State-based clickable controls
                if self.game_state == MAIN_MENU:
                    for key in ['start','quit']:
                        if self.buttons[key].is_clicked(mouse_pos, event):
                            if key == 'start':
                                self.game_state = GAME_MODE_SELECT
                            elif key == 'quit':
                                running = False

                elif self.game_state == GAME_MODE_SELECT:
                    for key in ['single','multi','back_mode']:
                        if self.buttons[key].is_clicked(mouse_pos, event):
                            if key == 'single':
                                self.game_mode = 'single'
                                self.game_state = DIFFICULTY_SELECT
                            elif key == 'multi':
                                self.game_mode = 'multi'
                                self.difficulty = None
                                self.reset_game()
                                self.game_state = IN_GAME
                            elif key == 'back_mode':
                                self.game_state = MAIN_MENU

                elif self.game_state == DIFFICULTY_SELECT:
                    for key in ['easy','medium','hard','back_diff']:
                        if self.buttons[key].is_clicked(mouse_pos, event):
                            if key in ['easy','medium','hard']:
                                self.difficulty = key
                                self.reset_game()
                                self.game_state = IN_GAME
                            elif key == 'back_diff':
                                self.game_state = GAME_MODE_SELECT

                elif self.game_state == IN_GAME:
                    if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                        self.handle_click(mouse_pos)

                elif self.game_state == GAME_OVER:
                    for key in ['play_again','main_menu']:
                        if self.buttons[key].is_clicked(mouse_pos, event):
                            if key == 'play_again':
                                self.reset_game()
                                self.game_state = IN_GAME
                            elif key == 'main_menu':
                                self.game_state = MAIN_MENU

            # Update buttons (hover & animation)
            for b in self.buttons.values():
                b.update(mouse_pos)

            # Auto-transition to GAME_OVER screen if game finished
            if self.game_state == IN_GAME and self.game_over:
                self.game_state = GAME_OVER

            # Drawing
            if self.game_state == MAIN_MENU:
                self.draw_main_menu(mouse_pos)
            elif self.game_state == GAME_MODE_SELECT:
                self.draw_game_mode_select(mouse_pos)
            elif self.game_state == DIFFICULTY_SELECT:
                self.draw_difficulty_select(mouse_pos)
            elif self.game_state == IN_GAME:
                screen.fill(WHITE)
                self.draw_board()
            elif self.game_state == GAME_OVER:
                self.draw_game_over(mouse_pos)

            pygame.display.flip()
            clock.tick(FPS)

        # Cleanup
        sound_manager.stop_background_music()
        pygame.quit()
        sys.exit()

# ----------------------------
# Run (entrypoint)
# ----------------------------
if __name__ == "__main__":
    game = TicTacToe()
    game.run()
