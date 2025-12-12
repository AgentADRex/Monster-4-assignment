# Monster 4- Based on 2009 board game produced by Lego
# The main goal of the game is to get 4 of your monsters in a row on the board.
# Each player picks one of four monsters and rolls a die to determin their action.
# The actions include using skeletons as a wild card to help form rows, and using a spider to scare off your opponents monsters.


# global variables
EMPTY = "."
Skeleton = "S"
Player1_Monster = "M1"
Player2_Monster = "M2"
Board_Size = 4

Die_Faces = [
    "Light Grave",
    "Dark Grave",
    "Any Grave",
    "Skeleton Move",
    "Graveyard Shift",
]

import random

def ask_yes_no(question):
    """Ask a yes or no question."""
    response = None
    while response not in ("y", "n"):
        response = input(question + " (y/n): ").lower()
    return response

def pieces():
    """Asks if the player or computer goes first.""" 
    go_first = ask_yes_no("Do you want to go first?")
    if go_first == "y":
        print ("\nGood luck! Let the game begin!")
        human = Player1_Monster
        computer = Player2_Monster
    else:
        print ("\nHope you aren't nervous playing against me. Good luck!")
        human = Player2_Monster
        computer = Player1_Monster
    return computer, human

def new_board():
    """
    Create a new 4x4 board initialized with empty spaces. 
    Also add a row solely used for holding the unused skeletons.
    """
    board = []

    board.append(["S", "S", "S", "S"])  # Row for unused skeletons
    for _ in range(4):
        board.append(["." for _ in range(4)])

    return board

def print_board(board):
    """
    Print the current state of the board.
    """
    print("\n  0 1 2 3")
    print("  ---------")
    # First row is skeletons (unused pieces)
    skel_row = board[0]
    print("S:", " ".join(skel_row))

    # Remaining rows are the 4x4 game board
    for i, row in enumerate(board[1:]):
        print(f"{i} ", " ".join(row))

#Grave colors distinguished
Light_Graves = {(0,0), (0,1), (1,0), (1,1), (2,2), (2,3), (3,2), (3,3)}
Dark_Graves = {(0,2), (0,3), (1,2), (1,3), (2,0), (2,1), (3,0), (3,1)}

def grave_color(x, y): 
    """I made this this function to determine the color of a grave based on its coordinates."""
    if (x, y) in Light_Graves:
        return "Light"
    elif (x, y) in Dark_Graves:
        return "Dark"
    else:
        return "Any"
    
def legal_grave_placement(board, x, y, face):
    """Check if placing a monster at (x, y) is legal for the given grave face."""
    color = grave_color(x, y)
    if face == "Light Grave" and color != "Light":
        return False
    if face == "Dark Grave" and color != "Dark":
        return False
    return True
def roll_die(human=False):
    """Return a randomly chosen die face from `Die_Faces`.

    If `human` is True, wait for the player to press Enter before
    performing the roll (so the player must press Enter to roll).
    """
    if human:
        input("Press Enter to roll the die...")
        face = random.choice(Die_Faces)
        print(f"You rolled: {face}")
        return face
    else:
        face = random.choice(Die_Faces)
        print(f"Computer rolled: {face}")
        return face
# (removed stray roll at import time)


# --- Per-face handler templates -------------------------------------------------
def handle_light_grave(board, player, is_human=False):
    """Handle the "Light Grave" face. Place a monster on a light grave.

    For now light graves behave like normal placements: place on any
    empty or skeleton-containing cell. Human players are prompted for
    coordinates; computer chooses randomly.
    """
    return _place_on_grave(board, player, is_human, face="Light Grave")

def handle_dark_grave(board, player, is_human=False):
    """Handle the "Dark Grave" face. See `handle_light_grave` notes."""
    return _place_on_grave(board, player, is_human, face="Dark Grave")

def handle_any_grave(board, player, is_human=False):
    """Handle the "Any Grave" face. Allow placement like light/dark."""
    return _place_on_grave(board, player, is_human, face="Any Grave")

def handle_skeleton_move(board, player, is_human=False):
    """Handle the "Skeleton Move" face. Place a skeleton from the skeleton row."""
    return _place_skeleton(board, is_human)
    
def handle_graveyard_shift(board, player):
    """Handle the "Graveyard Shift" face. Implement shifting logic."""
    # TODO: implement graveyard shift behaviour
    pass

def apply_face(face, board, player, is_human=False):
    """Dispatch the rolled face to the appropriate handler.

    This is a thin dispatcher that calls the placeholder handlers. Fill
    in the individual handlers to implement game rules for each face.
    """
    if face == "Light Grave":
        handle_light_grave(board, player, is_human)
    elif face == "Dark Grave":
        handle_dark_grave(board, player, is_human)
    elif face == "Any Grave":
        handle_any_grave(board, player, is_human)
    elif face == "Skeleton Move":
        handle_skeleton_move(board, player, is_human)
    elif face == "Graveyard Shift":
        handle_graveyard_shift(board, player)
    else:
        print(f"No handler for face: {face}")


# --- Placement helpers ----------------------------------------------------------
def _valid_placements(board, face=None):
    """Return list of (row,col) available for placement (0-based).

    Cells are valid when EMPTY or a Skeleton.
    """
    placements = []
    for r in range(Board_Size):
        for c in range(Board_Size):
            val = board[1 + r][c]
            if val == EMPTY or val == Skeleton:
                # If a face is provided, only allow placements legal for that face
                if face is None or legal_grave_placement(board, r, c, face):
                    placements.append((r, c))
    return placements


