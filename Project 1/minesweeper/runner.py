import pygame
import sys
import time

from minesweeper import Minesweeper, MinesweeperAI

# Game settings
HEIGHT = 8
WIDTH = 8
MINES = 8

# Colors
BLACK = (0, 0, 0)
GRAY = (180, 180, 180)
WHITE = (255, 255, 255)

# Initialize Pygame
pygame.init()
size = width, height = 600, 400
screen = pygame.display.set_mode(size)

# Fonts
OPEN_SANS = "assets/fonts/OpenSans-Regular.ttf"
small_font = pygame.font.Font(OPEN_SANS, 20)
medium_font = pygame.font.Font(OPEN_SANS, 28)
large_font = pygame.font.Font(OPEN_SANS, 40)

# Board dimensions and properties
BOARD_PADDING = 20
board_width = ((2 / 3) * width) - (BOARD_PADDING * 2)
board_height = height - (BOARD_PADDING * 2)
cell_size = int(min(board_width / WIDTH, board_height / HEIGHT))
board_origin = (BOARD_PADDING, BOARD_PADDING)

# Load images
flag_image = pygame.image.load("assets/images/flag.png")
flag_image = pygame.transform.scale(flag_image, (cell_size, cell_size))
mine_image = pygame.image.load("assets/images/mine.png")
mine_image = pygame.transform.scale(mine_image, (cell_size, cell_size))

# Initialize game and AI
minesweeper_game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
minesweeper_ai = MinesweeperAI(height=HEIGHT, width=WIDTH)

# Track game state
revealed_cells = set()
flagged_cells = set()
player_lost = False
show_instructions = True

while True:
    # Handle events
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            sys.exit()

    # Fill screen background
    screen.fill(BLACK)

    # Display instructions
    if show_instructions:
        title = large_font.render("Play Minesweeper", True, WHITE)
        title_rect = title.get_rect(center=(width / 2, 50))
        screen.blit(title, title_rect)

        rules = [
            "Click a cell to reveal it.",
            "Right-click a cell to mark it as a mine.",
            "Mark all mines successfully to win!"
        ]
        for i, rule in enumerate(rules):
            rule_text = small_font.render(rule, True, WHITE)
            rule_rect = rule_text.get_rect(center=(width / 2, 150 + 30 * i))
            screen.blit(rule_text, rule_rect)

        play_button = pygame.Rect(width / 4, (3 / 4) * height, width / 2, 50)
        play_button_text = medium_font.render("Play Game", True, BLACK)
        play_button_text_rect = play_button_text.get_rect(center=play_button.center)
        pygame.draw.rect(screen, WHITE, play_button)
        screen.blit(play_button_text, play_button_text_rect)

        if pygame.mouse.get_pressed()[0]:
            if play_button.collidepoint(pygame.mouse.get_pos()):
                show_instructions = False
                time.sleep(0.3)

        pygame.display.flip()
        continue

    # Draw the Minesweeper board
    cells = []
    for i in range(HEIGHT):
        row = []
        for j in range(WIDTH):
            cell_rect = pygame.Rect(
                board_origin[0] + j * cell_size,
                board_origin[1] + i * cell_size,
                cell_size, cell_size
            )
            pygame.draw.rect(screen, GRAY, cell_rect)
            pygame.draw.rect(screen, WHITE, cell_rect, 3)

            if minesweeper_game.is_mine((i, j)) and player_lost:
                screen.blit(mine_image, cell_rect)
            elif (i, j) in flagged_cells:
                screen.blit(flag_image, cell_rect)
            elif (i, j) in revealed_cells:
                neighbors_count = minesweeper_game.nearby_mines((i, j))
                neighbors_text = small_font.render(str(neighbors_count), True, BLACK)
                neighbors_text_rect = neighbors_text.get_rect(center=cell_rect.center)
                screen.blit(neighbors_text, neighbors_text_rect)

            row.append(cell_rect)
        cells.append(row)

    # AI Move button
    ai_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height - 50,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    ai_button_text = medium_font.render("AI Move", True, BLACK)
    ai_button_text_rect = ai_button_text.get_rect(center=ai_button.center)
    pygame.draw.rect(screen, WHITE, ai_button)
    screen.blit(ai_button_text, ai_button_text_rect)

    # Reset button
    reset_button = pygame.Rect(
        (2 / 3) * width + BOARD_PADDING, (1 / 3) * height + 20,
        (width / 3) - BOARD_PADDING * 2, 50
    )
    reset_button_text = medium_font.render("Reset", True, BLACK)
    reset_button_text_rect = reset_button_text.get_rect(center=reset_button.center)
    pygame.draw.rect(screen, WHITE, reset_button)
    screen.blit(reset_button_text, reset_button_text_rect)

    # Display win/loss status
    status_text = "Lost" if player_lost else "Won" if minesweeper_game.mines == flagged_cells else ""
    status_text_rendered = medium_font.render(status_text, True, WHITE)
    status_text_rect = status_text_rendered.get_rect(center=((5 / 6) * width, (2 / 3) * height))
    screen.blit(status_text_rendered, status_text_rect)

    move = None
    left_click, _, right_click = pygame.mouse.get_pressed()

    # Handle right-click for flagging cells
    if right_click and not player_lost:
        mouse_pos = pygame.mouse.get_pos()
        for i in range(HEIGHT):
            for j in range(WIDTH):
                if cells[i][j].collidepoint(mouse_pos) and (i, j) not in revealed_cells:
                    if (i, j) in flagged_cells:
                        flagged_cells.remove((i, j))
                    else:
                        flagged_cells.add((i, j))
                    time.sleep(0.2)

    # Handle left-click for moves
    elif left_click:
        mouse_pos = pygame.mouse.get_pos()

        if ai_button.collidepoint(mouse_pos) and not player_lost:
            move = minesweeper_ai.make_safe_move() or minesweeper_ai.make_random_move()
            if not move:
                flagged_cells = minesweeper_ai.mines.copy()
                print("No moves left to make.")
            time.sleep(0.2)

        elif reset_button.collidepoint(mouse_pos):
            minesweeper_game = Minesweeper(height=HEIGHT, width=WIDTH, mines=MINES)
            minesweeper_ai = MinesweeperAI(height=HEIGHT, width=WIDTH)
            revealed_cells.clear()
            flagged_cells.clear()
            player_lost = False
            continue

        else:
            for i in range(HEIGHT):
                for j in range(WIDTH):
                    if cells[i][j].collidepoint(mouse_pos) and (i, j) not in flagged_cells | revealed_cells:
                        move = (i, j)

    if move:
        if minesweeper_game.is_mine(move):
            player_lost = True
        else:
            revealed_cells.add(move)
            minesweeper_ai.add_knowledge(move, minesweeper_game.nearby_mines(move))

    pygame.display.flip()
