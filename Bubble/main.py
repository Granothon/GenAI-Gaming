import pygame
import sys
import math
import random
from pygame.locals import *

# Globaalit muuttujat
# Värit
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
PURPLE = (255, 0, 255)
COLORS = [RED, GREEN, BLUE, YELLOW, PURPLE]
LIGHT_BLUE = (135, 206, 250)
DARK_BLUE = (25, 25, 112)

# Score-näytön muuttujat
bubble_score_icon = None
crown_highscore_icon = None
score_font = None
score_text = None
highscore_text = None
last_score_value = -1
last_highscore_value = -1

class Particle:
    def __init__(self, x, y, color):
        self.x = x
        self.y = y
        self.color = color
        self.size = random.randint(int(BUBBLE_RADIUS*0.1), int(BUBBLE_RADIUS*0.25))
        self.speed = random.uniform(1, 3)
        self.angle = random.uniform(0, 2 * math.pi)
        self.life = 30  # frames
        
    def update(self):
        self.x += math.cos(self.angle) * self.speed
        self.y += math.sin(self.angle) * self.speed
        self.life -= 1
        
    def draw(self):
        opacity = int(255 * self.life / 30)
        s = pygame.Surface((self.size*2, self.size*2), pygame.SRCALPHA)
        adjusted_color = (*self.color, opacity)
        pygame.draw.circle(s, adjusted_color, (self.size, self.size), self.size)
        screen.blit(s, (int(self.x - self.size), int(self.y - self.size)))

def initialize_game():
    """Alustaa pelin tarvitsemat globaalit muuttujat"""
    global SCREEN_WIDTH, SCREEN_HEIGHT, screen, BUBBLE_RADIUS, GRID_COLS
    global GRID_ROWS, VISIBLE_ROWS, SHOOTER_Y, GAME_OVER_LINE_Y, SCROLL_SPEED
    global INITIAL_BOTTOM_Y, initial_bottom_row_y, scroll_offset, game_over, game_won
    global score, highscore, particles, grid, shooter_bubble, next_bubble
    global SHOT_SPEED, background_bubbles
    
    # Näytön koko
    SCREEN_WIDTH = 600
    SCREEN_HEIGHT = 800
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("Bubble Shooter")

    # Calculate optimal bubble size based on screen width - ALKUPERÄINEN KOKO
    TARGET_COLUMNS = 11
    BUBBLE_RADIUS = int(SCREEN_WIDTH / (TARGET_COLUMNS * 2 + 2))

    # Kuplien ominaisuudet
    GRID_COLS = TARGET_COLUMNS + 2
    GRID_ROWS = 100
    VISIBLE_ROWS = 8
    SHOOTER_Y = SCREEN_HEIGHT - BUBBLE_RADIUS * 3

    # Game over -linja - PALAUTETTU ALKUPERÄISEEN SIJAINTIIN
    GAME_OVER_LINE_Y = SCREEN_HEIGHT - BUBBLE_RADIUS * 7
    SCROLL_SPEED = BUBBLE_RADIUS * 0.01

    # Alimman kuplarivin korkeus pelin alussa
    INITIAL_BOTTOM_Y = -BUBBLE_RADIUS * 30
    initial_bottom_row_y = (VISIBLE_ROWS - 1) * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
    scroll_offset = INITIAL_BOTTOM_Y - initial_bottom_row_y

    # Peli-tila
    game_over = False
    game_won = False

    # Pisteet
    score = 0
    highscore = 0

    # Hiukkasten säilytys
    particles = []

    # Luodaan ruudukko
    grid = create_grid()

    # Ampumiskupla
    shooter_bubble = {
        'x': SCREEN_WIDTH // 2,
        'y': SHOOTER_Y,
        'color': random.choice(COLORS),
        'dx': 0,
        'dy': 0,
        'moving': False
    }

    # Seuraava kupla
    next_bubble = {
        'color': random.choice(COLORS)
    }

    # Shot speed relative to bubble size
    SHOT_SPEED = BUBBLE_RADIUS * 0.5

    # Background stars/bubbles position initialization
    background_bubbles = []
    for i in range(30):
        background_bubbles.append({
            'x': random.randint(0, SCREEN_WIDTH),
            'y': random.randint(0, SCREEN_HEIGHT),
            'size': random.randint(2, 6),
            'speed': random.uniform(0.2, 0.8),
            'drift': random.uniform(-0.3, 0.3)
        })
    
    # Alustetaan score- ja highscore-näytöt
    initialize_score_display()