def _place_monster(board, row, col, player):
    board[1 + row][col] = player


def _place_on_grave(board, player, is_human=False, face=None):
    """Common placement routine for grave faces.

    If `is_human` is True the user is prompted for coordinates; otherwise
    a random valid placement is chosen for the computer.
    """
    placements = _valid_placements(board, face=face)
    if not placements:
        print("No valid placements available.")
        return False

    if is_human:
        while True:
            coord = input("Enter placement as row,col (0-3): ").strip()
            try:
                r_s, c_s = coord.split(',')
                r = int(r_s)
                c = int(c_s)
            except Exception:
                print("Invalid format — use like 1,2")
                continue
            if (r, c) in placements:
                _place_monster(board, r, c, player)
                print(f"Placed {player} at ({r},{c}).")
                return True
            else:
                print("That cell is not valid. Choose an empty or skeleton cell.")
    else:
        r, c = random.choice(placements)
        _place_monster(board, r, c, player)
        print(f"Computer placed {player} at ({r},{c}).")
        return True

def _empty_placements(board):
    """Return list of (row,col) that are empty (0-based board coords)."""
    placements = []
    for r in range(Board_Size):
        for c in range(Board_Size):
            if board[1 + r][c] == EMPTY:
                placements.append((r, c))
    return placements


def _place_skeleton(board, is_human=False):
    """Place a skeleton from the skeleton row (row 0) onto an empty board cell.
    
    Removes a skeleton from row 0 and places it at the chosen location.
    For humans: prompts for coordinates. For computer: chooses randomly.
    """
    # Check if there are available skeletons in the skeleton row
    skel_count = board[0].count(Skeleton)
    if skel_count == 0:
        print("No skeletons available to place.")
        return False
    
    # Find empty placements
    placements = _empty_placements(board)
    if not placements:
        print("No empty cells available for skeleton placement.")
        return False
    
    if is_human:
        while True:
            coord = input("Enter skeleton placement as row,col (0-3): ").strip()
            try:
                r_s, c_s = coord.split(',')
                r = int(r_s)
                c = int(c_s)
            except Exception:
                print("Invalid format — use like 1,2")
                continue
            if (r, c) in placements:
                # Place skeleton on board
                board[1 + r][c] = Skeleton
                # Remove a skeleton from the skeleton row
                for i in range(Board_Size):
                    if board[0][i] == Skeleton:
                        board[0][i] = EMPTY
                        break
                print(f"Placed skeleton at ({r},{c}).")
                return True
            else:
                print("That cell is not empty. Choose an empty cell.")
    else:
        r, c = random.choice(placements)
        board[1 + r][c] = Skeleton
        # Remove a skeleton from the skeleton row
        for i in range(Board_Size):
            if board[0][i] == Skeleton:
                board[0][i] = EMPTY
                break
        print(f"Computer placed skeleton at ({r},{c}).")
        return True

# --- Win criteria----------------------------------------------
def winner(board):
    """Check the board for a winner."""
    Ways_to_Win = [
        # Horizontal
        ((1,0), (1,1), (1,2), (1,3)),
        ((2,0), (2,1), (2,2), (2,3)),
        ((3,0), (3,1), (3,2), (3,3)),
        ((4,0), (4,1), (4,2), (4,3)),
        # Vertical
        ((1,0), (2,0), (3,0), (4,0)),
        ((1,1), (2,1), (3,1), (4,1)),
        ((1,2), (2,2), (3,2), (4,2)),
        ((1,3), (2,3), (3,3), (4,3)),
    ]
    for line in Ways_to_Win:
        cells = [board[r][c] for (r, c) in line]

        # Ignore lines with any empty cells — they cannot be completed yet
        # (cells can be EMPTY, Skeleton, or a player's monster string)
        if any(cell == EMPTY for cell in cells):
            continue

        # Collect non-skeleton, non-empty entries (actual player pieces)
        players_in_line = [cell for cell in cells if cell != Skeleton and cell != EMPTY]

        # If there is exactly one player's symbol present and all other
        # cells are either that symbol or skeletons, that player wins.
        if players_in_line:
            players_set = set(players_in_line)
            if len(players_set) == 1:
                candidate = next(iter(players_set))
                if all(cell == candidate or cell == Skeleton for cell in cells):
                    return candidate
        # If there are no player pieces (all skeletons) we do not count that as a win.

    return None

def congrat_winner(the_winner, computer, human):
    """Congratulate the winner."""
    if the_winner == computer:
        print("The computer wins! Better luck next time.")
    elif the_winner == human:
        print("Congratulations! You win!")
    else:
        print("It's a tie!")
# --- Main game flow ------------------------------------------------
def main():
    # Minimal runnable flow: choose who goes first and show an initial board
    computer, human = pieces()
    board = new_board()
    print_board(board)

    # Alternating turn loop: human must press Enter to roll; computer auto-rolls.
    current = human
    try:
        while True:
            player_label = "Human" if current == human else "Computer"
            print(f"\n{player_label}'s turn.")

            if current == human:
                face = roll_die(human=True)
            else:
                face = roll_die(human=False)

            apply_face(face, board, current, is_human=(current == human))
            print_board(board)

            # Check for a winner
            w = winner(board)
            if w:
                congrat_winner(w, computer, human)
                break

            # Allow quit between turns
            resp = input("Press Enter to continue, or 'q' to quit: ").strip().lower()
            if resp == 'q':
                print("Quitting game.")
                break

            # swap players
            current = computer if current == human else human
    except KeyboardInterrupt:
        print("\nGame interrupted.")


if __name__ == "__main__":
    main()
