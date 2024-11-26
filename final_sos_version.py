import tkinter as tk
from tkinter import messagebox
import random
import openai
import os


class Team:
    def __init__(self, name, color, is_computer=False):
        self.name = name
        self.color = color
        self.score = 0
        self.is_computer = is_computer


class Square:
    def __init__(self, row, col, button):
        self.row = row
        self.col = col
        self.button = button
        self.state = "empty"

    def mark(self, letter, team):
        self.state = "full"
        self.button.config(text=letter, fg=team.color)
        return f"{team.name} placed '{letter}' at ({self.row}, {self.col})"


class Board:
    def __init__(self, root, rows, cols, on_square_click):
        self.rows = rows
        self.cols = cols
        self.squares = {}
        self.on_square_click = on_square_click
        self.create_board(root)

    def create_board(self, root):
        for row in range(self.rows):
            for col in range(self.cols):
                button = tk.Button(root, text="", width=5, height=2,
                                   command=lambda r=row, c=col: self.on_square_click(r, c))
                button.grid(row=row + 4, column=col, padx=2, pady=2)
                self.squares[(row, col)] = Square(row, col, button)

    def get_square(self, row, col):
        return self.squares.get((row, col))

    def reset_board(self):
        for square in self.squares.values():
            square.state = "empty"
            square.button.config(text="")


