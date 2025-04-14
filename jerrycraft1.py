import pygame
import sys
import random
import math

# --- Constants ---
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

BUILD_PHASE_DURATION = 60 * 1000  # 60 seconds in milliseconds
NIGHT_PHASE_DURATION = 60 * 1000  # 60 seconds in milliseconds
CREEPER_BASE_MOVE_DELAY = 750     # Milliseconds between creeper moves

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 0) # Changed UI text to yellow for better contrast sometimes
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
BROWN = (101, 67, 33)
ORANGE_RED = (255, 69, 0)
DARK_GREEN = (0, 100, 0) # Creeper color
JERRY_COLOR = (200, 50, 50) # Jerry color

# Block Types Definition
BLOCK_TYPES = {
    "grass": {
        "color": GREEN, "solid": True, "travel_cost": 1,
        "durability": float('inf'), "effect": None, "breakable": False
    },
    "mud": {
        "color": BROWN, "solid": True, "travel_cost": 3,
        "durability": 2, "effect": None, "breakable": True
    },
    "stone": {
        "color": GRAY, "solid": True, "travel_cost": float('inf'),
        "durability": 5, "effect": None, "breakable": True # Increased durability
    },
    "water": {
        "color": BLUE, "solid": False, "travel_cost": 4,
        "durability": float('inf'), "effect": None, "breakable": False # Water isn't breakable
    },
    "sand": {
        "color": YELLOW, "solid": True, "travel_cost": 2,
        "durability": 1, "effect": None, "breakable": True
    },
    "fire": {
        "color": ORANGE_RED, "solid": True, "travel_cost": 1, # Creepers *can* walk on it, but...
        "durability": 3, "effect": "burn", "breakable": True # Fire pits burn out
    }
}

# Block Selection Keys (1-5)
SELECTABLE_BLOCKS = ["mud", "stone", "water", "sand", "fire"]

# --- Classes ---

