import pygame
import sys
import random
import os

# Инициализация Pygame
pygame.init()
pygame.mixer.init()

# Константы окна
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Memory Game")

# Цвета
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
GRAY = (150, 150, 150)
DARK_GRAY = (100, 100, 100)
LIGHT_BLUE = (173, 216, 230)
RED = (255, 0, 0)
GREEN = (0, 200, 0)
PINK = (255, 200, 220)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)
TIFFANY = (120, 210, 190)
ROSE = (255, 190, 200)

# Шрифты
font_large = pygame.font.Font(None, 72)
font_medium = pygame.font.Font(None, 48)
font_small = pygame.font.Font(None, 36)

# ========== ЗАГРУЗКА КАРТИНОК ==========
def load_image(file_name, size=(100, 100)):
    if os.path.exists(file_name):
        try:
            image = pygame.image.load(file_name)
            return pygame.transform.scale(image, size)
        except:
            return None
    return None

card_back_image = load_image("card_back.png", (100, 100))

card_images = {
    'A': load_image("card_1.png", (100, 100)),
    'B': load_image("card_2.png", (100, 100)),
    'C': load_image("card_3.png", (100, 100)),
    'D': load_image("card_4.png", (100, 100)),
    'E': load_image("card_5.png", (100, 100)),
    'F': load_image("card_6.png", (100, 100)),
    'G': load_image("card_7.png", (100, 100)),
    'H': load_image("card_8.png", (100, 100)),
}

def get_card_image(symbol):
    img = card_images.get(symbol)
    if img is not None:
        return img
    else:
        surf = pygame.Surface((100, 100))
        colors = {
            'A': (255, 100, 100), 'B': (100, 255, 100), 'C': (100, 100, 255),
            'D': (255, 255, 100), 'E': (255, 100, 255), 'F': (100, 255, 255),
            'G': (255, 200, 100), 'H': (200, 100, 255),
        }
        color = colors.get(symbol, (200, 200, 200))
        surf.fill(color)
        pygame.draw.rect(surf, BLACK, surf.get_rect(), 3)
        text = font_medium.render(symbol, True, BLACK)
        text_rect = text.get_rect(center=(50, 50))
        surf.blit(text, text_rect)
        return surf

# ========== ЗАГРУЗКА ЗВУКОВ ==========
def load_sound(file_name):
    if os.path.exists(file_name):
        try:
            return pygame.mixer.Sound(file_name)
        except:
            return None
    return None

def load_sound_with_fallback(base_name):
    for ext in [".wav", ".ogg", ".mp3"]:
        sound = load_sound(f"{base_name}{ext}")
        if sound is not None:
            return sound
    return None

click_sound = load_sound_with_fallback("click")
match_sound = load_sound_with_fallback("match")
win_sound = load_sound_with_fallback("win")
lose_sound = load_sound_with_fallback("lose")

for ext in [".mp3", ".ogg", ".wav"]:
    if os.path.exists(f"background{ext}"):
        try:
            pygame.mixer.music.load(f"background{ext}")
            pygame.mixer.music.set_volume(0.3)
            pygame.mixer.music.play(-1)
            break
        except:
            pass

def play_sound(sound):
    if sound is not None:
        try:
            sound.play()
        except:
            pass

# ========== КЛАСС КАРТОЧКИ (без зелёной подсветки) ==========
class Card:
    def __init__(self, symbol, x, y, size=100):
        self.symbol = symbol
        self.rect = pygame.Rect(x, y, size, size)
        self.is_flipped = False
        self.is_matched = False
        self.size = size
    
    def draw(self, surface, font):
        if self.is_matched:
            return
        
        if self.is_flipped:
            color = (255, 255, 200)
        else:
            color = (100, 100, 150)
        
        pygame.draw.rect(surface, color, self.rect)
        pygame.draw.rect(surface, BLACK, self.rect, 3)
        
        if self.is_flipped:
            img = get_card_image(self.symbol)
            surface.blit(img, self.rect)
        else:
            if card_back_image is not None:
                surface.blit(card_back_image, self.rect)
            else:
                text = font.render("?", True, BLACK)
                text_rect = text.get_rect(center=self.rect.center)
                surface.blit(text, text_rect)
    
    def handle_click(self, pos):
        if self.is_matched:
            return False
        return self.rect.collidepoint(pos) and not self.is_flipped
    
    def flip(self):
        if not self.is_matched:
            self.is_flipped = not self.is_flipped
    
    def match(self):
        self.is_matched = True
        self.is_flipped = False

