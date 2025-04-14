import pygame
import sys

# Initialize pygame
pygame.init()

# Game constants
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
GRID_SIZE = 20
GRID_WIDTH = SCREEN_WIDTH // GRID_SIZE
GRID_HEIGHT = SCREEN_HEIGHT // GRID_SIZE
FPS = 60

# Colors
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED   = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE  = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY   = (128, 128, 128)

# Block types
BLOCK_TYPES = {
    "empty": {"color": BLACK, "solid": False},
    "grass": {"color": GREEN, "solid": True},
    "dirt": {"color": (139, 69, 19), "solid": True},
    "stone": {"color": GRAY, "solid": True},
    "water": {"color": BLUE, "solid": False},
    "sand": {"color": YELLOW, "solid": True}
}

# Set up the display
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Block Construction Game")
clock = pygame.time.Clock()

# Game grid - starts empty
grid = [[BLOCK_TYPES["empty"] for _ in range(GRID_HEIGHT)] for _ in range(GRID_WIDTH)]

# Current selected block type
current_block = "grass"

def draw_grid():
    for x in range(GRID_WIDTH):
        for y in range(GRID_HEIGHT):
            rect = pygame.Rect(x * GRID_SIZE, y * GRID_SIZE, GRID_SIZE, GRID_SIZE)
            pygame.draw.rect(screen, grid[x][y]["color"], rect)
            pygame.draw.rect(screen, BLACK, rect, 1)  # Grid lines

def draw_ui():
    font = pygame.font.SysFont(None, 24)
    text = font.render(f"Current: {current_block}", True, WHITE)
    screen.blit(text, (10, 10))

    instructions = [
        "Left click: Place block",
        "Right click: Remove block",
        "1-6: Select block type",
        "ESC: Quit"
    ]

    for i, instruction in enumerate(instructions):
        line = font.render(instruction, True, WHITE)
        screen.blit(line, (10, 40 + i * 25))

def handle_events():
    global current_block, running

    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                running = False
            elif event.key == pygame.K_1:
                current_block = "grass"
            elif event.key == pygame.K_2:
                current_block = "dirt"
            elif event.key == pygame.K_3:
                current_block = "stone"
            elif event.key == pygame.K_4:
                current_block = "water"
            elif event.key == pygame.K_5:
                current_block = "sand"
            elif event.key == pygame.K_6:
                current_block = "empty"

        elif event.type == pygame.MOUSEBUTTONDOWN:
            mouse_x, mouse_y = pygame.mouse.get_pos()
            grid_x, grid_y = mouse_x // GRID_SIZE, mouse_y // GRID_SIZE

            if 0 <= grid_x < GRID_WIDTH and 0 <= grid_y < GRID_HEIGHT:
                if event.button == 1:
                    grid[grid_x][grid_y] = BLOCK_TYPES[current_block]
                elif event.button == 3:
                    grid[grid_x][grid_y] = BLOCK_TYPES["empty"]

# Main game loop
running = True
while running:
    handle_events()

    screen.fill(BLACK)
    draw_grid()
    draw_ui()

    pygame.display.flip()
    clock.tick(FPS)

pygame.quit()
sys.exit()
