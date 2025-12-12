import tkinter as tk
from tkinter import messagebox
from functools import partial
import importlib.util
import os
import gemini_player

# Load the local monster4.py explicitly (avoids import shadowing issues)
spec_path = os.path.join(os.path.dirname(__file__), 'monster4.py')
spec = importlib.util.spec_from_file_location('monster4', spec_path)
monster4 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(monster4)

# === GEMINI CONFIGURATION ===
# To use Gemini AI opponent, get an API key from https://aistudio.google.com/app/apikey
# and paste it here:
GEMINI_API_KEY = None  # Set to your API key to enable Gemini AI

if GEMINI_API_KEY:
    gemini_player.configure_gemini(GEMINI_API_KEY)
    USE_GEMINI = True
else:
    USE_GEMINI = False

class BoardGUI:
    def __init__(self, root):
        self.root = root
        self.board = monster4.new_board()
        self.human = monster4.Player1_Monster
        self.computer = monster4.Player2_Monster
        self.current = self.human
        self.pending = None  # ('grave', face) or ('skeleton', None)
        self._build_ui()
        self.refresh()

    def _build_ui(self):
        top = tk.Frame(self.root)
        top.pack(padx=8, pady=4)
        self.skel_labels = []
        for i in range(4):
            lbl = tk.Label(top, text=self.board[0][i], width=3, relief='ridge')
            lbl.grid(row=0, column=i, padx=2)
            self.skel_labels.append(lbl)

        grid = tk.Frame(self.root)
        grid.pack(padx=8, pady=4)
        self.cell_buttons = [[None]*4 for _ in range(4)]
        for r in range(4):
            for c in range(4):
                btn = tk.Button(grid, text='.', width=3,
                                command=partial(self.on_cell_click, r, c))
                btn.grid(row=r, column=c, padx=2, pady=2)
                self.cell_buttons[r][c] = btn

        ctl = tk.Frame(self.root)
        ctl.pack(padx=8, pady=6)
        self.roll_btn = tk.Button(ctl, text='Roll', command=self.on_roll)
        self.roll_btn.pack(side='left')
        self.msg = tk.Label(ctl, text='')
        self.msg.pack(side='left', padx=8)

    def refresh(self):
        for i, lbl in enumerate(self.skel_labels):
            lbl.config(text=self.board[0][i])
        for r in range(4):
            for c in range(4):
                self.cell_buttons[r][c].config(text=self.board[1+r][c])

    def on_roll(self):
        if self.current != self.human:
            return
        # GUI uses a button press as the human action, so don't call the
        # console `input()`-blocking path; use non-blocking roll instead.
        face = monster4.roll_die(human=False)
        self.msg.config(text=face)
        if face in ("Light Grave", "Dark Grave", "Any Grave"):
            self.pending = ('grave', face)
            self.msg.config(text=f"Place on {face} - click a valid cell")
            # wait for click
        elif face == "Skeleton Move":
            self.pending = ('skeleton', None)
            self.msg.config(text="Place a skeleton - click an empty cell")
        else:
            # other faces: let the module handle (computer/human agnostic)
            monster4.apply_face(face, self.board, self.current, is_human=True)
            self.after_action()

    def on_cell_click(self, r, c):
        if self.current != self.human:
            return
        if not self.pending:
            return
        kind, data = self.pending
        if kind == 'grave':
            face = data
            # check valid placements for that face
            valid = monster4._valid_placements(self.board, face=face)
            if (r, c) not in valid:
                messagebox.showinfo('Invalid', 'That cell is not valid for this grave face.')
                return
            monster4._place_monster(self.board, r, c, self.human)
            self.pending = None
            self.msg.config(text='')
            self.after_action()
        elif kind == 'skeleton':
            # check empty
            empties = monster4._empty_placements(self.board)
            if (r, c) not in empties:
                messagebox.showinfo('Invalid', 'Cell not empty.')
                return
            # place skeleton and remove one from top row
            self.board[1 + r][c] = monster4.Skeleton
            for i in range(monster4.Board_Size):
                if self.board[0][i] == monster4.Skeleton:
                    self.board[0][i] = monster4.EMPTY
                    break
            self.pending = None
            self.msg.config(text='')
            self.after_action()

        self.refresh()

    def after_action(self):
        # refresh, check winner, then run computer turn
        self.refresh()
        w = monster4.winner(self.board)
        if w:
            monster4.congrat_winner(w, self.computer, self.human)
            messagebox.showinfo('Game Over', f'Winner: {w}')
            self.roll_btn.config(state='disabled')
            return
        # swap to computer and schedule computer turn
        self.current = self.computer
        self.root.after(600, self.computer_turn)

    def computer_turn(self):
        face = monster4.roll_die(human=False)
        self.msg.config(text=f'Computer: {face}')
        
        # Use Gemini for strategic moves if configured, otherwise random
        if USE_GEMINI and face in ("Light Grave", "Dark Grave", "Any Grave"):
            valid = monster4._valid_placements(self.board, face=face)
            if valid:
                r, c = gemini_player.gemini_choose_placement(
                    self.board, face, self.current, valid
                )
                monster4._place_monster(self.board, r, c, self.current)
            else:
                print(f"No valid placements for {face}")
        elif USE_GEMINI and face == "Skeleton Move":
            empties = monster4._empty_placements(self.board)
            if empties:
                r, c = gemini_player.gemini_choose_skeleton_placement(self.board, empties)
                self.board[1 + r][c] = monster4.Skeleton
                for i in range(monster4.Board_Size):
                    if self.board[0][i] == monster4.Skeleton:
                        self.board[0][i] = monster4.EMPTY
                        break
            else:
                print("No empty cells for skeleton placement")
        else:
            # Use default game logic for non-placement faces or if Gemini not configured
            monster4.apply_face(face, self.board, self.current, is_human=False)
        
        self.refresh()
        w = monster4.winner(self.board)
        if w:
            monster4.congrat_winner(w, self.computer, self.human)
            messagebox.showinfo('Game Over', f'Winner: {w}')
            self.roll_btn.config(state='disabled')
            return
        # back to human
        self.current = self.human
        self.msg.config(text='Your turn')

if __name__ == '__main__':
    root = tk.Tk()
    root.title('Monster 4')
    gui = BoardGUI(root)
    root.mainloop()
