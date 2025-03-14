import pygame
import random
import math
import sys
import colorsys
from pygame import mixer
import os

# Initialize pygame
pygame.init()
mixer.init()

# Load music files from data folder
bg_gameplay_music = mixer.Sound(os.path.join('data', 'bg-music.mp3'))
bg_menu_music = mixer.Sound(os.path.join('data', 'bg-menu-music.mp3'))

# Set volumes (adjust as needed)
bg_gameplay_music.set_volume(0.5)
bg_menu_music.set_volume(0.5)

# Variables to track music state
current_music = None

# Constants
SCREEN_WIDTH = 1000
SCREEN_HEIGHT = 600
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 60, 60)
GREEN = (80, 255, 80)
BLUE = (65, 105, 225)
YELLOW = (255, 215, 0)
GREY = (128, 128, 128)
CYAN = (0, 255, 255)
PURPLE = (186, 85, 211)
ORANGE = (255, 165, 0)
PLAYER_POS_X = SCREEN_WIDTH // 2
PLAYER_POS_Y = SCREEN_HEIGHT // 2
DEBRIS_TYPES = ["asteroid", "meteor", "satellite_fragment"]
DEBRIS_SPEED_MIN = 2
DEBRIS_SPEED_MAX = 5
NET_SPEED = 8
NET_SIZE = 20
TRAJECTORY_LENGTH = 100

# Stage settings - changed from 10 to 30 seconds
STAGE_DURATION = 30 * 1000
BASE_SPAWN_RATE = 0.45
SPAWN_RATE_INCREASE = 0.1
MAX_STAGES = 9
REPAIR_COST_PER_HEALTH = 1

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Space Debris Defense")
clock = pygame.time.Clock()

# Enhanced space background with varied celestial objects
NUM_STARS = 200
STAR_LAYERS = 3
stars = []
SPACE_OBJECTS = []  # For planets, asteroids, and other space objects

# Particle effects systems
debris_particles = []
explosion_particles = []

