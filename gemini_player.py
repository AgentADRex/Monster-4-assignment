"""
Gemini AI player for Monster 4 game.
Uses Google Generative AI (Gemini) to choose strategic moves.
"""

import google.generativeai as genai
import random
import re

# You must set this API key before using the Gemini player
GEMINI_API_KEY = None


def configure_gemini(api_key):
    """Configure Gemini with your API key from https://aistudio.google.com/app/apikey"""
    global GEMINI_API_KEY
    GEMINI_API_KEY = api_key
    genai.configure(api_key=api_key)


def format_board_for_prompt(board):
    """Format the board state as a readable string for the prompt."""
    lines = []
    lines.append("Board (rows 0-3, cols 0-3):")
    lines.append("  0 1 2 3")
    for i, row in enumerate(board[1:]):
        lines.append(f"{i} {' '.join(row)}")
    lines.append(f"Skeleton row (reserves): {' '.join(board[0])}")
    return "\n".join(lines)


def gemini_choose_placement(board, face, player, valid_placements):
    """
    Ask Gemini to choose a placement given the board state and valid moves.
    
    Args:
        board: The game board (row 0 is skeleton row, rows 1-4 are game board)
        face: The die face rolled (e.g. "Light Grave", "Dark Grave", "Any Grave")
        player: The player symbol (e.g. "M1" or "M2")
        valid_placements: List of (row, col) tuples that are valid for this turn
    
    Returns:
        (row, col) tuple if Gemini chooses a valid move, else random.choice(valid_placements)
    """
    if not GEMINI_API_KEY:
        # Fallback to random if no API key configured
        return random.choice(valid_placements)
    
    if not valid_placements:
        return None
    
    board_str = format_board_for_prompt(board)
    
    prompt = f"""You are the {player} player in Monster 4, a 4-in-a-row game on a 4x4 board.
You just rolled: {face}

{board_str}

Your valid placements (row, col): {valid_placements}

Choose ONE placement that helps you win (get 4 in a row) or blocks your opponent.
Reply with ONLY the coordinates in the format (row, col), for example: (1, 2)
Do not include any other text."""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt, timeout=5)
        text = response.text.strip()
        
        # Try to parse the response as coordinates
        # Look for pattern like (1, 2) or 1, 2
        match = re.search(r'\(?(\d+)\s*,\s*(\d+)\)', text)
        if match:
            row, col = int(match.group(1)), int(match.group(2))
            if (row, col) in valid_placements:
                return (row, col)
        
        # Fallback to random if parsing fails or coords are invalid
        return random.choice(valid_placements)
    
    except Exception as e:
        print(f"Gemini API error: {e}. Falling back to random move.")
        return random.choice(valid_placements)


def gemini_choose_skeleton_placement(board, valid_placements):
    """
    Ask Gemini to choose where to place a skeleton.
    
    Args:
        board: The game board
        valid_placements: List of (row, col) empty cells
    
    Returns:
        (row, col) tuple for skeleton placement, or random choice if Gemini fails
    """
    if not GEMINI_API_KEY:
        return random.choice(valid_placements)
    
    if not valid_placements:
        return None
    
    board_str = format_board_for_prompt(board)
    
    prompt = f"""You are the M2 player in Monster 4.
You rolled "Skeleton Move" and can place a skeleton on any empty cell.
Skeletons act as wildcards and help form winning rows.

{board_str}

Valid empty cells (row, col): {valid_placements}

Choose ONE cell to place a skeleton. Reply with ONLY the coordinates like (1, 2)."""

    try:
        model = genai.GenerativeModel('gemini-pro')
        response = model.generate_content(prompt, timeout=5)
        text = response.text.strip()
        
        match = re.search(r'\(?(\d+)\s*,\s*(\d+)\)', text)
        if match:
            row, col = int(match.group(1)), int(match.group(2))
            if (row, col) in valid_placements:
                return (row, col)
        
        return random.choice(valid_placements)
    
    except Exception as e:
        print(f"Gemini skeleton placement error: {e}. Using random.")
        return random.choice(valid_placements)