def initialize_score_display():
    """
    Alustaa score- ja highscore-näytöt.
    """
    global bubble_score_icon, crown_highscore_icon, score_font
    
    # Luo pieni kupla score-ikoniksi
    size = int(BUBBLE_RADIUS * 1.2)
    bubble_score_icon = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
    # Piirrä miniversio kuplasta
    pygame.draw.circle(bubble_score_icon, BLACK, (size, size), size)
    color = random.choice(COLORS)  # Käytä satunnaista väriä kuplasta
    for r in range(size, 0, -1):
        factor = 1 - (size - r) / size * 0.4
        adjusted_color = (
            min(255, int(color[0] * factor)),
            min(255, int(color[1] * factor)),
            min(255, int(color[2] * factor))
        )
        pygame.draw.circle(bubble_score_icon, adjusted_color, (size, size), r)
    
    # Lisää kiilto
    highlight_radius = size * 0.35
    s = pygame.Surface((highlight_radius*2, highlight_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 255, 255, 180), (highlight_radius, highlight_radius), highlight_radius)
    bubble_score_icon.blit(s, (int(size*0.3), int(size*0.3)))
    
    # Luo kruunu highscore-ikoniksi
    crown_size = int(BUBBLE_RADIUS * 1.4)
    crown_highscore_icon = pygame.Surface((crown_size*2, crown_size), pygame.SRCALPHA)
    # Piirrä yksinkertainen kruunu (kolmio)
    gold_color = (255, 215, 0)
    gold_shadow = (212, 175, 0)
    
    # Kruunun pohja
    pygame.draw.rect(crown_highscore_icon, gold_color, (0, crown_size*0.6, crown_size*2, crown_size*0.4))
    pygame.draw.rect(crown_highscore_icon, gold_shadow, (0, crown_size*0.6, crown_size*2, crown_size*0.4), 1)
    
    # Kruunun piikit (kolme terävää kärkeä)
    for i in range(3):
        x_base = crown_size*0.5 + i*crown_size*0.5
        points = [
            (x_base, crown_size*0.6),  # Pohja
            (x_base - crown_size*0.25, crown_size*0.1),  # Vasen
            (x_base, 0),              # Kärki
            (x_base + crown_size*0.25, crown_size*0.1),  # Oikea
        ]
        pygame.draw.polygon(crown_highscore_icon, gold_color, points)
        pygame.draw.polygon(crown_highscore_icon, gold_shadow, points, 1)
    
    # Lisää kiiltopisteet
    for i in range(3):
        x = crown_size*0.5 + i*crown_size*0.5
        y = crown_size*0.3
        radius = crown_size*0.1
        pygame.draw.circle(crown_highscore_icon, (255, 255, 255, 120), (x, y), radius)
    
    # Alusta fontti
    score_font = pygame.font.SysFont('Arial', int(BUBBLE_RADIUS*1.4), bold=True)

def update_score_display():
    """
    Päivittää score- ja highscore-näytöt vain kun arvot muuttuvat.
    """
    global score_text, highscore_text, last_score_value, last_highscore_value
    
    if score != last_score_value:
        score_text = score_font.render(str(score), True, WHITE)
        last_score_value = score
    
    if highscore != last_highscore_value:
        highscore_text = score_font.render(str(highscore), True, WHITE)
        last_highscore_value = highscore