# ========== КЛАСС ПОЛЯ ==========
class Board:
    def __init__(self, grid_size=4, card_size=100, margin=20):
        self.grid_size = grid_size
        self.card_size = card_size
        self.margin = margin
        self.cards = []
        self.symbols = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H']
        board_width = grid_size * (card_size + margin) - margin
        board_height = grid_size * (card_size + margin) - margin
        self.offset_x = (WIDTH - board_width) // 2
        self.offset_y = (HEIGHT - board_height) // 2
        self.create_cards()
    
    def create_cards(self):
        total_pairs = (self.grid_size * self.grid_size) // 2
        used_symbols = self.symbols[:total_pairs]
        card_values = used_symbols + used_symbols
        random.shuffle(card_values)
        self.cards = []
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                x = self.offset_x + col * (self.card_size + self.margin)
                y = self.offset_y + row * (self.card_size + self.margin)
                symbol = card_values[row * self.grid_size + col]
                self.cards.append(Card(symbol, x, y, self.card_size))
    
    def draw(self, surface, font):
        for card in self.cards:
            card.draw(surface, font)
    
    def reset(self):
        self.create_cards()

# ========== КЛАСС ИГРЫ ==========
class Game:
    def __init__(self, num_players=1, difficulty="easy"):
        self.board = Board(grid_size=4)
        self.font = pygame.font.Font(None, 48)
        self.small_font = pygame.font.Font(None, 36)
        self.first_card = None
        self.second_card = None
        self.waiting = False
        self.wait_start = 0
        self.game_over = False
        self.num_players = num_players
        self.difficulty = difficulty
        self.score = 0
        self.moves = 0
        self.total_pairs = 8
        self.win = False
        self.player_scores = [0, 0]
        self.current_player = 1
        self.player_time_seconds = 30
        self.time_left = 30
        self.timer_start_time = 0
        self.waiting_for_next_player = False
        self.wait_next_start = 0
        self.winner = 0
        self.single_timer_enabled = (difficulty == "timer")
        self.single_timer_seconds = 60 if self.single_timer_enabled else 0
        self.single_timer_start = 0
        self.single_time_over = False
    
    def start(self):
        if self.num_players == 2:
            self.timer_start_time = pygame.time.get_ticks()
            self.time_left = self.player_time_seconds
        elif self.single_timer_enabled:
            self.single_timer_start = pygame.time.get_ticks()
    
    def next_player(self):
        if self.current_player == 1:
            self.current_player = 2
            total_matched = sum(1 for card in self.board.cards if card.is_matched)
            self.player_scores[0] = total_matched
        else:
            total_matched = sum(1 for card in self.board.cards if card.is_matched)
            self.player_scores[1] = total_matched
            self.game_over = True
            if self.player_scores[0] > self.player_scores[1]:
                self.winner = 1
            elif self.player_scores[1] > self.player_scores[0]:
                self.winner = 2
            else:
                self.winner = 0
            play_sound(win_sound if self.winner != 0 else None)
            return
        self.board.reset()
        self.first_card = None
        self.second_card = None
        self.waiting = False
        self.time_left = self.player_time_seconds
        self.timer_start_time = pygame.time.get_ticks()
        self.waiting_for_next_player = False
    
    def handle_click(self, pos):
        if self.waiting or self.game_over:
            return
        if self.num_players == 2:
            if self.waiting_for_next_player or self.time_left <= 0:
                return
        for card in self.board.cards:
            if card.handle_click(pos):
                card.flip()
                play_sound(click_sound)
                if self.first_card is None:
                    self.first_card = card
                elif self.second_card is None and card != self.first_card:
                    self.second_card = card
                    if self.num_players == 1:
                        self.moves += 1
                    self.check_match()
                return
    
    def check_match(self):
        if self.first_card.symbol == self.second_card.symbol:
            play_sound(match_sound)
            self.first_card.match()
            self.second_card.match()
            if self.num_players == 1:
                self.score += 1
                if self.score >= self.total_pairs:
                    self.game_over = True
                    self.win = True
                    play_sound(win_sound)
            self.first_card = None
            self.second_card = None
        else:
            self.waiting = True
            self.wait_start = pygame.time.get_ticks()
    
    def update(self):
        if self.waiting:
            now = pygame.time.get_ticks()
            if now - self.wait_start > 700:
                if self.first_card and self.second_card:
                    self.first_card.flip()
                    self.second_card.flip()
                self.first_card = None
                self.second_card = None
                self.waiting = False
        
        if self.num_players == 2 and not self.game_over and not self.waiting_for_next_player:
            now = pygame.time.get_ticks()
            elapsed = (now - self.timer_start_time) // 1000
            self.time_left = max(0, self.player_time_seconds - elapsed)
            if self.time_left <= 0:
                self.waiting_for_next_player = True
                self.wait_next_start = pygame.time.get_ticks()
                play_sound(lose_sound)
        
        if self.waiting_for_next_player and not self.game_over:
            now = pygame.time.get_ticks()
            if now - self.wait_next_start > 2000:
                self.next_player()
        
        if self.num_players == 1 and self.single_timer_enabled and not self.game_over:
            now = pygame.time.get_ticks()
            elapsed = (now - self.single_timer_start) // 1000
            remaining = self.single_timer_seconds - elapsed
            if remaining <= 0 and not self.game_over:
                self.single_time_over = True
                self.game_over = True
                self.win = False
                play_sound(lose_sound)
    
    def draw(self, surface):
        surface.fill((220, 220, 240))
        self.board.draw(surface, self.font)
        
        if self.num_players == 1:
            score_text = self.small_font.render(f"Pairs: {self.score}/{self.total_pairs}", True, BLACK)
            moves_text = self.small_font.render(f"Moves: {self.moves}", True, BLACK)
            surface.blit(score_text, (10, 10))
            surface.blit(moves_text, (10, 50))
            if self.single_timer_enabled and not self.game_over:
                elapsed = (pygame.time.get_ticks() - self.single_timer_start) // 1000
                remaining = max(0, self.single_timer_seconds - elapsed)
                timer_text = self.small_font.render(f"Time: {remaining}s", True, RED if remaining < 10 else BLACK)
                surface.blit(timer_text, (WIDTH - 120, 10))
        else:
            if not self.game_over and not self.waiting_for_next_player:
                player_color = PURPLE if self.current_player == 1 else ORANGE
                turn_text = font_medium.render(f"PLAYER {self.current_player}", True, player_color)
                turn_rect = turn_text.get_rect(topright=(WIDTH - 20, 20))
                surface.blit(turn_text, turn_rect)
                time_text = font_large.render(f"{self.time_left}s", True, RED if self.time_left < 5 else BLACK)
                time_rect = time_text.get_rect(topright=(WIDTH - 20, 70))
                surface.blit(time_text, time_rect)
                score_text = self.small_font.render(f"P1: {self.player_scores[0]}  |  P2: {self.player_scores[1]}", True, BLACK)
                score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT - 30))
                surface.blit(score_text, score_rect)
            elif self.waiting_for_next_player and not self.game_over:
                wait_text = font_medium.render(f"Player {self.current_player}'s turn is over!", True, BLACK)
                wait_rect = wait_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
                surface.blit(wait_text, wait_rect)
                next_text = font_small.render("Next player starting soon...", True, DARK_GRAY)
                next_rect = next_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 20))
                surface.blit(next_text, next_rect)
        
        help_text = self.small_font.render("R: restart" , True, BLACK)
        surface.blit(help_text, (10, 90))
        help_text = self.small_font.render("M: menu", True, BLACK)
        surface.blit(help_text, (10, 70))
        if self.game_over:
            overlay = pygame.Surface((WIDTH, HEIGHT))
            overlay.set_alpha(180)
            overlay.fill((0, 0, 0))
            surface.blit(overlay, (0, 0))
            
            if self.num_players == 2:
                if self.winner == 1:
                    msg = "PLAYER 1 WINS!"
                    color = PURPLE
                elif self.winner == 2:
                    msg = "PLAYER 2 WINS!"
                    color = ORANGE
                else:
                    msg = "TIE!"
                    color = GRAY
                score_msg = f"{self.player_scores[0]} - {self.player_scores[1]}"
                score_surface = font_medium.render(score_msg, True, WHITE)
                score_rect = score_surface.get_rect(center=(WIDTH // 2, HEIGHT // 2))
                surface.blit(score_surface, score_rect)
            else:
                if self.win:
                    msg = "YOU WIN!"
                    color = GREEN
                elif self.single_time_over:
                    msg = "TIME'S UP! YOU LOSE!"
                    color = RED
                else:
                    msg = "GAME OVER"
                    color = RED
            
            text = font_large.render(msg, True, color)
            text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2 - 50))
            surface.blit(text, text_rect)
            restart_text = font_small.render("Press R to play again  |  M for menu", True, WHITE)
            restart_rect = restart_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 80))
            surface.blit(restart_text, restart_rect)
    
    def restart(self):
        if self.num_players == 2:
            self.__init__(2, "none")
        else:
            self.__init__(1, self.difficulty)
        self.start()