class Player:
    """ Represents Jerry """
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.grid_x = x // GRID_SIZE
        self.grid_y = y // GRID_SIZE
        self.color = JERRY_COLOR
        # Add image loading here if you have one
        # self.image = pygame.image.load("jerry.png").convert_alpha()

    def draw(self, screen):
        rect = pygame.Rect(self.grid_x * GRID_SIZE, self.grid_y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.ellipse(screen, self.color, rect)
        # If using image:
        # screen.blit(self.image, rect.topleft)

class Creeper:
    """ Represents a Creeper enemy """
    def __init__(self, x, y, target):
        self.x = x
        self.y = y
        self.target = target # The Player object
        self.color = DARK_GREEN
        self.last_move_time = pygame.time.get_ticks()
        self.move_delay = CREEPER_BASE_MOVE_DELAY # Initial delay

    def draw(self, screen):
        rect = pygame.Rect(self.x * GRID_SIZE, self.y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
        pygame.draw.rect(screen, self.color, rect)

    def get_move_options(self, grid):
        """ Calculates possible moves towards the target, considering costs. """
        options = []
        target_x, target_y = self.target.grid_x, self.target.grid_y

        for dx, dy in [(0, -1), (0, 1), (-1, 0), (1, 0), (-1,-1), (1,1), (-1,1), (1,-1)]: # Check adjacent including diagonals
            next_x, next_y = self.x + dx, self.y + dy

            # Check bounds
            if 0 <= next_x < GRID_WIDTH and 0 <= next_y < GRID_HEIGHT:
                cell_data = grid[next_x][next_y]
                block_type = BLOCK_TYPES[cell_data["type"]]

                # Cannot move into solid blocks unless it's the target cell (Jerry)
                # Or if the block is stone (handle breaking separately)
                is_target_cell = (next_x == target_x and next_y == target_y)
                is_stone = cell_data["type"] == "stone"

                if block_type["solid"] and not is_target_cell and not is_stone:
                    continue # Skip solid blocks (except stone)

                # Calculate cost: distance heuristic + travel cost
                distance = math.sqrt((next_x - target_x)**2 + (next_y - target_y)**2)
                cost = distance + block_type["travel_cost"]

                options.append(((next_x, next_y), cost))

        # Sort options by cost (lower is better)
        options.sort(key=lambda item: item[1])
        return [opt[0] for opt in options] # Return just the coordinates

    def move(self, grid):
        """ Attempts to move the creeper one step towards the target. """
        now = pygame.time.get_ticks()
        if now - self.last_move_time < self.move_delay:
            return False # Not time to move yet

        options = self.get_move_options(grid)
        if not options:
            self.last_move_time = now # Reset timer even if stuck
            return False # Cannot move

        next_x, next_y = options[0] # Choose the best option

        # --- Interaction Check ---
        target_cell = grid[next_x][next_y]
        target_block_type_name = target_cell["type"]
        target_block_props = BLOCK_TYPES[target_block_type_name]

        # 1. Check if moving onto Jerry
        if next_x == self.target.grid_x and next_y == self.target.grid_y:
            self.x, self.y = next_x, next_y # Move onto Jerry
            self.last_move_time = now
            return "reached_jerry" # Signal game over

        # 2. Check for Fire effect
        if target_block_props["effect"] == "burn" and target_cell["durability"] > 0:
             # Damage the fire block
            if target_block_props["breakable"]:
                grid[next_x][next_y]["durability"] -= 1
                if grid[next_x][next_y]["durability"] <= 0:
                    grid[next_x][next_y] = {"type": "grass", "durability": float('inf')} # Burned out
            self.last_move_time = now # Reset timer
            return "burned" # Creeper is destroyed

        # 3. Check for breakable solid blocks (Stone, Mud, Sand, exhausted Fire)
        if target_block_props["solid"] and target_block_props["breakable"] and target_cell["durability"] > 0:
            grid[next_x][next_y]["durability"] -= 1
            # If block breaks, turn it to grass
            if grid[next_x][next_y]["durability"] <= 0:
                 grid[next_x][next_y] = {"type": "grass", "durability": float('inf')}
            # Creeper doesn't move this turn, just attacks the block
            self.last_move_time = now
            # Adjust delay slightly after hitting a block? Optional.
            # self.move_delay = CREEPER_BASE_MOVE_DELAY * 1.1
            return False # Blocked movement this turn

        # 4. If the way is clear or non-solid (like water or grass), move
        self.x, self.y = next_x, next_y
        self.last_move_time = now
        # Adjust next move delay based on the terrain *entered*
        self.move_delay = CREEPER_BASE_MOVE_DELAY * target_block_props["travel_cost"]
        return True # Moved successfully


class Game:
    """ Manages the game state, objects, and main loop """
    def __init__(self):
        pygame.init()
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("JerryCraft")
        self.clock = pygame.time.Clock()
        self.font = pygame.font.SysFont(None, 24)
        self.running = True
        self.game_over = False

        # Game State
        self.phase = "build"  # "build" or "night"
        self.round_number = 1
        self.phase_start_time = pygame.time.get_ticks()
        self.time_left_in_phase = BUILD_PHASE_DURATION

        # Game Objects
        jerry_start_x = (GRID_WIDTH // 2) * GRID_SIZE
        jerry_start_y = (GRID_HEIGHT // 2) * GRID_SIZE
        self.player = Player(jerry_start_x, jerry_start_y)
        self.creepers = []

        # Grid and Inventory
        self.grid = self._initialize_grid()
        self.inventory = self._initial_inventory()
        self.current_block_index = 0  # Index into SELECTABLE_BLOCKS
        self.current_block_type = SELECTABLE_BLOCKS[self.current_block_index]

    def _initialize_grid(self):
        """ Creates the initial grid filled with grass """
        grid = [[{"type": "grass", "durability": float('inf')} for _ in range(GRID_HEIGHT)]
                for _ in range(GRID_WIDTH)]
        # Ensure Jerry's starting cell is also grass initially
        px, py = self.player.grid_x, self.player.grid_y
        if 0 <= px < GRID_WIDTH and 0 <= py < GRID_HEIGHT:
             grid[px][py] = {"type": "grass", "durability": float('inf')}
        return grid

    def _initial_inventory(self):
        """ Returns the starting inventory """
        return {
            "mud": 20, "stone": 10, "water": 5, "sand": 15, "fire": 3
        }

    def reward_inventory(self):
        """ Adds resources after surviving a night """
        print("Rewarding inventory!") # Debug
        self.inventory["mud"] += 5 + self.round_number
        self.inventory["stone"] += 3 + self.round_number
        self.inventory["water"] += 1 + (self.round_number // 2)
        self.inventory["sand"] += 4 + self.round_number
        self.inventory["fire"] += 1 + (self.round_number // 3)

    def spawn_creepers(self):
        """ Spawns creepers at the edges """
        self.creepers = []
        count = 3 + self.round_number * 2  # Increase difficulty
        print(f"Spawning {count} creepers for round {self.round_number}") # Debug
        for _ in range(count):
            edge = random.randint(0, 3)
            if edge == 0: x, y = random.randint(0, GRID_WIDTH - 1), 0
            elif edge == 1: x, y = random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1
            elif edge == 2: x, y = 0, random.randint(0, GRID_HEIGHT - 1)
            else: x, y = GRID_WIDTH - 1, random.randint(0, GRID_HEIGHT - 1)

            # Avoid spawning directly on Jerry
            if x == self.player.grid_x and y == self.player.grid_y:
                y = (y + 1) % GRID_HEIGHT # Move one step away if possible

            # Avoid spawning inside solid blocks if possible (simple check)
            if BLOCK_TYPES[self.grid[x][y]["type"]]["solid"]:
                 # Try another edge if the first spot is solid (basic avoidance)
                 edge = (edge + 1) % 4
                 if edge == 0: x, y = random.randint(0, GRID_WIDTH - 1), 0
                 elif edge == 1: x, y = random.randint(0, GRID_WIDTH - 1), GRID_HEIGHT - 1
                 elif edge == 2: x, y = 0, random.randint(0, GRID_HEIGHT - 1)
                 else: x, y = GRID_WIDTH - 1, random.randint(0, GRID_HEIGHT - 1)

            self.creepers.append(Creeper(x, y, self.player))

    def place_block(self, grid_x, grid_y):
        """ Places the current block if possible """
        # Cannot build on Jerry
        if grid_x == self.player.grid_x and grid_y == self.player.grid_y:
            return

        block_to_place = self.current_block_type
        if self.inventory[block_to_place] > 0:
            # Get default properties for the new block
            block_props = BLOCK_TYPES[block_to_place]
            new_durability = block_props["durability"] # Use default durability

            # Allow replacing existing blocks (except indestructible grass maybe?)
            # Optional: refund resource if replacing a non-grass block? For now, no.
            self.grid[grid_x][grid_y] = {"type": block_to_place, "durability": new_durability}
            self.inventory[block_to_place] -= 1
            print(f"Placed {block_to_place} at ({grid_x},{grid_y}). Remaining: {self.inventory[block_to_place]}") # Debug
        else:
            print(f"No more {block_to_place} left!") # Debug

    def remove_block(self, grid_x, grid_y):
        """ Resets a block back to grass (right-click) """
         # Cannot remove Jerry's spot
        if grid_x == self.player.grid_x and grid_y == self.player.grid_y:
            return

        # Optional: Refund resources when removing placed blocks?
        # current_block_type = self.grid[grid_x][grid_y]["type"]
        # if current_block_type != "grass" and current_block_type in self.inventory:
        #     self.inventory[current_block_type] += 1

        self.grid[grid_x][grid_y] = {"type": "grass", "durability": float('inf')}
        print(f"Removed block at ({grid_x},{grid_y})") # Debug

    def handle_events(self):
        """ Processes player input """
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
                            print(f"Selected block: {self.current_block_type}") # Debug
                    # Add Keys for scrolling through blocks? e.g., Q/E or mouse wheel
                    # elif event.key == pygame.K_e: # Cycle forward
                    #     self.current_block_index = (self.current_block_index + 1) % len(SELECTABLE_BLOCKS)
                    #     self.current_block_type = SELECTABLE_BLOCKS[self.current_block_index]
                    # elif event.key == pygame.K_q: # Cycle backward
                    #     self.current_block_index = (self.current_block_index - 1 + len(SELECTABLE_BLOCKS)) % len(SELECTABLE_BLOCKS)
                    #     self.current_block_type = SELECTABLE_BLOCKS[self.current_block_index]

            if event.type == pygame.MOUSEBUTTONDOWN and self.phase == "build" and not self.game_over:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE
                if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                    if event.button == 1:  # Left click
                        self.place_block(grid_x, grid_y)
                    elif event.button == 3: # Right click
                        self.remove_block(grid_x, grid_y)

    def update(self):
        """ Updates game state each frame """
        if self.game_over:
            return

        now = pygame.time.get_ticks()
        elapsed_in_phase = now - self.phase_start_time
        current_phase_duration = BUILD_PHASE_DURATION if self.phase == "build" else NIGHT_PHASE_DURATION
        self.time_left_in_phase = max(0, current_phase_duration - elapsed_in_phase)

        # --- Phase Transitions ---
        if self.time_left_in_phase <= 0:
            if self.phase == "build":
                self.phase = "night"
                self.phase_start_time = now
                self.time_left_in_phase = NIGHT_PHASE_DURATION
                self.spawn_creepers()
            elif self.phase == "night":
                # Night ended successfully
                self.phase = "build"
                self.round_number += 1
                self.phase_start_time = now
                self.time_left_in_phase = BUILD_PHASE_DURATION
                self.creepers = [] # Clear remaining creepers (optional)
                self.reward_inventory()

        # --- Update Creepers (only during night) ---
        if self.phase == "night":
            remaining_creepers = []
            for creeper in self.creepers:
                move_result = creeper.move(self.grid)
                if move_result == "reached_jerry":
                    self.game_over = True
                    print("GAME OVER - Creeper reached Jerry!") # Debug
                    break # Exit loop immediately
                elif move_result == "burned":
                    # Creeper was burned, don't add to remaining list
                    print("Creeper burned!") # Debug
                    continue
                else:
                    # Creeper moved, was blocked, or didn't move yet
                    remaining_creepers.append(creeper)
            if not self.game_over: # Only update list if game isn't over
                 self.creepers = remaining_creepers


    def draw_grid(self):
        """ Draws the game grid """
        for x in range(GRID_WIDTH):
            for y in range(GRID_HEIGHT):
                cell_data = self.grid[x][y]
                block_type = BLOCK_TYPES[cell_data["type"]]
                color = block_type["color"]
                rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
                pygame.draw.rect(self.screen, color, rect)
                # Draw durability indication (optional, simple example)
                if block_type["breakable"] and cell_data["durability"] < block_type["durability"] and cell_data["durability"] > 0:
                     # Draw a small indicator - e.g., smaller inner rect or a number
                     damage_rect = rect.inflate(-GRID_SIZE * 0.6, -GRID_SIZE * 0.6) # Smaller rect inside
                     # Vary color based on remaining health?
                     health_ratio = cell_data["durability"] / block_type["durability"]
                     damage_color = (255 * (1-health_ratio), 255 * health_ratio, 0) # Red to Green
                     pygame.draw.rect(self.screen, damage_color, damage_rect)

                pygame.draw.rect(self.screen, BLACK, rect, 1) # Grid lines

    def draw_ui(self):
        """ Draws the User Interface elements """
        # Phase and Timer
        phase_txt = f"Phase: {self.phase.capitalize()} | Round: {self.round_number}"
        timer_txt = f"Time Left: {self.time_left_in_phase // 1000}s"
        phase_surf = self.font.render(phase_txt, True, WHITE)
        timer_surf = self.font.render(timer_txt, True, WHITE)
        self.screen.blit(phase_surf, (10, 10))
        self.screen.blit(timer_surf, (10, 35))

        # Inventory and Selection
        inv_y = 60
        for i, block_name in enumerate(SELECTABLE_BLOCKS):
            prefix = "> " if i == self.current_block_index else "  "
            inv_text = f"{prefix}[{i+1}] {block_name.title()}: {self.inventory[block_name]}"
            inv_surf = self.font.render(inv_text, True, WHITE)
            self.screen.blit(inv_surf, (10, inv_y))
            inv_y += 25

        # Instructions (simplified)
        inst_y = SCREEN_HEIGHT - 70
        instructions = [
            "LMB: Place | RMB: Remove (Grass)",
            "1-5: Select Block | ESC: Quit"
        ]
        for line in instructions:
            inst_surf = self.font.render(line, True, WHITE)
            self.screen.blit(inst_surf, (10, inst_y))
            inst_y += 20

        # Game Over Message
        if self.game_over:
            font_large = pygame.font.SysFont(None, 72)
            go_surf = font_large.render("GAME OVER", True, RED)
            go_rect = go_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 20))
            esc_surf = self.font.render("Press ESC to Exit", True, WHITE)
            esc_rect = esc_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 30))
            # Semi-transparent background for message
            overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.SRCALPHA)
            overlay.fill((0,0,0, 180))
            self.screen.blit(overlay, (0,0))
            self.screen.blit(go_surf, go_rect)
            self.screen.blit(esc_surf, esc_rect)


    def draw(self):
        """ Draws all game elements """
        self.screen.fill(BLACK)  # Background
        self.draw_grid()
        self.player.draw(self.screen)
        if self.phase == "night" or self.game_over: # Draw creepers during night or on game over screen
             for creeper in self.creepers:
                 creeper.draw(self.screen)
        self.draw_ui() # Draw UI on top
        pygame.display.flip()

    def run(self):
        """ Main game loop """
        while self.running:
            self.handle_events()
            self.update()
            self.draw()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()

# --- Main Execution ---
if __name__ == '__main__':
    game = Game()
    game.run()