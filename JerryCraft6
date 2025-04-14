# %%--%%
import pygame
import sys
import random
import math
import heapq  # For A* priority queue
from typing import List, Tuple, Dict, Optional, Any

# --- Constants ---
# HD Resolution (16:9)
SCREEN_WIDTH: int = 1280
SCREEN_HEIGHT: int = 720
SIDEBAR_WIDTH: int = 240  # Width for the UI sidebar
GAME_AREA_WIDTH: int = SCREEN_WIDTH - SIDEBAR_WIDTH
GAME_AREA_HEIGHT: int = SCREEN_HEIGHT

GRID_SIZE: int = 20  # Keep block size the same
# Grid dimensions based on the GAME AREA now
GRID_WIDTH: int = GAME_AREA_WIDTH // GRID_SIZE
GRID_HEIGHT: int = GAME_AREA_HEIGHT // GRID_SIZE
FPS: int = 60

BUILD_PHASE_DURATION: int = 60 * 1000  # 60 seconds in milliseconds
NIGHT_PHASE_DURATION: int = 60 * 1000  # 60 seconds in milliseconds
CREEPER_BASE_MOVE_DELAY: int = 600     # Milliseconds between creeper moves
CREEPER_PATH_RECALC_INTERVAL: int = 2000 # Milliseconds between path recalculations

# Colors
BLACK: Tuple[int, int, int] = (0, 0, 0)
WHITE: Tuple[int, int, int] = (255, 255, 255)  # UI Text color
TEXT_SHADOW: Tuple[int, int, int] = (50, 50, 50)
RED: Tuple[int, int, int] = (255, 0, 0)
FOREST_GREEN: Tuple[int, int, int] = (34, 139, 34)
BLUE: Tuple[int, int, int] = (0, 0, 255)
YELLOW: Tuple[int, int, int] = (255, 255, 0)
GRAY: Tuple[int, int, int] = (128, 128, 128)
BROWN: Tuple[int, int, int] = (101, 67, 33)
ORANGE_RED: Tuple[int, int, int] = (255, 69, 0)
DARK_GREEN: Tuple[int, int, int] = (0, 100, 0)  # Jeeper color
JERRY_COLOR: Tuple[int, int, int] = (200, 50, 50)  # Jerry's color
HEALTH_BAR_HIGH: Tuple[int, int, int] = (0, 200, 0)
HEALTH_BAR_LOW: Tuple[int, int, int] = (200, 0, 0)
EFFECT_COLOR: Tuple[int, int, int] = (200, 200, 220)  # Placement/Removal effect
SIDEBAR_BG: Tuple[int, int, int] = (40, 40, 55)  # Dark background for sidebar
NIGHT_OVERLAY_COLOR: Tuple[int, int, int, int] = (50, 50, 70, 100)  # Grayish-blue overlay with alpha
BUTTON_COLOR: Tuple[int, int, int] = (80, 80, 100)
BUTTON_HOVER_COLOR: Tuple[int, int, int] = (110, 110, 130)
BUTTON_TEXT_COLOR: Tuple[int, int, int] = (220, 220, 255)

# UI Layout Constants (within Sidebar)
UI_PADDING: int = 15  # Padding inside the sidebar
UI_LOGO_AREA_HEIGHT: int = 100  # Space for logo at the top
UI_INFO_START_Y: int = UI_LOGO_AREA_HEIGHT + UI_PADDING
UI_LINE_HEIGHT: int = 28  # Increased line height for readability
UI_INV_START_Y: int = UI_INFO_START_Y + UI_LINE_HEIGHT * 3  # Below Phase/Round/Timer
UI_BUTTON_HEIGHT: int = 40
UI_BUTTON_WIDTH: int = SIDEBAR_WIDTH - UI_PADDING * 2
UI_BUTTON_Y: int = SCREEN_HEIGHT - UI_BUTTON_HEIGHT - UI_PADDING * 2  # For "Skip" button
UI_INST_START_Y: int = SCREEN_HEIGHT - 70  # Instructions at bottom

# New: Pause button dimensions
PAUSE_BUTTON_WIDTH: int = UI_BUTTON_WIDTH
PAUSE_BUTTON_HEIGHT: int = 35
PAUSE_BUTTON_Y: int = UI_PADDING  # Top of sidebar