class Game:
    def __init__(self, root):
        self.root = root
        self.root.title("SOS Game - Save vs Souls")

        self.game_log = []  # To store moves for recording
        self.log_file_path = "sos_game_log.txt"  # Default log file path

        self.team_save = Team("Red", "red")
        self.team_souls = Team("Blue", "blue")
        self.current_team = self.team_save

        self.game_mode = "simple"
        self.board_size = 5
        self.letter_choice = tk.StringVar(value="S")
        self.setup_ui()
        self.board = None




    def make_computer_move(self):
        """
        Handles the computer's turn, makes one move, and switches control.
        """
        # Find all empty squares
        empty_squares = [(row, col) for (row, col), square in self.board.squares.items() if square.state == "empty"]

        # No available moves, end the game
        if not empty_squares:
            self.status_label.config(text="No moves available. Game Over!")
            self.end_game(f"{self.get_winner()} wins! Final Scores - Save: {self.team_save.score}, Souls: {self.team_souls.score}")
            return

        # Select a strategic or random move
        row, col = self.choose_best_move()
        selected_letter = self.choose_best_letter(row, col)

        # Set the letter and play the move
        self.letter_choice.set(selected_letter)
        self.handle_move(row, col)

        # Check for game-end conditions
        if self.check_game_end_conditions():
            return

        # Relinquish control and switch turn to the other team
        self.switch_turn()



    def choose_best_move(self):
        """
        Intelligent move selection for the computer to prioritize scoring opportunities.
        Defaults to a random move if no strategic moves are found.
        """
        for (row, col), square in self.board.squares.items():
            if square.state == "empty":
                # Simulate placing an "S" or "O" and evaluate potential SOS
                if self.is_potential_sos(row, col, "S") or self.is_potential_sos(row, col, "O"):
                    return row, col
        # If no strategic move, pick a random empty square
        empty_squares = [(row, col) for (row, col), square in self.board.squares.items() if square.state == "empty"]
        return random.choice(empty_squares)



    def choose_best_letter(self, row, col):
        """
        Intelligent letter selection for maximizing the chance of scoring SOS.
        """
        if self.is_potential_sos(row, col, "S"):
            return "S"
        elif self.is_potential_sos(row, col, "O"):
            return "O"
        return random.choice(["S", "O"])  # Fallback to random if no clear choice


    def is_potential_sos(self, row, col, letter):
        """
        Determines if placing a specific letter at (row, col) creates an SOS.
        """
        # Simulate the placement and check all directions
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]
        for drow, dcol in directions:
            if letter == "S" and self.get_letter_at(row + drow, col + dcol) == "O" and self.get_letter_at(row + 2 * drow, col + 2 * dcol) == "S":
                return True
            if letter == "O" and self.get_letter_at(row - drow, col - dcol) == "S" and self.get_letter_at(row + drow, col + dcol) == "S":
                return True
        return False


    def check_game_end_conditions(self):
        """
        Checks if the game has reached an end state and handles it.
        """
        if self.game_mode == "simple" and self.current_team.score > 0:
            self.end_game(f"{self.current_team.name} wins by creating an SOS!")
            return True

        if self.game_mode == "general":
            empty_squares = [sq for sq in self.board.squares.values() if sq.state == "empty"]
            if not empty_squares:
                winner = self.get_winner()
                self.end_game(f"Game Over! {winner} wins! Final Scores - Save: {self.team_save.score}, Souls: {self.team_souls.score}")
                return True

        return False

         
    def handle_move(self, row, col):
        """
        Processes a move by the current team and updates the board state.
        """
        square = self.board.get_square(row, col)

        if square.state == "full":
            self.status_label.config(text=f"Square ({row}, {col}) is already full")
            return

        selected_letter = self.letter_choice.get()
        message = square.mark(selected_letter, self.current_team)
        self.status_label.config(text=message)

        # Add move to game log
        self.game_log.append(f"{self.current_team.name},{row},{col},{selected_letter}")

        # Check SOS and update score
        score = self.check_sos(row, col, selected_letter)
        if score > 0:
            self.current_team.score += score
            self.status_label.config(text=f"{self.current_team.name} scored! {self.current_team.score} points")



    def save_game_log(self):
        try:
            # Save metadata as the first lines in the log
            metadata = f"Mode:{self.game_mode}\nSize:{self.board_size}"
            with open(self.log_file_path, 'w') as log_file:
                log_file.write(metadata + "\n")
                log_file.write("\n".join(self.game_log))
            messagebox.showinfo("Game Log Saved", "The game log has been saved successfully!")
        except IOError as e:
            messagebox.showerror("Save Error", f"Failed to save the game log: {e}")


    def load_game_log(self):
        try:
            if os.path.exists(self.log_file_path):
                with open(self.log_file_path, 'r') as log_file:
                    lines = log_file.readlines()
                    # Extract metadata
                    metadata = lines[:2]  # First two lines are metadata
                    game_log = lines[2:]  # Remaining lines are moves
                    self.game_mode = metadata[0].strip().split(":")[1]
                    self.board_size = int(metadata[1].strip().split(":")[1])
                    return game_log
            else:
                return []
        except IOError as e:
            print(f"Error loading game log: {e}")
            return []


    def replay_game(self):
        log = self.load_game_log()
        if not log:
            messagebox.showinfo("Replay", "No game log available for replay.")
            return

        def make_move_from_log(index):
            if index < len(log):
                move = log[index].strip().split(",")
                team_name, row, col, letter = move
                row, col = int(row), int(col)
                self.letter_choice.set(letter)
                self.current_team = self.team_save if team_name == self.team_save.name else self.team_souls
                self.handle_move(row, col)
                self.root.after(1000, lambda: make_move_from_log(index + 1))

        # Reset the game with the loaded metadata
        self.board_size = self.board_size  # Already set in `load_game_log`
        self.game_mode = self.game_mode   # Already set in `load_game_log`
        self.start_new_game()  # Initialize a new game with the correct settings
        make_move_from_log(0)



    def end_game(self, message):
        messagebox.showinfo("Game Over", message)
        save_log = messagebox.askyesno("Save Game Log", "Do you want to save the game log?")
        if save_log:
            self.save_game_log()
        else:
            self.game_log = []
            messagebox.showinfo("Game Log Discarded", "The game log has been discarded.")
        self.start_new_game()

    def reset_game(self):
        self.board.reset_board()
        self.current_team = self.team_save
        self.team_save.score = 0
        self.team_souls.score = 0
        self.game_log = []  # Clear the log when a new game starts
        self.status_label.config(text="New game started.")
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")

    def setup_ui(self):
        tk.Label(self.root, text="Choose letter:").grid(row=0, column=0, columnspan=2)
        tk.Radiobutton(self.root, text="S", variable=self.letter_choice, value="S").grid(row=1, column=0)
        tk.Radiobutton(self.root, text="O", variable=self.letter_choice, value="O").grid(row=1, column=1)

        tk.Button(self.root, text="Replay Game", command=self.replay_game).grid(row=3, column=4)

        tk.Label(self.root, text="Game Mode:").grid(row=2, column=0, columnspan=2)
        self.mode_choice = tk.StringVar(value="simple")
        tk.Radiobutton(self.root, text="Simple", variable=self.mode_choice, value="simple").grid(row=3, column=0)
        tk.Radiobutton(self.root, text="General", variable=self.mode_choice, value="general").grid(row=3, column=1)

        tk.Label(self.root, text="Board Size:").grid(row=0, column=2, columnspan=2)
        self.board_size_entry = tk.Entry(self.root, width=5)
        self.board_size_entry.grid(row=1, column=2, columnspan=2)
        self.board_size_entry.insert(0, "5")

        tk.Button(self.root, text="Start New Game", command=self.start_new_game).grid(row=2, column=2, columnspan=2)

        self.status_label = tk.Label(self.root, text="Click a square to fill it",
                                     font=("Helvetica", 14, "bold"), bg="lightblue",
                                     fg="darkblue", pady=10, padx=10, borderwidth=2, relief="groove")
        self.status_label.grid(row=12, column=0, columnspan=10, pady=10)

        self.turn_label = tk.Label(self.root, text=f"Current turn: {self.current_team.name}",
                                   font=("Helvetica", 12, "bold"), bg="lightgrey", fg="black", pady=5)
        self.turn_label.grid(row=13, column=0, columnspan=10, pady=10)

    def start_new_game(self):
        try:
            self.board_size = int(self.board_size_entry.get())
            if self.board_size < 3:
                raise ValueError("Board size must be at least 3.")
        except ValueError:
            messagebox.showerror("Invalid Board Size", "Please enter a valid integer greater than 2.")
            return

        self.game_mode = self.mode_choice.get()
        self.team_save.is_computer = messagebox.askyesno("Select Player", "Is Red team a computer?")
        self.team_souls.is_computer = messagebox.askyesno("Select Player", "Is Blue team a computer?")
        self.current_team = self.team_save
        self.team_save.score = 0
        self.team_souls.score = 0
        self.status_label.config(text="Click a square to fill it")
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")

        if self.board:
            self.board.reset_board()
        else:
            self.board = Board(self.root, self.board_size, self.board_size, self.on_square_click)




    def on_square_click(self, row, col):
        """
        Handles clicks on the board squares and ensures proper turn alternation.
        """
        if not self.current_team.is_computer:
            # Handle human player's move
            self.handle_move(row, col)

            # Check if the game ends after the move
            if self.check_game_end_conditions():
                return

            # Switch turn to the computer if necessary
            self.switch_turn()
        else:
            # If it's the computer's turn (unlikely on click), force a computer move
            self.make_computer_move()


    def switch_turn(self):
        """
        Switches the turn to the other team and handles computer player logic.
        """
        # Alternate between the two teams
        self.current_team = self.team_souls if self.current_team == self.team_save else self.team_save
        self.turn_label.config(text=f"Current turn: {self.current_team.name}")

        # If the next team is a computer, make its move
        if self.current_team.is_computer:
            self.root.after(500, self.make_computer_move)






    def check_sos(self, row, col, letter):
        score = 0
        directions = [
            (-1, -1), (-1, 0), (-1, 1),
            (0, -1), (0, 1),
            (1, -1), (1, 0), (1, 1)
        ]

        for drow, dcol in directions:
            if (letter == "S" and
                self.get_letter_at(row + drow, col + dcol) == "O" and
                self.get_letter_at(row + 2 * drow, col + 2 * dcol) == "S"):
                score += 1
            if (letter == "O" and
                self.get_letter_at(row - drow, col - dcol) == "S" and
                self.get_letter_at(row + drow, col + dcol) == "S"):
                score += 1
            if (letter == "S" and
                self.get_letter_at(row - 2 * drow, col - 2 * dcol) == "S" and
                self.get_letter_at(row - drow, col - dcol) == "O"):
                score += 1

        return score

    def get_letter_at(self, row, col):
        square = self.board.get_square(row, col)
        return square.button["text"] if square and square.state == "full" else None

    def get_winner(self):
        if self.team_save.score > self.team_souls.score:
            return self.team_save.name
        elif self.team_save.score < self.team_souls.score:
            return self.team_souls.name
        return "It's a tie!"


root = tk.Tk()
game = Game(root)
root.mainloop()