# ========== ФУНКЦИИ МЕНЮ ==========
def draw_menu():
    screen.fill(LIGHT_BLUE)
    title = font_large.render("MEMORY GAME", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title, title_rect)
    start_rect = pygame.Rect(WIDTH // 2 - 100, HEIGHT // 2, 200, 60)
    pygame.draw.rect(screen, GREEN, start_rect)
    pygame.draw.rect(screen, BLACK, start_rect, 3)
    start_text = font_medium.render("START", True, BLACK)
    start_text_rect = start_text.get_rect(center=start_rect.center)
    screen.blit(start_text, start_text_rect)
    return start_rect

def draw_player_selection():
    screen.fill(LIGHT_BLUE)
    title = font_medium.render("SELECT NUMBER OF PLAYERS", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title, title_rect)
    one_player_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 60)
    pygame.draw.rect(screen, TIFFANY, one_player_rect)
    pygame.draw.rect(screen, BLACK, one_player_rect, 3)
    one_text = font_medium.render("1 PLAYER", True, BLACK)
    one_text_rect = one_text.get_rect(center=one_player_rect.center)
    screen.blit(one_text, one_text_rect)
    two_player_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60)
    pygame.draw.rect(screen, ROSE, two_player_rect)
    pygame.draw.rect(screen, BLACK, two_player_rect, 3)
    two_text = font_medium.render("2 PLAYERS", True, BLACK)
    two_text_rect = two_text.get_rect(center=two_player_rect.center)
    screen.blit(two_text, two_text_rect)
    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 130, 160, 40)
    pygame.draw.rect(screen, DARK_GRAY, back_rect)
    pygame.draw.rect(screen, BLACK, back_rect, 3)
    back_text = font_small.render("Back to menu", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    return one_player_rect, two_player_rect, back_rect

def draw_difficulty_selection():
    screen.fill(LIGHT_BLUE)
    title = font_medium.render("SELECT DIFFICULTY", True, BLACK)
    title_rect = title.get_rect(center=(WIDTH // 2, HEIGHT // 4))
    screen.blit(title, title_rect)
    easy_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 - 50, 300, 60)
    pygame.draw.rect(screen, GREEN, easy_rect)
    pygame.draw.rect(screen, BLACK, easy_rect, 3)
    easy_text = font_medium.render("NO TIMER", True, BLACK)
    easy_text_rect = easy_text.get_rect(center=easy_rect.center)
    screen.blit(easy_text, easy_text_rect)
    timer_rect = pygame.Rect(WIDTH // 2 - 150, HEIGHT // 2 + 40, 300, 60)
    pygame.draw.rect(screen, ORANGE, timer_rect)
    pygame.draw.rect(screen, BLACK, timer_rect, 3)
    timer_text = font_medium.render("1 MINUTE TIMER", True, BLACK)
    timer_text_rect = timer_text.get_rect(center=timer_rect.center)
    screen.blit(timer_text, timer_text_rect)
    back_rect = pygame.Rect(WIDTH // 2 - 80, HEIGHT // 2 + 130, 160, 40)
    pygame.draw.rect(screen, DARK_GRAY, back_rect)
    pygame.draw.rect(screen, BLACK, back_rect, 3)
    back_text = font_small.render("Back", True, BLACK)
    back_text_rect = back_text.get_rect(center=back_rect.center)
    screen.blit(back_text, back_text_rect)
    return easy_rect, timer_rect, back_rect

# ========== ГЛАВНЫЙ ЦИКЛ ==========
game = None
clock = pygame.time.Clock()
running = True
state = "menu"

while running:
    if state == "menu":
        start_rect = draw_menu()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if start_rect.collidepoint(event.pos):
                    state = "player_select"
    
    elif state == "player_select":
        one_rect, two_rect, back_rect = draw_player_selection()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if one_rect.collidepoint(event.pos):
                    state = "difficulty"
                elif two_rect.collidepoint(event.pos):
                    game = Game(num_players=2, difficulty="none")
                    game.start()
                    state = "playing"
                elif back_rect.collidepoint(event.pos):
                    state = "menu"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "menu"
    
    elif state == "difficulty":
        easy_rect, timer_rect, back_rect = draw_difficulty_selection()
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                if easy_rect.collidepoint(event.pos):
                    game = Game(num_players=1, difficulty="easy")
                    game.start()
                    state = "playing"
                elif timer_rect.collidepoint(event.pos):
                    game = Game(num_players=1, difficulty="timer")
                    game.start()
                    state = "playing"
                elif back_rect.collidepoint(event.pos):
                    state = "player_select"
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    state = "player_select"
    
    elif state == "playing":
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                game.handle_click(event.pos)
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    game.restart()
                elif event.key == pygame.K_m:
                    state = "menu"
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(60)

pygame.quit()
sys.exit()