# New: Restart button dimensions (shown on Game Over)
RESTART_BUTTON_WIDTH: int = UI_BUTTON_WIDTH
RESTART_BUTTON_HEIGHT: int = 40
RESTART_BUTTON_Y: int = SCREEN_HEIGHT - UI_BUTTON_HEIGHT - UI_PADDING * 4  # Positioned above instructions

# Block Types Definition
BlockData = Dict[str, Any]
GridCell = Dict[str, Any]  # {"type": str, "durability": float}
Grid = List[List[GridCell]]

BLOCK_TYPES: Dict[str, BlockData] = {
    "grass": {"color": FOREST_GREEN, "solid": False, "travel_cost": 1, "durability": float('inf'), "effect": None, "breakable": False},
    "mud": {"color": BROWN, "solid": True, "travel_cost": 3, "durability": 2, "effect": None, "breakable": True},
    "stone": {"color": GRAY, "solid": True, "travel_cost": float('inf'), "durability": 5, "effect": None, "breakable": True},
    "water": {"color": BLUE, "solid": False, "travel_cost": 4, "durability": float('inf'), "effect": None, "breakable": False},
    "sand": {"color": YELLOW, "solid": True, "travel_cost": 2, "durability": 1, "effect": None, "breakable": True},
    "fire": {"color": ORANGE_RED, "solid": True, "travel_cost": 1, "durability": 3, "effect": "burn", "breakable": True}
}
SELECTABLE_BLOCKS: List[str] = ["mud", "stone", "water", "sand", "fire"]

# --- Utility Functions ---
def heuristic(a: Tuple[int, int], b: Tuple[int, int]) -> float:
    (x1, y1) = a; (x2, y2) = b
    return abs(x1 - x2) + abs(y1 - y2)

