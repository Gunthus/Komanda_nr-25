import tkinter as tk
from tkinter import ttk
import time

###############################################################################
# Game Logic and Data Structures
###############################################################################

class Player:
    HUMAN = 0
    COMPUTER = 1

class GameState:
    def __init__(self, current_number, human_score, computer_score, current_player):
        self.current_number = current_number
        self.human_score = human_score
        self.computer_score = computer_score
        self.current_player = current_player

    def copy(self):
        return GameState(
            self.current_number,
            self.human_score,
            self.computer_score,
            self.current_player
        )

def is_terminal(state):
    """
    The game ends as soon as the current number is >= 1200.
    """
    return state.current_number >= 1200

def evaluate(state):
    """
    Heuristic/evaluation function for Minimax or Alpha-Beta.
    - If the state is terminal, return a large positive/negative score 
      if the computer is winning/losing, or 0 if tied.
    - Otherwise, use the score difference (computer_score - human_score).
    """
    if is_terminal(state):
        if state.human_score > state.computer_score:
            return -999999  # Big negative => losing for computer
        elif state.computer_score > state.human_score:
            return 999999   # Big positive => winning for computer
        else:
            return 0        # Tie
    else:
        # Non-terminal: difference in scores
        return state.computer_score - state.human_score

def get_successors(state):
    """
    Generates all possible next states for Minimax/Alpha-Beta by multiplying
    the current number by 2, 3, or 4 and applying the scoring rules:

      - If the result is even => opponent's points -1
      - If the result is odd  => current player's points +1
      - If the new number >= 1200 => game ends immediately

    We do switch the turn only if the game does not end.
    """
    if is_terminal(state):
        return []

    successors = []
    for multiplier in [2, 3, 4]:
        child = state.copy()
        new_number = child.current_number * multiplier
        child.current_number = new_number

        # Determine if it's even or odd
        if new_number % 2 == 0:
            # Even => Opponent loses 1 point
            if child.current_player == Player.HUMAN:
                child.computer_score -= 1
            else:
                child.human_score -= 1
        else:
            # Odd => Current player gains 1 point
            if child.current_player == Player.HUMAN:
                child.human_score += 1
            else:
                child.computer_score += 1

        # Check if game ends
        if new_number < 1200:
            # Switch player if not terminal
            if child.current_player == Player.HUMAN:
                child.current_player = Player.COMPUTER
            else:
                child.current_player = Player.HUMAN
        # If new_number >= 1200, the game ends immediately (no turn switch)

        successors.append((multiplier, child))

    return successors

###############################################################################
# Minimax and Alpha-Beta
###############################################################################

NODES_VISITED = 0  # For tracking how many nodes are expanded (useful for experiments)

def minimax(state, depth, maximizing_player):
    global NODES_VISITED
    NODES_VISITED += 1

    # Base case: depth limit or terminal state
    if depth == 0 or is_terminal(state):
        return evaluate(state), None

    if maximizing_player:
        best_value = float('-inf')
        best_move = None
        for move, child_state in get_successors(state):
            val, _ = minimax(child_state, depth - 1, False)
            if val > best_value:
                best_value = val
                best_move = move
        return best_value, best_move
    else:
        best_value = float('inf')
        best_move = None
        for move, child_state in get_successors(state):
            val, _ = minimax(child_state, depth - 1, True)
            if val < best_value:
                best_value = val
                best_move = move
        return best_value, best_move

def alpha_beta(state, depth, alpha, beta, maximizing_player):
    global NODES_VISITED
    NODES_VISITED += 1

    if depth == 0 or is_terminal(state):
        return evaluate(state), None

    if maximizing_player:
        best_value = float('-inf')
        best_move = None
        for move, child_state in get_successors(state):
            val, _ = alpha_beta(child_state, depth - 1, alpha, beta, False)
            if val > best_value:
                best_value = val
                best_move = move
            alpha = max(alpha, best_value)
            if alpha >= beta:
                break  # Alpha-Beta prune
        return best_value, best_move
    else:
        best_value = float('inf')
        best_move = None
        for move, child_state in get_successors(state):
            val, _ = alpha_beta(child_state, depth - 1, alpha, beta, True)
            if val < best_value:
                best_value = val
                best_move = move
            beta = min(beta, best_value)
            if beta <= alpha:
                break  # Alpha-Beta prune
        return best_value, best_move