def draw_score():
    """
    Piirtää score- ja highscore-näytöt ruudulle paremmilla sijainneilla.
    """
    # Päivitä tekstit tarvittaessa
    update_score_display()
    
    # Score vasempaan alakulmaan ikoni + numero - siirretään vasemmalle
    score_y = SCREEN_HEIGHT - BUBBLE_RADIUS * 3
    icon_x = BUBBLE_RADIUS * 2
    
    # Ensin ikoni
    if bubble_score_icon:
        screen.blit(bubble_score_icon, (icon_x - bubble_score_icon.get_width()//2, 
                                       score_y - bubble_score_icon.get_height()//2))
    
    # Sitten teksti
    if score_text:
        text_x = icon_x + BUBBLE_RADIUS*1.5
        screen.blit(score_text, (text_x, score_y - score_text.get_height()//2))
    
    # Highscore oikeaan alakulmaan kruunu + numero - siirretään oikeammalle
    highscore_y = SCREEN_HEIGHT - BUBBLE_RADIUS * 3
    icon_x = SCREEN_WIDTH - BUBBLE_RADIUS * 3.5  # Siirretty enemmän oikealle
    
    # Ensin kruunu
    if crown_highscore_icon:
        screen.blit(crown_highscore_icon, (icon_x - crown_highscore_icon.get_width()//2, 
                                          highscore_y - crown_highscore_icon.get_height()//2))
    
    # Sitten teksti
    if highscore_text:
        text_x = icon_x - BUBBLE_RADIUS*1.5 - highscore_text.get_width()
        screen.blit(highscore_text, (text_x, highscore_y - highscore_text.get_height()//2))

def create_pop_particles(x, y, color, count=15):
    for _ in range(count):
        particles.append(Particle(x, y, color))

def get_neighbors(row, col):
    """
    Palauttaa listan (r, c) naapureista, ottaen huomioon rivin parillisuuden.
    """
    neighbors = []
    if row % 2 == 0:  # parillinen rivi
        directions = [(-1, -1), (-1, 0), (0, -1), (0, 1), (1, -1), (1, 0)]
    else:             # pariton rivi
        directions = [(-1, 0), (-1, 1), (0, -1), (0, 1), (1, 0), (1, 1)]
    
    for dr, dc in directions:
        neighbors.append((row + dr, col + dc))
    return neighbors

def create_grid():
    """
    Luo ruudukon, jossa jokaisessa solussa voi olla kupla tai None.
    """
    grid = []
    for row in range(GRID_ROWS):
        row_bubbles = []
        is_odd_row = row % 2 == 1
        
        for col in range(GRID_COLS):
            # Joka toinen rivi on sisennetty
            x_offset = BUBBLE_RADIUS if is_odd_row else 0
            x = col * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS + x_offset
            y = row * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
            
            # Skip positions that would go off-screen
            if x + BUBBLE_RADIUS > SCREEN_WIDTH:
                row_bubbles.append(None)
                continue
                
            # Generate color
            color = random.choice(COLORS)
            
            # Modify fill logic to prioritize leftmost columns
            if row < VISIBLE_ROWS:
                # More likely to fill left columns
                probability = 0.95 - (col * 0.05)  # 95% for leftmost, decreasing right
                if random.random() < probability:
                    row_bubbles.append({
                        'x': x,
                        'y': y,
                        'color': color,
                        'row': row,
                        'col': col
                    })
                else:
                    row_bubbles.append(None)
            else:
                if row < VISIBLE_ROWS + 20:
                    probability = 0.9 - (col * 0.04)  # 90% for leftmost, decreasing right
                    if random.random() < probability:
                        row_bubbles.append({
                            'x': x,
                            'y': y,
                            'color': color,
                            'row': row,
                            'col': col
                        })
                    else:
                        row_bubbles.append(None)
                else:
                    row_bubbles.append(None)
        grid.append(row_bubbles)
    
    # Ensure there are no isolated bubbles (each has at least one neighbor)
    for row in range(1, len(grid)):
        for col in range(len(grid[0])):
            if grid[row][col] is not None:
                has_neighbor = False
                neighbors = get_neighbors(row, col)
                for nr, nc in neighbors:
                    if (0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and
                            grid[nr][nc] is not None):
                        has_neighbor = True
                        break
                
                if not has_neighbor:
                    # Force at least one neighbor to exist
                    for nr, nc in neighbors:
                        if 0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and nr < row:
                            x_offset = BUBBLE_RADIUS if nr % 2 == 1 else 0
                            x = nc * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS + x_offset
                            
                            # Skip if would go off-screen
                            if x + BUBBLE_RADIUS > SCREEN_WIDTH:
                                continue
                                
                            y = nr * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
                            
                            grid[nr][nc] = {
                                'x': x,
                                'y': y, 
                                'color': random.choice(COLORS),
                                'row': nr,
                                'col': nc
                            }
                            break
    
    return grid

def draw_background():
    """
    Piirtää taustan jossa pelialue ja ampuja-alue on selkeästi erotettu.
    """
    # Luo gradientti pelialueelle (punaisen viivan yläpuoli)
    for y in range(GAME_OVER_LINE_Y):
        # Calculate gradient color
        r = int(DARK_BLUE[0] + (LIGHT_BLUE[0] - DARK_BLUE[0]) * y / GAME_OVER_LINE_Y)
        g = int(DARK_BLUE[1] + (LIGHT_BLUE[1] - DARK_BLUE[1]) * y / GAME_OVER_LINE_Y)
        b = int(DARK_BLUE[2] + (LIGHT_BLUE[2] - DARK_BLUE[2]) * y / GAME_OVER_LINE_Y)
        pygame.draw.line(screen, (r, g, b), (0, y), (SCREEN_WIDTH, y))
    
    # Piirrä erillinen alue ohjauspaneelille (punaisen viivan alapuoli)
    control_panel_color = (40, 42, 54)  # Tumma väri ohjauspaneelille
    control_panel_rect = pygame.Rect(0, GAME_OVER_LINE_Y, SCREEN_WIDTH, SCREEN_HEIGHT - GAME_OVER_LINE_Y)
    pygame.draw.rect(screen, control_panel_color, control_panel_rect)
    
    # Erittäin hitaat partikkelit ohjauspaneelissa
    for i in range(8):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(GAME_OVER_LINE_Y, SCREEN_HEIGHT)
        size = random.randint(1, 2)
        opacity = random.randint(15, 40)
        
        # Käytännössä staattiset partikkelit
        s = pygame.Surface((size*2, size*2), pygame.SRCALPHA)
        pygame.draw.circle(s, (255, 255, 255, opacity), (size, size), size)
        screen.blit(s, (int(x - size), int(y - size)))
    
    # Hienovarainen kiiltävä reunaviiva game over -linjan alapuolelle
    highlight_y = GAME_OVER_LINE_Y + 2
    highlight_surface = pygame.Surface((SCREEN_WIDTH, 2), pygame.SRCALPHA)
    highlight_surface.fill((255, 255, 255, 30))
    screen.blit(highlight_surface, (0, highlight_y))
    
    # Update and draw falling background particles
    for bubble in background_bubbles:
        # Update position
        bubble['y'] += bubble['speed']
        bubble['x'] += bubble['drift']
        
        # If bubble goes off screen, reset at top
        if bubble['y'] > SCREEN_HEIGHT:
            bubble['y'] = -bubble['size'] * 2
            bubble['x'] = random.randint(0, SCREEN_WIDTH)
        
        # If bubble goes off sides, wrap around
        if bubble['x'] < -bubble['size'] * 2:
            bubble['x'] = SCREEN_WIDTH + bubble['size']
        elif bubble['x'] > SCREEN_WIDTH + bubble['size'] * 2:
            bubble['x'] = -bubble['size']
        
        # Piirrä taustapartikkelit vain jos ne ovat pelialueella
        if bubble['y'] < GAME_OVER_LINE_Y:
            s = pygame.Surface((bubble['size']*2, bubble['size']*2), pygame.SRCALPHA)
            pygame.draw.circle(s, (255, 255, 255, 70), (bubble['size'], bubble['size']), bubble['size'])
            screen.blit(s, (int(bubble['x'] - bubble['size']), int(bubble['y'] - bubble['size'])))

def check_win_condition():
    """
    Tarkistaa, onko kaikki kuplat poistettu ruudukosta.
    """
    for row in grid:
        for bubble in row:
            if bubble is not None:
                return False
    return True

def predict_trajectory(start_x, start_y, dx, dy, max_points=100):
    """
    Ennustaa ampumiskuplan radan pisteet seinien ja kuplien törmäykseen asti.
    Palauttaa listan pisteistä.
    """
    points = [(start_x, start_y)]
    x, y = start_x, start_y
    vx, vy = dx, dy
    
    for _ in range(max_points):
        x += vx
        y += vy
        
        # Heijastukset seinistä
        if x - BUBBLE_RADIUS <= 0:
            x = BUBBLE_RADIUS
            vx = -vx
        elif x + BUBBLE_RADIUS >= SCREEN_WIDTH:
            x = SCREEN_WIDTH - BUBBLE_RADIUS
            vx = -vx
        
        # Katto
        if y - BUBBLE_RADIUS <= 0:
            points.append((x, y))
            break
        
        # Törmäys muihin kupliin
        collision_detected = False
        for row in grid:
            for bubble in row:
                if bubble:
                    bubble_y = bubble['y'] + scroll_offset
                    distance = math.sqrt((x - bubble['x'])**2 + (y - bubble_y)**2)
                    if distance < BUBBLE_RADIUS * 2:
                        collision_detected = True
                        break
            if collision_detected:
                break
        
        if collision_detected:
            points.append((x, y))
            break
            
        points.append((x, y))
    
    return points

def draw_trajectory(points):
    if len(points) < 2:
        return
        
    # Use a bright color with glow effect for better visibility
    for i in range(1, len(points)):
        # Higher base opacity for better visibility
        opacity = 230 - int(150 * i / len(points))
        width = 3 - 1.5 * i / len(points)
        
        start_point = points[i-1]
        end_point = points[i]
        
        # First draw a glow/outline effect
        s_glow = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        glow_color = (200, 200, 255, opacity // 3)
        pygame.draw.line(s_glow, glow_color, start_point, end_point, max(3, int(width + 2)))
        screen.blit(s_glow, (0, 0))
        
        # Then draw the main white line
        s = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
        pygame.draw.line(s, (255, 255, 255, opacity), start_point, end_point, max(1, int(width)))
        screen.blit(s, (0, 0))
        
        # Add brighter dots at intervals
        if i % 4 == 0:
            s2 = pygame.Surface((8, 8), pygame.SRCALPHA)
            pygame.draw.circle(s2, (255, 255, 255, opacity), (4, 4), 3)
            screen.blit(s2, (int(end_point[0] - 4), int(end_point[1] - 4)))

def draw_bubble(x, y, color, radius, is_shooter=False):
    # Draw outer ring
    pygame.draw.circle(screen, BLACK, (int(x), int(y)), radius + 1)
    
    # Draw main bubble with gradient effect
    for r in range(radius, 0, -1):
        factor = 1 - (radius - r) / radius * 0.4
        adjusted_color = (
            min(255, int(color[0] * factor)),
            min(255, int(color[1] * factor)),
            min(255, int(color[2] * factor))
        )
        pygame.draw.circle(screen, adjusted_color, (int(x), int(y)), r)
    
    # Add shine effect
    highlight_radius = radius * 0.35
    highlight_offset = radius * 0.4
    s = pygame.Surface((highlight_radius*2, highlight_radius*2), pygame.SRCALPHA)
    pygame.draw.circle(s, (255, 255, 255, 180), (highlight_radius, highlight_radius), highlight_radius)
    screen.blit(s, (int(x - highlight_offset - highlight_radius), int(y - highlight_offset - highlight_radius)))
    
    # Add smaller second highlight
    small_highlight = radius * 0.15
    s2 = pygame.Surface((small_highlight*2, small_highlight*2), pygame.SRCALPHA)
    pygame.draw.circle(s2, (255, 255, 255, 200), (small_highlight, small_highlight), small_highlight)
    screen.blit(s2, (int(x + highlight_offset - small_highlight), int(y + highlight_offset - small_highlight)))
    
    # Add pulsing effect for shooter bubble
    if is_shooter:
        pulse = math.sin(pygame.time.get_ticks() * 0.005) * 3
        pygame.draw.circle(screen, WHITE, (int(x), int(y)), int(radius + pulse), 1)

def draw_bubbles():
    """
    Piirtää ruudukon kuplat suoraan grafiikkana.
    """
    for row in grid:
        for bubble in row:
            if bubble:
                bubble_y = bubble['y'] + scroll_offset
                if -BUBBLE_RADIUS < bubble_y < SCREEN_HEIGHT + BUBBLE_RADIUS:
                    draw_bubble(bubble['x'], bubble_y, bubble['color'], BUBBLE_RADIUS)

def draw_shooter():
    """
    Piirtää ampumiskuplan, tähtäysviivan ja seuraavan kuplan.
    """
    if not game_over and not game_won:
        # Piirrä ampujan taustalle pyöreä koroke
        platform_radius = BUBBLE_RADIUS * 2
        platform_y = SHOOTER_Y + BUBBLE_RADIUS * 0.5
        platform_color = (50, 52, 64)
        
        pygame.draw.circle(screen, platform_color, (SCREEN_WIDTH // 2, platform_y), platform_radius)
        pygame.draw.circle(screen, (80, 82, 94), (SCREEN_WIDTH // 2, platform_y), platform_radius, 2)
        
        # Ampumiskupla
        draw_bubble(shooter_bubble['x'], shooter_bubble['y'], shooter_bubble['color'], BUBBLE_RADIUS, True)
        
        # Ennustettu rata, jos kupla ei liiku
        if not shooter_bubble['moving']:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            angle = math.atan2(mouse_y - SHOOTER_Y, mouse_x - SCREEN_WIDTH // 2)
            dx = math.cos(angle) * SHOT_SPEED
            dy = math.sin(angle) * SHOT_SPEED
            trajectory_points = predict_trajectory(SCREEN_WIDTH // 2, SHOOTER_Y, dx, dy)
            draw_trajectory(trajectory_points)
        
        # Seuraava kupla vasemmalle puolelle ampujaa
        next_bubble_x = SCREEN_WIDTH // 2 - BUBBLE_RADIUS * 4
        
        # Korostus seuraavalle kuplalle (pienennetty hieman)
        next_bubble_platform = pygame.Surface((BUBBLE_RADIUS*2.2, BUBBLE_RADIUS*2.2), pygame.SRCALPHA)
        pygame.draw.circle(next_bubble_platform, (60, 62, 74, 180), (BUBBLE_RADIUS*1.1, BUBBLE_RADIUS*1.1), BUBBLE_RADIUS*1.1)
        screen.blit(next_bubble_platform, (next_bubble_x - BUBBLE_RADIUS*1.1, SHOOTER_Y - BUBBLE_RADIUS*1.1))
        
        # Next-teksti sijoitettu selkeästi kuplan yläpuolelle
        next_font = pygame.font.SysFont('Arial', int(BUBBLE_RADIUS*0.9))
        next_text = next_font.render("Next:", True, (180, 180, 180))
        text_width = next_text.get_width()
        # Keskitetty tekstin sijainti kuplan yläpuolelle
        screen.blit(next_text, (next_bubble_x - text_width//2, SHOOTER_Y - BUBBLE_RADIUS*2.5))
        
        # Piirrä seuraava kupla
        draw_bubble(next_bubble_x, SHOOTER_Y, next_bubble['color'], BUBBLE_RADIUS)

def draw_game_over_line():
    """
    Piirtää game over -linjan ruudun alareunaan.
    """
    line_y = GAME_OVER_LINE_Y
    # Create pulsing effect
    pulse = math.sin(pygame.time.get_ticks() * 0.003) * 2
    line_width = 3 + int(pulse)
    
    # Draw glow effect
    for i in range(5):
        opacity = 150 - i * 30
        width = line_width + i*2
        s = pygame.Surface((SCREEN_WIDTH, width), pygame.SRCALPHA)
        pygame.draw.line(s, (255, 50, 50, opacity), (0, width//2), (SCREEN_WIDTH, width//2), width)
        screen.blit(s, (0, line_y - width//2))

def check_collision():
    """
    Tarkistaa törmäykset seiniin, kattoon ja toisiin kupliin.
    """
    if shooter_bubble['x'] - BUBBLE_RADIUS <= 0:
        shooter_bubble['x'] = BUBBLE_RADIUS
        shooter_bubble['dx'] = -shooter_bubble['dx']
    elif shooter_bubble['x'] + BUBBLE_RADIUS >= SCREEN_WIDTH:
        shooter_bubble['x'] = SCREEN_WIDTH - BUBBLE_RADIUS
        shooter_bubble['dx'] = -shooter_bubble['dx']
    
    if shooter_bubble['y'] - BUBBLE_RADIUS <= 0:
        shooter_bubble['moving'] = False
        snap_to_grid()
        reset_shooter()
        return
    
    min_collision_dist = float('inf')
    closest_bubble = None
    
    for row in grid:
        for bubble in row:
            if bubble:
                bubble_y = bubble['y'] + scroll_offset
                distance = math.sqrt((shooter_bubble['x'] - bubble['x'])**2 +
                                     (shooter_bubble['y'] - bubble_y)**2)
                if distance < BUBBLE_RADIUS * 2 and distance < min_collision_dist:
                    min_collision_dist = distance
                    closest_bubble = bubble
    
    if closest_bubble:
        collision_x = shooter_bubble['x'] - closest_bubble['x']
        collision_y = shooter_bubble['y'] - (closest_bubble['y'] + scroll_offset)
        collision_dist = math.sqrt(collision_x**2 + collision_y**2)
        if collision_dist > 0:
            overlap = (BUBBLE_RADIUS * 2) - collision_dist
            shooter_bubble['x'] += (collision_x / collision_dist) * overlap
            shooter_bubble['y'] += (collision_y / collision_dist) * overlap
        
        shooter_bubble['moving'] = False
        snap_to_grid()
        reset_shooter()
        return

def snap_to_grid():
    """
    Kiinnittää ampumiskuplan lähimpään sopivaan paikkaan ruudukossa.
    """
    adjusted_y = shooter_bubble['y'] - scroll_offset
    row = int(adjusted_y / (BUBBLE_RADIUS * 2))
    row = max(0, min(row, len(grid) - 1))  # ensure row is in valid range
    
    is_odd_row = row % 2 == 1
    offset = BUBBLE_RADIUS if is_odd_row else 0
    col_width = BUBBLE_RADIUS * 2
    col = int((shooter_bubble['x'] - offset) / col_width)
    col = max(0, min(col, GRID_COLS - 1))  # ensure col is in valid range
    
    # Check for immediate neighbors first - direct collision point
    candidates = []
    
    # Check a wider area for valid positions
    search_radius = 3  # Increased search radius
    for r_offset in range(-search_radius, search_radius + 1):
        for c_offset in range(-search_radius, search_radius + 1):
            r = row + r_offset
            c = col + c_offset
            if (0 <= r < len(grid) and 0 <= c < len(grid[0]) and 
                grid[r][c] is None):
                
                # Calculate position
                x_offset = BUBBLE_RADIUS if r % 2 == 1 else 0
                grid_x = c * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS + x_offset
                grid_y = r * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
                actual_grid_y = grid_y + scroll_offset
                
                # Calculate distance
                distance = math.sqrt((grid_x - shooter_bubble['x'])**2 + 
                                    (actual_grid_y - shooter_bubble['y'])**2)
                
                # Has neighbor?
                has_neighbor = False
                neighbors = get_neighbors(r, c)
                for nr, nc in neighbors:
                    if (0 <= nr < len(grid) and 0 <= nc < len(grid[0]) and
                            grid[nr][nc] is not None):
                        has_neighbor = True
                        break
                
                if has_neighbor:
                    candidates.append((distance, r, c, grid_x, grid_y))
    
    # Sort by distance
    if candidates:
        candidates.sort()
        _, row, col, x, y = candidates[0]
        
        # Place the bubble
        animate_snap(shooter_bubble['x'], shooter_bubble['y'], x, y + scroll_offset)
        grid[row][col] = {
            'x': x,
            'y': y,
            'color': shooter_bubble['color'],
            'row': row,
            'col': col
        }
        remove_matching_bubbles(row, col, shooter_bubble['color'])
        remove_floating_bubbles()
    else:
        # Fallback - create a bubble at the top row
        for c in range(GRID_COLS):
            if grid[0][c] is None:
                x_offset = 0  # First row is always even
                x = c * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS + x_offset
                y = BUBBLE_RADIUS
                
                grid[0][c] = {
                    'x': x,
                    'y': y,
                    'color': shooter_bubble['color'],
                    'row': 0,
                    'col': c
                }
                remove_matching_bubbles(0, c, shooter_bubble['color'])
                remove_floating_bubbles()
                return

def animate_snap(start_x, start_y, end_x, end_y):
    """
    Pieni animaatio, jossa kupla siirtyy lopulliseen ruudukon paikkaansa.
    """
    frames = 5
    for i in range(frames):
        t = (i + 1) / frames
        x = start_x + (end_x - start_x) * t
        y = start_y + (end_y - start_y) * t
        
        draw_background()
        draw_bubbles()
        
        # Piirretään liikkuva kupla
        draw_bubble(x, y, shooter_bubble['color'], BUBBLE_RADIUS)
        
        # Päivitä hiukkaset
        for particle in particles[:]:
            particle.update()
            particle.draw()
            if particle.life <= 0:
                particles.remove(particle)
        
        draw_game_over_line()
        draw_score()  # Piirrä pistenäyttö animaation aikana
        pygame.display.flip()
        pygame.time.delay(20)

def remove_matching_bubbles(row, col, color):
    """
    Etsi samanväriset vierekkäiset kuplat DFS:llä ja poista, jos vähintään 3.
    """
    if (row < 0 or row >= len(grid) or
        col < 0 or col >= len(grid[0]) or
        grid[row][col] is None):
        return
    
    bubble_color = grid[row][col]['color']
    visited = set()
    matches = []
    
    def dfs(r, c):
        if ((r, c) in visited or
            r < 0 or r >= len(grid) or
            c < 0 or c >= len(grid[0]) or
            grid[r][c] is None):
            return
        if grid[r][c]['color'] == bubble_color:
            visited.add((r, c))
            matches.append((r, c))
            for nr, nc in get_neighbors(r, c):
                dfs(nr, nc)
    
    dfs(row, col)
    
    if len(matches) >= 3:
        for r, c in matches:
            if grid[r][c] is not None:
                bubble_x = grid[r][c]['x']
                bubble_y = grid[r][c]['y'] + scroll_offset
                create_pop_particles(bubble_x, bubble_y, grid[r][c]['color'])
                grid[r][c] = None
        
        # Päivitä pistelaskuri
        global score, highscore
        score += len(matches) * 10  # Esim. 10 pistettä per poistettu kupla
        if score > highscore:
            highscore = score
        
        print(f"Removed {len(matches)} matching bubbles of color {bubble_color}")
    else:
        print(f"Only found {len(matches)} matches, need at least 3 to remove")

def remove_floating_bubbles():
    """
    Poistaa "leijuvat" kuplat, joilla ei ole yhteyttä yläreunaan.
    """
    visited = set()
    # Merkitse yläreunan kuplat
    for col in range(len(grid[0])):
        if grid[0][col] is not None:
            dfs_mark_connected(0, col, visited)
    
    # Poista kaikki, joita ei ole merkitty
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] is not None and (row, col) not in visited:
                bubble_x = grid[row][col]['x']
                bubble_y = grid[row][col]['y'] + scroll_offset
                create_pop_particles(bubble_x, bubble_y, grid[row][col]['color'], 20)
                grid[row][col] = None

def dfs_mark_connected(row, col, visited):
    """
    DFS, joka merkitsee yläreunaan yhteydessä olevat kuplat.
    """
    if ((row, col) in visited or
        row < 0 or row >= len(grid) or
        col < 0 or col >= len(grid[0]) or
        grid[row][col] is None):
        return
    visited.add((row, col))
    for nr, nc in get_neighbors(row, col):
        dfs_mark_connected(nr, nc, visited)

def reset_shooter():
    """
    Palauttaa ampumiskuplan alkuasetuksiin ja päivittää seuraavan kuplan.
    """
    shooter_bubble['x'] = SCREEN_WIDTH // 2
    shooter_bubble['y'] = SHOOTER_Y
    shooter_bubble['dx'] = 0
    shooter_bubble['dy'] = 0
    shooter_bubble['color'] = next_bubble['color']
    next_bubble['color'] = random.choice(COLORS)

def check_game_over():
    """
    Tarkistaa, onko jokin kupla saavuttanut game over -linjan.
    """
    for row in range(len(grid)):
        for col in range(len(grid[row])):
            if grid[row][col] is not None:
                bubble_bottom_y = grid[row][col]['y'] + scroll_offset + BUBBLE_RADIUS
                if bubble_bottom_y >= GAME_OVER_LINE_Y:
                    return True
    return False

def draw_game_over():
    """
    Piirtää game over -viestin ja ohjetekstin.
    """
    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.SysFont('Arial', 72, bold=True)
    text = font.render('GAME OVER', True, RED)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add shadow effect
    shadow = font.render('GAME OVER', True, BLACK)
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3))
    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)
    
    font_small = pygame.font.SysFont('Arial', 24)
    instruction = font_small.render('Press SPACE to restart', True, WHITE)
    instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(instruction, instruction_rect)

def draw_win_message():
    """
    Piirtää voittoviestin ja ohjetekstin.
    """
    # Create semi-transparent overlay
    overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
    overlay.fill((0, 0, 0, 150))
    screen.blit(overlay, (0, 0))
    
    font = pygame.font.SysFont('Arial', 72, bold=True)
    text = font.render('YOU WIN!', True, GREEN)
    text_rect = text.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
    
    # Add shadow effect
    shadow = font.render('YOU WIN!', True, BLACK)
    shadow_rect = shadow.get_rect(center=(SCREEN_WIDTH // 2 + 3, SCREEN_HEIGHT // 2 + 3))
    screen.blit(shadow, shadow_rect)
    screen.blit(text, text_rect)
    
    font_small = pygame.font.SysFont('Arial', 24)
    instruction = font_small.render('Press SPACE to restart', True, WHITE)
    instruction_rect = instruction.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 60))
    screen.blit(instruction, instruction_rect)

def restart_game():
    """
    Nollaa ruudukon ja pelitilan.
    """
    global grid, scroll_offset, game_over, game_won, shooter_bubble, particles, score
    global last_score_value, last_highscore_value
    
    grid = create_grid()
    initial_bottom_row_y = (VISIBLE_ROWS - 1) * BUBBLE_RADIUS * 2 + BUBBLE_RADIUS
    scroll_offset = INITIAL_BOTTOM_Y - initial_bottom_row_y
    game_over = False
    game_won = False
    particles = []
    shooter_bubble['x'] = SCREEN_WIDTH // 2
    shooter_bubble['y'] = SHOOTER_Y
    shooter_bubble['color'] = random.choice(COLORS)
    shooter_bubble['dx'] = 0
    shooter_bubble['dy'] = 0
    shooter_bubble['moving'] = False
    next_bubble['color'] = random.choice(COLORS)
    
    # Nollaa nykyinen pistemäärä
    score = 0
    
    # Pakota tekstin päivitys
    last_score_value = -1
    last_highscore_value = -1

def main():
    """
    Pelin pääsilmukka
    """
    global game_over, game_won, score, highscore, scroll_offset
    
    clock = pygame.time.Clock()
    running = True

    while running:
        draw_background()
        
        for event in pygame.event.get():
            if event.type == QUIT:
                running = False
            elif event.type == KEYDOWN and event.key == K_ESCAPE:
                running = False
            elif event.type == MOUSEBUTTONDOWN and not shooter_bubble['moving'] and not game_over and not game_won:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                angle = math.atan2(mouse_y - SHOOTER_Y, mouse_x - SCREEN_WIDTH // 2)
                shooter_bubble['dx'] = math.cos(angle) * SHOT_SPEED
                shooter_bubble['dy'] = math.sin(angle) * SHOT_SPEED
                shooter_bubble['moving'] = True
            elif event.type == KEYDOWN and (game_over or game_won) and event.key == K_SPACE:
                restart_game()
        
        # Päivitetään ampumiskuplan liike
        if shooter_bubble['moving'] and not game_over and not game_won:
            shooter_bubble['x'] += shooter_bubble['dx']
            shooter_bubble['y'] += shooter_bubble['dy']
            check_collision()
        
        # Scrollaus, jos ei peli ohi tai voitettu
        if not game_over and not game_won:
            scroll_offset += SCROLL_SPEED
            game_over = check_game_over()
            game_won = check_win_condition()
        
        # Päivitä hiukkaset
        for particle in particles[:]:
            particle.update()
            particle.draw()
            if particle.life <= 0:
                particles.remove(particle)
        
        # Piirrä kaikki elementit
        draw_bubbles()
        draw_shooter()
        draw_game_over_line()
        draw_score()

        if game_over:
            draw_game_over()
        elif game_won:
            draw_win_message()
        
        pygame.display.flip()

        clock.tick(60)

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    # Alusta pygame
    pygame.init()
    
    # Alusta peli
    initialize_game()
    
    # Käynnistä peli
    main()