# --- Splash Screen Function (Adjusted for HD) ---
def show_splash_screen(screen: pygame.Surface, clock: pygame.time.Clock, font: pygame.font.Font, large_font: pygame.font.Font, logo_path: str):
    try:
        logo_image_original = pygame.image.load(logo_path).convert_alpha()
        target_logo_width = min(600, screen.get_width() - 100)
        scale_factor = target_logo_width / logo_image_original.get_width()
        new_height = int(logo_image_original.get_height() * scale_factor)
        logo_image = pygame.transform.smoothscale(logo_image_original, (target_logo_width, new_height))
    except pygame.error as e:
        print(f"Warning: Could not load or scale image '{logo_path}': {e}")
        logo_image = None

    story_lines = [
        "Jerry is lost in a strange, blocky world...",
        "Every night, terrifying Jeepers emerge from the darkness.",
        "Use your limited blocks to build defenses before night falls.",
        "Survive the Jeeper onslaught!", "",
        "How many nights can Jerry survive?"
    ]

    def draw_centered_text_lines(lines: List[str], font_obj: pygame.font.Font, y_start: int, line_spacing: int = 45):
        y_offset = y_start
        for line in lines:
            text_surf = font_obj.render(line, True, WHITE)
            text_rect = text_surf.get_rect(center=(screen.get_width()//2, y_offset))
            shadow_surf = font_obj.render(line, True, TEXT_SHADOW)
            screen.blit(shadow_surf, (text_rect.x + 2, text_rect.y + 2))
            screen.blit(text_surf, text_rect)
            y_offset += line_spacing

    showing_splash = True
    while showing_splash:
        for event in pygame.event.get():
            if event.type == pygame.QUIT: pygame.quit(); sys.exit()
            elif event.type in (pygame.KEYDOWN, pygame.MOUSEBUTTONDOWN): showing_splash = False

        screen.fill(BLACK)
        logo_y_pos = 180
        if logo_image:
            logo_rect = logo_image.get_rect(center=(screen.get_width()//2, logo_y_pos))
            screen.blit(logo_image, logo_rect)
        else:
            title_surf = large_font.render("JerryCraft", True, YELLOW)
            title_rect = title_surf.get_rect(center=(screen.get_width()//2, logo_y_pos))
            shadow_surf = large_font.render("JerryCraft", True, TEXT_SHADOW)
            screen.blit(shadow_surf, (title_rect.x + 3, title_rect.y + 3))
            screen.blit(title_surf, title_rect)

        story_start_y = logo_y_pos + (logo_image.get_height() // 2 if logo_image else 50) + 70
        draw_centered_text_lines(story_lines, font, story_start_y)

        prompt_text = "Press any key or click to begin..."
        prompt_surf = font.render(prompt_text, True, YELLOW)
        prompt_rect = prompt_surf.get_rect(center=(screen.get_width()//2, screen.get_height() - 80))
        shadow_prompt = font.render(prompt_text, True, TEXT_SHADOW)
        screen.blit(shadow_prompt, (prompt_rect.x + 2, prompt_rect.y + 2))
        screen.blit(prompt_surf, prompt_rect)

        pygame.display.flip()
        clock.tick(FPS)

# --- Game Classes ---
class Player:
    """Represents Jerry, the player."""
    def __init__(self, grid_x: int, grid_y: int):
        self.grid_x: int = grid_x
        self.grid_y: int = grid_y
        self.color: Tuple[int, int, int] = JERRY_COLOR

    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.ellipse(surface, self.color, rect)

class VisualEffect:
    """A simple temporary visual effect (e.g., for placement)."""
    def __init__(self, grid_x: int, grid_y: int, max_radius: int, duration: int):
        self.cx: int = grid_x * GRID_SIZE + GRID_SIZE // 2
        self.cy: int = grid_y * GRID_SIZE + GRID_SIZE // 2
        self.max_radius: int = max_radius
        self.duration: int = duration
        self.start_time: int = pygame.time.get_ticks()
        self.current_radius: float = 0

    def update(self) -> bool:
        now = pygame.time.get_ticks()
        elapsed = now - self.start_time
        if elapsed >= self.duration:
            return False
        progress = elapsed / self.duration
        self.current_radius = self.max_radius * (4 * progress * (1 - progress))
        return True

    def draw(self, surface: pygame.Surface) -> None:
        if self.current_radius > 0:
            pygame.draw.circle(surface, EFFECT_COLOR, (self.cx, self.cy), int(self.current_radius), 1)

class Creeper:
    """Represents an enemy Jeeper using A* pathfinding."""
    def __init__(self, x: int, y: int, target: Player):
        self.x: int = x
        self.y: int = y
        self.target: Player = target
        self.color: Tuple[int, int, int] = DARK_GREEN
        self.last_move_time: int = pygame.time.get_ticks()
        self.move_delay: int = CREEPER_BASE_MOVE_DELAY + random.randint(-50, 50)
        self.path: List[Tuple[int, int]] = []
        self.last_path_recalc: int = 0

    def draw(self, surface: pygame.Surface) -> None:
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(surface, self.color, rect)

    def find_path(self, grid: Grid) -> None:
        start = (self.x, self.y)
        goal = (self.target.grid_x, self.target.grid_y)
        now = pygame.time.get_ticks()
        if not self.path or now - self.last_path_recalc > CREEPER_PATH_RECALC_INTERVAL:
            self.last_path_recalc = now
        else:
            return
        frontier = [(0, start)]
        came_from: Dict[Tuple[int, int], Optional[Tuple[int, int]]] = {start: None}
        cost_so_far: Dict[Tuple[int, int], float] = {start: 0}
        path_found = False
        while frontier:
            _, current = heapq.heappop(frontier)
            if current == goal:
                path_found = True
                break
            for dx in [-1, 0, 1]:
                for dy in [-1, 0, 1]:
                    if dx == 0 and dy == 0:
                        continue
                    next_node = (current[0] + dx, current[1] + dy)
                    nx, ny = next_node
                    if not (0 <= nx < GRID_WIDTH and 0 <= ny < GRID_HEIGHT):
                        continue
                    cell_data = grid[nx][ny]
                    block_props = BLOCK_TYPES[cell_data["type"]]
                    is_impassable = block_props["travel_cost"] == float('inf') and cell_data["durability"] > 0
                    if is_impassable and next_node != goal:
                        continue
                    move_cost = block_props["travel_cost"]
                    if move_cost == float('inf') and next_node == goal:
                        move_cost = 1000
                    elif move_cost == float('inf'):
                        continue
                    if dx != 0 and dy != 0:
                        move_cost *= 1.414
                    new_cost = cost_so_far[current] + move_cost
                    if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                        cost_so_far[next_node] = new_cost
                        priority = new_cost + heuristic(goal, next_node)
                        heapq.heappush(frontier, (priority, next_node))
                        came_from[next_node] = current
        self.path = []
        if path_found:
            curr = goal
            while curr != start:
                self.path.append(curr)
                pred = came_from.get(curr)
                if pred is None:
                    self.path = []
                    break
                curr = pred
            self.path.reverse()
        if not self.path:
            self.path = []

    def move(self, grid: Grid) -> Optional[str]:
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return None
        if not self.path:
            self.find_path(grid)
            if not self.path:
                self.last_move_time = now
                return None
        if not self.path:
            return None
        next_x, next_y = self.path[0]
        target_cell = grid[next_x][next_y]
        block_props = BLOCK_TYPES[target_cell["type"]]
        if next_x == self.target.grid_x and next_y == self.target.grid_y:
            self.x, self.y = next_x, next_y
            self.last_move_time = now
            if self.path:
                self.path.pop(0)
            return "reached_jerry"
        if block_props["effect"] == "burn" and target_cell["durability"] > 0:
            if block_props["breakable"]:
                grid[next_x][next_y]["durability"] -= 1
                if grid[next_x][next_y]["durability"] <= 0:
                    grid[next_x][next_y] = {"type": "grass", "durability": float('inf')}
            self.last_move_time = now
            return "burned"
        is_currently_impassable = block_props["travel_cost"] == float('inf') and target_cell["durability"] > 0
        if is_currently_impassable:
            if block_props["breakable"]:
                grid[next_x][next_y]["durability"] -= 1
                if grid[next_x][next_y]["durability"] <= 0:
                    grid[next_x][next_y] = {"type": "grass", "durability": float('inf')}
                    self.path = []
                    self.last_path_recalc = 0
            self.last_move_time = now
            return None
        else:
            self.x, self.y = next_x, next_y
            self.last_move_time = now
            self.move_delay = int(CREEPER_BASE_MOVE_DELAY * block_props["travel_cost"])
            if self.path:
                self.path.pop(0)
            return "moved"

class Game:
    """Manages overall game state, drawing, events, and updates."""
    def __init__(self, screen: pygame.Surface, clock: pygame.time.Clock,
                 font: pygame.font.Font, large_font: pygame.font.Font, logo_path: str):
        self.screen: pygame.Surface = screen  # Main screen
        self.clock: pygame.time.Clock = clock
        self.font: pygame.font.Font = font
        self.large_font: pygame.font.Font = large_font
        self.running: bool = True
        self.game_over: bool = False
        self.phase: str = "build"
        self.round_number: int = 1
        self.phase_start_time: int = pygame.time.get_ticks()
        self.time_left_in_phase: int = BUILD_PHASE_DURATION
        self.total_jeepers_spawned: int = 0

        # Transition message variables for bonus win
        self.transition_message: Optional[str] = None
        self.transition_message_end: int = 0

        # Pause state
        self.paused: bool = False
        self.pause_button_rect: Optional[pygame.Rect] = None
        self.restart_button_rect: Optional[pygame.Rect] = None

        # Surfaces for game area and overlay
        self.game_surface = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT))
        self.night_overlay = pygame.Surface((GAME_AREA_WIDTH, GAME_AREA_HEIGHT), pygame.SRCALPHA)
        self.night_overlay.fill(NIGHT_OVERLAY_COLOR)

        jerry_start_gx: int = GRID_WIDTH // 2
        jerry_start_gy: int = GRID_HEIGHT // 2
        self.player: Player = Player(jerry_start_gx, jerry_start_gy)
        self.grid: Grid = self._initialize_grid()
        self.inventory: Dict[str, int] = self._initial_inventory()
        self.current_block_index: int = 0
        self.current_block_type: str = SELECTABLE_BLOCKS[self.current_block_index]
        self.creepers: List[Creeper] = []
        self.effects: List[VisualEffect] = []

        self.sidebar_logo: Optional[pygame.Surface] = None
        try:
            logo_orig = pygame.image.load(logo_path).convert_alpha()
            logo_h = int(logo_orig.get_height() * (SIDEBAR_WIDTH - UI_PADDING * 2) / logo_orig.get_width())
            self.sidebar_logo = pygame.transform.smoothscale(logo_orig, (SIDEBAR_WIDTH - UI_PADDING*2, logo_h))
        except pygame.error as e:
            print(f"Warning: Could not load sidebar logo '{logo_path}': {e}")

        self.skip_button_rect: Optional[pygame.Rect] = None

    def _initialize_grid(self) -> Grid:
        grid = [[{"type": "grass", "durability": float('inf')} for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]
        grid[self.player.grid_x][self.player.grid_y] = {"type": "grass", "durability": float('inf')}
        return grid

    def _initial_inventory(self) -> Dict[str, int]:
        return {"mud": 20, "stone": 10, "water": 5, "sand": 15, "fire": 3}

    def reward_inventory(self) -> None:
        self.inventory["mud"] += 5 + self.round_number
        self.inventory["stone"] += 3 + self.round_number
        self.inventory["water"] += 1 + (self.round_number // 2)
        self.inventory["sand"] += 4 + self.round_number
        self.inventory["fire"] += 4 + (self.round_number // 3)

    def reward_inventory_bonus(self) -> None:
        # Bonus: Award three fire blocks instead of one
        self.inventory["mud"] += 5 + self.round_number
        self.inventory["stone"] += 3 + self.round_number
        self.inventory["water"] += 1 + (self.round_number // 2)
        self.inventory["sand"] += 4 + self.round_number
        self.inventory["fire"] += 4

    def spawn_creepers(self) -> None:
        self.creepers = []
        count = 3 + self.round_number * 2
        self.total_jeepers_spawned += count
        for _ in range(count):
            edge = random.randint(0, 3)
            x, y = 0, 0
            if edge == 0:
                x, y = random.randint(0, GRID_WIDTH - 1), 0
            elif edge == 1:
                x, y = random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1
            elif edge == 2:
                x, y = 0, random.randint(0, GRID_HEIGHT - 1)
            else:
                x, y = GRID_WIDTH - 1, random.randint(0, GRID_HEIGHT - 1)
            if (x, y) == (self.player.grid_x, self.player.grid_y):
                y = (y + 1) % GRID_HEIGHT
            if 0 <= x < GRID_WIDTH and 0 <= y < GRID_HEIGHT:
                if BLOCK_TYPES[self.grid[x][y]["type"]]["travel_cost"] == float('inf') and self.grid[x][y]["durability"] > 0:
                    continue
            else:
                continue
            self.creepers.append(Creeper(x, y, self.player))

    def place_block(self, grid_x: int, grid_y: int) -> None:
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return
        if grid_x == self.player.grid_x and grid_y == self.player.grid_y:
            return
        block_to_place = self.current_block_type
        if self.inventory[block_to_place] > 0:
            block_props = BLOCK_TYPES[block_to_place]
            new_durability = block_props["durability"]
            self.grid[grid_x][grid_y] = {"type": block_to_place, "durability": new_durability}
            self.inventory[block_to_place] -= 1
            self.effects.append(VisualEffect(grid_x, grid_y, GRID_SIZE // 2, 200))
            if block_props["travel_cost"] == float('inf') or block_props["solid"]:
                self.invalidate_nearby_creeper_paths(grid_x, grid_y, 5)

    def remove_block(self, grid_x: int, grid_y: int) -> None:
        if not (0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT):
            return
        if grid_x == self.player.grid_x and grid_y == self.player.grid_y:
            return
        current_cell = self.grid[grid_x][grid_y]
        if current_cell["type"] != "grass":
            was_obstacle = BLOCK_TYPES[current_cell["type"]]["travel_cost"] == float('inf') or BLOCK_TYPES[current_cell["type"]]["solid"]
            self.grid[grid_x][grid_y] = {"type": "grass", "durability": float('inf')}
            self.effects.append(VisualEffect(grid_x, grid_y, GRID_SIZE // 2, 200))
            if was_obstacle:
                self.invalidate_nearby_creeper_paths(grid_x, grid_y, 5)

    def invalidate_nearby_creeper_paths(self, grid_x: int, grid_y: int, radius: int) -> None:
        radius_sq = radius ** 2
        for creeper in self.creepers:
            dist_sq = (creeper.x - grid_x) ** 2 + (creeper.y - grid_y) ** 2
            if dist_sq < radius_sq:
                creeper.path = []
                creeper.last_path_recalc = 0

    def handle_events(self) -> None:
        mouse_pos = pygame.mouse.get_pos()
        game_area_mouse_x = mouse_pos[0] - SIDEBAR_WIDTH
        game_area_mouse_y = mouse_pos[1]
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                if self.phase == "build" and not self.game_over:
                    if pygame.K_1 <= event.key <= pygame.K_5:
                        index = event.key - pygame.K_1
                        if index < len(SELECTABLE_BLOCKS):
                            self.current_block_index = index
                            self.current_block_type = SELECTABLE_BLOCKS[self.current_block_index]
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Check Pause Button Click (always active)
                if self.pause_button_rect and self.pause_button_rect.collidepoint(mouse_pos):
                    self.paused = not self.paused
                    print("Pause toggled:", self.paused)
                    continue
                # Check Restart Button (active when game over)
                if self.game_over and self.restart_button_rect and self.restart_button_rect.collidepoint(mouse_pos):
                    self.__init__(self.screen, self.clock, self.font, self.large_font, logo_file_path)
                    print("Game Restarted")
                    return
                # Check Skip Button Click (only in build phase)
                if self.phase == "build" and not self.game_over and self.skip_button_rect and self.skip_button_rect.collidepoint(mouse_pos):
                    self.time_left_in_phase = 0
                    print("Skipping to Night Phase")
                elif self.phase == "build" and not self.game_over and mouse_pos[0] >= SIDEBAR_WIDTH:
                    grid_x, grid_y = game_area_mouse_x // GRID_SIZE, game_area_mouse_y // GRID_SIZE
                    if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                        if event.button == 1:
                            self.place_block(grid_x, grid_y)
                        elif event.button == 3:
                            self.remove_block(grid_x, grid_y)

    def update(self) -> None:
        if self.game_over or self.paused:
            return
        now = pygame.time.get_ticks()
        elapsed = now - self.phase_start_time
        phase_duration = BUILD_PHASE_DURATION if self.phase == "build" else NIGHT_PHASE_DURATION
        if self.time_left_in_phase > 0:
            self.time_left_in_phase = max(0, phase_duration - elapsed)
        # Phase Transitions
        if self.phase == "build" and self.time_left_in_phase <= 0:
            self.phase = "night"
            self.phase_start_time = now
            self.time_left_in_phase = NIGHT_PHASE_DURATION
            self.spawn_creepers()
        elif self.phase == "night" and self.time_left_in_phase <= 0:
            if not self.game_over:
                self.phase = "build"
                self.round_number += 1
                self.phase_start_time = now
                self.time_left_in_phase = BUILD_PHASE_DURATION
                self.creepers = []
                self.reward_inventory()
        # Early transition: if in night phase and all Jeepers are killed
        if self.phase == "night" and not self.game_over and len(self.creepers) == 0:
            self.phase = "build"
            self.round_number += 1
            self.phase_start_time = now
            self.time_left_in_phase = BUILD_PHASE_DURATION
            self.reward_inventory_bonus()
            self.creepers = []
            self.transition_message = f"You made it to round {self.round_number}!"
            self.transition_message_end = now + 3000
        # Update Creepers (Night Phase)
        if self.phase == "night" and not self.game_over:
            remaining_creepers = []
            for creeper in self.creepers:
                result = creeper.move(self.grid)
                if result == "reached_jerry":
                    self.game_over = True
                    remaining_creepers = self.creepers
                    break
                elif result == "burned":
                    self.effects.append(VisualEffect(creeper.x, creeper.y, GRID_SIZE // 2, 300))
                    continue
                else:
                    remaining_creepers.append(creeper)
            if not self.game_over:
                self.creepers = remaining_creepers
        # Update Visual Effects
        active_effects = []
        for effect in self.effects:
            if effect.update():
                active_effects.append(effect)
        self.effects = active_effects

    def draw_grid_to_surface(self, surface: pygame.Surface) -> None:
        surface.fill(BLACK)
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell: GridCell = self.grid[x][y]
                block_props: BlockData = BLOCK_TYPES[cell["type"]]
                color: Tuple[int, int, int] = block_props["color"]
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(surface, color, rect)
                if block_props["breakable"] and 0 < cell["durability"] < block_props["durability"]:
                    health_ratio: float = cell["durability"] / block_props["durability"]
                    bar_width: int = int(GRID_SIZE * 0.8 * health_ratio)
                    bar_height: int = max(1, GRID_SIZE // 8)
                    bar_x: int = rect.left + (GRID_SIZE - int(GRID_SIZE * 0.8)) // 2
                    bar_y: int = rect.bottom - bar_height - 2
                    bar_color_r = int(HEALTH_BAR_LOW[0] * (1 - health_ratio) + HEALTH_BAR_HIGH[0] * health_ratio)
                    bar_color_g = int(HEALTH_BAR_LOW[1] * (1 - health_ratio) + HEALTH_BAR_HIGH[1] * health_ratio)
                    bar_color_b = int(HEALTH_BAR_LOW[2] * (1 - health_ratio) + HEALTH_BAR_HIGH[2] * health_ratio)
                    bar_color = (max(0, min(255, bar_color_r)), max(0, min(255, bar_color_g)), max(0, min(255, bar_color_b)))
                    pygame.draw.rect(surface, bar_color, (bar_x, bar_y, bar_width, bar_height))
                pygame.draw.rect(surface, BLACK, rect, 1)

    def draw_text(self, text: str, x: int, y: int, color: Tuple[int, int, int] = WHITE,
                  shadow: bool = True, font_override: Optional[pygame.font.Font] = None, center_x_in: Optional[int] = None):
        font_to_use = font_override if font_override else self.font
        shadow_offset = 2 if font_to_use == self.large_font else 1
        text_surf = font_to_use.render(text, True, color)
        text_rect = text_surf.get_rect()
        if center_x_in is not None:
            text_rect.centerx = center_x_in // 2
            text_rect.top = y
        else:
            text_rect.topleft = (x, y)
        if shadow:
            shadow_surf = font_to_use.render(text, True, TEXT_SHADOW)
            self.screen.blit(shadow_surf, (text_rect.x + shadow_offset, text_rect.y + shadow_offset))
        self.screen.blit(text_surf, text_rect)
        return text_rect

    def draw_ui(self) -> None:
        # Draw Sidebar background
        pygame.draw.rect(self.screen, SIDEBAR_BG, (0, 0, SIDEBAR_WIDTH, SCREEN_HEIGHT))
        current_y = UI_PADDING

        # 0. Pause/Resume Button at the top right of the sidebar
        self.pause_button_rect = pygame.Rect(SIDEBAR_WIDTH - UI_BUTTON_WIDTH - UI_PADDING, UI_PADDING, UI_BUTTON_WIDTH, PAUSE_BUTTON_HEIGHT)
        pause_text = "Resume" if self.paused else "Pause"
        mouse_pos = pygame.mouse.get_pos()
        button_color = BUTTON_HOVER_COLOR if self.pause_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
        pygame.draw.rect(self.screen, button_color, self.pause_button_rect, border_radius=5)
        pause_text_surf = self.font.render(pause_text, True, BUTTON_TEXT_COLOR)
        pause_text_rect = pause_text_surf.get_rect(center=self.pause_button_rect.center)
        self.screen.blit(pause_text_surf, pause_text_rect)
        current_y += PAUSE_BUTTON_HEIGHT + UI_PADDING

        # 1. Logo
        if self.sidebar_logo:
            logo_rect = self.sidebar_logo.get_rect(centerx=SIDEBAR_WIDTH // 2, top=current_y)
            self.screen.blit(self.sidebar_logo, logo_rect)
            current_y += logo_rect.height + UI_PADDING * 2
        else:
            self.draw_text("JerryCraft", UI_PADDING, current_y, YELLOW, font_override=self.large_font, center_x_in=SIDEBAR_WIDTH)
            current_y += self.large_font.get_height() + UI_PADDING * 2

        # 2. Phase/Round/Timer Info
        phase_txt = f"Phase: {self.phase.capitalize()}"
        round_txt = f"Round: {self.round_number}"
        timer_txt = f"Time Left: {self.time_left_in_phase // 1000}s"
        self.draw_text(phase_txt, UI_PADDING, current_y)
        current_y += UI_LINE_HEIGHT
        self.draw_text(round_txt, UI_PADDING, current_y)
        current_y += UI_LINE_HEIGHT
        self.draw_text(timer_txt, UI_PADDING, current_y)
        current_y += int(UI_LINE_HEIGHT * 1.5)

        # 3. Inventory
        inv_y = current_y
        self.draw_text("Inventory:", UI_PADDING, inv_y, YELLOW)
        inv_y += int(UI_LINE_HEIGHT * 0.8)
        for i, block_name in enumerate(SELECTABLE_BLOCKS):
            prefix = "> " if i == self.current_block_index else "  "
            inv_text = f"{prefix}[{i+1}] {block_name.title()}: {self.inventory[block_name]}"
            self.draw_text(inv_text, UI_PADDING, inv_y)
            inv_y += UI_LINE_HEIGHT

        # 4. Skip Button (only during build phase)
        self.skip_button_rect = None
        if self.phase == "build" and not self.game_over:
            button_rect = pygame.Rect(UI_PADDING, UI_BUTTON_Y, UI_BUTTON_WIDTH, UI_BUTTON_HEIGHT)
            self.skip_button_rect = button_rect
            mouse_pos = pygame.mouse.get_pos()
            button_color = BUTTON_HOVER_COLOR if button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, button_color, button_rect, border_radius=5)
            btn_text_surf = self.font.render("Skip to Night", True, BUTTON_TEXT_COLOR)
            btn_text_rect = btn_text_surf.get_rect(center=button_rect.center)
            self.screen.blit(btn_text_surf, btn_text_rect)

        # 5. Instructions
        inst_y = UI_INST_START_Y
        instructions = ["LMB: Place | RMB: Remove", "1-5: Select Block | ESC: Quit"]
        for line in instructions:
            self.draw_text(line, UI_PADDING, inst_y)
            inst_y += int(UI_LINE_HEIGHT * 0.8)

        # 6. Transition Message (if bonus win)
        if self.transition_message:
            if pygame.time.get_ticks() < self.transition_message_end:
                # Draw message in a centered box in the sidebar
                self.draw_text(self.transition_message, 0, UI_INFO_START_Y, YELLOW, shadow=True, font_override=self.large_font, center_x_in=SIDEBAR_WIDTH)
            else:
                self.transition_message = None

        # 7. Game Over Message and Restart Button
        if self.game_over:
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0, 0, 0, 180))
            self.screen.blit(overlay, (0, 0))
            self.draw_text("GAME OVER", 0, SCREEN_HEIGHT // 2 - 80, RED, shadow=True, font_override=self.large_font, center_x_in=SCREEN_WIDTH)
            summary1 = f"You survived {max(0, self.round_number - 1)} nights."
            summary2 = f"Total Jeepers Spawned: {self.total_jeepers_spawned}"
            summary3 = "Press ESC to Exit"
            self.draw_text(summary1, 0, SCREEN_HEIGHT // 2 + 10, WHITE, shadow=True, center_x_in=SCREEN_WIDTH)
            self.draw_text(summary2, 0, SCREEN_HEIGHT // 2 + 10 + UI_LINE_HEIGHT, WHITE, shadow=True, center_x_in=SCREEN_WIDTH)
            self.draw_text(summary3, 0, SCREEN_HEIGHT // 2 + 10 + UI_LINE_HEIGHT * 2.5, YELLOW, shadow=True, center_x_in=SCREEN_WIDTH)
            # Draw Restart Button
            self.restart_button_rect = pygame.Rect(UI_PADDING, RESTART_BUTTON_Y, RESTART_BUTTON_WIDTH, RESTART_BUTTON_HEIGHT)
            mouse_pos = pygame.mouse.get_pos()
            restart_btn_color = BUTTON_HOVER_COLOR if self.restart_button_rect.collidepoint(mouse_pos) else BUTTON_COLOR
            pygame.draw.rect(self.screen, restart_btn_color, self.restart_button_rect, border_radius=5)
            restart_text_surf = self.font.render("Restart", True, BUTTON_TEXT_COLOR)
            restart_text_rect = restart_text_surf.get_rect(center=self.restart_button_rect.center)
            self.screen.blit(restart_text_surf, restart_text_rect)

    def draw(self) -> None:
        self.draw_grid_to_surface(self.game_surface)
        self.player.draw(self.game_surface)
        if self.phase == "night" or self.game_over:
            for creeper in self.creepers:
                creeper.draw(self.game_surface)
        for effect in self.effects:
            effect.draw(self.game_surface)
        if self.phase == "night" and not self.game_over:
            self.game_surface.blit(self.night_overlay, (0, 0))
        self.screen.blit(self.game_surface, (SIDEBAR_WIDTH, 0))
        self.draw_ui()
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

# --- Main Execution ---
if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption("JerryCraft - Loading...")
    clock = pygame.time.Clock()

    ui_font_size = 22
    story_font_size = 32
    large_font_size = 72
    ui_font = pygame.font.SysFont(None, ui_font_size)
    story_font = pygame.font.SysFont(None, story_font_size)
    large_font = pygame.font.SysFont(None, large_font_size)

    logo_file_path = "JerryCraftLogo.png"
    show_splash_screen(
        screen=screen,
        clock=clock,
        font=story_font,
        large_font=large_font,
        logo_path=logo_file_path
    )
    pygame.display.set_caption("JerryCraft")
    game = Game(screen=screen, clock=clock, font=ui_font, large_font=large_font, logo_path=logo_file_path)
    game.run()

    pygame.quit()
    sys.exit()
# %%--%%