# Initialize enhanced space background
def init_stars():
    global stars, SPACE_OBJECTS
    stars = []
    SPACE_OBJECTS = []
    
    # Create distant space objects (behind most stars)
    # 1. Small distant planet
    for _ in range(1):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(50, SCREEN_HEIGHT-50)
        size = random.randint(40, 70)  # Small distant planet
        
        # Planet types
        planet_type = random.choice(['rocky', 'gas', 'ice', 'ringed'])
        if planet_type == 'rocky':
            base_color = random.choice([(120, 100, 80), (180, 160, 140), (80, 70, 60)])
            has_atmosphere = random.random() < 0.5
        elif planet_type == 'gas':
            base_color = random.choice([(230, 180, 100), (160, 180, 210), (180, 140, 200)])
            has_atmosphere = True
        elif planet_type == 'ice':
            base_color = random.choice([(170, 200, 230), (200, 220, 255), (160, 180, 210)])
            has_atmosphere = random.random() < 0.7
        else:  # ringed
            base_color = random.choice([(200, 180, 140), (180, 160, 120), (160, 140, 100)])
            has_atmosphere = True
            
        planet = {
            'x': x,
            'y': y,
            'size': size,
            'color': base_color,
            'type': planet_type,
            'atmosphere': has_atmosphere,
            'speed': 0.05,  # Very slow movement - all moving LEFT
            'rotation': 0,
            'rotation_speed': random.uniform(0.01, 0.05)
        }
        SPACE_OBJECTS.append(planet)
    
    # 2. Distant nebula/gas cloud (very subtle)
    for _ in range(2):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.randint(200, 300)
        
        # Very subdued colors
        hue = random.random()
        r, g, b = colorsys.hsv_to_rgb(hue, 0.2, 0.8)
        color = (int(r*255), int(g*255), int(b*255))
        
        nebula = {
            'x': x,
            'y': y,
            'size': size,
            'color': color,
            'opacity': random.randint(5, 12),  # Very transparent
            'speed': 0.03,  # Very slow movement - all moving LEFT
            'type': 'nebula'
        }
        SPACE_OBJECTS.append(nebula)
    
    # 3. Distant asteroid field (group of tiny dots)
    for _ in range(1):
        center_x = random.randint(0, SCREEN_WIDTH)
        center_y = random.randint(0, SCREEN_HEIGHT)
        field_width = random.randint(150, 300)
        
        asteroids = []
        for _ in range(20):
            ast_x = random.randint(-field_width//2, field_width//2)
            ast_y = random.randint(-field_width//2, field_width//2)
            ast_size = random.uniform(0.5, 2)
            asteroids.append((ast_x, ast_y, ast_size))
        
        asteroid_field = {
            'x': center_x,
            'y': center_y,
            'asteroids': asteroids,
            'width': field_width,
            'speed': 0.08,  # Moving LEFT
            'type': 'asteroid_field'
        }
        SPACE_OBJECTS.append(asteroid_field)
    
    # Regular stars (three layers)
    # Layer 3 - Background stars (most distant)
    background_stars = []
    for _ in range(NUM_STARS // 2):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.uniform(0.5, 1.0)
        brightness = random.randint(100, 160)
        color = (brightness, brightness, brightness)
        speed = random.uniform(0.05, 0.1)  # Slowest, but ALL moving LEFT
        background_stars.append([x, y, size, color, speed])
    stars.append(background_stars)
    
    # Layer 2 - Mid-distance stars
    mid_stars = []
    for _ in range(NUM_STARS // 3):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.uniform(1.0, 1.5)
        brightness = random.randint(160, 200)
        color = (brightness, brightness, brightness)
        speed = random.uniform(0.2, 0.4)  # Medium speed, ALL moving LEFT
        mid_stars.append([x, y, size, color, speed])
    stars.append(mid_stars)
    
    # Layer 1 - Foreground stars (closest)
    foreground_stars = []
    for _ in range(NUM_STARS // 6):
        x = random.randint(0, SCREEN_WIDTH)
        y = random.randint(0, SCREEN_HEIGHT)
        size = random.uniform(1.5, 2.5)
        brightness = random.randint(200, 255)
        color = (brightness, brightness, brightness)
        speed = random.uniform(0.5, 1.0)  # Fastest, ALL moving LEFT
        foreground_stars.append([x, y, size, color, speed])
    stars.append(foreground_stars)

# Update space objects and stars
def update_stars():
    # Update space objects
    for obj in SPACE_OBJECTS:
        if obj['type'] == 'nebula' or obj['type'] == 'planet':
            obj['x'] -= obj['speed']
            if obj['x'] + obj['size'] < 0:
                obj['x'] = SCREEN_WIDTH + obj['size']//2
                obj['y'] = random.randint(50, SCREEN_HEIGHT-50)
        
        if obj['type'] == 'planet':
            obj['rotation'] += obj['rotation_speed']
            
        if obj['type'] == 'asteroid_field':
            obj['x'] -= obj['speed']
            if obj['x'] + obj['width']//2 < 0:
                obj['x'] = SCREEN_WIDTH + obj['width']//2
                obj['y'] = random.randint(50, SCREEN_HEIGHT-50)
    
    # Update stars with variable speeds - ALL moving LEFT
    for layer in stars:
        for star in layer:
            star[0] -= star[4]  # Subtract speed to move LEFT
            if star[0] < 0:
                star[0] = SCREEN_WIDTH
                star[1] = random.randint(0, SCREEN_HEIGHT)

# Draw space objects and stars
def draw_stars(surface):
    # Draw space objects first
    for obj in SPACE_OBJECTS:
        if obj['type'] == 'nebula':
            # Very subtle nebula that won't distract
            nebula_surf = pygame.Surface((obj['size']*2, obj['size']*2), pygame.SRCALPHA)
            for radius in range(obj['size'], 0, -30):
                # Extremely low opacity
                opacity = max(1, obj['opacity'] * (radius/obj['size']))
                color = (*obj['color'][:3], int(opacity))
                pygame.draw.circle(nebula_surf, color, (obj['size'], obj['size']), radius)
            
            surface.blit(nebula_surf, (int(obj['x']-obj['size']), int(obj['y']-obj['size'])))
            
        elif obj['type'] == 'planet':
            # Draw a distant planet (small circle with subtle details)
            # Base planet
            pygame.draw.circle(surface, obj['color'], (int(obj['x']), int(obj['y'])), obj['size'])
            
            # Subtle surface details
            if obj['type'] == 'rocky':
                # Add a few craters or surface marks
                for _ in range(3):
                    crater_pos = (int(obj['x'] + random.randint(-obj['size']//2, obj['size']//2)),
                                 int(obj['y'] + random.randint(-obj['size']//2, obj['size']//2)))
                    crater_size = random.randint(2, 4)
                    darker = tuple(max(0, c-40) for c in obj['color'])
                    pygame.draw.circle(surface, darker, crater_pos, crater_size)
            
            elif obj['type'] == 'gas':
                # Add bands/swirls
                for i in range(2):
                    offset = -obj['size']//3 + i*obj['size']//1.5
                    band_rect = pygame.Rect(obj['x']-obj['size'], obj['y']+offset-2, obj['size']*2, 5)
                    band_color = tuple(min(255, c+20) if i%2==0 else max(0, c-20) for c in obj['color'])
                    pygame.draw.ellipse(surface, band_color, band_rect)
            
            elif obj['type'] == 'ringed':
                # Add rings
                ring_surf = pygame.Surface((obj['size']*3, obj['size']*3), pygame.SRCALPHA)
                ring_color = tuple(min(255, c+40) for c in obj['color'])
                pygame.draw.ellipse(ring_surf, (*ring_color, 100), (0, obj['size']-2, obj['size']*3, 4))
                pygame.draw.ellipse(ring_surf, (*ring_color, 70), (5, obj['size'], obj['size']*3-10, 2))
                
                # Rotate rings slightly
                rot_ring = pygame.transform.rotate(ring_surf, obj['rotation'])
                ring_rect = rot_ring.get_rect(center=(obj['x'], obj['y']))
                surface.blit(rot_ring, ring_rect)
            
            # Add subtle atmosphere glow if present
            if obj['atmosphere']:
                atmo_surf = pygame.Surface((obj['size']*2.5, obj['size']*2.5), pygame.SRCALPHA)
                atmo_color = (200, 220, 255, 10) if obj['type'] == 'ice' else (255, 255, 220, 8)
                pygame.draw.circle(atmo_surf, atmo_color, 
                                (int(atmo_surf.get_width()//2), int(atmo_surf.get_height()//2)), 
                                int(obj['size']*1.2))
                surface.blit(atmo_surf, (int(obj['x']-atmo_surf.get_width()//2), 
                                       int(obj['y']-atmo_surf.get_height()//2)))
        
        elif obj['type'] == 'asteroid_field':
            # Very subtle, distant asteroid field
            for ast_x, ast_y, ast_size in obj['asteroids']:
                # Fixed calculation - asteroids should move with field
                current_x = obj['x'] + ast_x
                current_y = obj['y'] + ast_y
                # Draw very small dots
                brightness = random.randint(100, 170)
                pygame.draw.circle(surface, (brightness, brightness, brightness), 
                                 (int(current_x), int(current_y)), int(ast_size))
    
    # Draw stars after space objects
    for layer_index, layer in enumerate(stars):
        for star in layer:
            # Simple star without excessive glow
            brightness_change = random.randint(-10, 10)
            b = min(255, max(50, star[3][0] + brightness_change))
            pygame.draw.circle(surface, (b, b, b), (int(star[0]), int(star[1])), star[2])
            
            # Only add subtle glow to the largest stars
            if layer_index == 2 and star[2] > 2:
                glow = pygame.Surface((int(star[2]*5), int(star[2]*5)), pygame.SRCALPHA)
                pygame.draw.circle(glow, (b, b, b, 30), 
                                (int(star[2]*2.5), int(star[2]*2.5)), int(star[2]*2))
                surface.blit(glow, (int(star[0]-star[2]*2.5), int(star[1]-star[2]*2.5)))

# Create particle effect
def create_particles(x, y, color, count, speed_range, size_range, life_range):
    particles = []
    for _ in range(count):
        angle = random.uniform(0, math.pi * 2)
        speed = random.uniform(speed_range[0], speed_range[1])
        size = random.uniform(size_range[0], size_range[1])
        life = random.uniform(life_range[0], life_range[1])
        particles.append({
            'x': x,
            'y': y,
            'dx': math.cos(angle) * speed,
            'dy': math.sin(angle) * speed,
            'size': size,
            'color': color,
            'life': life,
            'max_life': life
        })
    return particles

# Update particles
def update_particles(particles):
    for i in range(len(particles)-1, -1, -1):
        p = particles[i]
        p['x'] += p['dx']
        p['y'] += p['dy']
        p['life'] -= 0.05
        
        # Remove dead particles
        if p['life'] <= 0:
            particles.pop(i)

# Draw particles
def draw_particles(surface, particles):
    for p in particles:
        # Fade out as life decreases
        alpha = int(255 * (p['life'] / p['max_life']))
        size = max(1, p['size'] * (p['life'] / p['max_life']))
        
        # Create surface with transparency for the particle
        particle_surf = pygame.Surface((int(size*2), int(size*2)), pygame.SRCALPHA)
        r, g, b = p['color']
        pygame.draw.circle(particle_surf, (r, g, b, alpha), (int(size), int(size)), int(size))
        surface.blit(particle_surf, (int(p['x'] - size), int(p['y'] - size)))

# Enhanced Text Functions
def draw_text_with_shadow(surface, text, font, color, position, shadow_offset=1):
    """Draw text with a simple shadow effect"""
    # Solid black shadow
    shadow = font.render(text, True, (0, 0, 0))
    text_surface = font.render(text, True, color)
    
    # Simple offset shadow
    surface.blit(shadow, (position[0] + shadow_offset, position[1] + shadow_offset))
    surface.blit(text_surface, position)

def draw_plain_text(surface, text, font, color, position):
    """Draw text with no effects - just plain text"""
    text_surface = font.render(text, True, color)
    surface.blit(text_surface, position)

def draw_button(surface, rect, text, font, color, bg_color, hover=False, disabled=False):
    """Draw a button with hover and press effects"""
    if disabled:
        bg_color = GREY
    elif hover:
        # Lighten color when hovered
        r, g, b = bg_color
        bg_color = (min(r+30, 255), min(g+30, 255), min(b+30, 255))
    
    # Draw button with rounded corners
    pygame.draw.rect(surface, bg_color, rect, border_radius=8)
    
    # Add highlight on top
    highlight = pygame.Surface((rect.width, rect.height//3), pygame.SRCALPHA)
    highlight.fill((255, 255, 255, 50))
    highlight_rect = highlight.get_rect(topleft=(rect.x, rect.y))
    surface.blit(highlight, highlight_rect)
    
    # Add 3D effect with border
    pygame.draw.rect(surface, (50, 50, 50), rect, 2, border_radius=8)
    
    # Draw text
    text_surf = font.render(text, True, color)
    text_rect = text_surf.get_rect(center=rect.center)
    surface.blit(text_surf, text_rect)
    
    return rect

# Improved load_image function with more detailed visuals
def load_image(name, size=None):
    """Create visually enhanced placeholders for game objects"""
    try:
        if name == "player":
            image = pygame.Surface((60, 60), pygame.SRCALPHA)
            
            # Main hull - more elongated shape
            pygame.draw.polygon(image, (50, 80, 150), [(30, 5), (15, 40), (45, 40)])
            pygame.draw.rect(image, (70, 100, 170), (15, 40, 30, 10))
            
            # Collection bay/cargo hold (open area for debris storage)
            pygame.draw.rect(image, (40, 60, 120), (20, 30, 20, 15))
            pygame.draw.rect(image, (30, 40, 100), (22, 33, 16, 9))
            
            # Collection arms/manipulators
            pygame.draw.line(image, CYAN, (10, 35), (20, 30), 3)  # Left arm
            pygame.draw.line(image, CYAN, (50, 35), (40, 30), 3)  # Right arm
            pygame.draw.circle(image, WHITE, (10, 35), 3)  # Left gripper
            pygame.draw.circle(image, WHITE, (50, 35), 3)  # Right gripper
            
            # Cockpit - larger and more detailed
            pygame.draw.ellipse(image, (200, 230, 255), (25, 15, 10, 12))
            pygame.draw.ellipse(image, (150, 200, 255), (27, 17, 6, 8))
            
            # Engine systems
            pygame.draw.rect(image, (80, 80, 100), (18, 50, 24, 5))  # Engine housing
            
            # Thruster glow effects
            pygame.draw.polygon(image, ORANGE, [(22, 55), (28, 63), (32, 63), (38, 55)])
            pygame.draw.polygon(image, YELLOW, [(25, 55), (29, 60), (31, 60), (35, 55)])
            
            # Detail lines for tech look
            pygame.draw.line(image, WHITE, (30, 5), (30, 15), 1)  # Antenna
            pygame.draw.circle(image, RED, (30, 5), 2)  # Antenna tip
            pygame.draw.line(image, WHITE, (15, 45), (45, 45), 1)  # Hull detail
            
            # Side thrusters for maneuvering
            pygame.draw.rect(image, (60, 60, 100), (10, 42, 5, 6))  # Left thruster
            pygame.draw.rect(image, (60, 60, 100), (45, 42, 5, 6))  # Right thruster
            pygame.draw.polygon(image, (255, 120, 0), [(10, 45), (5, 45), (7, 48)])  # Left thrust
            pygame.draw.polygon(image, (255, 120, 0), [(50, 45), (55, 45), (53, 48)])  # Right thrust
            
            # Scanner lights
            pygame.draw.circle(image, (0, 255, 200), (15, 25), 2)
            pygame.draw.circle(image, (0, 255, 200), (45, 25), 2)
            
        elif name == "satellite":
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            # Main body
            pygame.draw.circle(image, GREY, (25, 25), 15)
            # Solar panels
            pygame.draw.rect(image, BLUE, (0, 20, 10, 10))
            pygame.draw.rect(image, BLUE, (40, 20, 10, 10))
            # Detail lines
            pygame.draw.line(image, WHITE, (10, 25), (0, 25), 2)
            pygame.draw.line(image, WHITE, (40, 25), (50, 25), 2)
            # Antenna
            pygame.draw.line(image, WHITE, (25, 10), (25, 0), 2)
            pygame.draw.circle(image, RED, (25, 0), 2)
            # Highlight
            pygame.draw.circle(image, WHITE, (20, 20), 3)
            
        elif name == "asteroid":
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            # Create more irregular, realistic asteroid shape
            points = []
            radius = 15
            num_points = 12  # More points for more irregular shape
            for i in range(num_points):
                angle = i * (2 * math.pi / num_points)
                r = radius * (0.7 + random.random() * 0.5)  # More variation in radius
                points.append((25 + r * math.cos(angle), 25 + r * math.sin(angle)))
            
            # Base color variations - some rocky, some metallic
            base_color = random.choice([
                (120, 110, 100),  # Rocky brown
                (100, 100, 110),  # Gray stone
                (130, 120, 110),  # Light brown
                (80, 75, 70)      # Dark rocky
            ])
            
            # Draw base asteroid
            pygame.draw.polygon(image, base_color, points)
            
            # Add realistic surface details - craters, cracks, and highlights
            for _ in range(6):  # More details
                pos = (random.randint(10, 40), random.randint(10, 40))
                size = random.randint(2, 6)
                # Vary crater colors
                crater_color = (base_color[0] - 30, base_color[1] - 30, base_color[2] - 30)
                pygame.draw.circle(image, crater_color, pos, size)
                # Add crater rim highlights
                highlight_pos = (pos[0] - 1, pos[1] - 1)
                pygame.draw.circle(image, (min(base_color[0] + 40, 255), min(base_color[1] + 40, 255), min(base_color[2] + 40, 255)), highlight_pos, size - 1, 1)
            
            # Add surface striations/cracks
            for _ in range(3):
                start = (random.randint(10, 40), random.randint(10, 40))
                end = (start[0] + random.randint(-10, 10), start[1] + random.randint(-10, 10))
                pygame.draw.line(image, (60, 60, 60), start, end, 1)
            
        elif name == "meteor":
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Create more realistic meteor with molten core
            core_size = random.randint(8, 12)
            outer_size = core_size + random.randint(3, 6)
            
            # Draw heated/burning outer layer with glow
            for r in range(outer_size + 5, outer_size - 1, -1):
                # Graduated heat colors from outer to inner
                alpha = 100 if r > outer_size else 255
                if r > outer_size:
                    color = (255, 150, 50, alpha)  # Outer glow
                elif r > outer_size - 2:
                    color = (230, 120, 30)  # Outer edge
                else:
                    color = (200, 80, 20)  # Near core
                pygame.draw.circle(image, color, (25, 25 - outer_size//3), r)
            
            # Molten core
            pygame.draw.circle(image, (255, 200, 50), (25, 25 - outer_size//3), core_size)
            pygame.draw.circle(image, (255, 255, 200), (25, 25 - outer_size//3 - 1), core_size//2)
            
            # Dynamic flame trail with multiple layers
            flame_points = []
            flame_center = 25
            flame_start = 25 - outer_size//3 + outer_size
            
            # Primary flame layer
            flame_points = [
                (flame_center - outer_size//2, flame_start),
                (flame_center - outer_size, flame_start + outer_size*1.5),
                (flame_center - outer_size//4, flame_start + outer_size*1.2),
                (flame_center, flame_start + outer_size*2),
                (flame_center + outer_size//4, flame_start + outer_size*1.2),
                (flame_center + outer_size, flame_start + outer_size*1.5),
                (flame_center + outer_size//2, flame_start)
            ]
            pygame.draw.polygon(image, (255, 120, 30), flame_points)
            
            # Inner hotter flame
            inner_flame = [
                (flame_center - outer_size//4, flame_start),
                (flame_center - outer_size//2, flame_start + outer_size),
                (flame_center, flame_start + outer_size*1.5),
                (flame_center + outer_size//2, flame_start + outer_size),
                (flame_center + outer_size//4, flame_start)
            ]
            pygame.draw.polygon(image, (255, 200, 50), inner_flame)
            
            # Hottest core flame
            core_flame = [
                (flame_center - outer_size//8, flame_start),
                (flame_center, flame_start + outer_size),
                (flame_center + outer_size//8, flame_start)
            ]
            pygame.draw.polygon(image, (255, 255, 150), core_flame)
            
        elif name == "satellite_fragment":
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Choose a random fragment type
            fragment_type = random.choice(['panel', 'antenna', 'module', 'frame'])
            
            if fragment_type == 'panel':
                # Broken solar panel
                panel_color = random.choice([(70, 130, 180), (100, 149, 237), (30, 144, 255)])
                
                # Draw broken panel base
                points = [
                    (10, 10), (40, 5), (45, 30), 
                    (35, 35), (40, 25), (20, 30), (15, 20)
                ]
                pygame.draw.polygon(image, panel_color, points)
                
                # Draw solar cell grid lines
                for x in range(15, 40, 5):
                    pygame.draw.line(image, (50, 50, 50), (x, 10), (x, 30), 1)
                for y in range(10, 35, 5):
                    pygame.draw.line(image, (50, 50, 50), (15, y), (40, y), 1)
                
                # Add torn wires/connections
                for _ in range(4):
                    start_x = random.choice([15, 20, 25, 30, 35])
                    start_y = random.choice([10, 15, 20, 25, 30])
                    pygame.draw.line(image, (255, 50, 50), 
                                  (start_x, start_y), 
                                  (start_x + random.randint(-5, 5), start_y + random.randint(-5, 5)), 
                                  1)
            
            elif fragment_type == 'antenna':
                # Broken antenna or communication equipment
                base_color = (180, 180, 180)
                
                # Main body
                pygame.draw.rect(image, base_color, (20, 15, 10, 25))
                
                # Bent/broken antenna
                pygame.draw.line(image, (200, 200, 200), (25, 15), (15, 5), 3)
                pygame.draw.line(image, (200, 200, 200), (25, 15), (35, 5), 3)
                
                # Electronics/wiring exposed
                pygame.draw.rect(image, (20, 20, 20), (22, 20, 6, 15))
                pygame.draw.line(image, RED, (23, 22), (23, 33), 1)
                pygame.draw.line(image, YELLOW, (25, 22), (25, 33), 1)
                pygame.draw.line(image, GREEN, (27, 22), (27, 33), 1)
            
            elif fragment_type == 'module':
                # Broken satellite module
                pygame.draw.rect(image, (100, 100, 100), (10, 10, 30, 25))
                
                # Damage effect - exposed internal components
                pygame.draw.polygon(image, (50, 50, 50), 
                                 [(15, 10), (35, 15), (30, 25), (20, 30), (10, 20)])
                
                # Circuit boards and components
                pygame.draw.rect(image, (0, 100, 0), (18, 15, 15, 10))
                for i in range(3):
                    x = 20 + i*5
                    pygame.draw.rect(image, (200, 200, 0), (x, 17, 2, 2))
                    pygame.draw.rect(image, (0, 200, 200), (x, 22, 2, 2))
            
            else:  # frame
                # Structural framework piece
                pygame.draw.polygon(image, (150, 150, 150), 
                                 [(10, 10), (40, 15), (45, 35), (15, 40), (5, 30)])
                
                # Rivets and connection points
                for x, y in [(15, 15), (35, 20), (40, 30), (20, 35), (10, 25)]:
                    pygame.draw.circle(image, (200, 200, 200), (x, y), 2)
                    pygame.draw.circle(image, (100, 100, 100), (x, y), 1)
                
                # Torn/bent metal details
                pygame.draw.line(image, (180, 180, 180), (10, 10), (5, 5), 2)
                pygame.draw.line(image, (180, 180, 180), (45, 35), (50, 40), 2)
            
        elif name == "net":
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            
            # Create outer containment ring
            pygame.draw.circle(image, (180, 200, 255), (25, 25), 20, 2)
            
            # Inner energy field - semi-transparent capture zone
            inner_field = pygame.Surface((36, 36), pygame.SRCALPHA)
            pygame.draw.circle(inner_field, (100, 200, 255, 70), (18, 18), 16)
            # Add ripple effect in the energy field
            pygame.draw.circle(inner_field, (150, 220, 255, 40), (18, 18), 12)
            pygame.draw.circle(inner_field, (200, 240, 255, 30), (18, 18), 8)
            image.blit(inner_field, (7, 7))
            
            # Stabilizing emitters around the ring (4 points)
            for angle in range(0, 360, 90):
                rad = math.radians(angle)
                emitter_x = int(25 + 18 * math.cos(rad))
                emitter_y = int(25 + 18 * math.sin(rad))
                # Draw emitter node
                pygame.draw.circle(image, (220, 220, 220), (emitter_x, emitter_y), 3)
                pygame.draw.circle(image, (50, 200, 255), (emitter_x, emitter_y), 2)
            
            # Energy field connection lines
            for angle in range(0, 360, 45):
                rad = math.radians(angle)
                start_x = int(25 + 10 * math.cos(rad))
                start_y = int(25 + 10 * math.sin(rad))
                end_x = int(25 + 18 * math.cos(rad))
                end_y = int(25 + 18 * math.sin(rad))
                pygame.draw.line(image, (100, 200, 255, 150), (start_x, start_y), (end_x, end_y), 1)
            
            # Central control module
            pygame.draw.circle(image, (220, 220, 255), (25, 25), 6)
            pygame.draw.circle(image, (100, 150, 255), (25, 25), 4)
            pygame.draw.circle(image, (230, 230, 255), (23, 23), 1)  # Highlight
            
            # Tether beam/line (high-tech alternative to a rope)
            pygame.draw.line(image, (150, 220, 255), (25, 25), (25, 50), 3)
            
            # Energy pulse along the tether
            pulse_height = 8
            pulse_pos = random.randint(25, 45)
            pulse_surf = pygame.Surface((8, pulse_height), pygame.SRCALPHA)
            for i in range(pulse_height):
                # Gradient pulse effect
                alpha = 255 if i == pulse_height//2 else 100 - abs(i - pulse_height//2) * 30
                pygame.draw.line(pulse_surf, (200, 230, 255, max(0, alpha)), 
                                (0, i), (8, i), 2)
            image.blit(pulse_surf, (21, pulse_pos))
            
        else:
            # Fallback
            image = pygame.Surface((50, 50), pygame.SRCALPHA)
            pygame.draw.rect(image, WHITE, (0, 0, 50, 50), 1)
        
        # Make sure size is properly formatted before scaling
        if size and isinstance(size, tuple) and len(size) == 2:
            return pygame.transform.scale(image, size)
        return image
    except pygame.error as e:
        print(f"Unable to load image: {e}")
        return pygame.Surface((50, 50))

class Player:
    """Player spaceship that throws nets to catch space debris"""
    def __init__(self):
        self.x = PLAYER_POS_X
        self.y = PLAYER_POS_Y
        self.image = load_image("player", (60, 60))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.health = 100
        self.net = None
        self.max_net_distance = self.y - NET_SIZE
        self.thruster_particles = []
        self.shield_active = False
        self.shield_timer = 0

    def update(self):
        # Create thruster particles
        if random.random() < 0.3:
            self.thruster_particles.extend(create_particles(
                self.x, self.y + 30, 
                (random.randint(200, 255), random.randint(100, 170), 0),
                3, (0.2, 1.0), (1, 3), (0.5, 1.0)
            ))
        
        # Update thruster particles
        update_particles(self.thruster_particles)
        
        # Update shield effect
        if self.shield_active:
            self.shield_timer -= 1
            if self.shield_timer <= 0:
                self.shield_active = False

    def draw(self, surface):
        # Draw thruster particles
        draw_particles(surface, self.thruster_particles)
        
        # Draw player
        surface.blit(self.image, self.rect)
        
        # Draw shield effect if active
        if self.shield_active:
            shield_surf = pygame.Surface((80, 80), pygame.SRCALPHA)
            shield_color = (100, 150, 255, 100)
            pygame.draw.circle(shield_surf, shield_color, (40, 40), 35)
            pygame.draw.circle(shield_surf, (200, 230, 255, 50), (40, 40), 38)
            surface.blit(shield_surf, (self.x - 40, self.y - 40))

    def take_damage(self, amount):
        """Reduce player health and check if destroyed"""
        self.health -= amount
        
        # Visual feedback - create damage particles
        explosion_particles.extend(create_particles(
            self.x, self.y, (255, 100, 0), 
            20, (1, 3), (2, 4), (0.5, 1.5)
        ))
        
        # Activate shield effect briefly for visual feedback
        self.shield_active = True
        self.shield_timer = 15
        
        if self.health <= 0:
            self.health = 0
            # Big explosion on death
            explosion_particles.extend(create_particles(
                self.x, self.y, (255, 200, 0), 
                50, (2, 5), (3, 6), (1.0, 2.0)
            ))
            return True
        return False
        
    def repair(self, amount):
        """Repair the ship"""
        previous_health = self.health
        self.health = min(100, self.health + amount)
        
        # Visual feedback - create repair particles
        if self.health > previous_health:
            repair_particles = create_particles(
                self.x, self.y, (100, 255, 100), 
                15, (0.5, 2), (2, 4), (0.5, 1.5)
            )
            explosion_particles.extend(repair_particles)

    def throw_net(self, angle, power):
        """Create and throw a new net if none is active"""
        if self.net is None or (self.net and not self.net.active):
            self.net = Net(self.x, self.y, angle, power)
            return self.net
        return None

class Satellite:
    """Stationary satellites that need to be protected"""
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.image = load_image("satellite", (40, 40))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.alive = True
        self.rotation = 0
        self.rotation_speed = random.uniform(0.2, 0.8)
        
    def update(self):
        if self.alive:
            # Slowly rotate the satellite
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation = 0

    def draw(self, surface):
        """Draw the satellite if it's still alive"""
        if self.alive:
            # Rotate the image
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            new_rect = rotated_image.get_rect(center=self.rect.center)
            surface.blit(rotated_image, new_rect)
            
            # Draw a more subtle glow that won't create overlapping halos
            glow_surf = pygame.Surface((50, 50), pygame.SRCALPHA)
            # Much less intense glow with lower opacity
            pygame.draw.circle(glow_surf, (100, 255, 100, 15), (25, 25), 20)
            surface.blit(glow_surf, (self.x - 25, self.y - 25))

    def destroy(self):
        """Mark the satellite as destroyed"""
        self.alive = False
        # Create explosion particles
        explosion_particles.extend(create_particles(
            self.x, self.y, (255, 150, 0), 
            30, (1, 3), (2, 5), (0.8, 1.8)
        ))

class Debris:
    """Space debris that threatens the player and satellites"""
    def __init__(self, spawn_x, spawn_y, target_x, target_y, debris_type):
        self.x = spawn_x
        self.y = spawn_y
        self.type = debris_type
        self.image = load_image(debris_type, (30, 30))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.caught = False
        self.rotation = random.randint(0, 360)
        self.rotation_speed = random.uniform(1, 3) * (1 if random.random() > 0.5 else -1)
        
        # Aseta pistearvot ja vaurius debris-tyypin mukaan
        if debris_type == "asteroid":
            self.value = 20
            self.damage = 15
            self.trail_color = (100, 100, 100)
        elif debris_type == "meteor":
            self.value = 30
            self.damage = 25
            self.trail_color = (255, 100, 0)
        else:  # satellite_fragment
            self.value = 10
            self.damage = 10
            self.trail_color = (100, 200, 255)
        
        # Lasketaan suunta kohteeseen ja asetetaan nopeus
        dx = target_x - spawn_x
        dy = target_y - spawn_y
        distance = math.hypot(dx, dy)
        # Valitaan satunnaisesti nopeus debris-tyypin mukaisesti
        speed = random.uniform(DEBRIS_SPEED_MIN, DEBRIS_SPEED_MAX)
        self.vx = (dx / distance) * speed
        self.vy = (dy / distance) * speed
        
        self.trail_particles = []
    
    def update(self):
        """Move the debris and check if it's off-screen"""
        if not self.caught:
            self.x += self.vx
            self.y += self.vy
            self.rect.center = (self.x, self.y)
            self.rotation += self.rotation_speed
            if self.rotation >= 360:
                self.rotation -= 360
            # Luodaan trail-partikkeleita
            if random.random() < 0.2:
                self.trail_particles.extend(create_particles(
                    self.x - 5, self.y, self.trail_color, 
                    2, (0.1, 0.3), (1, 2), (0.3, 0.7)
                ))
            update_particles(self.trail_particles)
            # Jos debris on liian kaukana ruudusta, merkitään poistettavaksi
            if (self.x < -50 or self.x > SCREEN_WIDTH + 50 or 
                self.y < -50 or self.y > SCREEN_HEIGHT + 50):
                return True
        return False

    def draw(self, surface):
        """Draw the debris if not caught"""
        if not self.caught:
            draw_particles(surface, self.trail_particles)
            rotated_image = pygame.transform.rotate(self.image, self.rotation)
            new_rect = rotated_image.get_rect(center=self.rect.center)
            surface.blit(rotated_image, new_rect)

class Net:
    """Net thrown by player to catch debris"""
    def __init__(self, x, y, angle, power):
        self.start_x = x
        self.start_y = y
        self.x = x
        self.y = y
        self.angle = angle  # Angle in radians
        self.power = power  # 0 to 1
        self.speed = NET_SPEED  # Constant speed
        
        # Max distance is determined by power
        self.max_distance = self.start_y * power  # The higher the power, the farther it goes
        
        self.image = load_image("net", (40, 40))
        self.rect = self.image.get_rect(center=(self.x, self.y))
        self.active = True
        self.returning = False
        self.distance_traveled = 0
        self.caught_debris = None
        self.trail_particles = []
        self.pulse_effect = 0
        self.pulse_increasing = True

    def update(self):
        """Update net position and state"""
        if not self.active:
            return False
            
        # Pulse effect animation
        if self.pulse_increasing:
            self.pulse_effect += 0.05
            if self.pulse_effect >= 1:
                self.pulse_increasing = False
        else:
            self.pulse_effect -= 0.05
            if self.pulse_effect <= 0:
                self.pulse_increasing = True
                
        # Create trail particles
        if random.random() < 0.2:
            self.trail_particles.extend(create_particles(
                self.x, self.y, (200, 200, 255), 
                2, (0.1, 0.3), (1, 2), (0.3, 0.5)
            ))
            
        # Update trail particles
        update_particles(self.trail_particles)
            
        if not self.returning:
            # Moving outward
            dx = math.cos(self.angle) * self.speed
            dy = math.sin(self.angle) * self.speed
            self.x += dx
            self.y += dy
            self.distance_traveled += math.sqrt(dx**2 + dy**2)
            
            # Check if max distance reached
            if self.distance_traveled >= self.max_distance:
                self.returning = True
                # Create particles for turnaround effect
                self.trail_particles.extend(create_particles(
                    self.x, self.y, (255, 255, 255), 
                    10, (0.5, 1.0), (1, 3), (0.5, 1.0)
                ))
        else:
            # Returning to player
            direction_x = self.start_x - self.x
            direction_y = self.start_y - self.y
            distance = math.sqrt(direction_x**2 + direction_y**2)
            
            if distance < self.speed:
                self.active = False
                # Create particles for return effect
                explosion_particles.extend(create_particles(
                    self.start_x, self.start_y, (150, 150, 255), 
                    15, (0.3, 1.0), (1, 3), (0.3, 0.8)
                ))
                return True
                
            normalized_x = direction_x / distance
            normalized_y = direction_y / distance
            
            self.x += normalized_x * self.speed
            self.y += normalized_y * self.speed
            
        self.rect.center = (self.x, self.y)
        
        # If caught debris, update its position
        if self.caught_debris:
            self.caught_debris.x = self.x
            self.caught_debris.y = self.y
            self.caught_debris.rect.center = (self.x, self.y)
            
        return False

    def draw(self, surface):
        """Draw the net and its rope"""
        if self.active:
            # Draw trail particles
            draw_particles(surface, self.trail_particles)
            
            # Draw rope line with gradient effect
            steps = 20
            for i in range(steps):
                progress = i / steps
                x1 = self.start_x + (self.x - self.start_x) * progress
                y1 = self.start_y + (self.y - self.start_y) * progress
                x2 = self.start_x + (self.x - self.start_x) * (progress + 1/steps)
                y2 = self.start_y + (self.y - self.start_y) * (progress + 1/steps)
                
                # Make rope fade out toward the net
                alpha = 255 - int(200 * progress)
                color = (255, 255, 255, alpha)
                
                # Draw on temporary surface for alpha support
                temp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, color, (x1, y1), (x2, y2), 2)
                surface.blit(temp_surf, (0, 0))
            
            # Draw pulsing effect around net
            pulse_size = 5 + int(self.pulse_effect * 10)
            pulse_surf = pygame.Surface((40 + pulse_size*2, 40 + pulse_size*2), pygame.SRCALPHA)
            pulse_alpha = int(100 * (1 - self.pulse_effect))
            pygame.draw.circle(pulse_surf, (200, 200, 255, pulse_alpha), 
                              (20 + pulse_size, 20 + pulse_size), 25 + pulse_size)
            surface.blit(pulse_surf, (self.x - 20 - pulse_size, self.y - 20 - pulse_size))
            
            # Draw net
            surface.blit(self.image, self.rect)

    def catch_debris(self, debris):
        """Catch a piece of debris in the net"""
        if not self.caught_debris and not debris.caught:
            self.caught_debris = debris
            debris.caught = True
            
            # Create particles for catch effect
            explosion_particles.extend(create_particles(
                self.x, self.y, (255, 255, 100), 
                20, (0.5, 2.0), (2, 4), (0.5, 1.2)
            ))
            return True
        return False

class PowerMeter:
    """Power meter for determining net throw strength"""
    def __init__(self):
        self.power = 0
        self.charge_speed = 0.03
        self.glow_effect = 0
        self.glow_increasing = True

    def reset(self):
        """Reset power to zero"""
        self.power = 0

    def increase(self):
        """Increase power if not at max"""
        if self.power < 1.0:
            self.power += self.charge_speed
            if self.power > 1.0:
                self.power = 1.0  # Clamp at max

    def update_glow(self):
        """Update glow effect animation"""
        if self.glow_increasing:
            self.glow_effect += 0.05
            if self.glow_effect >= 1:
                self.glow_increasing = False
        else:
            self.glow_effect -= 0.05
            if self.glow_effect <= 0:
                self.glow_increasing = True

    def get_power(self):
        """Get the current power level"""
        return self.power

class Game:
    """Main game class that manages all game elements and logic"""
    def __init__(self):
        self.running = True
        self.game_over = False
        self.victory = False
        self.player = Player()
        self.satellites = []
        self.debris_list = []
        self.power_meter = PowerMeter()
        self.zel = 0  # Starting money 
        self.satellite_cost = 200  # Cost when a satellite is destroyed
        self.aiming = False
        self.aim_angle = 0
        
        # Add mouse button tracking
        self.mouse_down = False
        self.power_charging = False
        
        # Stage settings
        self.stage = 1
        self.stage_start_time = pygame.time.get_ticks()
        self.stage_paused = False
        self.repair_interface_active = False
        
        # Add a flag to track if initial debris has been spawned
        self.initial_debris_spawned = False
        
        # Create satellites
        self.spawn_satellites(5)
        
        # Initialize fonts without bold
        self.title_font = pygame.font.SysFont('arial', 48)
        self.font = pygame.font.SysFont('arial', 36)
        self.small_font = pygame.font.SysFont('arial', 26)
        
        # UI animation variables
        self.ui_pulse = 0
        self.ui_pulse_increasing = True
        
        # Screen shake effect for impacts
        self.screen_shake = 0
        
        # Debris spawn timers and rates
        self.last_spawn_time = pygame.time.get_ticks()
        self.spawn_delay = 2000  # milliseconds between potential spawns
        
        # Initialize starfield
        init_stars()
        
        # Start gameplay music
        self.switch_to_gameplay_music()

    def spawn_initial_debris(self):
        """Spawn initial debris at the start of the stage targeting the player."""
        spawn_distance = 50  # Kiinteä etäisyys ruudun ulkopuolelta
        spawn_x = -spawn_distance  # Spawnataan vasemmalta
        spawn_y = random.uniform(0, SCREEN_HEIGHT)  # Satunnainen y-arvo ruudun sisällä
        target_x = self.player.x  # Kohteena pelaaja
        target_y = self.player.y
        debris_type = random.choice(DEBRIS_TYPES)
        
        new_debris = Debris(spawn_x, spawn_y, target_x, target_y, debris_type)
        self.debris_list.append(new_debris)

    def play_music(self, music_track):
        """Play a music track if it's not already playing"""
        global current_music
        
        # If this track is already playing, do nothing
        if current_music == music_track:
            return
            
        # Stop any currently playing music
        if current_music:
            current_music.stop()
        
        # Start the new music and loop it
        music_track.play(-1)  # -1 means loop indefinitely
        current_music = music_track

    def switch_to_gameplay_music(self):
        """Switch to gameplay music"""
        self.play_music(bg_gameplay_music)
        
    def switch_to_menu_music(self):
        """Switch to menu/victory music"""
        self.play_music(bg_menu_music)

    def spawn_satellites(self, count):
        """Create satellites positioned on the right side of the screen"""
        for i in range(count):
            x = SCREEN_WIDTH * 0.8  # More to the right
            y = (i + 1) * SCREEN_HEIGHT / (count + 1)
            self.satellites.append(Satellite(x, y))

    def get_current_spawn_rate(self):
        """Calculate spawn rate based on current stage"""
        return BASE_SPAWN_RATE * (1 + (self.stage - 1) * SPAWN_RATE_INCREASE)

    def spawn_debris(self):
        if self.stage_paused:
            return

        current_time = pygame.time.get_ticks()
        if current_time - self.last_spawn_time > self.spawn_delay:
            self.last_spawn_time = current_time
            # Arvotaan 30 % kohdistettua hyökkäystä ja 70 % suoraa lentoa
            if random.random() < 0.3 and any(sat.alive for sat in self.satellites):
                self.spawn_targeted_debris_to_satellite()
            else:
                self.spawn_straight_debris()
    
    def spawn_targeted_debris_to_satellite(self):
        """Spawn debris from off-screen, targeting a random alive satellite."""
        # Valitaan kohteeksi satelliitti
        alive_sats = [sat for sat in self.satellites if sat.alive]
        if not alive_sats:
            # Jos ei löydy elossa olevia satelliitteja, palataan suoraan spawn_straight_debris-funktioon
            self.spawn_straight_debris()
            return

        target = random.choice(alive_sats)
        target_x, target_y = target.x, target.y

        spawn_distance = 50  # Kiinteä etäisyys ruudun ulkopuolelta

        # Valitaan satunnaisesti spawn-tyyppi: vasen vai ylä/ala
        if random.random() < 0.5:
            # Vasemmalta spawn: x on ruudun ulkopuolella ja y ruudun sisällä
            spawn_x = -spawn_distance
            spawn_y = random.uniform(0, SCREEN_HEIGHT)
        else:
            # Ylhäältä tai alhaalta spawn: x tulee ensimmäisestä kolmanneksesta ja y offscreen
            spawn_x = random.uniform(0, SCREEN_WIDTH / 3)
            if random.random() < 0.5:
                spawn_y = -spawn_distance  # Ylhäällä
            else:
                spawn_y = SCREEN_HEIGHT + spawn_distance  # Alhaalla

        debris_type = random.choice(DEBRIS_TYPES)
        new_debris = Debris(spawn_x, spawn_y, target_x, target_y, debris_type)
        self.debris_list.append(new_debris)

    def spawn_straight_debris(self):
        """Spawn debris from off-screen on the left side, flying horizontally."""
        spawn_distance = 50  # Kiinteä etäisyys ruudun ulkopuolelta
        spawn_x = -spawn_distance
        spawn_y = random.uniform(0, SCREEN_HEIGHT)
        # Kohteena asetetaan piste ruudun oikealla puolella, y pysyy samana
        target_x = SCREEN_WIDTH + spawn_distance
        target_y = spawn_y

        debris_type = random.choice(DEBRIS_TYPES)
        new_debris = Debris(spawn_x, spawn_y, target_x, target_y, debris_type)
        self.debris_list.append(new_debris)


    def update_stage_timer(self):
        """Check if stage time has elapsed"""
        if self.stage_paused:
            return
            
        current_time = pygame.time.get_ticks()
        elapsed = current_time - self.stage_start_time
        
        if elapsed >= STAGE_DURATION:
            self.stage_paused = True
            self.repair_interface_active = True
            # Clear any debris on screen
            self.debris_list = []
            # Switch to menu music
            self.switch_to_menu_music()

    def repair_ship(self):
        """Repair the ship using ZEL"""
        missing_health = 100 - self.player.health
        
        # Only attempt repair if there's damage to repair and player has ZEL
        if missing_health > 0 and self.zel > 0:
            # Calculate how much health can be repaired with available ZEL
            health_points_to_repair = min(missing_health, self.zel // REPAIR_COST_PER_HEALTH)
            
            if health_points_to_repair > 0:
                # Calculate the exact cost for the repairs
                repair_cost = health_points_to_repair * REPAIR_COST_PER_HEALTH
                
                # Perform repairs
                self.player.repair(health_points_to_repair)
                
                # Only deduct the amount needed for repairs
                self.zel -= repair_cost

    def continue_to_next_stage(self):
        """Move to the next stage"""
        # Check if already at max stage before incrementing
        if self.stage >= MAX_STAGES:
            # You win!
            self.victory = True
            self.repair_interface_active = False  # Hide the repair interface
            self.switch_to_menu_music()  # Keep menu music for victory
            return
            
        # Only increment if not at max stage
        self.stage += 1
        
        # Reset for next stage
        self.stage_paused = False
        self.repair_interface_active = False
        self.stage_start_time = pygame.time.get_ticks()
        
        # Reset the initial debris spawned flag
        self.initial_debris_spawned = False
        
        # Reset aiming state, power meter, and player's net
        self.aiming = False
        self.power_charging = False
        self.mouse_down = False
        self.power_meter.reset()
        self.player.net = None
        
        # Always regenerate all satellites at the start of each new stage
        self.satellites = []
        self.spawn_satellites(5)
            
        # Switch back to gameplay music
        self.switch_to_gameplay_music()

    def handle_events(self):
        """Process pygame events"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                
            # Add ESC key to exit the game
            if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
                self.running = False
                
            if self.game_over or self.victory:
                if event.type == pygame.KEYDOWN and event.key == pygame.K_r:
                    self.__init__()  # Reset the game
                continue
                
            if self.repair_interface_active:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    
                    # Check if repair button was clicked (only if player needs repair and has ZEL)
                    if self.zel > 0 and self.player.health < 100:
                        if hasattr(self, 'repair_button_rect') and self.repair_button_rect.collidepoint(mouse_x, mouse_y):
                            self.repair_ship()
                        
                    # Check if continue button was clicked
                    if hasattr(self, 'continue_button_rect') and self.continue_button_rect.collidepoint(mouse_x, mouse_y):
                        self.continue_to_next_stage()
                continue
            
            # Handle mouse events for click and hold power meter
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and not self.aiming and self.player.net is None:  # Left mouse button
                    # Start aiming and charging power
                    mouse_x, mouse_y = pygame.mouse.get_pos()
                    dx = mouse_x - self.player.x
                    dy = mouse_y - self.player.y
                    self.aim_angle = math.atan2(dy, dx)
                    self.aiming = True
                    self.mouse_down = True
                    self.power_charging = True
                    self.power_meter.reset()  # Reset power to 0
            
            elif event.type == pygame.MOUSEBUTTONUP:
                if event.button == 1 and self.aiming:  # Left mouse button released
                    # Fire with current power
                    power = self.power_meter.get_power()
                    self.player.throw_net(self.aim_angle, power)
                    self.aiming = False
                    self.mouse_down = False
                    self.power_charging = False

    def update(self):
        """Update game state"""
        if self.game_over or self.victory:
            return
            
        # Check if it's time to spawn initial debris (after 1 second)
        if not self.initial_debris_spawned and not self.stage_paused and not self.repair_interface_active:
            current_time = pygame.time.get_ticks()
            elapsed = current_time - self.stage_start_time
            
            if elapsed >= 1000:  # 1000 milliseconds = 1 second
                self.spawn_initial_debris()
                self.initial_debris_spawned = True
        
        # Update star background
        update_stars()
        
        # Update particles
        update_particles(explosion_particles)
        
        # Update UI pulse effect
        if self.ui_pulse_increasing:
            self.ui_pulse += 0.02
            if self.ui_pulse >= 1:
                self.ui_pulse_increasing = False
        else:
            self.ui_pulse -= 0.02
            if self.ui_pulse <= 0:
                self.ui_pulse_increasing = True
        
        # Reduce screen shake if active
        if self.screen_shake > 0:
            self.screen_shake -= 1
            
        # Update player effects
        self.player.update()
        
        # Update power meter - only increase when charging
        if self.power_charging:
            self.power_meter.increase()
        
        # Always update the glow effect
        self.power_meter.update_glow()
        
        # Update satellites
        for satellite in self.satellites:
            satellite.update()
            
        # Check if stage time is up
        self.update_stage_timer()
        
        # If repair interface is active, don't update game elements
        if self.repair_interface_active:
            return
            
        # Update aim angle if aiming
        if self.aiming:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            dx = mouse_x - self.player.x
            dy = mouse_y - self.player.y
            self.aim_angle = math.atan2(dy, dx)
            
        # Update net
        if self.player.net and self.player.net.active:
            if self.player.net.update():
                # Net has returned to player
                if self.player.net.caught_debris:
                    # Add money for caught debris
                    self.zel += self.player.net.caught_debris.value
                    # Remove the caught debris
                    self.debris_list.remove(self.player.net.caught_debris)
                self.player.net = None
                
        # Spawn and update debris
        self.spawn_debris()
        debris_to_remove = []
        
        for debris in self.debris_list:
            if debris.update():  # Returns True if debris is off-screen
                debris_to_remove.append(debris)
                
            # Check for collisions with net
            if self.player.net and self.player.net.active and not debris.caught:
                if self.player.net.rect.colliderect(debris.rect):
                    self.player.net.catch_debris(debris)
                    
            # Check for collisions with satellites
            for satellite in self.satellites:
                if satellite.alive and debris.rect.colliderect(satellite.rect) and not debris.caught:
                    satellite.destroy()
                    debris_to_remove.append(debris)
                    # Add screen shake for impact
                    self.screen_shake = 10
                    
            # Check for collisions with player
            if not debris.caught and debris.rect.colliderect(self.player.rect):
                if self.player.take_damage(debris.damage):
                    self.game_over = True
                    self.switch_to_menu_music()  # Switch to menu music on game over
                debris_to_remove.append(debris)
                # Add screen shake for impact
                self.screen_shake = 15
        
        # Remove debris that is off-screen or has collided
        for debris in debris_to_remove:
            if debris in self.debris_list:
                self.debris_list.remove(debris)
                
        # Check if all satellites are destroyed
        if all(not satellite.alive for satellite in self.satellites) and not self.game_over:
            self.game_over = True
            self.switch_to_menu_music()  # Switch to menu music on game over

    def draw(self):
        """Draw all game elements to the screen"""
        screen.fill(BLACK)
        
        # Apply screen shake
        shake_offset_x = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        shake_offset_y = random.randint(-self.screen_shake, self.screen_shake) if self.screen_shake > 0 else 0
        
        # Draw star background
        draw_stars(screen)
        
        # Draw satellites with shake offset
        for satellite in self.satellites:
            satellite.draw(screen)
            
        # Draw debris with shake offset
        for debris in self.debris_list:
            debris.draw(screen)
            
        # Draw explosion particles
        draw_particles(screen, explosion_particles)
            
        # Draw player with shake offset
        self.player.draw(screen)
        
        # Draw power meter halo around the spaceship when aiming
        if self.aiming:
            power = self.power_meter.get_power()
            
            # Set halo color based on power (green to yellow to red)
            if power < 0.3:
                # Green to yellow
                r = int(255 * (power / 0.3))
                g = 255
                b = 0
            else:
                # Yellow to red
                r = 255
                g = int(255 * (1 - ((power - 0.3) / 0.7)))
                b = 0
            
            # Draw expanding halo based on power
            max_halo_size = 120  # Maximum halo diameter
            halo_size = 30 + int(power * max_halo_size)  # Scale with power
            
            halo_surf = pygame.Surface((halo_size, halo_size), pygame.SRCALPHA)
            # Outer glow (more transparent)
            pygame.draw.circle(halo_surf, (r, g, b, 30), (halo_size//2, halo_size//2), halo_size//2)
            # Inner glow (more visible)
            pygame.draw.circle(halo_surf, (r, g, b, 60), (halo_size//2, halo_size//2), halo_size//3)
            
            # Pulsing effect when power is maxed out
            if power >= 0.99:  # If power is at maximum
                pulse_intensity = 50 + int(30 * self.power_meter.glow_effect)
                max_glow = pygame.Surface((halo_size + 20, halo_size + 20), pygame.SRCALPHA)
                pygame.draw.circle(max_glow, (r, g, b, pulse_intensity), 
                                 (max_glow.get_width()//2, max_glow.get_height()//2), 
                                 (halo_size + 10)//2)
                screen.blit(max_glow, (self.player.x - max_glow.get_width()//2, 
                                      self.player.y - max_glow.get_height()//2))
            
            # Position the halo centered on the player
            screen.blit(halo_surf, (self.player.x - halo_size//2, self.player.y - halo_size//2))
        
        # Draw net with shake offset
        if self.player.net and self.player.net.active:
            self.player.net.draw(screen)
            
        # Draw aiming line if aiming (original yellow style)
        if self.aiming:
            # Calculate endpoints for segments
            segments = 8
            segment_length = TRAJECTORY_LENGTH / segments
            
            for i in range(segments):
                start_x = self.player.x + math.cos(self.aim_angle) * (i * segment_length)
                start_y = self.player.y + math.sin(self.aim_angle) * (i * segment_length)
                end_x = self.player.x + math.cos(self.aim_angle) * ((i + 1) * segment_length)
                end_y = self.player.y + math.sin(self.aim_angle) * ((i + 1) * segment_length)
                
                # Fade out color and thickness as segments progress
                alpha = 255 - int(180 * (i / segments))
                thickness = max(1, 3 - int(2 * (i / segments)))
                
                # Draw segment on temporary surface for alpha
                temp_surf = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
                pygame.draw.line(temp_surf, (255, 255, 0, alpha), (start_x, start_y), (end_x, end_y), thickness)
                screen.blit(temp_surf, (0, 0))
                
                # Add small dots at segment joints
                if i < segments - 1:
                    pygame.draw.circle(screen, (255, 255, 0), (int(end_x), int(end_y)), thickness//2)
        
        # Draw UI with enhanced visuals
        # Health bar with glowing effect
        bar_width = 200
        bar_height = 25
        bar_x = SCREEN_WIDTH // 2 - bar_width // 2
        bar_y = 20
        
        # Draw glow under health bar
        if self.player.health < 30:
            # Pulsing red glow for low health
            glow_alpha = int(100 + 50 * self.ui_pulse)
            glow_surf = pygame.Surface((bar_width + 20, bar_height + 20), pygame.SRCALPHA)
            pygame.draw.rect(glow_surf, (255, 0, 0, glow_alpha), 
                            (10, 10, bar_width, bar_height), border_radius=5)
            screen.blit(glow_surf, (bar_x - 10, bar_y - 10))
        
        # Health bar background
        pygame.draw.rect(screen, (60, 60, 60), (bar_x, bar_y, bar_width, bar_height), border_radius=5)
        
        # Health fill
        health_width = bar_width * (self.player.health / 100)
        
        # Health gradient based on value
        if self.player.health > 60:
            health_color = GREEN
        elif self.player.health > 30:
            health_color = YELLOW
        else:
            health_color = RED
            
        pygame.draw.rect(screen, health_color, (bar_x, bar_y, health_width, bar_height), border_radius=5)
        
        # Health bar border
        pygame.draw.rect(screen, WHITE, (bar_x, bar_y, bar_width, bar_height), 2, border_radius=5)
        
        # Health text
        health_text = f"HEALTH: {self.player.health}%"
        draw_text_with_shadow(screen, health_text, self.font, WHITE, 
                             (bar_x + bar_width//2 - self.font.size(health_text)[0]//2, bar_y + 30))
        
        # ZEL counter with plain text
        zel_text = f"ZEL: {self.zel}"
        draw_plain_text(screen, zel_text, self.font, YELLOW, (20, 20))
        
        # Stage info
        stage_text = f"STAGE: {self.stage}/{MAX_STAGES}"
        draw_text_with_shadow(screen, stage_text, self.font, WHITE, (20, 60))
        
        # Draw time remaining if not in repair mode
        if not self.repair_interface_active:
            elapsed = pygame.time.get_ticks() - self.stage_start_time
            time_left = max(0, (STAGE_DURATION - elapsed) // 1000)  # Convert to seconds
            
            if time_left <= 10:
                # Pulsing color for last 10 seconds
                pulse_value = int(155 + 100 * self.ui_pulse)
                time_color = (255, pulse_value, pulse_value)
            else:
                time_color = WHITE
                
            time_text = f"TIME: {time_left}s"
            draw_text_with_shadow(screen, time_text, self.font, time_color, (20, 100))
        
        # Draw repair interface if active and not in victory state
        if self.repair_interface_active and not self.victory:
            # Draw semi-transparent overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))  # Semi-transparent black
            screen.blit(overlay, (0, 0))
            
            # Draw repair interface with plain text title (moved up)
            repair_title = f"STAGE {self.stage} COMPLETE"
            draw_plain_text(screen, repair_title, self.title_font, WHITE, 
                           (SCREEN_WIDTH // 2 - self.title_font.size(repair_title)[0]//2, SCREEN_HEIGHT // 3 - 70))
            
            # Calculate repair info
            missing_health = 100 - self.player.health
            
            # Display ship status (moved down)
            status_text = f"Ship Damage: {missing_health}%"
            draw_text_with_shadow(screen, status_text, self.font, WHITE, 
                                 (SCREEN_WIDTH // 2 - self.font.size(status_text)[0]//2, SCREEN_HEIGHT // 3 + 10))
            
            # Display available ZEL directly under ship damage (with plain text)
            zel_text = f"Available ZEL: {self.zel}"
            draw_plain_text(screen, zel_text, self.font, YELLOW, 
                           (SCREEN_WIDTH // 2 - self.font.size(zel_text)[0]//2, SCREEN_HEIGHT // 3 + 50))
            
            # Only show repair info and button if ZEL > 0 and repairs needed
            button_y_position = SCREEN_HEIGHT // 3 + 110
            
            # Button dimensions - increased width for buttons
            button_width = 160  # Increased from 130
            button_height = 50
            
            # Määritellään button_y_position ennen ehtoa
            button_y_position = SCREEN_HEIGHT // 3 + 150

            if self.zel > 0 and missing_health > 0:
                health_points_repairable = min(missing_health, self.zel // REPAIR_COST_PER_HEALTH)
                if health_points_repairable > 0:
                    repair_cost = health_points_repairable * REPAIR_COST_PER_HEALTH
                    repair_text = f"Can repair {health_points_repairable}% for {repair_cost} ZEL"
                    draw_text_with_shadow(screen, repair_text, self.small_font, WHITE, 
                                        (SCREEN_WIDTH // 2 - self.small_font.size(repair_text)[0] // 2, 
                                        SCREEN_HEIGHT // 3 + 110))
                button_spacing = 30
                total_width = (button_width * 2) + button_spacing
                
                # Piirretään "repair" -painike
                self.repair_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - total_width // 2,
                    button_y_position,
                    button_width, 
                    button_height
                )
                mouse_pos = pygame.mouse.get_pos()
                button_hover = self.repair_button_rect.collidepoint(mouse_pos)
                draw_button(screen, self.repair_button_rect, "REPAIR", self.font, BLACK, GREEN, hover=button_hover)
                
                # Piirretään "continue" -painike oikealle
                self.continue_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - total_width // 2 + button_width + button_spacing,
                    button_y_position,
                    button_width, 
                    button_height
                )
                button_hover = self.continue_button_rect.collidepoint(mouse_pos)
                draw_button(screen, self.continue_button_rect, "CONTINUE", self.font, BLACK, BLUE, hover=button_hover)
            else:
                # Piirretään keskitetty "continue" -painike
                self.continue_button_rect = pygame.Rect(
                    SCREEN_WIDTH // 2 - button_width // 2,
                    button_y_position,
                    button_width, 
                    button_height
                )
                mouse_pos = pygame.mouse.get_pos()
                button_hover = self.continue_button_rect.collidepoint(mouse_pos)
                draw_button(screen, self.continue_button_rect, "CONTINUE", self.font, BLACK, BLUE, hover=button_hover)
        
        # Draw game over screen
        if self.game_over:
            # Dark overlay
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 200))
            screen.blit(overlay, (0, 0))
            
            # Game over title with plain text
            game_over_text = "GAME OVER"
            draw_plain_text(screen, game_over_text, self.title_font, RED, 
                           (SCREEN_WIDTH // 2 - self.title_font.size(game_over_text)[0]//2, SCREEN_HEIGHT // 2 - 50))
            
            # Restart text
            restart_text = "Press R to restart"
            draw_text_with_shadow(screen, restart_text, self.font, WHITE, 
                                 (SCREEN_WIDTH // 2 - self.font.size(restart_text)[0]//2, SCREEN_HEIGHT // 2 + 10))
            
        # Draw victory screen
        if self.victory:
            # Dark overlay with stars still visible
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            screen.blit(overlay, (0, 0))
            
            # Victory title with plain text - ONLY "MISSION COMPLETE!" shown
            victory_text = "MISSION COMPLETE!"
            draw_plain_text(screen, victory_text, self.title_font, WHITE, 
                           (SCREEN_WIDTH // 2 - self.title_font.size(victory_text)[0]//2, SCREEN_HEIGHT // 2 - 50))
            
            # Celebration particles
            if random.random() < 0.1:
                for _ in range(3):
                    x = random.randint(0, SCREEN_WIDTH)
                    y = random.random() * SCREEN_HEIGHT // 3
                    color = tuple(int(c * 255) for c in colorsys.hsv_to_rgb(random.random(), 0.8, 1.0))
                    explosion_particles.extend(create_particles(
                        x, y, color, 15, (0.5, 2.0), (2, 4), (0.8, 1.5)
                    ))
            
            # Restart text
            restart_text = "Press R to play again"
            draw_text_with_shadow(screen, restart_text, self.font, WHITE, 
                                 (SCREEN_WIDTH // 2 - self.font.size(restart_text)[0]//2, SCREEN_HEIGHT // 2 + 30))
            
        pygame.display.flip()

    def run(self):
        """Main game loop"""
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            clock.tick(60)  # 60 FPS
            
        # Clean up before exiting
        global current_music
        if current_music:
            current_music.stop()
        pygame.quit()
        sys.exit()

# Main function to run the game
def main():
    """Initialize and start the game"""
    game = Game()
    game.run()

if __name__ == "__main__":
    main()