def computer_move(state, algorithm, depth=10):
    """
    Decide which multiplier (2, 3, or 4) the computer will use,
    based on the selected algorithm (Minimax or Alpha-Beta).
    """
    if algorithm == "Minimax":
        _, move = minimax(state, depth, True)
    else:
        _, move = alpha_beta(state, depth, float('-inf'), float('inf'), True)
    return move

###############################################################################
# Tkinter GUI
###############################################################################

class GameGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("Multiplication Game (Even=Opponent -1, Odd=+1)")

        # Use a ttk.Style for a cleaner look
        style = ttk.Style()
        style.theme_use("clam")

        # Variables for user settings
        self.initial_num = tk.IntVar(value=8)
        self.first_player = tk.StringVar(value="Human")
        self.algorithm = tk.StringVar(value="Minimax")

        # Game state variables
        self.state = None
        self.game_over = False

        # Tracking stats
        self.nodes_label_var = tk.StringVar(value="Visited Nodes: 0")
        self.time_label_var = tk.StringVar(value="Move Time: 0.000s")
        self.status_label_var = tk.StringVar(value="No game in progress.")

        # Scoreboard variables
        self.human_score_var = tk.StringVar(value="Human Score: 0")
        self.computer_score_var = tk.StringVar(value="Computer Score: 0")
        self.current_number_var = tk.StringVar(value="Current Number: 0")

        self.create_widgets()

    def create_widgets(self):
        # Top frame for settings
        top_frame = ttk.Frame(self.root, padding=10)
        top_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(top_frame, text="Initial Number (8–18):").grid(row=0, column=0, sticky=tk.W, padx=5)
        spin = ttk.Spinbox(top_frame, from_=8, to=18, textvariable=self.initial_num, width=5)
        spin.grid(row=0, column=1, sticky=tk.W, padx=5)

        ttk.Label(top_frame, text="Who starts:").grid(row=1, column=0, sticky=tk.W, padx=5)
        who_menu = ttk.OptionMenu(top_frame, self.first_player, "Human", "Human", "Computer")
        who_menu.grid(row=1, column=1, sticky=tk.W, padx=5)

        ttk.Label(top_frame, text="Algorithm:").grid(row=2, column=0, sticky=tk.W, padx=5)
        algo_menu = ttk.OptionMenu(top_frame, self.algorithm, "Minimax", "Minimax", "Alpha-Beta")
        algo_menu.grid(row=2, column=1, sticky=tk.W, padx=5)

        start_btn = ttk.Button(top_frame, text="Start Game", command=self.start_game)
        start_btn.grid(row=3, column=0, pady=5, sticky=tk.E)
        restart_btn = ttk.Button(top_frame, text="Restart", command=self.restart_game)
        restart_btn.grid(row=3, column=1, pady=5, sticky=tk.W)

        # Scoreboard frame
        scoreboard_frame = ttk.Frame(self.root, padding=10)
        scoreboard_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(scoreboard_frame, textvariable=self.human_score_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=20)
        ttk.Label(scoreboard_frame, textvariable=self.computer_score_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=20)
        ttk.Label(scoreboard_frame, textvariable=self.current_number_var, font=("Arial", 10, "bold")).pack(side=tk.LEFT, padx=20)

        # Middle frame for status
        mid_frame = ttk.Frame(self.root, padding=10)
        mid_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(mid_frame, textvariable=self.status_label_var, foreground="blue").pack(anchor=tk.W)
        ttk.Label(mid_frame, textvariable=self.nodes_label_var).pack(anchor=tk.W)
        ttk.Label(mid_frame, textvariable=self.time_label_var).pack(anchor=tk.W)

        # Bottom frame for moves
        bottom_frame = ttk.Frame(self.root, padding=10)
        bottom_frame.pack(side=tk.TOP, fill=tk.X)

        ttk.Label(bottom_frame, text="Your Move: ").pack(side=tk.LEFT)
        for m in [2, 3, 4]:
            btn = ttk.Button(bottom_frame, text=f"x{m}", command=lambda mul=m: self.user_move(mul))
            btn.pack(side=tk.LEFT, padx=5)

    def start_game(self):
        global NODES_VISITED
        NODES_VISITED = 0
        self.nodes_label_var.set("Visited Nodes: 0")
        self.time_label_var.set("Move Time: 0.000s")
        self.game_over = False

        init_num = self.initial_num.get()
        first_p = Player.HUMAN if self.first_player.get() == "Human" else Player.COMPUTER

        self.state = GameState(
            current_number=init_num,
            human_score=0,
            computer_score=0,
            current_player=first_p
        )
        self.update_display()

        # If computer goes first, let it move after a short delay
        if self.state.current_player == Player.COMPUTER:
            self.root.after(500, self.computer_turn)

    def restart_game(self):
        self.start_game()

    def user_move(self, multiplier):
        if self.game_over or self.state.current_player != Player.HUMAN:
            return
        self.apply_move(multiplier)
        self.update_display()
        if not self.game_over and self.state.current_player == Player.COMPUTER:
            self.root.after(500, self.computer_turn)

    def computer_turn(self):
        if self.game_over or self.state.current_player != Player.COMPUTER:
            return

        global NODES_VISITED
        NODES_VISITED = 0

        start_time = time.time()
        move = computer_move(self.state, self.algorithm.get(), depth=10)
        elapsed = time.time() - start_time

        self.nodes_label_var.set(f"Visited Nodes: {NODES_VISITED}")
        self.time_label_var.set(f"Move Time: {elapsed:.3f}s")

        self.apply_move(move)
        self.update_display()

    def apply_move(self, multiplier):
        """
        Multiply the current number by 2, 3, or 4.
        - If even => opponent's score -1
        - If odd  => current player's score +1
        - If result >= 1200 => game ends immediately
        """
        new_number = self.state.current_number * multiplier

        if new_number % 2 == 0:
            # Even => Opponent loses 1 point
            if self.state.current_player == Player.HUMAN:
                self.state.computer_score -= 1
            else:
                self.state.human_score -= 1
        else:
            # Odd => Current player gains 1 point
            if self.state.current_player == Player.HUMAN:
                self.state.human_score += 1
            else:
                self.state.computer_score += 1

        self.state.current_number = new_number

        if new_number >= 1200:
            # Game ends immediately
            self.game_over = True
        else:
            # Switch turn if game not over
            if self.state.current_player == Player.HUMAN:
                self.state.current_player = Player.COMPUTER
            else:
                self.state.current_player = Player.HUMAN

    def update_display(self):
        """
        Refresh scoreboard and status message.
        """
        if not self.state:
            self.status_label_var.set("No game in progress.")
            return

        self.human_score_var.set(f"Human Score: {self.state.human_score}")
        self.computer_score_var.set(f"Computer Score: {self.state.computer_score}")
        self.current_number_var.set(f"Current Number: {self.state.current_number}")

        if is_terminal(self.state):
            # Check final scores for winner
            if self.state.human_score > self.state.computer_score:
                self.status_label_var.set("--- GAME OVER ---  Human Wins!")
            elif self.state.computer_score > self.state.human_score:
                self.status_label_var.set("--- GAME OVER ---  Computer Wins!")
            else:
                self.status_label_var.set("--- GAME OVER ---  It's a Tie!")
        else:
            current = "Human" if self.state.current_player == Player.HUMAN else "Computer"
            self.status_label_var.set(f"Current Player: {current}")

###############################################################################
# Main Entry Point
###############################################################################

if __name__ == "__main__":
    root = tk.Tk()
    GameGUI(root)
    root.mainloop()
